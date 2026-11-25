"""Measure Windows-local synthetic HTTP read and Job Object recovery."""
import _winapi as win
import argparse
import base64
import ctypes as ct
from ctypes import wintypes as wt
from datetime import datetime, timezone
import hashlib
import http.client
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import threading
import time
import traceback


CLOCK = time.perf_counter_ns
SECOND = 1_000_000_000
PREFIX = b"\x00stage1b\xff"
BODY = PREFIX + b"\r\ncomplete\n"
FORCED_EXIT = 77
DETACHED_PROCESS = 0x8
CONNECT_AUTHORITY = "fixture.invalid:80"
LIMITS = [
    # name, fixture, connect, stop, force, reclaim, reader behavior, expected reason
    ("normal", "normal", 10, 24.5, 24.75, 25, "cooperate", "complete"),
    ("missing", "missing", 10, 24.5, 24.75, 25, "cooperate", "missing"),
    ("connect-short", "connect", 1, 1, 1.25, 2, "cooperate", "connect_deadline"),
    ("body-short", "body", 1, 1, 1.25, 2, "cooperate", "total_stop"),
    ("connect-10", "connect", 10, 10, 10.25, 25, "cooperate", "connect_deadline"),
    ("body-25-reserve", "body", 10, 24.5, 24.75, 25, "cooperate", "total_stop"),
    ("ignore-stop", "body", 10, 24.5, 24.75, 25, "ignore", "forced"),
    ("process-tree", "body", 10, 24.5, 24.75, 25, "tree", "forced"),
    ("near-before", "near-before", 10, 24.5, 24.75, 25, "cooperate", "complete"),
    ("boundary-25", "boundary-25", 10, 25, 25.25, 25, "cooperate", "total_stop"),
]
CASE_KEYS = ("name", "fixture", "connect_s", "stop_s", "force_s", "limit_s", "mode", "expected")


def stamp():
    return {"mono_ns": CLOCK(), "utc": datetime.now(timezone.utc).isoformat()}


def event(name, **data):
    return {"event": name, **stamp(), **data}


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def append_event(path, kind, **data):
    row = event(kind, pid=os.getpid(), **data)
    with path.open("ab", buffering=0) as stream:
        stream.write((json.dumps(row) + "\n").encode("ascii"))


def read_events(path, *, final=False):
    if not path.exists():
        return []
    raw = path.read_bytes()
    if final and raw and not raw.endswith(b"\n"):
        raise ValueError(f"incomplete event record: {path.name}")
    return [json.loads(line) for line in raw.split(b"\n")[:-1]]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class BasicLimit(ct.Structure):
    _fields_ = [
        ("process_time", ct.c_int64), ("job_time", ct.c_int64), ("flags", wt.DWORD),
        ("min_working_set", ct.c_size_t), ("max_working_set", ct.c_size_t),
        ("active_limit", wt.DWORD), ("affinity", ct.c_size_t),
        ("priority_class", wt.DWORD), ("scheduling_class", wt.DWORD),
    ]


class Accounting(ct.Structure):
    _fields_ = [
        ("user", ct.c_int64), ("kernel", ct.c_int64),
        ("period_user", ct.c_int64), ("period_kernel", ct.c_int64),
        ("page_faults", wt.DWORD), ("total", wt.DWORD),
        ("active", wt.DWORD), ("limit_terminated", wt.DWORD),
    ]


class ExtendedLimit(ct.Structure):
    _fields_ = [
        ("basic", BasicLimit), ("io_counts", ct.c_uint64 * 6),
        ("process_memory_limit", ct.c_size_t), ("job_memory_limit", ct.c_size_t),
        ("peak_process_memory", ct.c_size_t), ("peak_job_memory", ct.c_size_t),
    ]


kernel = ct.WinDLL("kernel32", use_last_error=True)


def bind(name, result, *args):
    fn = getattr(kernel, name)
    fn.argtypes = args
    fn.restype = result
    return fn


create_job = bind("CreateJobObjectW", wt.HANDLE, wt.LPVOID, wt.LPCWSTR)
set_job = bind("SetInformationJobObject", wt.BOOL, wt.HANDLE, ct.c_int, wt.LPVOID, wt.DWORD)
query_job = bind("QueryInformationJobObject", wt.BOOL, wt.HANDLE, ct.c_int, wt.LPVOID, wt.DWORD, wt.LPVOID)
assign_job = bind("AssignProcessToJobObject", wt.BOOL, wt.HANDLE, wt.HANDLE)
terminate_job = bind("TerminateJobObject", wt.BOOL, wt.HANDLE, wt.UINT)
is_in_job = bind("IsProcessInJob", wt.BOOL, wt.HANDLE, wt.HANDLE, ct.POINTER(wt.BOOL))
resume = bind("ResumeThread", wt.DWORD, wt.HANDLE)


def checked(result):
    if not result:
        raise ct.WinError(ct.get_last_error())
    return result


def job_account(job):
    data = Accounting()
    checked(query_job(job, 1, ct.byref(data), ct.sizeof(data), None))
    return {"total": data.total, "active": data.active, "limit_terminated": data.limit_terminated}


def job_member(handle, job):
    result = wt.BOOL()
    checked(is_in_job(handle, job, ct.byref(result)))
    return bool(result.value)


class PipeStream:
    """A duplex stream from two inherited anonymous, local Windows pipes."""

    def __init__(self, incoming, outgoing, stopped):
        self.incoming = incoming
        self.outgoing = outgoing
        self.stopped = stopped
        self.deadline = None
        self.buffer = bytearray()

    def makefile(self, mode):
        if mode != "rb":
            raise ValueError("only binary input is supported")
        return self

    def close(self):
        # HTTPResponse closes its parser view. The endpoint owns both handles.
        pass

    def flush(self):
        # Writes go directly to the pipe.
        pass

    def close_handles(self):
        win.CloseHandle(self.incoming)
        win.CloseHandle(self.outgoing)

    def check(self):
        if self.deadline is not None and CLOCK() >= self.deadline:
            raise TimeoutError("absolute connection deadline")
        return self.stopped()

    def sendall(self, data):
        count, error = win.WriteFile(self.outgoing, data)
        if error or count != len(data):
            raise OSError("incomplete local pipe write")

    def read_pipe(self, limit):
        while not self.check():
            try:
                available, _ = win.PeekNamedPipe(self.incoming, 0)
                if available:
                    data, error = win.ReadFile(self.incoming, min(available, limit))
                    if error:
                        raise OSError(error, "local pipe read failed")
                    return data
            except OSError as error:
                if getattr(error, "winerror", None) in (109, 232):
                    return b""
                raise
            time.sleep(0.002)
        return b""

    def readline(self, limit):
        while len(self.buffer) < limit and b"\n" not in self.buffer:
            chunk = self.read_pipe(limit - len(self.buffer))
            if not chunk:
                break
            self.buffer.extend(chunk)
        newline = self.buffer.find(b"\n", 0, limit)
        end = newline + 1 if newline >= 0 else min(limit, len(self.buffer))
        data = bytes(self.buffer[:end])
        del self.buffer[:end]
        return data

    def read1(self, limit):
        if limit == 0:
            return b""
        if not self.buffer:
            return self.read_pipe(limit)
        data = bytes(self.buffer[:limit])
        del self.buffer[:limit]
        return data


def reader(folder, incoming, outgoing, mode, origin, connect_ns):
    log = folder / "reader.jsonl"
    append_event(log, "reader_started", ppid=os.getppid())
    for handle in (incoming, outgoing):
        os.set_handle_inheritable(handle, False)
    if mode == "tree":
        child = subprocess.Popen(
            [sys.executable, "-B", __file__, "--leaf", str(folder)],
            creationflags=DETACHED_PROCESS,
        )
        append_event(log, "child_created", child_pid=child.pid)
    acknowledged = False

    def stopped():
        nonlocal acknowledged
        if not acknowledged and (folder / "stop").exists():
            acknowledged = True
            append_event(log, "stop_received", honored=mode == "cooperate")
        return acknowledged and mode == "cooperate"

    connection = PipeStream(incoming, outgoing, stopped)
    connection.deadline = origin + connect_ns
    connected = False
    try:
        connection.check()
        append_event(log, "pipe_endpoints_ready")
        connection.sendall(f"CONNECT {CONNECT_AUTHORITY} HTTP/1.1\r\nHost: {CONNECT_AUTHORITY}\r\n\r\n".encode())
        tunnel = http.client.HTTPResponse(connection, method="HEAD")
        tunnel.begin()
        tunnel.close()
        connection.check()
        if tunnel.status != 200:
            raise ValueError("unexpected synthetic CONNECT status")
        connected = True
        append_event(log, "tunnel_connected", proxy_status=tunnel.status)
        connection.deadline = None
        connection.sendall(b"GET /target HTTP/1.1\r\nHost: fixture.invalid\r\nConnection: close\r\n\r\n")
        response = http.client.HTTPResponse(connection, method="GET")
        try:
            response.begin()
            append_event(log, "http_status", status=response.status, declared_body_bytes=response.length)
            with (folder / "body.bin").open("xb", buffering=0) as payload:
                while chunk := response.read1(4096):
                    payload.write(chunk)
            if stopped():
                reason, code = "total_stop", 21
            elif response.length:
                reason, code = "incomplete_response", 23
            else:
                reason, code = {200: ("complete", 0), 404: ("missing", 4)}.get(
                    response.status, ("unexpected_http_status", 23))
        finally:
            response.close()
    except TimeoutError:
        if connected:
            raise
        append_event(log, "connect_deadline_observed")
        reason, code = "connect_deadline", 20
    except http.client.HTTPException:
        if not stopped():
            raise
        reason, code = ("total_stop", 21) if connected else ("connect_deadline", 20)
    finally:
        connection.close_handles()
    append_event(log, "reader_exit_intent", reason=reason, code=code)
    return code


def leaf(folder):
    append_event(folder / "leaf.jsonl", "leaf_started", ppid=os.getppid())
    threading.Event().wait()


def request_headers(connection):
    first = connection.readline(4096)
    for line in iter(lambda: connection.readline(4096), b"\r\n"):
        if not line:
            raise EOFError("synthetic request headers ended before terminator")
    return first


class Fixture:
    def __init__(self, scenario):
        self.scenario = scenario
        self.cancel = threading.Event()
        server_in, reader_out = win.CreatePipe(None, 0)
        try:
            reader_in, server_out = win.CreatePipe(None, 0)
        except OSError:
            win.CloseHandle(server_in)
            win.CloseHandle(reader_out)
            raise
        self.reader_handles = [reader_in, reader_out]
        self.stream = PipeStream(server_in, server_out, self.cancel.is_set)
        self.events = []
        self.thread = None

    def start(self, origin):
        self.thread = threading.Thread(target=self.serve, args=(origin,))
        self.thread.start()

    def close(self):
        self.close_reader_handles()
        self.cancel.set()
        if self.thread:
            self.thread.join(timeout=2)
        self.stream.close_handles()
        return self.thread is None or not self.thread.is_alive()

    def close_reader_handles(self):
        for handle in self.reader_handles:
            win.CloseHandle(handle)
        self.reader_handles.clear()

    def serve(self, origin):
        def record(kind, **data):
            self.events.append(event(kind, **data))

        def wait_peer(until):
            connection.deadline = until
            try:
                if connection.read1(1):
                    raise ValueError("unexpected bytes while fixture response stalled")
                if not self.cancel.is_set():
                    record("fixture_peer_eof")
                return False
            except TimeoutError:
                return not self.cancel.is_set()
            finally:
                connection.deadline = None

        connection = self.stream
        try:
            if request_headers(connection) != f"CONNECT {CONNECT_AUTHORITY} HTTP/1.1\r\n".encode():
                raise ValueError("unexpected CONNECT request")
            record("fixture_connect_received")
            if self.scenario == "connect":
                wait_peer(origin + 30 * SECOND)
                return
            connection.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            if request_headers(connection) != b"GET /target HTTP/1.1\r\n":
                raise ValueError("unexpected GET request")
            record("fixture_get_received")
            if self.scenario == "missing":
                connection.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
                return
            headers = f"HTTP/1.1 200 OK\r\nContent-Length: {len(BODY)}\r\nConnection: close\r\n\r\n".encode()
            connection.sendall(headers + PREFIX)
            record("fixture_prefix_sent", size=len(PREFIX))
            releases = {"normal": 0, "near-before": 24.2, "boundary-25": 25.2, "body": 30}
            release = origin + int(releases[self.scenario] * SECOND)
            if wait_peer(release) and self.scenario != "body":
                connection.sendall(BODY[len(PREFIX):])
                record("fixture_tail_sent")
        except (OSError, ValueError, EOFError) as error:
            if not self.cancel.is_set():
                record("fixture_error", detail=repr(error))
        finally:
            record("fixture_finished")


def monitor(case, folder, job, root, origin, handles, observations, timeline):
    stop_path = folder / "stop"
    stop_due = None
    stop_at = origin + int(case["stop_s"] * SECOND)
    force_at = origin + int(case["force_s"] * SECOND)
    connect_at = origin + int(case["connect_s"] * SECOND)
    hard_at = origin + int(case["limit_s"] * SECOND)
    connected = False
    while True:
        account = job_account(job)
        reader_events = read_events(folder / "reader.jsonl")
        connected |= any(e["event"] == "tunnel_connected" and e["mono_ns"] <= connect_at
                         for e in reader_events)
        for row in reader_events:
            if row["event"] == "child_created" and row["child_pid"] not in handles:
                pid = row["child_pid"]
                handle = win.OpenProcess(0x100000 | 0x0400 | 0x1000, False, pid)
                if not job_member(handle, job):
                    win.CloseHandle(handle)
                    raise ValueError("announced child is outside the dedicated Job")
                handles[pid] = handle
                timeline.append(event("child_handle_verified", pid=pid, ppid=root))
        for pid, handle in handles.items():
            if pid not in observations and win.WaitForSingleObject(handle, 0) == win.WAIT_OBJECT_0:
                observations[pid] = event("process_exit_observed", pid=pid,
                                          code=win.GetExitCodeProcess(handle))
                timeline.append(observations[pid])

        now = CLOCK()
        if now >= hard_at and not any(e["event"] == "hard_deadline_observed" for e in timeline):
            timeline.append(event("hard_deadline_observed", scheduled_ns=hard_at))
        if not connected and now >= connect_at and stop_due is None:
            timeline.append(event("deadline_fired", kind="connection", scheduled_ns=connect_at))
            stop_due = "connection"
        elif now >= stop_at and stop_due is None:
            timeline.append(event("deadline_fired", kind="operation_stop", scheduled_ns=stop_at))
            stop_due = "operation_stop"

        if not account["active"] and len(observations) == len(handles):
            timeline.append(event("job_empty_observed", **account))
            return account
        if stop_due and not stop_path.exists():
            timeline.append(event("stop_request", kind=stop_due))
            with stop_path.open("xb"):
                pass
            timeline.append(event("stop_request_published"))
            if stop_due == "connection":
                force_at = connect_at + SECOND // 4
        if stop_due and now >= force_at and not any(e["event"] == "force_request" for e in timeline):
            timeline.append(event("force_request", scheduled_ns=force_at))
            checked(terminate_job(job, FORCED_EXIT))
            timeline.append(event("force_request_returned"))
        if now > max(hard_at, force_at) + 2 * SECOND:
            raise TimeoutError("Job did not become observably empty within cleanup observation window")
        time.sleep(0.002)


def run_case(case, folder, run_id):
    folder.mkdir()
    timeline = []
    job = None
    fixture = None
    root = thread = None
    handles, observations = {}, {}
    setup_error = monitoring_error = None
    account = None
    origin = None
    assigned = False
    fixture_closed = False
    try:
        fixture = Fixture(case["fixture"])
        job = checked(create_job(None, None))
        limits = ExtendedLimit()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        checked(set_job(job, 9, ct.byref(limits), ct.sizeof(limits)))
        start = event("launch_begin")
        timeline.append(start)
        origin = start["mono_ns"]
        for reader_handle in fixture.reader_handles:
            os.set_handle_inheritable(reader_handle, True)
        startup = subprocess.STARTUPINFO(lpAttributeList={"handle_list": fixture.reader_handles})
        command = [sys.executable, "-B", __file__, "--reader", str(folder),
                   *(str(handle) for handle in fixture.reader_handles),
                   case["mode"], str(origin), str(int(case["connect_s"] * SECOND))]
        handle, thread, root, tid = win.CreateProcess(
            sys.executable, subprocess.list2cmdline(command), None, None, True,
            0x4 | DETACHED_PROCESS, None, None, startup,
        )
        handles[root] = handle
        timeline.append(event("process_created_suspended", pid=root, ppid=os.getpid(), tid=tid))
        fixture.close_reader_handles()
        checked(assign_job(job, handle))
        assigned = True
        checked(job_member(handle, job))
        timeline.append(event("root_job_membership_verified", pid=root))
        fixture.start(origin)
        if resume(thread) != 1:
            raise OSError("expected one suspended thread")
        timeline.append(event("process_resumed", pid=root))
        win.CloseHandle(thread)
        thread = None
        account = monitor(case, folder, job, root, origin, handles, observations, timeline)
    except (OSError, ValueError) as error:
        if any(e["event"] == "process_resumed" for e in timeline):
            monitoring_error = repr(error)
        else:
            setup_error = repr(error)
        timeline.append(event("probe_error", detail=repr(error)))
    finally:
        try:
            if account is None and assigned:
                timeline.append(event("cleanup_job_force_request"))
                checked(terminate_job(job, FORCED_EXIT))
            elif account is None and root is not None:
                timeline.append(event("cleanup_suspended_root_force_request", pid=root))
                win.TerminateProcess(handles[root], FORCED_EXIT)
            if account is None:
                for pid, handle in handles.items():
                    if win.WaitForSingleObject(handle, 2000) == win.WAIT_OBJECT_0:
                        observations[pid] = event("cleanup_exit_observed", pid=pid,
                                                  code=win.GetExitCodeProcess(handle))
                        timeline.append(observations[pid])
                if assigned:
                    timeline.append(event("cleanup_job_accounting", **job_account(job)))
        except OSError as error:
            timeline.append(event("cleanup_error", detail=repr(error)))
        finally:
            if job is not None:
                win.CloseHandle(job)
            if thread is not None:
                win.CloseHandle(thread)
            for handle in handles.values():
                win.CloseHandle(handle)
            timeline.append(event("handles_closed"))
            if fixture is not None:
                fixture_closed = fixture.close()

    evidence_error = None
    streams = {}
    for name in ("reader", "leaf"):
        try:
            streams[name] = read_events(folder / f"{name}.jsonl", final=True)
        except ValueError as error:
            evidence_error = repr(error)
            streams[name] = read_events(folder / f"{name}.jsonl")
    body_path = folder / "body.bin"
    body = body_path.read_bytes() if body_path.exists() else b""
    ended = event("collection_finished")
    timeline.append(ended)
    elapsed = None if origin is None else ended["mono_ns"] - origin
    timeline.extend(streams["reader"] + streams["leaf"] + (fixture.events if fixture else []))
    timeline.sort(key=lambda row: row["mono_ns"])
    status = next((row["status"] for row in timeline if row["event"] == "http_status"), None)
    intent = next((row for row in timeline if row["event"] == "reader_exit_intent"), None)
    root_code = observations[root]["code"] if root in observations else None
    forced = any(row["event"] == "force_request_returned" for row in timeline)
    reason = "forced" if forced and root_code == FORCED_EXIT else (intent and intent["reason"])
    expected_count = 2 if case["mode"] == "tree" else 1
    leaf_links = [(row["pid"], row["ppid"]) for row in streams["leaf"] if row["event"] == "leaf_started"]
    child_links = [(row["pid"], row["ppid"]) for row in timeline if row["event"] == "child_handle_verified"]
    residual = None if account is None else account["active"] != 0
    complete_recovery = (residual is False and len(observations) == len(handles) and fixture_closed
                         and not evidence_error)
    if complete_recovery:
        timeline.append({**ended, "event": "recovery_completed"})
    expected_reason = case["expected"]
    expected_status = None if expected_reason == "connect_deadline" else (404 if expected_reason == "missing" else 200)
    expected_body = {"complete": BODY, "missing": b"", "connect_deadline": b""}.get(expected_reason, PREFIX)
    expected_code = {"complete": 0, "missing": 4, "connect_deadline": 20, "total_stop": 21, "forced": 77}[expected_reason]
    names = {e["event"] for e in timeline}
    stop_ack = next((e for e in timeline if e["event"] == "stop_received"), None)
    mismatch = []
    if account is not None:
        if account["total"] != expected_count or len(observations) != expected_count or leaf_links != child_links:
            mismatch.append("expected process count or verified child parentage mismatch")
        reader_parent = next((row["ppid"] for row in streams["reader"]
                              if row["event"] == "reader_started"), None)
        if reader_parent != os.getpid():
            mismatch.append("reader parent PID mismatch")
        if reason != expected_reason or root_code != expected_code:
            mismatch.append("reader reason or exit code mismatch")
        if status != expected_status or body != expected_body:
            mismatch.append("HTTP status or response bytes mismatch")
        if expected_reason in {"forced", "total_stop"} and (
            not stop_ack or stop_ack["honored"] != (expected_reason == "total_stop")
        ):
            mismatch.append("cooperative stop acknowledgement mismatch")
        if expected_reason == "forced" and any(row["code"] != FORCED_EXIT for row in observations.values()):
            mismatch.append("process exit code differs from Job termination code")
        if expected_reason == "connect_deadline" and (
            not {"pipe_endpoints_ready", "fixture_connect_received", "deadline_fired"} <= names
            or "tunnel_connected" in names or "fixture_get_received" in names
        ):
            mismatch.append("connection-stage fault evidence mismatch")
        if expected_reason == "total_stop" and forced:
            mismatch.append("cooperative stop unexpectedly required force")
        if expected_reason in {"total_stop", "forced"} and not {
            "deadline_fired", "stop_request_published", "stop_received"
        } <= names:
            mismatch.append("missing deadline, stop request or acknowledgement")
        if "fixture_error" in names:
            mismatch.append("fixture reported an error")
        if elapsed > int(case["limit_s"] * SECOND):
            mismatch.append("strict recovery limit exceeded")
    if setup_error:
        verdict = "BLOCKED"
    elif mismatch or residual is True:
        verdict = "FAIL"
    elif not complete_recovery or monitoring_error:
        verdict = "UNKNOWN"
    else:
        verdict = "PASS"
    return {
        "run_id": run_id, "case": case, "supervisor_pid": os.getpid(), "root_pid": root,
        "started_at_utc": timeline[0]["utc"] if origin is not None else None,
        "ended_at_utc": ended["utc"], "elapsed_ns": elapsed, "job_accounting": account,
        "exit_observations": list(observations.values()), "exit_reason": reason,
        "exit_code": root_code, "direct_http_status": status,
        "direct_http_status_obtained": status is not None,
        "body": {"base64": base64.b64encode(body).decode(), "bytes": len(body), "sha256": digest(body),
                 "captured_file": body_path.exists(), "complete_and_accepted": verdict == "PASS" and reason == "complete"},
        "residual_processes": residual, "fixture_thread_joined": fixture_closed,
        "verdict": verdict, "mismatches": mismatch, "setup_error": setup_error,
        "monitoring_error": monitoring_error, "evidence_error": evidence_error, "timeline": timeline,
    }


def outputs(run_dir, case_names):
    run_dir.mkdir()
    run_id = run_dir.name
    cases = [dict(zip(CASE_KEYS, row)) for row in LIMITS if row[0] in case_names]
    file = Path(__file__)
    lock = {
        "run_id": run_id, "locked_at": stamp(), "clock": vars(time.get_clock_info("perf_counter")),
        "sha256": {name: digest(file.with_name(name).read_bytes()) for name in ("probe.py", "PLAN.md")},
        "cases": cases,
    }
    write_json(run_dir / "run-lock.json", lock)
    results = []
    with (run_dir / "stop-recovery.jsonl").open("x", encoding="utf-8", newline="\n") as log:
        for case in cases:
            print(f"{case['name']}: running", flush=True)
            result = run_case(case, run_dir / case["name"], run_id)
            write_json(run_dir / case["name"] / "observation.json", result)
            for row in result["timeline"]:
                log.write(json.dumps({"run_id": run_id, "case": case["name"], **row}) + "\n")
            log.flush()
            results.append(result)
            print(case["name"], result["verdict"], result["elapsed_ns"], result["mismatches"],
                  result["setup_error"], result["monitoring_error"], flush=True)
            if result["verdict"] == "BLOCKED":
                break
    write_json(run_dir / "observations.json", {
        "run_id": run_id, "comparison_id_candidate": "CODEX-LOCAL", "platform": platform.platform(),
        "python": sys.version, "supervisor_pid": os.getpid(), "supervisor_ppid": os.getppid(),
        "supervisor_in_outer_job": job_member(win.GetCurrentProcess(), None),
        "plan_lock": lock, "trials": results,
        "not_tested": [case["name"] for case in cases[len(results):]],
    })
    return 0 if all(r["verdict"] == ("FAIL" if r["case"]["name"] == "boundary-25" else "PASS")
                    and (r["verdict"] != "FAIL" or r["mismatches"] == ["strict recovery limit exceeded"])
                    for r in results) else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reader":
        _, _, folder, incoming, outgoing, mode, origin, connect_ns = sys.argv
        try:
            sys.exit(reader(Path(folder), int(incoming), int(outgoing), mode, int(origin), int(connect_ns)))
        except Exception:
            append_event(Path(folder) / "reader.jsonl", "reader_error", detail=traceback.format_exc())
            raise
    if len(sys.argv) > 1 and sys.argv[1] == "--leaf":
        leaf(Path(sys.argv[2]))
        sys.exit()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new run directory with an existing parent")
    parser.add_argument("--case", action="append", choices=[row[0] for row in LIMITS])
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output directory already exists")
    if args.output.name in ("", ".", ".."):
        parser.error("output directory needs a run name")
    sys.exit(outputs(args.output.resolve(), args.case or [row[0] for row in LIMITS]))

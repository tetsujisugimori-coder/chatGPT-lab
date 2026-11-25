"""Verify a probe run and prepare a timeline summary with no process IDs or host paths."""
import argparse
import base64
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fingerprint(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def json_lines(path):
    return [json.loads(line) for line in path.read_bytes().splitlines()]


def write_json(path, data):
    with path.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


def verify_run(run, code):
    ledger = load(run / "observations.json")
    lock = load(run / "run-lock.json")
    require(ledger["plan_lock"] == lock, "lock differs from observations")
    for filename in ("probe.py", "PLAN.md"):
        require(lock["sha256"][filename] == fingerprint((code / filename).read_bytes())["sha256"],
                f"locked SHA-256 mismatch for {filename}")
    require(not ledger["not_tested"], "run has unexecuted cases")
    require([trial["case"] for trial in ledger["trials"]] == lock["cases"], "cases differ from lock")
    log = []
    summaries = []
    for trial in ledger["trials"]:
        name = trial["case"]["name"]
        folder = run / name
        require(trial == load(folder / "observation.json"), f"{name}: raw trial differs from ledger")
        timeline = trial["timeline"]
        for row in timeline:
            log.append({"run_id": ledger["run_id"], "case": name, **row})
        times = [row["mono_ns"] for row in timeline]
        require(times == sorted(times), f"{name}: non-monotonic event order")
        require(times[0] > lock["locked_at"]["mono_ns"], f"{name}: launch preceded lock")
        for stream in ("reader", "leaf"):
            path = folder / f"{stream}.jsonl"
            if path.exists():
                entries = json_lines(path)
                require(all(entry in timeline for entry in entries), f"{name}: {stream} events missing")
        reads = trial["body"]
        raw = base64.b64decode(reads["base64"], validate=True)
        require(fingerprint(raw) == {key: reads[key] for key in ("bytes", "sha256")},
                f"{name}: raw response fails hash or size check")
        path = folder / "body.bin"
        require(path.exists() == reads["captured_file"], f"{name}: missing or extra response file")
        require(path.read_bytes() == raw if path.exists() else not raw, f"{name}: body file differs")
        indexes = {}
        for row in timeline:
            indexes.setdefault(row["event"], []).append(row)
        def elapsed(kind):
            return [row["mono_ns"] - times[0] for row in indexes.get(kind, [])]

        require(elapsed("launch_begin") == [0], f"{name}: bad launch boundary")
        require(elapsed("recovery_completed") == [trial["elapsed_ns"]], f"{name}: bad recovery")
        require(elapsed("collection_finished") == elapsed("recovery_completed"), f"{name}: missing collection")
        require(trial["fixture_thread_joined"] and trial["residual_processes"] is False
                and trial["job_accounting"]["active"] == 0 and len(elapsed("job_empty_observed")) == 1,
                f"{name}: no proof of empty Job and fixture completion")
        finished = elapsed("process_exit_observed")
        require(len(finished) == trial["job_accounting"]["total"] == len(trial["exit_observations"]),
                f"{name}: missing process exits")
        require(max(finished) <= elapsed("job_empty_observed")[0] <= elapsed("handles_closed")[0]
                <= trial["elapsed_ns"], f"{name}: out-of-order process, Job or handle observation")
        requests = elapsed("stop_request_published")
        force = elapsed("force_request")
        fired = elapsed("deadline_fired")
        if requests:
            require(len(fired) == len(requests) == 1 and fired[0] <= requests[0] < max(finished),
                    f"{name}: stop request or firing order mismatch")
        if force:
            require(len(force) == 1 and requests[0] < force[0] < min(finished), f"{name}: bad force order")
        for kind in ("deadline_fired", "hard_deadline_observed", "force_request"):
            for row in indexes.get(kind, []):
                require(row["mono_ns"] >= row["scheduled_ns"], f"{name}: early {kind}")
        status = [r["status"] for r in indexes.get("http_status", [])]
        require(status == ([trial["direct_http_status"]] if trial["direct_http_status_obtained"] else []),
                f"{name}: HTTP status lacks direct parser evidence")
        expected_fail = name == "boundary-25"
        overrun = trial["elapsed_ns"] > round(trial["case"]["limit_s"] * 1_000_000_000)
        require(overrun == expected_fail and trial["verdict"] == ("FAIL" if overrun else "PASS")
                and trial["mismatches"] == (["strict recovery limit exceeded"] if overrun else []),
                f"{name}: trial did not match the predeclared acceptance criteria")
        summaries.append({
            "case": name,
            "verdict": trial["verdict"],
            "start_utc": trial["started_at_utc"],
            "end_utc": trial["ended_at_utc"],
            "deadline_fired_ns": fired,
            "hard_deadline_observed_ns": elapsed("hard_deadline_observed"),
            "stop_request_ns": elapsed("stop_request"),
            "stop_published_ns": requests,
            "stop_received_ns": elapsed("stop_received"),
            "force_request_ns": force,
            "exit_observations_ns": finished,
            "job_empty_ns": elapsed("job_empty_observed"),
            "recovery_ns": trial["elapsed_ns"],
            "process_count": trial["job_accounting"]["total"],
            "active_at_recovery": trial["job_accounting"]["active"],
            "exit_codes": [row["code"] for row in trial["exit_observations"]],
            "exit_reason": trial["exit_reason"],
            "direct_synthetic_http_status": trial["direct_http_status"],
            "response": fingerprint(raw),
            "accepted_as_complete": reads["complete_and_accepted"],
            "observation_fingerprint": fingerprint((folder / "observation.json").read_bytes()),
        })
    require(log == json_lines(run / "stop-recovery.jsonl"), "stop and recovery log differs from raw ledger")
    return {
        "schema_version": 1,
        "run_id": ledger["run_id"],
        "source_files": {p: fingerprint((run / p).read_bytes())
                         for p in ("observations.json", "stop-recovery.jsonl", "run-lock.json")},
        "plan_lock": lock,
        "trials": summaries,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--summary", type=Path, help="optional new destination for the public summary")
    args = parser.parse_args()
    summary = verify_run(args.run, Path(__file__).resolve().parent)
    if args.summary:
        write_json(args.summary, summary)
    print(f"{len(summary['trials'])} trials verified against the frozen plan and local raw evidence")

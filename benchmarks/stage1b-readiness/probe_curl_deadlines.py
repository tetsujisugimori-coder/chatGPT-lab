"""Check curl deadlines against loopback fixtures only."""

from concurrent.futures import ThreadPoolExecutor
import json
import socket
import subprocess
from time import monotonic


def serve_once(listener, mode):
    connection, _ = listener.accept()
    with connection:
        connection.settimeout(33)
        if mode == "connect-timeout":
            # Accept TCP but never answer the TLS ClientHello.
            assert connection.recv(1) == b"\x16", "expected a TLS handshake"
        else:
            with connection.makefile("rb") as request:
                assert request.readline().startswith(b"GET /fixture HTTP/"), "unexpected request"
                for header in request:
                    if header == b"\r\n":
                        break
            responses = {
                "ok": b"200 OK\r\nContent-Length: 2\r\n\r\nok",
                "missing": b"404 Not Found\r\nContent-Length: 0\r\n\r\n",
                "total-timeout": b"200 OK\r\nContent-Length: 2\r\n\r\nx",
            }
            connection.sendall(b"HTTP/1.1 " + responses[mode])
            if mode in {"ok", "missing"}:
                return
        while connection.recv(4096):
            pass


def probe(mode, expected):
    scheme = "https" if mode == "connect-timeout" else "http"
    with socket.socket() as listener, ThreadPoolExecutor(max_workers=1) as server:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        listener.settimeout(5)
        port = listener.getsockname()[1]
        serving = server.submit(serve_once, listener, mode)
        started = monotonic()
        result = subprocess.run(
            ["curl", "-q", "--noproxy", "*", "--silent", "--show-error",
             "--connect-timeout", "10", "--max-time", "25",
             "--write-out", "\n%{http_code}\n",
             f"{scheme}://127.0.0.1:{port}/fixture"],
            capture_output=True, timeout=30, check=False,
        )
        elapsed = monotonic() - started
        serving.result()

    body, http_code = result.stdout.removesuffix(b"\n").rsplit(b"\n", 1)
    exit_code, status, expected_body, minimum, maximum = expected
    assert (result.returncode, http_code.decode(), body) == (exit_code, status, expected_body), (
        mode, result.returncode, result.stdout, result.stderr,
    )
    assert minimum <= elapsed < maximum, (mode, elapsed, minimum, maximum)
    return {
        "case": mode,
        "curl_exit": result.returncode,
        "http_code": None if http_code == b"000" else int(http_code),
        "body_bytes": len(body),
        "elapsed_seconds": round(elapsed, 6),
    }


def main():
    # Measurement windows allow local process startup and scheduler delay.
    cases = {
        "ok": (0, "200", b"ok", 0, 5),
        "missing": (0, "404", b"", 0, 5),
        "connect-timeout": (28, "000", b"", 9.5, 11),
        "total-timeout": (28, "200", b"x", 24.5, 26),
    }
    with ThreadPoolExecutor(max_workers=len(cases)) as pool:
        tasks = [pool.submit(probe, mode, expected) for mode, expected in cases.items()]
        print(json.dumps([task.result() for task in tasks], indent=2))


if __name__ == "__main__":
    main()

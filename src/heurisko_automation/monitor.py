from __future__ import annotations

import time
from pathlib import Path

from heurisko_automation.errors import MonitorTimeoutError


class FileDoneMonitor:
    def __init__(
        self,
        path: Path,
        done_marker: str = "$$DONE$$",
        poll_interval: float = 0.2,
        stable_delay: float = 0.3,
    ):
        self.path = path
        self.done_marker = done_marker
        self.poll_interval = poll_interval
        self.stable_delay = stable_delay

    def wait_done(self, run_id: str, timeout: float):
        deadline = time.time() + timeout
        last_mtime = None

        while time.time() < deadline:
            if not self.path.exists():
                time.sleep(self.poll_interval)
                continue

            stat = self.path.stat()
            if last_mtime is None or stat.st_mtime != last_mtime:
                last_mtime = stat.st_mtime
                time.sleep(self.stable_delay)
                if self._contains_done(run_id):
                    return True

            time.sleep(self.poll_interval)

        raise MonitorTimeoutError(
            f"Timeout waiting for done marker {self.done_marker!r} and run_id {run_id!r} in {self.path}"
        )

    def _contains_done(self, run_id: str) -> bool:
        tail = self._read_tail()
        for line in reversed(tail.splitlines()[-20:]):
            if self.done_marker in line and run_id in line:
                return True
        return False

    def _read_tail(self, max_bytes: int = 8192) -> str:
        with self.path.open("rb") as stream:
            stream.seek(0, 2)
            size = stream.tell()
            stream.seek(max(0, size - max_bytes))
            return stream.read().decode("utf-8", errors="replace")

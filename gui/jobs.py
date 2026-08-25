"""Background job execution, cancellation, and event buffering for polling from JS."""
from __future__ import annotations

import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable

from pipeline import ffmpeg_utils


@dataclass
class Job:
    id: str
    kind: str
    cancel_event: threading.Event = field(default_factory=threading.Event)
    status: str = "running"  # running | done | error | cancelled
    events: deque = field(default_factory=lambda: deque(maxlen=2000))
    lock: threading.Lock = field(default_factory=threading.Lock)
    seq: int = 0
    result: Any = None
    thread: threading.Thread | None = None

    def push(self, event_type: str, **payload) -> None:
        with self.lock:
            self.seq += 1
            self.events.append({"seq": self.seq, "type": event_type, "ts": time.time(), **payload})


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def start(self, kind: str, target_fn: Callable[..., dict], *args, **kwargs) -> str:
        job_id = uuid.uuid4().hex
        job = Job(id=job_id, kind=kind)

        def _run():
            try:
                on_log = lambda msg: job.push("log", message=msg)
                on_progress = lambda value, label: job.push("progress", value=value, label=label)
                result = target_fn(*args, on_log=on_log, on_progress=on_progress, cancel_event=job.cancel_event, **kwargs)
                job.result = result
                job.status = "done"
                job.push("done", result=result)
            except ffmpeg_utils.CancelledError:
                job.status = "cancelled"
                job.push("cancelled")
            except Exception as exc:  # noqa: BLE001 - surface any pipeline failure to the UI
                job.status = "error"
                job.push("error", message=str(exc))

        job.thread = threading.Thread(target=_run, daemon=True)
        with self._lock:
            self._jobs[job_id] = job
        job.thread.start()
        return job_id

    def cancel(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job is None or job.status != "running":
            return False
        job.cancel_event.set()
        return True

    def get_events(self, job_id: str, since_seq: int = 0) -> dict:
        job = self._jobs.get(job_id)
        if job is None:
            return {"events": [], "status": "unknown", "latestSeq": since_seq}
        with job.lock:
            events = [e for e in job.events if e["seq"] > since_seq]
            latest_seq = job.seq
        return {"events": events, "status": job.status, "latestSeq": latest_seq}

    def get_status(self, job_id: str) -> dict:
        job = self._jobs.get(job_id)
        if job is None:
            return {"status": "unknown"}
        return {"status": job.status, "kind": job.kind, "result": job.result}

    def terminate_all(self) -> None:
        for job in self._jobs.values():
            if job.status == "running":
                job.cancel_event.set()

    def wait_for_idle(self, timeout: float = 3.0) -> None:
        """Block briefly until every job has actually stopped (not just been signalled).
        Cancellation is cooperative — ffmpeg_utils.run() terminates/kills the subprocess on
        its own poll thread, which needs a moment to happen. Called on window close so the
        app doesn't exit mid-terminate and leave an orphaned ffmpeg/yt-dlp process (or a
        WebView2 profile lock) for the next launch to trip over."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not any(job.status == "running" for job in self._jobs.values()):
                return
            time.sleep(0.1)

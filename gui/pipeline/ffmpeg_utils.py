"""Subprocess helpers shared by every pipeline stage: cancellable process runner and ffprobe duration lookup."""
from __future__ import annotations

import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Callable

CREATE_NO_WINDOW = 0x08000000


class CancelledError(Exception):
    pass


def run(cmd: list[str], on_line: Callable[[str], None], cancel_event: threading.Event, poll_interval: float = 0.2) -> int:
    """Run cmd, streaming stdout+stderr lines to on_line. Raises CancelledError if cancel_event is set
    before the process exits, after terminating (then killing) the process."""
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=CREATE_NO_WINDOW,
    )

    def _pump():
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.rstrip("\n")
            if line:
                on_line(line)

    pump_thread = threading.Thread(target=_pump, daemon=True)
    pump_thread.start()

    while proc.poll() is None:
        if cancel_event.is_set():
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)
            pump_thread.join(timeout=2)
            raise CancelledError()
        time.sleep(poll_interval)

    pump_thread.join(timeout=5)
    return proc.returncode


def probe_duration(ffprobe_path: str, video_path: str) -> float | None:
    try:
        result = subprocess.run(
            [ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video_path)],
            capture_output=True,
            text=True,
            creationflags=CREATE_NO_WINDOW,
        )
        value = result.stdout.strip()
        if not value:
            return None
        return float(value)
    except (ValueError, OSError):
        return None


_PROGRESS_TIME_RE = re.compile(r"out_time_ms=(\d+)")
_PROGRESS_FIELD_RE = re.compile(
    r"^(frame|fps|stream_\d+_\d+_q|bitrate|total_size|out_time_us|out_time|"
    r"dup_frames|drop_frames|speed|progress)="
)


def parse_progress_seconds(line: str) -> float | None:
    """Parse an ffmpeg -progress pipe:1 line for out_time_ms, returning seconds."""
    match = _PROGRESS_TIME_RE.search(line)
    if match:
        return int(match.group(1)) / 1_000_000
    return None


def is_progress_field(line: str) -> bool:
    """True for the other key=value lines in an ffmpeg -progress pipe:1 block (noise once
    out_time_ms is already being used for the progress bar)."""
    return bool(_PROGRESS_FIELD_RE.match(line))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

"""Download YouTube playlists via yt-dlp and sanitize resulting filenames.

Ports sanitize_video_names.ps1 (which, despite its name, also performs the download).
"""
from __future__ import annotations

import re
import threading
from pathlib import Path
from typing import Callable

from . import ffmpeg_utils

_NON_WORD_RE = re.compile(r"[^\w]")
_EDGE_UNDERSCORE_RE = re.compile(r"^_+|_+$")
_ITEM_RE = re.compile(r"Downloading item (\d+) of (\d+)")
_PERCENT_RE = re.compile(r"\[download\]\s+(\d+(?:\.\d+)?)% of")

# yt-dlp's --download-archive: one entry per already-downloaded video ID, so re-running a
# playlist only fetches videos that weren't there before. Tracked by video ID (survives our
# filename sanitizing below), one archive per output folder. Must never be swept up by the
# sanitize-filenames loop, or the archive "disappears" on the very next run.
ARCHIVE_FILENAME = ".download_archive.txt"


def sanitize_filename(name: str) -> str:
    cleaned = _NON_WORD_RE.sub("", name)
    return _EDGE_UNDERSCORE_RE.sub("", cleaned)


class _PlaylistProgressTracker:
    """Parses yt-dlp's own stdout to turn "Downloading item N of M" + "NN.N% of" lines
    into a smooth 0..1 progress fraction *within one playlist* — without this, on_progress
    only fires once the whole playlist finishes, so the bar sits at 0% for the entire
    download (which can take many minutes) then jumps straight to 100%."""

    def __init__(self) -> None:
        self.item_index = 0
        self.item_total = 0
        self.item_percent = 0.0

    def update(self, line: str) -> float | None:
        item_match = _ITEM_RE.search(line)
        if item_match:
            self.item_index = int(item_match.group(1))
            self.item_total = int(item_match.group(2))
            self.item_percent = 0.0
            return self.fraction()

        percent_match = _PERCENT_RE.search(line)
        if percent_match:
            self.item_percent = float(percent_match.group(1))
            return self.fraction()

        return None

    def fraction(self) -> float:
        if not self.item_total:
            return self.item_percent / 100
        completed_items = max(self.item_index - 1, 0)
        return min((completed_items + self.item_percent / 100) / self.item_total, 1.0)


def run_download_job(
    config: dict,
    tool_paths: dict,
    on_log: Callable[[str], None],
    on_progress: Callable[[float, str], None],
    cancel_event: threading.Event,
) -> dict:
    import config as app_config  # gui/config.py, absolute import (gui/ is on sys.path)

    download_cfg = config["download"]
    playlists = [p for p in download_cfg.get("playlists", []) if p.get("playlistUrl") and p.get("folderName")]
    if not playlists:
        raise ValueError("Aucune playlist configurée (URL + nom de dossier requis).")

    base_dir = app_config.resolve_path(download_cfg["baseDir"])
    yt_dlp_path = tool_paths["ytDlp"]
    ffmpeg_dir = str(Path(tool_paths["ffmpeg"]).parent)
    fmt = download_cfg.get("format") or app_config.DEFAULT_CONFIG["download"]["format"]

    total = len(playlists)
    downloaded_folders = []

    for index, playlist in enumerate(playlists):
        if cancel_event.is_set():
            raise ffmpeg_utils.CancelledError()

        folder_name = playlist["folderName"]
        url = playlist["playlistUrl"]
        out_dir = base_dir / folder_name
        ffmpeg_utils.ensure_dir(out_dir)

        on_log(f"[TELECHARGEMENT] Playlist {index + 1}/{total} -> {out_dir}")
        cmd = [
            yt_dlp_path,
            "-f", fmt,
            "--merge-output-format", "mp4",  # downstream pipeline only ever scans for *.mp4
            "--ffmpeg-location", ffmpeg_dir,
            "--download-archive", str(out_dir / ARCHIVE_FILENAME),  # skip videos already downloaded here
            "-o", str(out_dir / "%(title)s.%(ext)s"),
            "-i", url,
        ]

        tracker = _PlaylistProgressTracker()

        def _on_line(line: str, index=index) -> None:
            on_log(line)
            playlist_fraction = tracker.update(line)
            if playlist_fraction is not None:
                overall = (index + playlist_fraction) / total
                label = f"Playlist {index + 1}/{total}"
                if tracker.item_total:
                    label += f" — vidéo {min(tracker.item_index, tracker.item_total)}/{tracker.item_total}"
                on_progress(overall, label)

        ffmpeg_utils.run(cmd, _on_line, cancel_event)

        on_log(f"[NETTOYAGE] Sanitisation des noms de fichiers dans {out_dir}")
        renamed = 0
        for entry in out_dir.iterdir():
            if not entry.is_file() or entry.name == ARCHIVE_FILENAME:
                continue
            new_stem = sanitize_filename(entry.stem)
            new_name = new_stem + entry.suffix
            if new_name and new_name != entry.name:
                target = ffmpeg_utils.unique_path(entry.with_name(new_name))
                entry.rename(target)
                renamed += 1
        on_log(f"[OK] {renamed} fichier(s) renommé(s)")

        downloaded_folders.append(str(out_dir))
        on_progress((index + 1) / total, f"{index + 1}/{total} playlists")

    return {"folders": downloaded_folders}

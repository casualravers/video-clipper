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


def sanitize_filename(name: str) -> str:
    cleaned = _NON_WORD_RE.sub("", name)
    return _EDGE_UNDERSCORE_RE.sub("", cleaned)


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
            "-o", str(out_dir / "%(title)s.%(ext)s"),
            "-i", url,
        ]
        ffmpeg_utils.run(cmd, on_log, cancel_event)

        on_log(f"[NETTOYAGE] Sanitisation des noms de fichiers dans {out_dir}")
        renamed = 0
        for entry in out_dir.iterdir():
            if not entry.is_file():
                continue
            new_stem = sanitize_filename(entry.stem)
            new_name = new_stem + entry.suffix
            if new_name and new_name != entry.name:
                target = entry.with_name(new_name)
                entry.rename(target)
                renamed += 1
        on_log(f"[OK] {renamed} fichier(s) renommé(s)")

        downloaded_folders.append(str(out_dir))
        on_progress((index + 1) / total, f"{index + 1}/{total} playlists")

    return {"folders": downloaded_folders}

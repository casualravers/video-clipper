"""Post-processing effects: glitch (add_glitch_effect.ps1) and datamosh (cut_clips_10s.ps1's datamosh block)."""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable

from . import ffmpeg_utils

GLITCH_FILTER = "scale={w}:{h},fps={fps},hue=s=1.2,noise=alls=0.05:allf=t"
DATAMOSH_FILTER = (
    "split=2[orig][dup];"
    "[dup]scale={w}:{h},eq=contrast=1.2:brightness=0.1,noise=alls=0.15[glitch];"
    "[orig][glitch]blend=all_mode=lighten:all_opacity=0.4,fps={fps}"
)


def run_effect_job(
    input_video: str,
    output_video: str,
    effect: str,
    width: int,
    height: int,
    fps: int,
    tool_paths: dict,
    on_log: Callable[[str], None],
    on_progress: Callable[[float, str], None],
    cancel_event: threading.Event,
) -> dict:
    ffmpeg_path = tool_paths["ffmpeg"]
    ffprobe_path = tool_paths["ffprobe"]

    if not Path(input_video).is_file():
        raise ValueError(f"Vidéo d'entrée introuvable : {input_video}")

    unique_output = ffmpeg_utils.unique_path(Path(output_video))
    if unique_output.name != Path(output_video).name:
        on_log(f"[INFO] Le fichier existait déjà, sortie renommée : {unique_output.name}")
    output_video = str(unique_output)

    duration = ffmpeg_utils.probe_duration(ffprobe_path, input_video) or 0.0

    if effect == "datamosh":
        vf = DATAMOSH_FILTER.format(w=width, h=height, fps=fps)
        crf = "20"
    else:
        vf = GLITCH_FILTER.format(w=width, h=height, fps=fps)
        crf = "18"

    on_log(f"[EFFET] Application de l'effet '{effect}' sur {input_video}")

    cmd = [
        ffmpeg_path, "-y",
        "-i", input_video,
        "-progress", "pipe:1", "-nostats",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", crf,
        "-c:a", "aac", "-b:a", "192k",
        output_video,
    ]

    def _on_line(line: str) -> None:
        seconds = ffmpeg_utils.parse_progress_seconds(line)
        if seconds is not None and duration > 0:
            on_progress(min(seconds / duration, 1.0), f"{seconds:.0f}s / {duration:.0f}s")
        elif not ffmpeg_utils.is_progress_field(line):
            on_log(line)

    ffmpeg_utils.run(cmd, _on_line, cancel_event)

    if not Path(output_video).exists():
        raise ValueError("Échec de l'application de l'effet.")

    on_log(f"[OK] Effet appliqué : {output_video}")
    return {"outputPath": output_video}


def derive_output_path(input_video: str, effect: str) -> str:
    p = Path(input_video)
    suffix = "_datamosh" if effect == "datamosh" else "_glitch"
    return str(p.with_name(p.stem + suffix + p.suffix))

"""Entry point: creates the pywebview window and wires up the Api."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import webview

from api import Api


def main() -> None:
    api = Api()
    window = webview.create_window(
        "VHS Glitch Generator",
        str(Path(__file__).resolve().parent / "web" / "index.html"),
        js_api=api,
        width=1200,
        height=800,
        min_size=(1000, 700),
        background_color="#0d0d0f",
    )
    api.window = window
    window.events.closing += api.on_window_closing
    webview.start(gui="edgechromium", debug=False)


if __name__ == "__main__":
    main()

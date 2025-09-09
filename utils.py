from __future__ import annotations
import os
import sys
from datetime import datetime

PRIMARY_ACCENT = "#2E87FF"
PRIMARY_ACCENT_DARK = "#0F6FE8"
PRIMARY_ACCENT_LIGHT = "#66B8FF"
TEXT_HIGH = "#E6F2FA"
BG = "#0B1115"
CARD = "#0E1619"
BORDER = "#22303A"
MUTED = "#6B7882"
ERROR_RED = "#C92A2A"
WARN_AMBER = "#B46900"
SUCCESS_GREEN = "#0B7A2F"
PROGRESS_BLUE = "#075E9B"

OUTPUT_DIR = "downloads"
RETRY_COUNT = 3
RETRY_DELAY = 5

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
APP_LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logoApp.png")

def timestamp() -> str:
    """Get the current time as a string in the format "HH:MM:SS"."""
    return datetime.now().strftime("%H:%M:%S")

def maybe_add_bundled_ffmpeg_to_path():
    """If the app is bundled with ffmpeg in an 'ffmpeg' folder, add to PATH."""
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(base, "ffmpeg")
    if os.path.isdir(ffmpeg_dir):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

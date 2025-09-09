#!/usr/bin/env python3
"""
Download YouTube links from links.txt at the best possible resolution (video+audio merged).
Requires: yt-dlp and ffmpeg installed.
"""

import os
import sys
import time
from typing import List
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

LINKS_FILE = "links.txt"
OUTPUT_DIR = "downloads"
RETRY_COUNT = 3
RETRY_DELAY = 5


def maybe_add_bundled_ffmpeg_to_path():
    """
    If packaged (PyInstaller) and we've bundled an `ffmpeg` folder
    next to the exe, add it to PATH so yt-dlp/ffmpeg subprocesses can find it.
    """
    if getattr(sys, "frozen", False):
        # _MEIPASS is the temp dir PyInstaller extracts files to in --onefile mode
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    ffmpeg_dir = os.path.join(base, "ffmpeg")  # we will bundle a folder named 'ffmpeg'
    if os.path.isdir(ffmpeg_dir):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")


def read_links(path: str) -> List[str]:
    """Read links from a text file, ignoring blank lines and comments (#...)."""
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f.readlines()]
    links = [ln for ln in lines if ln and not ln.startswith("#")]
    return links


def on_progress(d):
    """Progress hook for yt-dlp (prints simple progress)."""
    if d["status"] == "downloading":
        downloaded = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        percent = None
        if total:
            percent = downloaded / total * 100
        speed = d.get("speed")
        eta = d.get("eta")
        line = f"Downloading: {d.get('filename', '')}"
        if percent is not None:
            line += f" — {percent:5.1f}%"
        if speed:
            line += f" — {human_readable_size(speed)}/s"
        if eta is not None:
            line += f" — ETA {int(eta)}s"
        print(line, end="\r", flush=True)
    elif d["status"] == "finished":
        print()
        print("Download finished, now post-processing (merging if needed)...")


def human_readable_size(num: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}"
        num /= 1024.0
    return f"{num:.1f}PB"


def make_output_dir(path: str):
    os.makedirs(path, exist_ok=True)


def download_link(url: str, ydl_opts: dict):
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return info


def main():
    links = read_links(LINKS_FILE)
    if not links:
        print("No links found in links.txt (or file missing). Add one URL per line.")
        sys.exit(1)

    make_output_dir(OUTPUT_DIR)

    # Best practice format: try to get the best video + best audio and merge.
    ydl_opts_base = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(OUTPUT_DIR, "%(title)s - %(id)s.%(ext)s"),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "progress_hooks": [on_progress],
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": False,
        "retries": 2,
    }

    successful_links = []
    failed_links = []

    for idx, url in enumerate(links, start=1):
        print(f"\n[{idx}/{len(links)}] Processing: {url}")
        success = False
        for attempt in range(1, RETRY_COUNT + 1):
            try:
                print(f"Attempt {attempt}...")
                ydl_opts = dict(ydl_opts_base)
                ydl_opts["quiet"] = False
                ydl_opts["progress_hooks"] = [on_progress]
                info = download_link(url, ydl_opts)
                print(f"Downloaded: {info.get('title', 'unknown title')}")
                success = True
                break
            except DownloadError as e:
                print(f"DownloadError: {e}.")
            except Exception as e:
                print(f"Error while downloading: {type(e).__name__}: {e}")
            if attempt < RETRY_COUNT:
                print(f"Retrying after {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
        if success:
            successful_links.append(url)
        else:
            failed_links.append(url)

    # Rewrite links.txt with only failed links (so successes are removed)
    if successful_links:
        print("\nCleaning up links.txt...")
        with open(LINKS_FILE, "w", encoding="utf-8") as f:
            for link in failed_links:
                f.write(link + "\n")

    print("\nAll done.")
    print("Files saved in:", os.path.abspath(OUTPUT_DIR))
    if failed_links:
        print(f"{len(failed_links)} link(s) failed. They remain in {LINKS_FILE}.")
    else:
        print("All links downloaded successfully. links.txt is now empty.")


if __name__ == "__main__":
    maybe_add_bundled_ffmpeg_to_path()
    main()

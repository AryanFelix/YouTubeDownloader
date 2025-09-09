from __future__ import annotations
import os
import time
from typing import List
from PySide6.QtCore import QThread, Signal

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from utils import OUTPUT_DIR, RETRY_COUNT, RETRY_DELAY, maybe_add_bundled_ffmpeg_to_path

class TitleFetcher(QThread):
    """Fetches titles (metadata) for a list of URLs in the background."""
    title_fetched = Signal(str, str, str)   # url, title, id
    fetch_error = Signal(str, str)          # url, error message
    finished_batch = Signal()

    def __init__(self, urls: List[str]):
        super().__init__()
        self.urls = urls
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        ydl_opts = {"quiet": True, "no_warnings": True}
        for url in self.urls:
            if self._stop:
                break
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                title = info.get("title") or info.get("id") or url
                vid = info.get("id") or ""
                self.title_fetched.emit(url, title, vid)
            except Exception as e:
                self.fetch_error.emit(url, str(e))
        self.finished_batch.emit()

class DownloadWorker(QThread):
    """Downloads a list of URLs sequentially, emitting progress & events."""
    progress = Signal(int, str)          # percent, filename
    info = Signal(str)
    warn = Signal(str)
    error = Signal(str)
    success = Signal(str)
    wait_tick = Signal(int)
    wait_start = Signal(int)
    finished_result = Signal(list, list) # successes, failures

    def __init__(self, urls: List[str]):
        super().__init__()
        self.urls = urls
        self._stop = False

    def run(self):
        maybe_add_bundled_ffmpeg_to_path()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        successes, failures = [], []
        for url in self.urls:
            if self._stop:
                self.info.emit("Stop requested; ending worker.")
                break
            ok = self._download_single(url)
            if ok:
                successes.append(url)
            else:
                failures.append(url)
        self.finished_result.emit(successes, failures)

    def stop(self):
        self._stop = True

    def _on_progress(self, d):
        try:
            status = d.get("status")
            if status == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes", 0)
                pct = int(downloaded / total * 100) if total else 0
                fn = d.get("filename", "")
                self.progress.emit(pct, fn)
            elif status == "finished":
                self.info.emit("Finishing / merging streams...")
        except Exception as e:
            self.warn.emit(f"Progress hook error: {e}")

    def _download_single(self, url: str) -> bool:
        opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": os.path.join(OUTPUT_DIR, "%(title)s - %(id)s.%(ext)s"),
            "merge_output_format": "mp4",
            "noplaylist": True,
            "progress_hooks": [self._on_progress],
            "quiet": True,
            "no_warnings": True,
            "retries": 0,
        }
        attempt = 0
        while attempt < RETRY_COUNT and not self._stop:
            attempt += 1
            try:
                self.info.emit(f"[Attempt {attempt}] Starting download: {url}")
                with YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                title = info.get("title", "unknown title")
                self.success.emit(f"Downloaded: {title}")
                return True
            except DownloadError as e:
                self.warn.emit(f"DownloadError (attempt {attempt}): {e}")
            except Exception as e:
                self.warn.emit(f"Error (attempt {attempt}): {type(e).__name__}: {e}")

            if attempt < RETRY_COUNT and not self._stop:
                total_wait = RETRY_DELAY
                self.info.emit(f"Waiting {total_wait}s before retry ({attempt}/{RETRY_COUNT})...")
                self.wait_start.emit(total_wait)
                for remaining in range(total_wait, 0, -1):
                    if self._stop:
                        self.info.emit("Stop requested during wait; aborting retries.")
                        break
                    self.wait_tick.emit(remaining)
                    time.sleep(1)
            else:
                if attempt >= RETRY_COUNT:
                    self.info.emit("Retries exhausted for this item.")
        self.error.emit(f"Failed after {RETRY_COUNT} attempts: {url}")
        return False

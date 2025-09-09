from __future__ import annotations
import os
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QPushButton,
    QListWidget, QLabel, QProgressBar, QSizePolicy, QListWidgetItem
)
from PySide6.QtGui import QFont, QTextCursor, QPixmap, QIcon, QDesktopServices
from PySide6.QtCore import Qt, QTimer, QUrl, QSize

from workers import TitleFetcher, DownloadWorker
from utils import (ERROR_RED, LOGO_PATH, PROGRESS_BLUE, SUCCESS_GREEN, TEXT_HIGH, WARN_AMBER, timestamp, maybe_add_bundled_ffmpeg_to_path,
                   PRIMARY_ACCENT, PRIMARY_ACCENT_DARK, PRIMARY_ACCENT_LIGHT, BORDER, MUTED)
import styles

class UXWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTubeDownloader")
        self.resize(1000, 640)
        self.setFont(QFont("Segoe UI" if os.name == "nt" else "Sans Serif", 10))

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(14, 14, 14, 14)

        # LEFT column
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)

        # logo (centered)
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        if os.path.exists(LOGO_PATH):
            try:
                pix = QPixmap(LOGO_PATH)
                if not pix.isNull():
                    src_w = pix.width()
                    desired_w = src_w * 3
                    window_initial_w = 1000
                    max_target = int(0.8 * window_initial_w)
                    target_width = min(desired_w, max_target)
                    target_width = max(target_width, min(src_w * 2, 720))
                    scaled = pix.scaledToWidth(target_width, Qt.SmoothTransformation)
                    max_h = 220
                    if scaled.height() > max_h:
                        scaled = pix.scaledToHeight(max_h, Qt.SmoothTransformation)
                    logo_label.setPixmap(scaled)
                    logo_label.setFixedHeight(scaled.height())
                else:
                    logo_label.hide()
            except Exception:
                logo_label.hide()
        else:
            logo_label.hide()

        left_layout.addWidget(logo_label, alignment=Qt.AlignHCenter)

        lbl_input = QLabel("Paste YouTube links (one per line)")
        lbl_input.setStyleSheet(f"font-weight:700; color: {MUTED};")
        left_layout.addWidget(lbl_input)

        self.input = QTextEdit()
        self.input.setPlaceholderText("Paste URLs here, one link per line. Example:\nhttps://www.youtube.com/watch?v=...")
        self.input.setFixedHeight(300)
        self.input.setStyleSheet(styles.textedit_style())
        left_layout.addWidget(self.input)

        hint = QLabel("Tip: Use the Add button to push links into the queue.")
        hint.setStyleSheet(f"color: {MUTED}; font-size:9pt;")
        left_layout.addWidget(hint)

        # ---------- input actions: Add | GitHub | Donate (with icons & colors) ----------
        input_actions = QHBoxLayout()
        input_actions.setSpacing(12)

        # Add button (expands)
        self.btn_add = QPushButton("Add")
        self.btn_add.setFixedHeight(36)
        self.btn_add.setStyleSheet(styles.secondary_button_style())
        input_actions.addWidget(self.btn_add, stretch=1)

        # load icons
        github_icon_path = os.path.join("assets", "github.png")
        bmac_icon_path = os.path.join("assets", "bmac.png")
        github_icon = QIcon(github_icon_path) if os.path.exists(github_icon_path) else QIcon()
        bmac_icon = QIcon(bmac_icon_path) if os.path.exists(bmac_icon_path) else QIcon()

        # GitHub button: white background, bold black text
        self.btn_github = QPushButton("GitHub")
        self.btn_github.setFixedHeight(36)
        self.btn_github.setIcon(github_icon)
        self.btn_github.setIconSize(QSize(20, 20))
        self.btn_github.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #000000;
                font-weight: 700;
                border: 1px solid rgba(0,0,0,0.15);
                border-radius: 8px;
                padding: 6px 12px;
                text-align: left;
            }
            QPushButton::hover {
                background-color: #f0f0f0;
            }
        """)
        self.btn_github.setToolTip("Open project on GitHub")
        input_actions.addWidget(self.btn_github, stretch=0)

        # Donate (BuyMeACoffee) button: yellow background, bold dark text
        self.btn_donate = QPushButton("Donate")
        self.btn_donate.setFixedHeight(36)
        self.btn_donate.setIcon(bmac_icon)
        self.btn_donate.setIconSize(QSize(20, 20))
        self.btn_donate.setStyleSheet("""
            QPushButton {
                background-color: #ffdd00;
                color: #0d0c22;
                font-weight: 700;
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: 8px;
                padding: 6px 12px;
                text-align: left;
            }
            QPushButton::hover {
                background-color: #ffd600;
            }
        """)
        self.btn_donate.setToolTip("Support the project on Buy Me A Coffee")
        input_actions.addWidget(self.btn_donate, stretch=0)

        left_layout.addLayout(input_actions)

        # Add left and right layouts with equal stretch so columns are same width
        main_layout.addLayout(left_layout, 1)

        # RIGHT column
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        q_label = QLabel("Queue")
        q_label.setStyleSheet(f"font-weight:700; color: {MUTED};")
        right_layout.addWidget(q_label)

        self.queue = QListWidget()
        self.queue.setFixedHeight(170)
        self.queue.setStyleSheet(styles.list_style())
        right_layout.addWidget(self.queue)

        queue_controls = QHBoxLayout()
        self.btn_remove = QPushButton("Remove")
        self.btn_clear = QPushButton("Clear")
        for b in (self.btn_remove, self.btn_clear):
            b.setFixedHeight(34)
            b.setStyleSheet(styles.secondary_button_style(outline=True))
        queue_controls.addWidget(self.btn_remove)
        queue_controls.addWidget(self.btn_clear)
        right_layout.addLayout(queue_controls)

        log_label = QLabel("Activity Log")
        log_label.setStyleSheet(f"font-weight:700; color: {MUTED};")
        right_layout.addWidget(log_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet(styles.log_style())
        right_layout.addWidget(self.log, stretch=1)

        # progress + current item label
        self.current_item_label = QLabel("")
        self.current_item_label.setStyleSheet(f"color: {MUTED}; font-weight:600;")
        right_layout.addWidget(self.current_item_label)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(22)
        self.progress.setTextVisible(True)
        self.progress.setAlignment(Qt.AlignCenter)
        self._set_progress_styles(primary_color=PRIMARY_ACCENT, chunk_color=PRIMARY_ACCENT_DARK)
        right_layout.addWidget(self.progress)

        # subtle animation timer
        self._progress_anim_timer = QTimer(self)
        self._progress_anim_timer.setInterval(650)
        self._progress_anim_state = False
        self._progress_anim_timer.timeout.connect(self._toggle_progress_animation)

        # ---------- bottom controls (evenly fill column width) ----------
        bottom_controls = QHBoxLayout()
        bottom_controls.setSpacing(12)
        self.btn_download_selected = QPushButton("Download Selected")
        self.btn_download_all = QPushButton("Download All")
        self.btn_stop = QPushButton("Stop")

        for btn in (self.btn_download_selected, self.btn_download_all, self.btn_stop):
            btn.setFixedHeight(42)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_download_selected.setStyleSheet(styles.primary_button_style(accent=False))
        self.btn_download_all.setStyleSheet(styles.primary_button_style(accent=True))
        self.btn_stop.setStyleSheet(styles.secondary_button_style(outline=True))

        bottom_controls.addWidget(self.btn_download_selected, stretch=1)
        bottom_controls.addWidget(self.btn_download_all, stretch=1)
        bottom_controls.addWidget(self.btn_stop, stretch=1)

        right_layout.addLayout(bottom_controls)

        # add right layout with same stretch as left to make columns equal width
        main_layout.addLayout(right_layout, 1)

        # connections
        self.btn_add.clicked.connect(self._add_from_input)
        self.btn_remove.clicked.connect(self._remove_selected)
        self.btn_clear.clicked.connect(self._clear_queue)
        self.btn_download_selected.clicked.connect(self._download_selected)
        self.btn_download_all.clicked.connect(self._download_all)
        self.btn_stop.clicked.connect(self._stop_worker)

        # GitHub / Donate open urls
        self.btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/AryanFelix/YouTubeDownloader")))
        self.btn_donate.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://buymeacoffee.com/aryanfelix")))

        # state objects
        self.worker: Optional[DownloadWorker] = None
        self._active_title_fetchers: List[TitleFetcher] = []
        self._log_entries: List[Dict[str, str]] = []
        self._wait_entry_index: Optional[int] = None

        self._update_buttons_state()

    # ---------- progress helpers ----------
    def _set_progress_styles(self, primary_color: str, chunk_color: str):
        style = styles.progress_style(primary_color=primary_color, chunk_color=chunk_color, border=BORDER)
        self.progress.setStyleSheet(style)

    def _toggle_progress_animation(self):
        self._progress_anim_state = not self._progress_anim_state
        if self._progress_anim_state:
            self._set_progress_styles(primary_color=PRIMARY_ACCENT, chunk_color=PRIMARY_ACCENT_LIGHT)
        else:
            self._set_progress_styles(primary_color=PRIMARY_ACCENT_DARK, chunk_color=PRIMARY_ACCENT)

    # ---------- input & title fetching ----------
    def _add_from_input(self):
        text = self.input.toPlainText().strip()
        if not text:
            self._append_log("warn", "No links to add.")
            return
        raw_urls = [ln.strip() for ln in text.splitlines() if ln.strip()]
        added = 0
        urls_to_fetch = []
        for url in raw_urls:
            if not self._in_queue_url(url):
                item = QListWidgetItem(url)
                item.setData(Qt.UserRole, {"url": url, "title": None, "id": None})
                self.queue.addItem(item)
                added += 1
                urls_to_fetch.append(url)
        self.input.clear()
        if added:
            self._append_log("info", f"Added {added} link(s) to queue; fetching titles…")
            fetcher = TitleFetcher(urls_to_fetch)
            fetcher.title_fetched.connect(self._on_title_fetched)
            fetcher.fetch_error.connect(self._on_title_fetch_error)
            fetcher.finished_batch.connect(lambda: self._cleanup_fetcher(fetcher))
            self._active_title_fetchers.append(fetcher)
            fetcher.start()
        else:
            self._append_log("warn", "No new links to add.")
        self._update_buttons_state()

    def _on_title_fetched(self, url: str, title: str, vid: str):
        for i in range(self.queue.count()):
            item = self.queue.item(i)
            data = item.data(Qt.UserRole)
            if data and data.get("url") == url:
                display = f"{title} — {vid}" if vid else title
                item.setText(display)
                newdata = {"url": url, "title": title, "id": vid}
                item.setData(Qt.UserRole, newdata)
                self._append_log("info", f"Title fetched: {title}")
                return

    def _on_title_fetch_error(self, url: str, err: str):
        self._append_log("warn", f"Failed fetching title for {url}: {err}")

    def _cleanup_fetcher(self, fetcher: TitleFetcher):
        try:
            self._active_title_fetchers.remove(fetcher)
        except ValueError:
            pass

    # ---------- queue helpers ----------
    def _remove_selected(self):
        for it in self.queue.selectedItems():
            self.queue.takeItem(self.queue.row(it))
        self._append_log("info", "Removed selected items.")
        self._update_buttons_state()

    def _clear_queue(self):
        self.queue.clear()
        self._append_log("info", "Cleared queue.")
        self._update_buttons_state()

    def _in_queue_url(self, url: str) -> bool:
        for i in range(self.queue.count()):
            item = self.queue.item(i)
            data = item.data(Qt.UserRole)
            if data and data.get("url") == url:
                return True
            if item.text() == url:
                return True
        return False

    # ---------- download orchestration ----------
    def _download_selected(self):
        selected = self.queue.selectedItems()
        if not selected:
            self._append_log("warn", "No items selected.")
            return
        urls = [it.data(Qt.UserRole)["url"] for it in selected if it.data(Qt.UserRole)]
        self._start_worker(urls)

    def _download_all(self):
        if self.queue.count() == 0:
            self._append_log("warn", "Queue is empty.")
            return
        urls = [self.queue.item(i).data(Qt.UserRole)["url"] for i in range(self.queue.count())]
        self._start_worker(urls)

    def _start_worker(self, urls: List[str]):
        if self.worker and self.worker.isRunning():
            self._append_log("warn", "Worker already running.")
            return
        self._set_controls_enabled(False)
        self._append_log("info", f"Starting download of {len(urls)} item(s).")
        self.progress.setValue(0)
        self.current_item_label.setText("")
        self._progress_anim_state = False
        self._progress_anim_timer.start()
        self.worker = DownloadWorker(urls)
        self.worker.progress.connect(self._on_progress)
        self.worker.info.connect(lambda s: self._append_log("info", s))
        self.worker.warn.connect(lambda s: self._append_log("warn", s))
        self.worker.error.connect(lambda s: self._append_log("error", s))
        self.worker.success.connect(lambda s: self._append_log("success", s))
        self.worker.wait_start.connect(self._on_wait_start)
        self.worker.wait_tick.connect(self._on_wait_tick)
        self.worker.finished_result.connect(self._on_finished)
        self.worker.start()

    def _stop_worker(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self._append_log("info", "Stop requested. Worker will finish current item then stop.")
        else:
            self._append_log("info", "No active worker to stop.")

    def _on_progress(self, pct: int, filename: str):
        self.progress.setValue(max(0, min(100, pct)))
        name = os.path.basename(filename) if filename else ""
        if len(name) > 60:
            name = name[:57] + "..."
        self.current_item_label.setText(f"Downloading: {name}")
        self._append_log("progress", f"{name} — {pct}%")

    def _on_finished(self, successes: List[str], failures: List[str]):
        if self._progress_anim_timer.isActive():
            self._progress_anim_timer.stop()
            self._set_progress_styles(primary_color=PRIMARY_ACCENT, chunk_color=PRIMARY_ACCENT_DARK)
        for s in successes:
            for i in range(self.queue.count()):
                try:
                    data = self.queue.item(i).data(Qt.UserRole)
                    if data and data.get("url") == s:
                        self.queue.takeItem(i)
                        break
                except Exception:
                    continue
        self._append_log("info", f"Worker finished. Successes: {len(successes)}, Failures: {len(failures)}")
        self.progress.setValue(0)
        self.current_item_label.setText("")
        self.worker = None
        self._set_controls_enabled(True)
        self._update_buttons_state()

    # ---------- wait updates (update-in-place) ----------
    def _on_wait_start(self, total_seconds: int):
        entry = {"level": "wait", "text": f"Waiting {total_seconds}s before retry...", "ts": timestamp()}
        if self._wait_entry_index is not None:
            self._log_entries[self._wait_entry_index] = entry
        else:
            self._log_entries.append(entry)
            self._wait_entry_index = len(self._log_entries) - 1
        self._render_logs()

    def _on_wait_tick(self, remaining: int):
        if self._wait_entry_index is None:
            self._on_wait_start(remaining)
            return
        self._log_entries[self._wait_entry_index]["text"] = f"Waiting... {remaining}s"
        self._log_entries[self._wait_entry_index]["ts"] = timestamp()
        self._render_logs()

    # ---------- logging ----------
    def _append_log(self, level: str, text: str):
        if self._wait_entry_index is not None and level != "wait":
            try:
                del self._log_entries[self._wait_entry_index]
            except Exception:
                pass
            self._wait_entry_index = None

        entry = {"level": level, "text": text, "ts": timestamp()}
        self._log_entries.append(entry)
        if len(self._log_entries) > 800:
            self._log_entries = self._log_entries[-800:]
        self._render_logs()

    def _render_logs(self):
        html_lines = []
        for e in self._log_entries[-500:]:
            level = e.get("level", "info")
            ts = e.get("ts", "")
            txt = e.get("text", "")
            color = {
                "info": TEXT_HIGH,
                "warn": WARN_AMBER,
                "error": ERROR_RED,
                "success": SUCCESS_GREEN,
                "progress": PROGRESS_BLUE,
                "wait": MUTED
            }.get(level, TEXT_HIGH)
            safe = (txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            html_lines.append(f'<div style="margin:4px 0;"><span style="color:{MUTED}; font-family:monospace;">[{ts}]</span> '
                              f'<span style="color:{color}; font-weight:600; margin-left:8px;">{safe}</span></div>')
        html = "\n".join(html_lines)
        self.log.setHtml(html)
        self.log.moveCursor(QTextCursor.End)

    # ---------- UI helpers ----------
    def _set_controls_enabled(self, enabled: bool):
        for w in (self.btn_add, self.btn_remove, self.btn_clear,
                  self.btn_download_selected, self.btn_download_all):
            w.setEnabled(enabled)
        self.btn_stop.setEnabled(not enabled)

    def _update_buttons_state(self):
        has_items = self.queue.count() > 0
        self.btn_download_all.setEnabled(has_items)
        self.btn_download_selected.setEnabled(has_items and len(self.queue.selectedItems()) > 0)
        self.btn_remove.setEnabled(has_items and len(self.queue.selectedItems()) > 0)
        self.btn_clear.setEnabled(has_items)

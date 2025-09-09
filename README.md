# YouTubeDownloader (GUI)

YouTubeDownloader is a modern, cross-platform desktop app for downloading YouTube videos in the best available quality (video + audio merged).  
It features a clean user interface, queue management, activity logs, and retry handling.  
Executables for Windows, Linux, and macOS are published automatically via [GitHub Releases](../../releases).

---

## Features
- Modern GUI with dark theme, queue view, activity log, and progress bar.
- Download best possible resolution (`bestvideo+bestaudio` merged with ffmpeg).
- Retries failed downloads up to 3 times with visible countdown logs.
- Queue displays video titles instead of raw URLs.
- Remove or clear queue items at any time.
- Animated progress bar with per-item status updates.
- Saves files into a `downloads/` folder with video title and ID in the filename.
- Prebuilt executables for Windows, Linux, and macOS.
- Custom app logo (`assets/logo.png`) used in UI and as application icon.
- Open source, licensed under [MIT](./LICENSE).

---

## Quick Start

### Windows / Linux / macOS (prebuilt binaries)

1. Download the latest release for your platform from the [Releases page](../../releases).
2. Extract (if `.tar.gz`) or place the executable in any folder.
3. Run the app:
   - **Windows**: Double-click `YouTubeDownloader.exe`
   - **Linux/macOS**:
     ```bash
     chmod +x YouTubeDownloader
     ./YouTubeDownloader
     ```
4. Paste one or more YouTube links into the input box.
5. Press **Add**, then choose **Download All** or **Download Selected**.
6. Downloads are saved into the `downloads/` folder.

---

## For Developers

### Requirements
- Python 3.9+ (tested with Python 3.11)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [PySide6](https://doc.qt.io/qtforpython/)
- ffmpeg (installed or bundled)

### Install dependencies
```bash
pip install -r requirements.txt
```

### Running from source
```bash
python main.py
```

### Building executables (local)
1. Place `ffmpeg` (and optionally `ffprobe`) into an `ffmpeg/` folder.
2. Run:
   ```bash
   pyinstaller --onefile --name "YouTubeDownloader.exe" --add-data "ffmpeg;ffmpeg" main.py
   ```
3. The executable will be in `dist/`.

### Automated builds (GitHub Actions)
This repo includes a workflow that:
- Builds Windows, Linux, and macOS executables on tagged releases (`v1.0.0`, etc.).
- Downloads a fresh portable ffmpeg build for each OS at build time.
- Uploads all executables to the GitHub Release page.

---

## Notes & Limitations
- This tool is for personal use only. Make sure your usage complies with YouTube’s Terms of Service.
- Executables are unsigned; on Windows/macOS you may see a SmartScreen or Gatekeeper warning.
- Antivirus software may flag PyInstaller-built executables — this is a common false positive.
- Large playlists are not currently supported (single videos only).

---

## License
This project is licensed under the [MIT License](./LICENSE).

---

## Credits
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube downloader library  
- [ffmpeg](https://ffmpeg.org) — video and audio processing  
- [PySide6](https://doc.qt.io/qtforpython/) — Qt bindings for Python  
- [PyInstaller](https://pyinstaller.org) — packaging into standalone executables  

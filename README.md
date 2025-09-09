# 🎬 YouTubeDownloader

**YouTubeDownloader** is a simple command-line tool that downloads YouTube videos in the **best available quality (video + audio merged)**.  
It reads links from a text file (`links.txt`) and saves the downloads into a `downloads/` folder.  
After successful downloads, those links are automatically removed from `links.txt`, leaving only failed ones for retry.

This project is written in **Python** with [yt-dlp](https://github.com/yt-dlp/yt-dlp) and packaged into a standalone Windows executable with **PyInstaller**.

---

## ✨ Features
- 📥 Download best possible resolution (`bestvideo+bestaudio` merged with `ffmpeg`).
- 🔁 Retries failed downloads up to 3 times before skipping.
- 📝 Maintains `links.txt` — removes successfully downloaded links automatically.
- 📂 Saves files into a `downloads/` folder with video title and ID in the filename.
- ⚡ Bundles [ffmpeg](https://ffmpeg.org) inside the executable for easy use.
- 🚀 Prebuilt **Windows executable** (`YouTubeDownloader.exe`) available via [GitHub Releases](../../releases).

---

## 🚀 Quick Start (Windows Users)

1. Download the latest release from the [Releases page](../../releases).
2. Place `YouTubeDownloader.exe` in any folder.
3. In the same folder, create a file named `links.txt` and put one YouTube link per line, for example:
- https://www.youtube.com/watch?v=dQw4w9WgXcQ
- https://www.youtube.com/watch?v=oHg5SJYRHA0
4. Run the program by double-clicking `YouTubeDownloader.exe` **or** from the terminal:
    ```
    powershell .\YouTubeDownloader.exe
    ```
5. Videos will be saved in the downloads/ folder.
Once finished, successfully downloaded links are removed from links.txt.

---

## 🛠 For Developers
### Requirements

- Python 3.9+ (tested with Python 3.11)
- yt-dlp
- pyinstaller
- ffmpeg (for local runs; the exe bundles it automatically)

### Install dependencies:
```
pip install -r requirements.txt
```

### Running from source
```
python download_youtube_best.py
```

### Building the executable (local)

1. Place ffmpeg.exe (and optionally ffprobe.exe) in an ffmpeg/ folder.
2. Run:
    ```
    pyinstaller --onefile --name "YouTubeDownloader.exe" --add-data "ffmpeg;ffmpeg" download_youtube_best.py
    ```
3. The executable will be in dist/YouTubeDownloader.exe.

### Automated builds (GitHub Actions)

This repo includes a GitHub Actions workflow that:
- Builds YouTubeDownloader.exe on every tagged release (v1.0.0, etc.).
- Downloads a fresh portable ffmpeg build at build time.
- Uploads the exe to the GitHub Release.

---

## ⚠️ Notes & Limitations

- This tool is for personal use only. Make sure your usage complies with YouTube’s Terms of Service.
- Executables are unsigned; on Windows you may get a SmartScreen warning.
- Antivirus software may flag PyInstaller-built exes. This is a common false positive.

---

## 🙌 Credits

- yt-dlp
 — powerful YouTube downloader library.
- ffmpeg
 — video and audio processing.
- PyInstaller
 — packaging Python into standalone executables.
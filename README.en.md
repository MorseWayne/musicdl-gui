<div align="center">

# MusicdlGUI

[简体中文](README.md) | **English**

**Find music. Keep the sounds you love.**

A desktop music search and download app built with [musicdl](https://github.com/CharlesPikachu/musicdl) and PyQt5.

Search several music sources in one window, filter and download tracks in batches, and save the original audio or convert it to WAV or MP3.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](requirements.txt)
[![PyQt5 5.15.11](https://img.shields.io/badge/PyQt5-5.15.11-41CD52?logo=qt&logoColor=white)](requirements.txt)
[![musicdl 2.14.0](https://img.shields.io/badge/musicdl-2.14.0-3299ED)](https://github.com/CharlesPikachu/musicdl)
[![License MIT](https://img.shields.io/badge/License-MIT-blue)](LICENSE)
[![v1.3.0](https://img.shields.io/badge/release-v1.3.0-3299ED)](https://github.com/MorseWayne/musicdl-gui/releases/tag/v1.3.0)

[Get started](#get-started) · [Features](#features) · [Screenshots](#screenshots) · [Language](#interface-language) · [Usage](#usage) · [Troubleshooting](#troubleshooting)

</div>

![MusicdlGUI English interface: multiple sources, checked tracks and WAV output](resource/screenshot-english.png)

<p align="center"><sub>Current application widgets with offline example data. Actual results and source formats depend on the music platform.</sub></p>

> This project is for learning and educational use only and must not be used commercially. Respect platform terms and copyright. See the [disclaimer and license](#disclaimer-and-license).

## Features

| From search to saved audio | What you can do |
| --- | --- |
| **Search several sources** | QQ Music, Kuwo Music, Migu Music, Qianqian Music, Kugou Music and NetEase Music run independently, with results arriving as each source finishes. |
| **Find the version you want** | Search by song, artist or album, filter current results, and sort columns to compare duration, size, format and source. |
| **Download checked tracks** | Download a single track, a batch, or a track from the context menu. Follow per-track status and retry failed downloads. |
| **Choose a save format** | Keep the source audio or automatically convert downloads to WAV or MP3. No separate FFmpeg command installation is needed. |
| **Organize your files** | Use a flat folder, source folders, or source/date-and-keyword folders. Duplicate names receive a number instead of overwriting files. |
| **See task progress** | Each source has its own status and errors. Tasks support timeouts, cancellation, retry and logs. |
| **Make it yours** | Switch between Simplified Chinese and English, use light or dark mode, adjust search limits and timeouts, and configure platform cookies. |

The default sources are **Kuwo, Migu and NetEase**. Up to three sources run concurrently. Each source defaults to at most five results and a 60-second timeout, adjustable in Settings. Availability depends on your network, account permissions and upstream API changes.

## Screenshots

### Dark mode

![MusicdlGUI dark mode with search results and batch selection](resource/screenshot-dark.png)

Use **Switch theme** in the upper-right corner. The source format in the table and the save format at the bottom are shown separately. This screenshot uses the Chinese interface; the theme is also available in English.

<details>
<summary><strong>Settings: language, formats, folders and search preferences</strong></summary>

![MusicdlGUI settings with the bilingual language selector](resource/screenshot-settings.png)

The language selector is at the top. Download preferences, logs and platform cookies are configured in the same dialog. Paths are examples and cookie fields are empty.

</details>

## Get started

### Windows download

Download `MusicdlGUI-Windows-x64.zip` from the [v1.3.0 release page](https://github.com/MorseWayne/musicdl-gui/releases/tag/v1.3.0), **extract the entire archive**, and run `MusicdlGUI.exe`. Python and a separate FFmpeg installation are not required.

The official package targets Windows x64. No verified x86, macOS or Linux binary is provided. On macOS or Linux, use the source instructions below with a working graphical desktop and the required Qt system libraries.

The release also provides `SHA256SUMS.txt`. Compare its hash with the output of:

```powershell
Get-FileHash .\MusicdlGUI-Windows-x64.zip -Algorithm SHA256
```

Extract upgrades into a new folder. Existing user settings and your selected download folder are preserved. See the [quick-start guide](QUICKSTART.en.md) and [changelog](CHANGELOG.md).

### Run from source

Use **Python 3.10+**; **Python 3.11 / 3.12 x64** is recommended. This project targets `musicdl==2.14.0` and `PyQt5==5.15.11`.

Clone the repository, or download its source and open the project folder:

```bash
git clone https://github.com/MorseWayne/musicdl-gui.git
cd musicdl-gui
python -m venv .venv
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe check_env.py
.\.venv\Scripts\python.exe musicdlgui.py
```

**Linux / macOS:**

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python check_env.py
.venv/bin/python musicdlgui.py
```

If Linux reports an `xcb` plugin error, check your graphical environment and Qt system dependencies.

Older executables may contain obsolete platform APIs. Updating the repository does not update an existing executable: download the new release, run from source, or follow the [Windows build guide](BUILD.en.md).

## Interface language

Open **Settings (设置 / Settings)** → **Language (语言 / Language)** → **English** → **Save**.

The settings dialog previews the selected language immediately. Saving switches the main window without restarting, preserving search results, filters and checked tracks. The app remembers your choice for the next launch. Cancelling the dialog leaves the main window's language unchanged.

Simplified Chinese remains the default for compatibility with existing settings. Song titles, artist names, albums and other platform metadata stay as supplied by the music source. Language switching is included in v1.3.0; older executables need to be updated or rebuilt.

## Usage

### Save music in three steps

1. **Search:** select sources, enter a song, artist or album, and press `Enter`. Results arrive independently for each source.
2. **Choose:** click column headers to sort, use **Filter current results**, then check the tracks you want. If no boxes are checked, highlighted rows can be downloaded. Right-click a track to download it individually.
3. **Save:** choose the save format at the bottom and click **Download selected**. Follow each track's status, retry failures if needed, and use **Open download folder** to find completed files.

| Action | Effect |
| --- | --- |
| `Enter` in the search box | Start a search |
| `Ctrl+L` | Focus the search box |
| `Esc` | Cancel the current task |
| Select visible | Check only results currently visible after filtering |
| Retry failed sources / Retry failed downloads | Retry only failed sources or tracks |

You can also use **Cancel search** or **Cancel download**. Cancelling a search keeps results already received. Cancelling a download removes its temporary files and stops the remaining queue. Closing the window stops background tasks before exiting.

**Selection note:** checked tracks still count toward **Download selected** even when a filter hides them.

### Save formats

The save format is available in both the main window and Settings, for single and batch downloads.

| Format | Behavior and trade-off |
| --- | --- |
| **Keep original** (default) | Save the audio returned by the platform without conversion. |
| **WAV (lossless PCM)** | Preserve the sample rate, channels and decoded precision. Files are usually larger; 24-bit FLAC is stored as 32-bit PCM. |
| **MP3 (lossy)** | Conversion uses 320 kbps. Audio with more than two channels is mixed to stereo, and the sample rate is adapted to 32 / 44.1 / 48 kHz. |

For example, choose **Save format → WAV (lossless PCM)** before downloading FLAC tracks. The app shows conversion status and progress, then keeps only the target file.

- Conversion does not improve source audio quality or automatically convert files you already have.
- If the actual audio already matches the target format, it is kept without re-encoding. The app checks the content rather than just renaming the extension; existing MP3 files keep their original bitrate.
- Cancelling conversion or closing the app cleans up temporary source and unfinished target files. A failed conversion shows the cause; retry downloads the track again.
- Conversion uses the FFmpeg libraries in the PyAV wheel. A source installation needs all dependencies from [requirements.txt](requirements.txt), but no separate `ffmpeg` command.

### Settings and saved files

- **Download folder:** new installations default to `Musicdl` under your user's Music folder. Choose a flat structure, source folders, or source/date-and-keyword folders. Duplicate names are numbered, and files are published only after integrity checks pass.
- **Cookies:** configure them per platform. Empty download cookies inherit search cookies. Search again after editing cookies. Access remains limited to the permissions of your account.
- **Settings and logs:** settings are stored in `MusicdlGUI/settings.json` under the system user configuration directory; logs are in `MusicdlGUI/logs/` under the system user data directory. Log files and folders can be opened from Settings.
- **Migration:** on first launch, settings beside the old program are migrated without removing the original file or changing the download folder. Old relative paths are resolved against the old settings file's folder.
- **Credentials:** cookies are stored locally as plaintext. Do not share your settings file. Legacy Quark cookie values are preserved, but none of the current six sources uses a Quark entry, so that obsolete field is hidden.

## Troubleshooting

### A source fails or returns no tracks

The app distinguishes failed requests from a successful search with no downloadable results, shows the cause for each source and lets you retry only failed sources. The timeout includes source initialization and audio URL resolution.

For a bounded network diagnostic that does not read personal cookies or download songs:

```bash
python check_env.py --search "晴天" --timeout 60 --limit 5
python check_env.py --search "晴天" --sources MiguMusicClient,KuwoMusicClient
```

Use the Python interpreter from the virtual environment above. Diagnostic exit codes are `0` for a valid environment with search results, `1` for environment or argument errors, and `2` when no usable search results are obtained. Some diagnostic output is in Chinese.

Try another source or increase the timeout in Settings. If a download URL has expired, search again before downloading.

### Supported download types

The app supports HTTP direct-link audio from the six listed platforms. It does not support HLS playlists, DRM decryption or audio preview. Paid and login-required content remains subject to your account permissions.

## Development and validation

```bash
python -m pip install -r requirements.txt pytest
python -m pytest -q
```

Tests cover musicdl adaptation, subprocess cancellation and timeouts, cookies, HTTP downloads, actual WAV/MP3 encoding, conversion cancellation, complete file publication, settings migration, language switching, selection and batch queues. Qt tests use offscreen mode. Platform availability is checked separately with the diagnostic commands above.

| Module | Responsibility |
| --- | --- |
| `musicdlgui.py` | Main window, selection and download queue |
| `backend.py` | Platform adaptation and file transfers |
| `audio_conversion.py` | Streaming audio conversion |
| `workers.py` | Bounded subprocesses and background tasks |
| `app_config.py` | Settings, migration and user directories |
| `i18n.py` | Chinese/English text, live switching and task languages |

See [BUILD.en.md](BUILD.en.md) for Windows packaging and release checks. Passing source tests alone does not validate a packaged executable.

## Disclaimer and license

This project is for learning and educational use only and must not be used commercially. It does not host or distribute copyrighted content. Buy or subscribe to the relevant music services to access paid tracks; do not bypass payment restrictions or DRM.

The repository code is licensed under the [MIT License](LICENSE). Use and distribution of musicdl must also comply with its own license.

Thanks to [musicdl](https://github.com/CharlesPikachu/musicdl) author Charles's Pikachu for the music platform integrations.

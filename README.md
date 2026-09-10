# JoyHub Melody Player

A Linux desktop media player for controlling the **JoyHub Melody** while playing local videos and matching `.funscript` files.

## Highlights

- Direct BLE support for JoyHub Melody
- Local video playback through MPV
- Funscript-to-vibration conversion
- Vibration patterns
- Pump / suction controls
- R4 release timing controls
- Playlist / next-video workflow
- Funscript timeline with seeking controls
- **Bilingual interface: Français / English**
- Language choice is saved in the application configuration
- No hard-coded personal home directory or private Python virtual environment

## Requirements

- Linux
- Python 3
- Bluetooth Low Energy adapter
- JoyHub Melody
- MPV
- Python packages from `requirements.txt`

On Debian/Ubuntu:

```bash
sudo apt install mpv python3-tk python3-venv
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 src/JoyHub-Melody-Player.py
```

## Video directory

By default the application starts from:

```text
~/Videos
```

You can override this with:

```bash
export JOYHUB_VIDEO_DIR="/path/to/your/videos"
python3 src/JoyHub-Melody-Player.py
```

## Language

Use the language selector in the top-right area of the interface:

- Français
- English

The selected language is stored in the application configuration.

## Funscripts

The application searches for a matching script using the video filename, including `.funscript` and `.vib.funscript` variants.

Example:

```text
example.mp4
example.funscript
```

## Status

Experimental community-developed software. Hardware/firmware and Bluetooth compatibility may vary.

## Disclaimer

This is an independent community project. It is not affiliated with, endorsed by, sponsored by, or officially supported by JoyHub or its manufacturers.

Use the software and connected hardware at your own risk.

## uv deployment

The recommended deployment method is [`uv`](https://docs.astral.sh/uv/). The project uses the system Python so Tkinter remains provided by the Linux distribution.

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install -y python3 python3-tk mpv bluetooth bluez
```

Install `uv` using the official installation method, then clone and synchronize the project:

```bash
git clone https://github.com/st3ph666/JoyHub-Melody-Player.git
cd JoyHub-Melody-Player
uv sync
uv run python JoyHub-Melody-Player-v2.5.4.py
```

Do not run `uv sync` with `sudo`. Bluetooth access remains managed by the normal Linux user session and BlueZ.

### Update an existing installation

```bash
git pull
uv sync
uv run python JoyHub-Melody-Player-v2.5.4.py
```

## Source architecture

```text
JoyHub-Melody-Player-v2.5.4.py  # Compatibility launcher
src/joyhub_melody/
├── __init__.py                 # Version metadata
├── settings.py                 # Paths, UI strings, patterns and colors
├── engine.py                   # Embedded BLE engine bundle installer
├── funscript.py                # Funscript discovery and conversion helpers
├── app.py                      # Tkinter application
└── main.py                     # Application entry point
```

Source-code comments are maintained in **English only**. The graphical interface remains bilingual French / English.


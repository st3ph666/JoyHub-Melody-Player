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

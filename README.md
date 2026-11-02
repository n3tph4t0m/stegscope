<div align="center">

# StegScope

**Self-hosted image analysis and steganography, built for CTF.**

A minimalist, fast alternative to Aperi'Solve: drop an image, the server chains
the usual analysis tools and returns a readable report, highlighting flag-like
patterns along the way.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask&logoColor=white)
![Status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)

</div>

---

## Overview

StegScope exposes a dark web interface where you drop an image. In the
background, a Flask server runs a battery of analysis tools in an isolated
environment, aggregates the results and automatically highlights strings that
look like a flag.

```
┌──────────────┐   upload    ┌───────────────┐   subprocess   ┌──────────────────────────┐
│   Browser    │ ──────────▶ │  Flask (API)  │ ─────────────▶ │ file · exiftool · strings │
│  (dark UI)   │ ◀────────── │  /api/analyze │ ◀───────────── │ binwalk · zsteg           │
└──────────────┘   report    └───────────────┘    results     └──────────────────────────┘
```

## Quick start

```bash
git clone https://github.com/qkjhdflj/stegscope.git
cd stegscope
./start.sh
```

`start.sh` creates the virtual environment, installs the dependencies on first
run, then serves the interface at **http://127.0.0.1:5000**.

## Features

- Upload by drag-and-drop or file picker.
- Automatic chaining of `file`, `exiftool`, `strings`, `binwalk` and `zsteg`.
- String filtering on flag patterns (`xxx{...}`) and sensitive lines.
- Detection of tools missing on the server, reported without aborting the analysis.
- Clean dark interface, validated upload and work in an isolated temporary directory.

## Tech stack

| Layer | Technologies |
|---|---|
| Backend | Python 3, Flask, `subprocess` (no shell, with timeout) |
| Analysis | `file`, `exiftool`, `strings`, `binwalk`, `zsteg` |
| Frontend | HTML5, Tailwind CSS (CDN), vanilla JavaScript — no build step |

## Requirements

Python 3.10 or later, and the analysis tools available in the `PATH`.

```bash
# Debian / Ubuntu / Kali
sudo apt install exiftool binwalk file binutils
# zsteg (Ruby gem)
sudo gem install zsteg
```

Missing tools do not block the application: they appear as "unavailable" in the
report.

## Manual installation

If you prefer not to use `start.sh`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Configuration

Adjustable through environment variables:

| Variable | Purpose | Default |
|---|---|---|
| `STEGSCOPE_SECRET` | Flask session key | random |
| `STEGSCOPE_UPLOADS` | Working directory | `./uploads` |
| `STEGSCOPE_MAX_BYTES` | Maximum upload size | `16777216` (16 MB) |
| `STEGSCOPE_TIMEOUT` | Per-tool timeout, in seconds | `25` |

## Usage

1. Open the interface and drop an image (PNG, JPG, GIF, BMP, WEBP, TIFF).
2. Each tool produces a result card; detected flag patterns are highlighted at
   the top of the `strings` card.
3. The file is deleted from the server as soon as the analysis finishes.

## Project layout

```
stegscope/
├── run.py                   entry point
├── start.sh                 launcher (venv + install + run)
├── requirements.txt
└── stegscope/
    ├── __init__.py          application factory
    ├── config.py            configuration via environment variables
    ├── analysis.py          analysis engine (tool registry)
    ├── views.py             routes and API
    ├── templates/index.html interface
    └── static/app.js        front-end logic
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) to add an
analysis tool or propose an improvement.

## Security

StegScope runs analysis binaries on the files you provide. Host it on a trusted
machine and use it only on files you are authorised to analyse: CTF, labs and
permitted environments.

## License

Released under the MIT License. See [LICENSE](LICENSE).

# Moon to Ko

> [!WARNING]
> **DISCLAIMER: This is a 100% vibe-coded project built expressly for my personal use.** Started at 1 am and didnt read anything written after 2 am.
> While it works on my machine™, I highly advise against using it. If you decide to do so anyway, against my advice, you do so entirely at your own risk. I take no responsibility if it accidentally turns your e-reader into a toaster or scrambles your reading history.

A CLI tool for migrating reading progress, statistics, EPUB files, and text replacement rules from Moon+ Reader Pro (`.mrpro` backups) to KOReader.

## Features

- **Metadata Sync**: Reconstructs your reading progress and statistics seamlessly into KOReader format (`percent_finished`, `statistics.sqlite3`).
- **EPUB Extraction**: Directly dumps your entire EPUB library embedded within the backup zip into usable files.
- **Text Replacements**: Parses custom Lua/Regex book-specific replacements and seamlessly generates KOReader `.sdr` rule sidecars.
- **Desktop GUI**: A clean, dark-mode graphical interface. No terminal required.

## Quick Start (Standalone Executable)

Download the latest `MoonToKo.exe` from the [Releases](../../releases) page. Double-click it. No Python installation required.

## Usage (CLI)

```bash
uv run python -m src.main -i <path_to_mrpro> -o <path_for_output_dir> [--extract-epubs] [--extract-replacements]
```

### Options

- `-i`, `--input`: (Required) Path to the `.mrpro` backup file.
- `-o`, `--output`: (Required) Path where KOReader output files will be generated.
- `--extract-epubs`: Extracts all EPUB books from the backup directly into `<output_dir>/books`.
- `--extract-replacements`: Automatically injects book-specific Moon+ text replacement configurations into generated KOReader `.sdr` configurations.

## Moving Files

1. Copy the generated `statistics.sqlite3` file directly into your KOReader `settings/` folder to apply your global reading history.
2. Copy the generated `.sdr` folders and place them next to your actual book files on the e-reader to import reading positions and text replacements.

## Building from Source

### Prerequisites

- Python 3.12+
- `uv` package manager

### Running the GUI locally

```bash
uv run python -m src.gui
```

### Building the standalone executable

```bash
uv run pyinstaller --onefile --windowed --name MoonToKo --add-data "src;src" src/gui.py
```

The executable will be generated in the `dist/` directory.

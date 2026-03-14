# Project Overview: Moon+ to KOReader Migration

## Goal
Evaluate and potentially implement a tool that allows people to use a Moon+ Reader Pro backup file (`.mrpro`) to transfer their books and reading progress to KOReader.

## Active Phase
- **Phase 3: Optional Extractions [COMPLETED]**
  - Implement `--extract-epubs` CLI argument.
  - Implement `--extract-replacements` CLI argument for global and book-specific replacements.
  - Output KOReader compatible `htmlreplacer` Lua scripts.

## Previous Phases
- **Phase 2: Implementation [COMPLETED]**
  - Initialize project with `uv`.
  - Build `mrpro_extractor.py`.
  - Build `db_mapper.py`.
  - Build `koreader_exporter.py`.
  - Build `main.py` CLI.

## Previous Phases
- **Phase 1: Research and Evaluation [COMPLETED]**
  - Understand the `.mrpro` format.
  - Understand the KOReader metadata format.
  - Determine feasibility and mapping logic.

## Evaluation Findings
**1. The `.mrpro` Format:**
- A `.mrpro` backup extracts into a directory containing chronologically or sequentially numbered files (e.g., `1.tag`, `2.tag`, ...).
- It relies on a `_names.list` index file to map the original Android filesystem paths to these `.tag` files.
- The core data resides in an SQLite DB named `mrbooks.db` (usually mapped to an early `.tag` file like `2.tag`).

**2. KOReader Metadata:**
- Global read data is tracked within `settings/statistics.sqlite`.
- Book-local progress (percentage, layout, XPaths) is tracked in Lua `.sdr` sidecar files adjacent to the EPUBs.

**3. Feasibility Assessment - POSITIVE, BUT WITH CAVEATS:**
- Transferring **Books, Categories, and Global Statistics** is 100% viable by mapping records from `mrbooks.db` into KOReader's `statistics.sqlite`.
- perfectly translating **Reading Progress** is technically imperfect due to differing layout engines. Moon+ stores layout offsets (`lastPosition` / `.epub.r` files) while KOReader relies on XPaths and absolute percentage. However, we *can* approximate the `percent_finished` based on the data and inject it into dynamically created `.sdr` Lua files.

**Conclusion:** It is highly feasible to construct a Python parsing tool (`mrpro_to_koreader.py`) that unzips/parses the `.mrpro` backup, extracts the DB, maps the book library properties, and generates KOReader `.sdr` sidecar files containing estimated reading percentages.

## Single Source of Truth
This file serves as the Single Source of Truth (SSOT). All planning and coordination must happen here.

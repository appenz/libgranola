# libgranola library

A Python library to read local Granola meeting notes from the application's cache file.

The library provides read-only access to:
- Meeting documents (title, attendees, calendar event, notes, overview, summary)
- Transcripts (timestamped segments with speaker attribution)
- People directory (contacts with enriched company/role details)

The library has a comprehensive set of tests, they can be invoked via `make test`. Packages are managed with uv.

# Directory Layout

- `src/libgranola/` - Library source code
- `tests/` - Pytest test suite (runs against the real Granola cache)
- `examples/` - Runnable example scripts
- `spec/` - Project specification

# Packaging

- Build system: `uv_build` (configured in pyproject.toml)
- `uv build` produces sdist + wheel in `dist/`
- Makefile targets: `make build` (build), `make clean` (remove artifacts)
- Classifiers: macOS, Python 3.13, Apache 2.0

# Cache Format

The Granola cache is at `~/Library/Application Support/Granola/cache-v6.json`.

Outer structure: `{"cache": {"version": N, "state": {...}}}`.

Key state fields:
- `documents` - dict of meeting documents keyed by UUID
- `transcripts` - dict of transcript segment lists keyed by meeting UUID
- `people` - list of contact records
- `calendars` - list of linked calendar accounts

Each document contains: `id`, `title`, `created_at`, `updated_at`, `type`, `people` (creator + attendees with enriched details), `google_calendar_event`, `notes` (ProseMirror), `notes_plain`, `notes_markdown`, `overview`, `summary`, and more.

Each transcript is a list of segments: `{id, document_id, start_timestamp, end_timestamp, text, source, is_final}`.

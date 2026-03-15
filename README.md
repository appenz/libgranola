# libgranola

A Python library to read local Granola meeting notes from the application's cache file.

## Overview

NOTE: As of Granola cache-v6.json, this library no longer works. The actual data seems to live in an encrypted SQLite database. Below a best guess from Codex where the data is located. They also don't have a local API and they don't have a cloud API for basic users. This probably means it's time to switch away from Granola.

Buried in Chromium's Origin Private File System (OPFS), there are two key files:

OPFS file	Maps to	Size
File System/000/t/00/00000001	/granola.db	2.3 MB
File System/000/t/00/00000003	/granola.db-wal	4.6 MB
The WAL file has a valid SQLite WAL header (magic 0x377F0682, page size 4096, format version 3007000, 1118 frames across 232 unique pages). However, all page content is encrypted — page 1 has random bytes instead of the standard SQLite format 3\0 header. This is consistent with SQLCipher or a similar encryption extension used by wa-sqlite inside the Electron app.

"Saki Weisman" and "Guido/Kamakshi" were not found anywhere — not in the cache JSON, not in the OPFS database (encrypted), not in Session Storage, Local Storage, IndexedDB, or any of the 356 files in the Granola data directory.

Bottom line: Granola stores its full notes and transcripts in an encrypted SQLite database accessible only to the running Electron app. The cache-v6.json that libgranola reads is a lightweight metadata layer with mostly empty note/transcript fields. To get full transcript access, you'd likely need to go through Granola's Supabase API (the app has auth tokens in supabase.json) rather than reading local files.

- Read-only access to Granola meetings, transcripts, and people
- Zero dependencies beyond the Python standard library
- Fully typed with frozen dataclasses
- Apache 2.0

Written by Guido Appenzeller, guido@appenzeller.net.

## Requirements

- macOS (Granola stores its cache in `~/Library/Application Support/Granola/`)
- Python 3.13+
- A local Granola installation with cached data

## Installation

With pip:

```bash
pip install LibGranola
```

With uv:

```bash
uv add LibGranola
```

For development:

```bash
git clone https://github.com/appenz/libgranola
cd libgranola
make install
```

## Quick Start

```python
from libgranola import GranolaStore

store = GranolaStore()

# List all meetings (newest first)
for meeting in store.list_meetings():
    print(f"{meeting.created_at:%Y-%m-%d} {meeting.title}")

# Search meetings
results = store.find_meetings("standup")

# Search specific fields
results = store.find_meetings("@acme.com", fields=["attendee_email"])

# Get transcript for a meeting
transcript = store.get_transcript(meeting.id)
if transcript:
    for seg in transcript:
        print(f"[{seg.start:%H:%M:%S}] {seg.text}")

# List people directory
for person in store.list_people():
    print(f"{person.name} ({person.email})")
```

## Searchable Fields

When using `find_meetings`, you can restrict search to specific fields:

- `title`, `notes_plain`, `notes_markdown`, `overview`, `summary`
- `creator_name`, `creator_email`
- `attendee_name`, `attendee_email`

Pass `fields=None` (default) to search all fields.

## Development

```bash
make install    # Install with dev dependencies
make test       # Run tests
make lint       # Check code style
make format     # Auto-format code
make build      # Build package
```

## License

Apache 2.0. See [LICENSE](LICENSE).

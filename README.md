# libgranola

A Python library to read local Granola meeting notes from the application's cache file.

## Overview

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

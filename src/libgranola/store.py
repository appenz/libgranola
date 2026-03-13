"""GranolaStore: main entry point for reading local Granola meeting notes."""

from __future__ import annotations

from pathlib import Path

from .types import Meeting, Person, TranscriptSegment


class GranolaStore:
    """Provides read-only access to Granola meeting notes from the local cache.

    On initialization, loads and parses the Granola cache file.  By default the
    highest-version ``cache-v*.json`` in ``~/Library/Application Support/Granola``
    is used, but an explicit path may be supplied.
    """

    SEARCHABLE_FIELDS: list[str] = [
        "title",
        "notes_plain",
        "notes_markdown",
        "overview",
        "summary",
        "attendee_name",
        "attendee_email",
        "creator_name",
        "creator_email",
    ]

    def __init__(self, path: Path | str | None = None) -> None:
        from ._parser import (
            find_cache_file,
            load_state,
            parse_meetings,
            parse_people,
            parse_transcripts,
        )

        if path is not None:
            cache_path = Path(path)
        else:
            cache_path = find_cache_file()

        self._path = cache_path
        state = load_state(cache_path)
        self._meetings = parse_meetings(state)
        self._transcripts = parse_transcripts(state)
        self._people = parse_people(state)

    @property
    def cache_path(self) -> Path:
        """The path to the cache file that was loaded."""
        return self._path

    def list_meetings(self, *, include_invalid: bool = False) -> list[Meeting]:
        """Return all meetings, sorted by creation date (newest first).

        Args:
            include_invalid: If True, include meetings flagged as invalid.
        """
        meetings = list(self._meetings.values())
        if not include_invalid:
            meetings = [m for m in meetings if m.is_valid]
        return sorted(meetings, key=lambda m: m.created_at, reverse=True)

    def get_meeting(self, meeting_id: str) -> Meeting | None:
        """Return a single meeting by ID, or None if not found."""
        return self._meetings.get(meeting_id)

    def find_meetings(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        case_sensitive: bool = False,
    ) -> list[Meeting]:
        """Search meetings by text query with optional field restriction.

        Args:
            query: Text to search for.
            fields: Which fields to search.  None means all searchable fields.
                See ``GranolaStore.SEARCHABLE_FIELDS`` for valid names.
            case_sensitive: Whether the search is case-sensitive.  Default False.
        """
        targets = fields or self.SEARCHABLE_FIELDS
        q = query if case_sensitive else query.lower()
        results: list[Meeting] = []

        for meeting in self._meetings.values():
            if _meeting_matches(meeting, q, targets, case_sensitive):
                results.append(meeting)

        return sorted(results, key=lambda m: m.created_at, reverse=True)

    def get_transcript(self, meeting_id: str) -> list[TranscriptSegment] | None:
        """Return transcript segments for a meeting, or None if unavailable."""
        return self._transcripts.get(meeting_id)

    def list_people(self) -> list[Person]:
        """Return the people directory from the cache."""
        return list(self._people)


def _meeting_matches(
    meeting: Meeting,
    query: str,
    fields: list[str],
    case_sensitive: bool,
) -> bool:
    for field_name in fields:
        value = _get_field_value(meeting, field_name)
        if value is None:
            continue
        text = value if case_sensitive else value.lower()
        if query in text:
            return True
    return False


def _get_field_value(meeting: Meeting, field_name: str) -> str | None:
    if field_name == "title":
        return meeting.title
    if field_name == "notes_plain":
        return meeting.notes_plain or None
    if field_name == "notes_markdown":
        return meeting.notes_markdown or None
    if field_name == "overview":
        return meeting.overview
    if field_name == "summary":
        return meeting.summary
    if field_name == "attendee_name":
        return " ".join(a.name or "" for a in meeting.attendees) or None
    if field_name == "attendee_email":
        return " ".join(a.email or "" for a in meeting.attendees) or None
    if field_name == "creator_name":
        return meeting.creator.name if meeting.creator else None
    if field_name == "creator_email":
        return meeting.creator.email if meeting.creator else None
    return None

"""Internal: parse Granola cache JSON into typed dataclasses."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from .types import Attendee, CalendarEvent, Meeting, Person, TranscriptSegment

log = logging.getLogger("libgranola")

DEFAULT_CACHE_DIR = Path.home() / "Library" / "Application Support" / "Granola"
SUPPORTED_VERSIONS = {5}


def find_cache_file(base: Path = DEFAULT_CACHE_DIR) -> Path:
    """Find the highest-version cache-v*.json in *base*."""
    candidates = sorted(
        base.glob("cache-v*.json"),
        key=lambda p: int(p.stem.removeprefix("cache-v")),
        reverse=True,
    )
    if not candidates:
        msg = f"No cache-v*.json found in {base}"
        raise FileNotFoundError(msg)
    return candidates[0]


def load_state(path: Path) -> dict[str, Any]:
    """Read a Granola cache file and return the inner state dict."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    cache = raw.get("cache", raw)
    if isinstance(cache, str):
        cache = json.loads(cache)
    version = cache.get("version")
    if version not in SUPPORTED_VERSIONS:
        log.warning(
            "Granola cache version %s (file %s) has not been tested; "
            "parsing will proceed but may produce incomplete results",
            version,
            path.name,
        )
    state = cache.get("state", cache)
    return state


# -- Timestamp helpers -------------------------------------------------------

def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    s = value.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


def _parse_dt_required(value: str) -> datetime:
    s = value.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


def _parse_calendar_dt(obj: dict[str, Any] | str | None) -> tuple[datetime | None, str | None]:
    """Parse a Google Calendar start/end object like ``{dateTime, timeZone}``."""
    if obj is None:
        return None, None
    if isinstance(obj, str):
        return _parse_dt(obj), None
    dt_str = obj.get("dateTime") or obj.get("date")
    tz = obj.get("timeZone")
    return _parse_dt(dt_str), tz


# -- Attendee / Person helpers -----------------------------------------------

def _parse_attendee(raw: dict[str, Any]) -> Attendee:
    details = raw.get("details", {})
    person = details.get("person", {})
    company = details.get("company", {})
    employment = person.get("employment", {})
    linkedin_info = person.get("linkedin", {})
    return Attendee(
        name=raw.get("name") or _fullname(person),
        email=raw.get("email"),
        company=employment.get("name") or company.get("name"),
        job_title=employment.get("title"),
        linkedin=linkedin_info.get("handle"),
        avatar=person.get("avatar"),
    )


def _fullname(person: dict[str, Any]) -> str | None:
    name_obj = person.get("name", {})
    if isinstance(name_obj, str):
        return name_obj
    return name_obj.get("fullName")


# -- Document -> Meeting -----------------------------------------------------

def parse_meeting(doc: dict[str, Any]) -> Meeting:
    """Convert a single cache document dict into a Meeting dataclass."""
    people = doc.get("people") or {}
    creator_raw = people.get("creator")
    attendees_raw = people.get("attendees") or []

    creator = _parse_attendee(creator_raw) if creator_raw else None
    attendees = [_parse_attendee(a) for a in attendees_raw]

    cal_event = _parse_calendar_event(doc.get("google_calendar_event"))

    notes_content = doc.get("notes") or {}
    notes_text = ""
    if isinstance(notes_content, dict) and notes_content.get("content"):
        notes_text = _extract_prosemirror_text(notes_content["content"])

    notes_plain = doc.get("notes_plain") or notes_text
    notes_markdown = doc.get("notes_markdown") or ""

    return Meeting(
        id=doc["id"],
        title=doc.get("title", ""),
        created_at=_parse_dt_required(doc["created_at"]),
        updated_at=_parse_dt(doc.get("updated_at")),
        type=doc.get("type", "meeting"),
        creator=creator,
        attendees=attendees,
        calendar_event=cal_event,
        notes_plain=notes_plain,
        notes_markdown=notes_markdown,
        overview=doc.get("overview"),
        summary=doc.get("summary"),
        transcribe=bool(doc.get("transcribe")),
        is_valid=bool(doc.get("valid_meeting", True)),
        source=doc.get("creation_source"),
        workspace_id=doc.get("workspace_id"),
    )


def _parse_calendar_event(raw: dict[str, Any] | None) -> CalendarEvent | None:
    if not raw:
        return None
    start_dt, start_tz = _parse_calendar_dt(raw.get("start"))
    end_dt, _ = _parse_calendar_dt(raw.get("end"))
    return CalendarEvent(
        provider_id=raw.get("id", ""),
        summary=raw.get("summary"),
        description=raw.get("description"),
        location=raw.get("location"),
        start=start_dt,
        end=end_dt,
        timezone=start_tz,
    )


# -- ProseMirror text extraction ---------------------------------------------

def _extract_prosemirror_text(nodes: list[dict[str, Any]]) -> str:
    """Recursively extract plain text from ProseMirror node list."""
    parts: list[str] = []
    for node in nodes:
        ntype = node.get("type", "")
        if ntype == "text":
            parts.append(node.get("text", ""))
        elif "content" in node:
            parts.append(_extract_prosemirror_text(node["content"]))
        if ntype in ("paragraph", "heading", "bulletList", "orderedList", "listItem"):
            parts.append("\n")
    return "".join(parts).strip()


# -- Transcript segments -----------------------------------------------------

def parse_transcript_segments(
    raw_segments: list[dict[str, Any]],
) -> list[TranscriptSegment]:
    """Convert a list of raw transcript segment dicts."""
    result: list[TranscriptSegment] = []
    for seg in raw_segments:
        result.append(
            TranscriptSegment(
                id=seg["id"],
                document_id=seg.get("document_id", ""),
                start=_parse_dt_required(seg["start_timestamp"]),
                end=_parse_dt_required(seg["end_timestamp"]),
                text=seg.get("text", ""),
                source=seg.get("source"),
                is_final=seg.get("is_final", True),
            )
        )
    return result


# -- People ------------------------------------------------------------------

def parse_person(raw: dict[str, Any]) -> Person:
    return Person(
        id=raw["id"],
        name=raw.get("name", ""),
        email=raw.get("email"),
        job_title=raw.get("job_title"),
        company_name=raw.get("company_name"),
        company_description=raw.get("company_description"),
        avatar=raw.get("avatar"),
        links=raw.get("links") or [],
    )


# -- Full cache parsing ------------------------------------------------------

def parse_meetings(state: dict[str, Any]) -> dict[str, Meeting]:
    docs = state.get("documents", {})
    return {doc_id: parse_meeting(doc) for doc_id, doc in docs.items()}


def parse_transcripts(state: dict[str, Any]) -> dict[str, list[TranscriptSegment]]:
    raw = state.get("transcripts", {})
    result: dict[str, list[TranscriptSegment]] = {}
    for key, segments in raw.items():
        if isinstance(segments, list):
            result[key] = parse_transcript_segments(segments)
    return result


def parse_people(state: dict[str, Any]) -> list[Person]:
    return [parse_person(p) for p in state.get("people", [])]

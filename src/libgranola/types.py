"""Data types for libgranola: dataclass representations of Granola cache objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Attendee:
    """A meeting participant with optional enriched details."""

    name: str | None = None
    email: str | None = None
    company: str | None = None
    job_title: str | None = None
    linkedin: str | None = None
    avatar: str | None = None


@dataclass(frozen=True)
class CalendarEvent:
    """Calendar event metadata linked to a Granola meeting."""

    provider_id: str
    summary: str | None = None
    description: str | None = None
    location: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    timezone: str | None = None


@dataclass(frozen=True)
class TranscriptSegment:
    """A single segment of a meeting transcript."""

    id: str
    document_id: str
    start: datetime
    end: datetime
    text: str
    source: str | None = None
    is_final: bool = True


@dataclass(frozen=True)
class Person:
    """A contact in the Granola people directory."""

    id: str
    name: str
    email: str | None = None
    job_title: str | None = None
    company_name: str | None = None
    company_description: str | None = None
    avatar: str | None = None
    links: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Meeting:
    """A Granola meeting note (document)."""

    id: str
    title: str
    created_at: datetime
    updated_at: datetime | None = None

    type: str = "meeting"
    creator: Attendee | None = None
    attendees: list[Attendee] = field(default_factory=list)
    calendar_event: CalendarEvent | None = None

    notes_plain: str = ""
    notes_markdown: str = ""
    overview: str | None = None
    summary: str | None = None

    transcribe: bool = False
    is_valid: bool = True
    source: str | None = None
    workspace_id: str | None = None

"""libgranola: Python library to read local Granola meeting notes."""

import logging

from .store import GranolaStore
from .types import (
    Attendee,
    CalendarEvent,
    Meeting,
    Person,
    TranscriptSegment,
)

logging.getLogger("libgranola").addHandler(logging.NullHandler())

__all__ = [
    "Attendee",
    "CalendarEvent",
    "GranolaStore",
    "Meeting",
    "Person",
    "TranscriptSegment",
]

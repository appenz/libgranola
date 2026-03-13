"""Tests for libgranola data types."""

from __future__ import annotations

from datetime import UTC, datetime

from libgranola import Attendee, CalendarEvent, Meeting, Person, TranscriptSegment


class TestAttendee:
    def test_construct(self):
        a = Attendee(name="Alice", email="alice@example.com")
        assert a.name == "Alice"
        assert a.email == "alice@example.com"
        assert a.company is None

    def test_frozen(self):
        a = Attendee(name="Alice")
        try:
            a.name = "Bob"  # type: ignore[misc]
            raise AssertionError("Expected FrozenInstanceError")
        except AttributeError:
            pass


class TestMeeting:
    def test_construct_minimal(self):
        m = Meeting(
            id="abc",
            title="Test",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
        assert m.id == "abc"
        assert m.attendees == []
        assert m.notes_plain == ""

    def test_defaults(self):
        m = Meeting(
            id="x",
            title="T",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
        assert m.type == "meeting"
        assert m.is_valid is True
        assert m.transcribe is False


class TestTranscriptSegment:
    def test_construct(self):
        seg = TranscriptSegment(
            id="s1",
            document_id="d1",
            start=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
            end=datetime(2026, 1, 1, 10, 1, tzinfo=UTC),
            text="Hello",
        )
        assert seg.text == "Hello"
        assert seg.is_final is True


class TestPerson:
    def test_construct(self):
        p = Person(id="p1", name="Bob", email="bob@example.com")
        assert p.name == "Bob"
        assert p.links == []


class TestCalendarEvent:
    def test_construct(self):
        ce = CalendarEvent(
            provider_id="g123",
            summary="Standup",
            start=datetime(2026, 1, 1, 9, 0, tzinfo=UTC),
            end=datetime(2026, 1, 1, 9, 30, tzinfo=UTC),
            timezone="America/Los_Angeles",
        )
        assert ce.summary == "Standup"
        assert ce.timezone == "America/Los_Angeles"

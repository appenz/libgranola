"""Tests for GranolaStore loading and query methods."""

from __future__ import annotations

from datetime import datetime


class TestGranolaStore:
    def test_store_loads(self, store):
        assert store is not None
        assert store.cache_path.exists()

    def test_list_meetings(self, store):
        meetings = store.list_meetings()
        assert isinstance(meetings, list)
        assert len(meetings) > 0
        for m in meetings:
            assert m.id
            assert m.title
            assert isinstance(m.created_at, datetime)

    def test_meetings_sorted_newest_first(self, store):
        meetings = store.list_meetings()
        if len(meetings) >= 2:
            for a, b in zip(meetings, meetings[1:]):
                assert a.created_at >= b.created_at

    def test_get_meeting(self, store):
        meetings = store.list_meetings()
        first = meetings[0]
        fetched = store.get_meeting(first.id)
        assert fetched is not None
        assert fetched.id == first.id
        assert fetched.title == first.title

    def test_get_meeting_not_found(self, store):
        assert store.get_meeting("nonexistent-id-12345") is None

    def test_find_meetings(self, store):
        meetings = store.list_meetings()
        if not meetings:
            return
        title_word = meetings[0].title.split()[0]
        results = store.find_meetings(title_word)
        assert len(results) >= 1
        assert any(m.id == meetings[0].id for m in results)

    def test_find_meetings_field_restriction(self, store):
        meetings = store.list_meetings()
        if not meetings:
            return
        title_word = meetings[0].title.split()[0]
        results = store.find_meetings(title_word, fields=["title"])
        assert len(results) >= 1

    def test_find_meetings_no_match(self, store):
        results = store.find_meetings("xyzzy_absolutely_no_meeting_has_this_string_42")
        assert results == []

    def test_meeting_has_creator_or_attendees(self, store):
        meetings = store.list_meetings()
        has_people = any(m.creator is not None or len(m.attendees) > 0 for m in meetings)
        assert has_people, "Expected at least one meeting with creator or attendees"

    def test_meeting_calendar_event(self, store):
        meetings = store.list_meetings()
        has_cal = any(m.calendar_event is not None for m in meetings)
        assert has_cal, "Expected at least one meeting with a calendar event"

    def test_searchable_fields(self, store):
        assert "title" in store.SEARCHABLE_FIELDS
        assert "attendee_email" in store.SEARCHABLE_FIELDS

    def test_list_people(self, store):
        people = store.list_people()
        assert isinstance(people, list)
        assert len(people) > 0
        for p in people:
            assert p.id
            assert p.name


class TestTranscripts:
    def test_get_transcript(self, store):
        meetings = store.list_meetings()
        found = False
        for m in meetings:
            segments = store.get_transcript(m.id)
            if segments is not None:
                found = True
                assert len(segments) > 0
                seg = segments[0]
                assert seg.text
                assert isinstance(seg.start, datetime)
                assert isinstance(seg.end, datetime)
                break
        if not found:
            for tid in store._transcripts:
                segments = store._transcripts[tid]
                assert len(segments) > 0
                break

    def test_get_transcript_not_found(self, store):
        assert store.get_transcript("nonexistent-id-12345") is None

"""List recent Granola meetings."""

from libgranola import GranolaStore

store = GranolaStore()

for meeting in store.list_meetings():
    creator = meeting.creator.name if meeting.creator else "unknown"
    n_attendees = len(meeting.attendees)
    print(f"{meeting.created_at:%Y-%m-%d %H:%M}  {meeting.title}")
    print(f"  Creator: {creator}, Attendees: {n_attendees}")
    if meeting.calendar_event and meeting.calendar_event.start:
        print(f"  Scheduled: {meeting.calendar_event.start:%Y-%m-%d %H:%M}")
    print()

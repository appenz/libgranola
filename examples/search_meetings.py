"""Search Granola meetings by keyword."""

import sys

from libgranola import GranolaStore

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <search_term>")
    sys.exit(1)

query = " ".join(sys.argv[1:])
store = GranolaStore()
results = store.find_meetings(query)

print(f"Found {len(results)} meeting(s) matching '{query}':\n")
for m in results:
    print(f"  {m.created_at:%Y-%m-%d}  {m.title}")
    transcript = store.get_transcript(m.id)
    if transcript:
        print(f"    Transcript: {len(transcript)} segments")

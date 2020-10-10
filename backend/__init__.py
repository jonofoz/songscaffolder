import os
import json
from SongScaffolder import BASE_DIR

def generate_starter_data():
    starter_data = {}
    for field_name in ["chords", "feels", "genres", "influences", "instruments", "key-signatures", "moods", "themes", "time-signatures"]:
        with open(os.path.join(BASE_DIR, "backend", "starter_data", f"{field_name}.json")) as f:
            starter_data[field_name] = json.load(f)
    return starter_data
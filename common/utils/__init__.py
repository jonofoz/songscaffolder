import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient

sys.path.append(os.path.join("..", ".."))

from SongScaffolder import BASE_DIR
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))
try:
    os.getenv("DB_USER")
except KeyError:
    # Handled by Travis for testing purposes.
    raise

def get_file_dir(filename):
    return os.path.dirname(os.path.abspath(os.path.basename(filename)))
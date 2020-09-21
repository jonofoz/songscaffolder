import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient

sys.path.append(os.path.join("..", ".."))

from SongScaffolder import BASE_DIR
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))
try:
    os.environ["DB_USER"]
except KeyError:
    # Handled by Travis for testing purposes.
    raise

def get_file_dir(filename):
    return os.path.dirname(os.path.abspath(os.path.basename(filename)))

def connect_to_database(use_test_db=False):
    # Load user_data from MongoDB.
    cluster = MongoClient(f'mongodb+srv://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_PATH")}?retryWrites=true&w=majority')
    if not use_test_db:
        return cluster[os.getenv("DB_NAME")]
    else:
        return cluster["test_" + os.getenv("DB_NAME")]

def get_file_dir(filename):
    import os
    return os.path.dirname(os.path.abspath(os.path.basename(filename)))

def connect_to_database():
    import pymongo
    from pymongo import MongoClient
    # Load user_data from MongoDB.
    cluster = MongoClient("mongodb+srv://<user?:<password>@<cluster>?retryWrites=true&w=majority")
    return cluster["<db-name>"]
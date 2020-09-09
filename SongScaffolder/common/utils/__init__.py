import os

def get_file_dir(filename):
    return os.path.dirname(os.path.abspath(os.path.basename(filename)))

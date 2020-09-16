
def get_file_dir(filename):
    import os
    return os.path.dirname(os.path.abspath(os.path.basename(filename)))

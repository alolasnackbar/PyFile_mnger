import os

def get_file_size(file_path):
    return os.path.getsize(file_path)

def get_file_extension(file_path):
    return os.path.splitext(file_path)[1]

def is_valid_path(path):
    return os.path.exists(path)
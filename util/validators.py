def validate_file_name(name):
    # Check if file name is valid
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
    return not any(char in name for char in invalid_chars)

def validate_folder_path(path):
    import os
    return os.path.isdir(path)
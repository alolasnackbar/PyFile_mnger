import os

class Editor:
    def rename_file(self, old_path, new_path):
        os.rename(old_path, new_path)

    def edit_metadata(self, file_path, metadata):
        # Logic to edit file metadata
        pass
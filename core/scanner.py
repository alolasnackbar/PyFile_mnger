import os

class Scanner:
    def scan(self, folder_path):
        file_data = []

        for root, dirs, files in os.walk(folder_path):
            relative_path = os.path.relpath(root, folder_path)
            file_data.append(f"\n📁 Folder: {relative_path}")

            for file in files:
                name, ext = os.path.splitext(file)
                ext = ext if ext else "No extension"
                file_data.append(f"  - {file} ({ext})")

        return file_data
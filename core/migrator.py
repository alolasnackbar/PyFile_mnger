import shutil
import os

class Migrator:
    def move_file(self, src, dst):
        shutil.move(src, dst)

    def copy_file(self, src, dst):
        shutil.copy2(src, dst)

    def export_to_txt(self, data, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(data))
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from core.editor import Editor

class EditTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.editor = Editor()

        # Widgets for editing
        ttk.Label(self.frame, text="Edit / Rename Files").pack(pady=10)
        self.rename_button = ttk.Button(self.frame, text="Rename File", command=self.rename_file)
        self.rename_button.pack(pady=5)

    def rename_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            new_name = simpledialog.askstring("Rename", "Enter new name:")
            if new_name:
                import os
                dir_path = os.path.dirname(file_path)
                new_path = os.path.join(dir_path, new_name)
                self.editor.rename_file(file_path, new_path)
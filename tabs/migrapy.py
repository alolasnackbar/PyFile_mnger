import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.migrator import Migrator
from core.scanner import Scanner

class MigrateTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.migrator = Migrator()
        self.scanner = Scanner()

        # Widgets for migrating
        ttk.Label(self.frame, text="Migrate / Export").pack(pady=10)
        self.export_button = ttk.Button(self.frame, text="Export to TXT", command=self.export_txt)
        self.export_button.pack(pady=5)

    def export_txt(self):
        folder = filedialog.askdirectory()
        if folder:
            data = self.scanner.scan(folder)
            save_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")]
            )
            if save_path:
                self.migrator.export_to_txt(data, save_path)
                messagebox.showinfo("Success", "Exported successfully!")
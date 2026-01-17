import tkinter as tk
from tkinter import ttk
from tabs.identipy import IdentifyTab
from tabs.editapy import EditTab
from tabs.migrapy import MigrateTab

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager App")
        self.root.geometry("800x600")

        # Create tab manager
        self.tab_control = ttk.Notebook(self.root)

        # Create tabs
        self.identify_tab = IdentifyTab(self.tab_control)
        self.tab_control.add(self.identify_tab.frame, text='Identify')

        self.edit_tab = EditTab(self.tab_control)
        self.tab_control.add(self.edit_tab.frame, text='Edit')

        self.migrate_tab = MigrateTab(self.tab_control)
        self.tab_control.add(self.migrate_tab.frame, text='Migrate')

        self.tab_control.pack(expand=1, fill="both")

    def run(self):
        self.root.mainloop()
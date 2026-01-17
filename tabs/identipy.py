import tkinter as tk
from tkinter import ttk, filedialog
from core.scanner import scan_files, scan_root_folders

class IdentifyTab(tk.Frame):
    # START HERE
    def __init__(self, parent):
        super().__init__(parent)

        self.folder_path = tk.StringVar()
        self.scan_all_files = tk.BooleanVar(value=False)
        self.scan_folders_only = tk.BooleanVar(value=False)
        self.scan_subfolders = tk.BooleanVar(value=True)
        self.depth_level = tk.StringVar(value="2")

        self.page_size = 50
        self.page_index = 0
        self.results_cache = []

        self.file_types = {
            "mp4": tk.BooleanVar(value=True),
            "mkv": tk.BooleanVar(value=True),
            "jpg": tk.BooleanVar(value=True),
            "png": tk.BooleanVar(value=True),
        }

        self.build_ui()

    # ---------------- UI ---------------- #

    def build_ui(self):
        tk.Button(self, text="Select Folder", command=self.select_folder).pack(pady=4)
        tk.Label(self, textvariable=self.folder_path, wraplength=850).pack()

        self.file_type_frame = tk.LabelFrame(self, text="File Types")
        self.file_type_frame.pack(fill="x", padx=5, pady=5)

        tk.Checkbutton(
            self.file_type_frame,
            text="All Files (*.*)",
            variable=self.scan_all_files,
            command=self.toggle_file_types
        ).pack(side="left", padx=5)

        for ext, var in self.file_types.items():
            tk.Checkbutton(
                self.file_type_frame,
                text=ext.upper(),
                variable=var
            ).pack(side="left", padx=5)

        tk.Checkbutton(
            self,
            text="Folders only (root level)",
            variable=self.scan_folders_only
        ).pack(pady=4)

        opts = tk.Frame(self)
        opts.pack(pady=4)

        tk.Checkbutton(opts, text="Scan Subfolders", variable=self.scan_subfolders).pack(side="left")
        ttk.Combobox(opts, values=["0","1","2"], textvariable=self.depth_level,
                     state="readonly", width=3).pack(side="left", padx=5)
        tk.Label(opts, text="Depth").pack(side="left")

        tk.Button(self, text="Scan", command=self.run_scan).pack(pady=5)

        # ---- Tree + Scrollbars ---- #
        tree_frame = tk.Frame(self)
        tree_frame.pack(expand=True, fill="both", padx=5)

        v = ttk.Scrollbar(tree_frame, orient="vertical")
        h = ttk.Scrollbar(tree_frame, orient="horizontal")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Type", "Value"),
            show="headings",
            yscrollcommand=v.set,
            xscrollcommand=h.set
        )

        v.config(command=self.tree.yview)
        h.config(command=self.tree.xview)

        self.tree.heading("Type", text="Type")
        self.tree.heading("Value", text="Path / Name")

        self.tree.column("Type", width=90, anchor="center")
        self.tree.column("Value", width=700)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v.grid(row=0, column=1, sticky="ns")
        h.grid(row=1, column=0, sticky="ew")

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        nav = tk.Frame(self)
        nav.pack(pady=4)
        tk.Button(nav, text="◀ Prev", command=self.prev_page).pack(side="left", padx=5)
        tk.Button(nav, text="Next ▶", command=self.next_page).pack(side="left", padx=5)

        debug = tk.LabelFrame(self, text="Scan Status")
        debug.pack(fill="x", padx=5, pady=5)

        self.debug_text = tk.Text(debug, height=4, state="disabled")
        self.debug_text.pack(fill="x")

    # ---------------- Logic ---------------- #

    def log(self, msg):
        self.debug_text.config(state="normal")
        self.debug_text.insert("end", msg + "\n")
        self.debug_text.see("end")
        self.debug_text.config(state="disabled")
        self.update_idletasks()

    def toggle_file_types(self):
        state = tk.DISABLED if self.scan_all_files.get() else tk.NORMAL
        for w in self.file_type_frame.winfo_children():
            if isinstance(w, tk.Checkbutton) and w.cget("text") != "All Files (*.*)":
                w.configure(state=state)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)

    def run_scan(self):
        self.tree.delete(*self.tree.get_children())
        self.results_cache.clear()
        self.page_index = 0

        if not self.folder_path.get():
            return

        self.log("🔍 Starting scan...")

        if self.scan_folders_only.get():
            folders = scan_root_folders(self.folder_path.get())
            for f in folders:
                self.tree.insert("", "end", values=("FOLDER", f))
            self.log(f"✅ {len(folders)} folders found.")
            return

        extensions = [] if self.scan_all_files.get() else [
            e for e,v in self.file_types.items() if v.get()
        ]

        depth = int(self.depth_level.get()) if self.scan_subfolders.get() else 0

        self.results_cache = scan_files(
            self.folder_path.get(),
            extensions,
            depth,
            self.log
        )

        self.log(f"✅ Scan complete: {len(self.results_cache)} items found.")
        self.display_page()

    def display_page(self):
        self.tree.delete(*self.tree.get_children())
        start = self.page_index * self.page_size
        end = start + self.page_size

        for item in self.results_cache[start:end]:
            self.tree.insert("", "end", values=(item["ext"].upper(), item["path"]))

    def next_page(self):
        if (self.page_index + 1) * self.page_size < len(self.results_cache):
            self.page_index += 1
            self.display_page()

    def prev_page(self):
        if self.page_index > 0:
            self.page_index -= 1
            self.display_page()

    # ==== CUT OFF SECTIOn ==
    
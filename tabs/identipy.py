import tkinter as tk
import os
from tkinter import ttk, filedialog, messagebox
from core.scanner import scan_files, scan_root_folders, tag_duplicates
from util.file_utils import export_scan_results

class IdentifyTab(tk.Frame):
    # START HERE
    def __init__(self, parent):
        super().__init__(parent)

        self.folder_path = tk.StringVar()
        self.scan_all_files = tk.BooleanVar(value=False)
        self.scan_folders_only = tk.BooleanVar(value=False)
        self.scan_subfolders = tk.BooleanVar(value=True)
        self.depth_level = tk.StringVar(value="2")
        self.filename_filter = tk.StringVar()
        self.show_duplicates_only = tk.BooleanVar(value=False)
        self.show_unique_only = tk.BooleanVar(value=False)

        self.page_size = 50
        self.page_index = 0
        self.results_cache = []
        self.current_filter_results = []
        self.scan_metadata = {}  # Store scan parameters

        self.file_types = {
            "mp4": tk.BooleanVar(value=True),
            "mkv": tk.BooleanVar(value=True),
            "jpg": tk.BooleanVar(value=True),
            "png": tk.BooleanVar(value=True),
        }

        self.build_ui()

    # ---------------- UI ---------------- #

    def build_ui(self):
        tk.Button(self, text="Select Folder", command=self.select_folder, bg="blue", fg="white").pack(pady=4)
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

        # Filter options frame
        filter_frame = tk.LabelFrame(self, text="Filters")
        filter_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(filter_frame, text="Specific filename:").pack(side="left", padx=5)
        tk.Entry(filter_frame, textvariable=self.filename_filter, width=30).pack(side="left", padx=5)

        tk.Checkbutton(
            filter_frame,
            text="Duplicates Only",
            variable=self.show_duplicates_only
        ).pack(side="left", padx=5)

        tk.Checkbutton(
            filter_frame,
            text="Unique Only",
            variable=self.show_unique_only
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

        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Scan", command=self.run_scan).pack(side="left", padx=5)
        tk.Button(button_frame, text="Export Results", command=self.export_results).pack(side="left", padx=5)

        # ---- Tree + Scrollbars ---- #
        tree_frame = tk.Frame(self)
        tree_frame.pack(expand=True, fill="both", padx=5)

        v = ttk.Scrollbar(tree_frame, orient="vertical")
        h = ttk.Scrollbar(tree_frame, orient="horizontal")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Type", "Duplicate", "Value"),
            show="headings",
            yscrollcommand=v.set,
            xscrollcommand=h.set
        )

        v.config(command=self.tree.yview)
        h.config(command=self.tree.xview)

        self.tree.heading("Type", text="Type")
        self.tree.heading("Duplicate", text="Status")
        self.tree.heading("Value", text="Path / Name")

        self.tree.column("Type", width=80, anchor="center")
        self.tree.column("Duplicate", width=100, anchor="center")
        self.tree.column("Value", width=600)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v.grid(row=0, column=1, sticky="ns")
        h.grid(row=1, column=0, sticky="ew")

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        nav = tk.Frame(self)
        nav.pack(pady=4)
        tk.Button(nav, text="◀ Prev", command=self.prev_page).pack(side="left", padx=5)
        tk.Button(nav, text="Next ▶", command=self.next_page).pack(side="left", padx=5)
        tk.Label(nav, text="Page info:").pack(side="left", padx=5)
        self.page_info = tk.Label(nav, text="0/0")
        self.page_info.pack(side="left", padx=5)

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
            self.log("❌ Please select a folder first.")
            return

        self.log("🔍 Starting scan...")

        # Initialize metadata
        self.scan_metadata = {
            "folder_path": self.folder_path.get(),
            "scan_type": None,
            "scanned_items": [],
            "file_extensions": [],
            "filename_filter": None,
            "depth": 0
        }

        if self.scan_folders_only.get():
            folders = scan_root_folders(self.folder_path.get())
            self.scan_metadata["scan_type"] = "FOLDERS_ONLY"
            self.scan_metadata["scanned_items"] = folders
            
            # Store folders in results_cache for export capability
            for folder in folders:
                self.results_cache.append({
                    "name": folder,
                    "ext": "FOLDER",
                    "path": os.path.join(self.folder_path.get(), folder),
                    "is_duplicate": False,
                    "duplicate_count": 0
                })
            
            # Display in tree
            for f in folders:
                self.tree.insert("", "end", values=("FOLDER", "-", f))
            self.log(f"✅ {len(folders)} folders found.")
            return

        extensions = [] if self.scan_all_files.get() else [
            e for e,v in self.file_types.items() if v.get()
        ]

        depth = int(self.depth_level.get()) if self.scan_subfolders.get() else 0
        filename_filter = self.filename_filter.get().strip() if self.filename_filter.get() else None

        # Set metadata
        self.scan_metadata["scan_type"] = "FILES"
        self.scan_metadata["file_extensions"] = extensions if extensions else ["ALL"]
        self.scan_metadata["filename_filter"] = filename_filter
        self.scan_metadata["depth"] = depth

        self.results_cache = scan_files(
            self.folder_path.get(),
            extensions,
            depth,
            self.log,
            filename_filter
        )

        # Store scanned filenames
        self.scan_metadata["scanned_items"] = [r["name"] for r in self.results_cache]

        # Tag duplicates
        self.results_cache = tag_duplicates(self.results_cache)

        # Apply additional filters
        self.apply_filters()

        self.log(f"✅ Scan complete: {len(self.results_cache)} items found.")
        self.display_page()

    def apply_filters(self):
        """Apply duplicate/unique filters to results"""
        self.current_filter_results = self.results_cache.copy()

        if self.show_duplicates_only.get():
            self.current_filter_results = [
                r for r in self.current_filter_results if r.get("is_duplicate", False)
            ]
        elif self.show_unique_only.get():
            self.current_filter_results = [
                r for r in self.current_filter_results if not r.get("is_duplicate", False)
            ]

    def display_page(self):
        self.tree.delete(*self.tree.get_children())
        self.apply_filters()
        
        start = self.page_index * self.page_size
        end = start + self.page_size

        total_pages = (len(self.current_filter_results) + self.page_size - 1) // self.page_size
        current_page = self.page_index + 1 if self.current_filter_results else 0
        
        if hasattr(self, 'page_info'):
            self.page_info.config(text=f"{current_page}/{total_pages}")

        for item in self.current_filter_results[start:end]:
            status = "[DUPLICATE]" if item.get("is_duplicate", False) else "UNIQUE"
            self.tree.insert("", "end", values=(item["ext"].upper(), status, item["path"]))

    def next_page(self):
        self.apply_filters()
        total_pages = (len(self.current_filter_results) + self.page_size - 1) // self.page_size
        if self.page_index + 1 < total_pages:
            self.page_index += 1
            self.display_page()

    def prev_page(self):
        if self.page_index > 0:
            self.page_index -= 1
            self.display_page()

    def export_results(self):
        if not self.folder_path.get():
            messagebox.showwarning("Export", "Please scan a folder first.")
            return

        if not self.results_cache:
            messagebox.showwarning("Export", "No results to export. Run a scan first.")
            return

        try:
            filepath = export_scan_results(
                self.folder_path.get(), 
                self.results_cache,
                self.scan_metadata
            )
            messagebox.showinfo("Export Success", f"Results exported to:\n{filepath}")
            self.log(f"📁 Results exported to: {filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
            self.log(f"❌ Export failed: {str(e)}")

    # ==== CUT OFF SECTIOn ==
    
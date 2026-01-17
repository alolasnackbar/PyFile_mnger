import os
import tkinter as tk
from tkinter import filedialog, messagebox

def scan_folder(folder_path):
    file_data = []

    for root, dirs, files in os.walk(folder_path):
        relative_path = os.path.relpath(root, folder_path)
        file_data.append(f"\n📁 Folder: {relative_path}")

        for file in files:
            name, ext = os.path.splitext(file)
            ext = ext if ext else "No extension"
            file_data.append(f"  - {file} ({ext})")

    return file_data

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)

def export_txt():
    if not folder_path.get():
        messagebox.showerror("Error", "Please select a folder first.")
        return

    file_list = scan_folder(folder_path.get())

    save_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")]
    )

    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write("\n".join(file_list))

        messagebox.showinfo("Success", "File list exported successfully!")

# --- GUI SETUP ---
root = tk.Tk()
root.title("Simple File Lister")
root.geometry("500x200")

folder_path = tk.StringVar()

tk.Label(root, text="Selected Folder:").pack(pady=5)
tk.Entry(root, textvariable=folder_path, width=60).pack()

tk.Button(root, text="Select Folder", command=select_folder).pack(pady=5)
tk.Button(root, text="Export to TXT", command=export_txt).pack(pady=10)

root.mainloop()

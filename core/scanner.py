import os

def scan_files(base_path, extensions, max_depth, debug_cb=None):
    results = []
    base_depth = base_path.rstrip(os.sep).count(os.sep)

    for root, dirs, files in os.walk(base_path):
        depth = root.count(os.sep) - base_depth
        if depth > max_depth:
            dirs[:] = []
            continue

        for file in files:
            ext = os.path.splitext(file)[1].lower().replace(".", "")
            if not extensions or ext in extensions:
                results.append({
                    "name": file,
                    "ext": ext if ext else "N/A",
                    "path": os.path.join(root, file)
                })

                if debug_cb and len(results) % 10 == 0:
                    debug_cb(f"Found {len(results)} items...")

    return results


def scan_root_folders(base_path):
    folders = []
    for item in os.listdir(base_path):
        full = os.path.join(base_path, item)
        if os.path.isdir(full):
            folders.append(item)
    return folders

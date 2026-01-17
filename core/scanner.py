import os
from collections import defaultdict

def scan_files(base_path, extensions, max_depth, debug_cb=None, filename_filter=None):
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
                # Apply filename filter if provided
                if filename_filter and filename_filter.lower() not in file.lower():
                    continue
                
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


def detect_duplicates(results):
    """
    Detect duplicate filenames in results.
    Returns dict with filename as key and list of full paths as value.
    """
    duplicates = defaultdict(list)
    for item in results:
        duplicates[item["name"]].append(item["path"])
    
    # Filter to only keep actual duplicates
    return {k: v for k, v in duplicates.items() if len(v) > 1}


def tag_duplicates(results):
    """
    Tag results with duplicate information.
    Adds 'is_duplicate' and 'duplicate_count' fields to each result.
    """
    duplicates = detect_duplicates(results)
    
    for item in results:
        if item["name"] in duplicates:
            item["is_duplicate"] = True
            item["duplicate_count"] = len(duplicates[item["name"]])
        else:
            item["is_duplicate"] = False
            item["duplicate_count"] = 0
    
    return results

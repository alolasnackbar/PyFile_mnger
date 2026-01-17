import os
from datetime import datetime

def get_file_size(file_path):
    return os.path.getsize(file_path)

def get_file_extension(file_path):
    return os.path.splitext(file_path)[1]

def is_valid_path(path):
    return os.path.exists(path)


def get_drive_name(path):
    r"""
    Extract drive name from path.
    Handles:
    - Windows local drives: C:, D:, etc.
    - UNC network paths: //server/share or \\server\share
    - IP-based network paths: //198.245.233.3/media
    """
    if os.name == 'nt':  # Windows
        # Check for network path (UNC path)
        if path.startswith('//') or path.startswith('\\\\'):
            # Network path: //server/share or \\server\share
            # Extract server/IP name
            parts = path.replace('\\', '/').split('/')
            # Filter out empty parts
            parts = [p for p in parts if p]
            if parts:
                # Get the server/IP and share name
                server = parts[0]
                share = parts[1] if len(parts) > 1 else "SHARE"
                # Sanitize server name (remove dots and colons for IP addresses)
                server_safe = server.replace('.', '_').replace(':', '_')
                return f"{server_safe}_{share}"
            return "NETWORK"
        else:
            # Local drive letter
            drive = os.path.splitdrive(path)[0].replace(":", "")
            return drive if drive else "DRIVE"
    else:  # Unix/Linux
        if path.startswith('//'):
            # Network path on Unix
            parts = path.split('/')
            parts = [p for p in parts if p]
            if parts:
                server = parts[0].replace('.', '_').replace(':', '_')
                share = parts[1] if len(parts) > 1 else "SHARE"
                return f"{server}_{share}"
            return "NETWORK"
        return "ROOT"


def get_folder_name(path):
    """Get the last folder name from path"""
    return os.path.basename(path.rstrip(os.sep))


def sanitize_filename(filename):
    """Remove invalid filename characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def generate_export_filename(folder_path, scan_count):
    """
    Generate export filename with format:
    drive_foldername_datescan_count.txt
    """
    drive = get_drive_name(folder_path)
    folder = get_folder_name(folder_path)
    folder = sanitize_filename(folder)  # Remove invalid characters
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename = f"{drive}_{folder}_{date_str}_{scan_count}.txt"
    return filename


def export_scan_results(folder_path, results, scan_metadata=None, export_dir="exports"):
    """
    Export scan results to a text file.
    Includes duplicate tagging, scan parameters, and scanned items list.
    
    Args:
        folder_path: Base folder path that was scanned
        results: List of result items from scan
        scan_metadata: Dict with scan type, extensions, filter, etc.
        export_dir: Directory to save export file
    """
    # Make export_dir absolute path from script location
    if not os.path.isabs(export_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        export_dir = os.path.join(project_root, export_dir)
    
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    filename = generate_export_filename(folder_path, len(results))
    filepath = os.path.join(export_dir, filename)
    
    # Default metadata if not provided
    if not scan_metadata:
        scan_metadata = {
            "scan_type": "FILES",
            "scanned_items": [r["name"] for r in results],
            "file_extensions": [],
            "filename_filter": None,
            "depth": 0
        }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Scan Results for: {folder_path}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Scan Type: {scan_metadata.get('scan_type', 'UNKNOWN')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Scan parameters section
            f.write("SCAN PARAMETERS:\n")
            f.write("-" * 80 + "\n")
            if scan_metadata.get("file_extensions"):
                f.write(f"Extensions: {', '.join(scan_metadata['file_extensions'])}\n")
            if scan_metadata.get("filename_filter"):
                f.write(f"Filename Filter: {scan_metadata['filename_filter']}\n")
            f.write(f"Scan Depth: {scan_metadata.get('depth', 'N/A')}\n")
            f.write("\n")
            
            # Scanned items section
            f.write(f"SCANNED ITEMS ({len(scan_metadata.get('scanned_items', []))} total):\n")
            f.write("-" * 80 + "\n")
            if scan_metadata.get("scan_type") == "FOLDERS_ONLY":
                for item in sorted(scan_metadata.get('scanned_items', [])):
                    f.write(f"  [FOLDER] {item}\n")
            else:
                for item in sorted(set(scan_metadata.get('scanned_items', []))):
                    f.write(f"  [FILE] {item}\n")
            f.write("\n")
            
            f.write(f"Total items: {len(results)}\n")
            f.write("=" * 80 + "\n\n")
            
            # For FOLDERS_ONLY scan, list folders directly
            if scan_metadata.get("scan_type") == "FOLDERS_ONLY":
                f.write(f"FOLDER LIST:\n")
                f.write("-" * 80 + "\n")
                for item in sorted(results, key=lambda x: x["name"]):
                    f.write(f"  [FOLDER] {item['name']}\n")
                    f.write(f"  Path: {item['path']}\n\n")
            else:
                # Duplicates and unique sections for files
                duplicates = [r for r in results if r.get("is_duplicate", False)]
                unique = [r for r in results if not r.get("is_duplicate", False)]
                
                if duplicates:
                    f.write(f"DUPLICATES FOUND: {len(set(r['name'] for r in duplicates))}\n")
                    f.write("-" * 80 + "\n")
                    for item in sorted(duplicates, key=lambda x: x["name"]):
                        dup_tag = f"[DUPLICATE - {item.get('duplicate_count', 0)} total]"
                        f.write(f"{dup_tag}\n")
                        f.write(f"  Name: {item['name']}\n")
                        f.write(f"  Path: {item['path']}\n")
                        f.write(f"  Type: {item['ext']}\n\n")
                
                f.write(f"UNIQUE FILES: {len(unique)}\n")
                f.write("-" * 80 + "\n")
                for item in sorted(unique, key=lambda x: x["name"]):
                    f.write(f"  Name: {item['name']}\n")
                    f.write(f"  Path: {item['path']}\n")
                    f.write(f"  Type: {item['ext']}\n\n")
    except OSError as e:
        raise OSError(f"Failed to write export file to {filepath}: {e}")
    
    return filepath
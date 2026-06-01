import os
import re
import csv
import hashlib
import sys
from db_manager import init_db, get_import_log, save_import_log, clear_import_data, insert_keyword_rows

ASO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ASO_ROOT not in sys.path:
    sys.path.insert(0, ASO_ROOT)
from shared.locale_parser import extract_locale_from_filename

def get_file_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def normalize_locale(filename):
    return extract_locale_from_filename(filename, default="UNKNOWN")

def parse_int(val, default=0):
    if not val:
        return default
    try:
        # Strip any formatting like commas or spaces
        clean_val = str(val).replace(",", "").replace(" ", "").strip()
        # Handle float strings, e.g. "12.0"
        if "." in clean_val:
            return int(float(clean_val))
        return int(clean_val)
    except ValueError:
        return default

def parse_rank(val):
    if not val:
        return 0
    clean_val = str(val).strip()
    if clean_val.lower() == "unranked":
        return 0
    return parse_int(clean_val, 0)

def scan_and_import():
    # ASO-DEMO is the parent directory of Keyword_Tracker
    tracker_dir = os.path.dirname(os.path.abspath(__file__))
    aso_demo_dir = os.path.dirname(tracker_dir)
    
    # Initialize DB first
    init_db()
    
    # Step 1: Detect apps
    # Any directory inside aso_demo_dir that contains an "Input" folder is an app
    apps = []
    for item in os.listdir(aso_demo_dir):
        item_path = os.path.join(aso_demo_dir, item)
        if os.path.isdir(item_path) and not item.startswith(".") and item != "Keyword_Tracker" and item != "Docs_and_Templates" and item != "Master_Keywords":
            input_dir = os.path.join(item_path, "Input")
            if os.path.isdir(input_dir):
                apps.append((item, input_dir))
                
    total_files_imported = 0
    total_rows_imported = 0
    
    for app_name, input_dir in apps:
        # Step 2: In Input, look for MMYYYY folders
        for month_folder in os.listdir(input_dir):
            month_path = os.path.join(input_dir, month_folder)
            # Match 6 digits folder name (MMYYYY)
            if os.path.isdir(month_path) and re.match(r'^\d{6}$', month_folder):
                month = month_folder
                
                # Step 3: Scan CSV files in month folder
                for file_name in os.listdir(month_path):
                    if file_name.endswith(".csv"):
                        csv_path = os.path.join(month_path, file_name)
                        locale = normalize_locale(file_name)
                        
                        # Calculate file hash
                        file_hash = get_file_md5(csv_path)
                        
                        # Check database import log
                        relative_path = os.path.relpath(csv_path, aso_demo_dir)
                        existing_log = get_import_log(relative_path)
                        
                        if existing_log and existing_log["file_hash"] == file_hash:
                            # Skip if hash is unchanged
                            continue
                            
                        # Import file
                        print(f"Importing {relative_path} (App: {app_name}, Locale: {locale}, Month: {month})...")
                        rows_to_insert = []
                        
                        try:
                            with open(csv_path, mode='r', encoding='utf-8-sig') as f:
                                reader = csv.DictReader(f)
                                # Normalize column names (strip spaces, resolve dots)
                                # The keys in DictReader are headers.
                                # Example keys: 'App Id', 'App Name', 'Keyword', 'Brand', 'Volume', 'Max. Volume', 'Difficulty', 'KEI', 'Rank', 'Rank Status', 'Growth (Yesterday)'
                                fieldnames = reader.fieldnames
                                if not fieldnames:
                                    continue
                                    
                                normalized_fields = {}
                                for f_name in fieldnames:
                                    clean_name = f_name.strip()
                                    normalized_fields[clean_name] = f_name
                                
                                for row in reader:
                                    # Safe getter helpers using normalized field list
                                    def get_val(key, default=""):
                                        orig_key = normalized_fields.get(key)
                                        return row.get(orig_key, default) if orig_key else default
                                    
                                    kw = get_val("Keyword")
                                    if not kw:
                                        continue
                                        
                                    brand_val = get_val("Brand", "false").lower()
                                    brand = 1 if brand_val in ("true", "1", "yes") else 0
                                    
                                    volume = parse_int(get_val("Volume"))
                                    max_vol = parse_int(get_val("Max. Volume") or get_val("Max Volume"))
                                    difficulty = parse_int(get_val("Difficulty"))
                                    kei = parse_int(get_val("KEI"))
                                    rank = parse_rank(get_val("Rank"))
                                    rank_status = get_val("Rank Status", "unranked").strip().lower()
                                    growth = parse_int(get_val("Growth (Yesterday)") or get_val("Growth"))
                                    
                                    rows_to_insert.append({
                                        "app_name": app_name,
                                        "locale": locale,
                                        "month": month,
                                        "keyword": kw.strip(),
                                        "brand": brand,
                                        "volume": volume,
                                        "max_volume": max_vol,
                                        "difficulty": difficulty,
                                        "kei": kei,
                                        "rank": rank,
                                        "rank_status": rank_status,
                                        "growth": growth
                                    })
                                    
                            # Clear old database records for this app/locale/month
                            clear_import_data(app_name, locale, month)
                            
                            # Batch insert rows in chunks of 1000
                            chunk_size = 1000
                            for i in range(0, len(rows_to_insert), chunk_size):
                                insert_keyword_rows(rows_to_insert[i:i+chunk_size])
                                
                            # Save log entry
                            save_import_log(relative_path, file_hash, app_name, locale, month, len(rows_to_insert))
                            total_files_imported += 1
                            total_rows_imported += len(rows_to_insert)
                            
                        except Exception as e:
                            print(f"Error importing {csv_path}: {e}")
                            
    return total_files_imported, total_rows_imported

if __name__ == "__main__":
    imported_files, imported_rows = scan_and_import()
    print(f"Scan complete. Imported {imported_files} files, {imported_rows} rows.")

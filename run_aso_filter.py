import os
import sys
import re
import shutil
import subprocess
import argparse
from datetime import datetime

def detect_month(csv_path):
    # Tìm kiếm chuỗi định dạng MMYYYY (6 chữ số) trong đường dẫn file CSV
    # Ví dụ: AR_Filter/Input/052026/ARFilter_US_EN.csv -> "052026"
    normalized_path = csv_path.replace("\\", "/")
    parts = normalized_path.split("/")
    for part in parts:
        if re.match(r'^\d{6}$', part):
            return part
    # Nếu không tìm thấy, trả về tháng hiện tại
    return datetime.now().strftime("%m%Y")

def main():
    parser = argparse.ArgumentParser(description="ASO Master Orchestrator")
    parser.add_argument("--csv", type=str, required=True, help="Path to CSV file (Format: AppName_Country_Language.csv)")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive web UI mode")
    args = parser.parse_args()

    csv_path = os.path.abspath(args.csv)
    if not os.path.exists(csv_path):
        print(f"Error: File '{csv_path}' does not exist.")
        sys.exit(1)

    filename = os.path.basename(csv_path)
    # Match AppName_Country_Language.csv (e.g. GameEmulator_US_EN.csv, Pranky_PH_fil.csv, Pranky_BR_PT-BR.csv)
    match = re.match(r'^([A-Za-z0-9]+)_([A-Za-z]{2}_[A-Za-z0-9-]+)\.csv$', filename)
    if not match:
        # Fallback if filename is just Country_Language.csv (e.g. US_EN.csv)
        match_fallback = re.match(r'^([A-Za-z]{2}_[A-Za-z0-9-]+)\.csv$', filename)
        if match_fallback:
            app_name = "ControlWidget" # Default fallback
            try:
                with open(csv_path, "r", encoding="utf-8-sig") as f:
                    first_lines = [f.readline() for _ in range(3)]
                for line in first_lines:
                    if "fyp.meme" in line or "ar.effect" in line:
                        app_name = "ARFilter"
                        break
                    elif "gb4.retro" in line or "emulator" in line:
                        app_name = "GameEmulator"
                        break
            except Exception as e:
                print(f"Warning reading CSV header: {e}")
            market = match_fallback.group(1).upper()
        else:
            print(f"Error: Filename '{filename}' does not follow the required structure: AppName_Country_Language.csv or Country_Language.csv")
            sys.exit(1)
    else:
        app_name = match.group(1)
        market = match.group(2).upper()

    print(f"Detected App Name: {app_name}")
    print(f"Detected Market: {market}")

    # Map AppName to the appropriate script and folder name
    app_lower = app_name.lower()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if "arfilter" in app_lower or "ar_filter" in app_lower or "filter" in app_lower:
        app_folder = "AR_Filter"
        target_script = os.path.join(script_dir, "AR_Filter", "run_ar_filter_v3_5.py")
    elif "gameemulator" in app_lower or "gameretro" in app_lower or "emulator" in app_lower:
        app_folder = "Game_Emulator"
        target_script = os.path.join(script_dir, "Game_Emulator", "run_game_emulator_v3_5.py")
    elif "prank" in app_lower or "pranky" in app_lower:
        app_folder = "Prank_Sounds"
        target_script = os.path.join(script_dir, "Prank_Sounds", "run_pipeline.py")
    else:
        app_folder = "Control_Widget"
        target_script = os.path.join(script_dir, "Control_Widget", "run_control_widget_v3_5.py")

    if not os.path.exists(target_script):
        print(f"Error: Target script '{target_script}' does not exist.")
        sys.exit(1)

    print(f"App Target Folder: {app_folder}")
    print(f"Routing execution to: {target_script}")

    # Xác định tháng hoạt động
    month = detect_month(csv_path)
    print(f"Operating Month: {month}")

    # Tự động gom file CSV đầu vào vào đúng thư mục: [app_folder]/Input/[month]/
    target_input_dir = os.path.join(script_dir, app_folder, "Input", month)
    target_input_path = os.path.join(target_input_dir, filename)

    abs_target_path = os.path.abspath(target_input_path)

    if csv_path != abs_target_path:
        print(f"File is not in the correct Input archive path: {target_input_path}")
        print("Archiving input CSV to standard structure...")
        os.makedirs(target_input_dir, exist_ok=True)
        shutil.copy2(csv_path, target_input_path)
        print(f"Successfully copied input CSV to: {target_input_path}")
        csv_path = target_input_path

    # Xác định đường dẫn ghi file Excel kết quả đầu ra: [app_folder]/Output/[month]/
    target_output_dir = os.path.join(script_dir, app_folder, "Output", month)
    os.makedirs(target_output_dir, exist_ok=True)

    market_hyphen = market.replace("_", "-")
    output_filename = f"{app_name}_{market_hyphen}_Output.xlsx"
    target_output_path = os.path.join(target_output_dir, output_filename)
    print(f"Target Output Path: {target_output_path}")

    # Xây dựng lệnh thực thi
    cmd = [sys.executable, target_script, "--csv", csv_path, "--market", market, "--output", target_output_path]
    if args.interactive:
        cmd.append("--interactive")
        
    print(f"Executing command: {' '.join(cmd)}")
    
    # Run from target script directory
    result = subprocess.run(cmd, cwd=os.path.dirname(target_script), capture_output=True, text=True, encoding="utf-8", errors="ignore")
    
    # Print stdout and stderr
    if result.stdout:
        print("\n--- Script Output ---")
        print(result.stdout)
    if result.stderr:
        print("\n--- Script Error Output ---")
        print(result.stderr, file=sys.stderr)

    if result.returncode == 0:
        print("\n[SUCCESS] ASO Keyword Filter Pipeline executed successfully.")
        print(f"Result file: {os.path.abspath(target_output_path)}")
    else:
        print(f"\n[FAILURE] Pipeline execution failed with exit code {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()

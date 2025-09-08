import json
import sys
import os
from datetime import datetime

def validate_json_file(filepath):
    """
    Validates a JSON file by streaming it line-by-line to avoid memory overload.
    Returns True if valid, False otherwise with error details.
    """
    print(f"[{datetime.now()}] Starting validation of: {filepath}")
    print(f"File size: {os.path.getsize(filepath) / (1024*1024):.2f} MB")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                
                
                
                data = json.load(f)
                print(f"[{datetime.now()}] ✅ JSON is VALID.")
                return True
            except json.JSONDecodeError as e:
                print(f"[{datetime.now()}] ❌ INVALID JSON")
                print(f"Error: {e.msg}")
                print(f"Line: {e.lineno}, Column: {e.colno}")
                
                f.seek(0)
                lines = f.readlines()
                start_line = max(0, e.lineno - 3)
                end_line = min(len(lines), e.lineno + 2)
                print("\n--- Snippet around error ---")
                for i in range(start_line, end_line):
                    marker = ">> " if i + 1 == e.lineno else "   "
                    print(f"{marker}{i+1:4}: {lines[i].rstrip()}")
                print("--- End snippet ---")
                return False
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return False
    except UnicodeDecodeError as e:
        print(f"❌ Encoding error: {e}")
        print("Try opening with different encoding (e.g., 'utf-8-sig', 'latin-1')")
        return False
    except MemoryError:
        print("❌ Out of memory! File too large to load at once.")
        print("Consider using 'ijson' for true streaming validation (install via pip install ijson)")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return False


def quick_preview(filepath, n_chars=500):
    """Quickly preview start of file to check structure."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            snippet = f.read(n_chars)
            print(f"\n--- First {n_chars} characters ---")
            print(snippet)
            print("-" * 40)
    except Exception as e:
        print(f"⚠️ Could not preview file: {e}")


if __name__ == "__main__":
    
    json_file_path = r"C:\fyntune\agent_onboarding_backend\database\seeders\jsons\ifsc3.json"

    
    quick_preview(json_file_path)

    
    is_valid = validate_json_file(json_file_path)

    if is_valid:
        print("\n🎉 JSON file is valid!")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    print(f"📋 Contains {len(data)} items.")
                elif isinstance(data, dict):
                    print(f"📋 Contains {len(data)} keys.")
        except:
            pass
    else:
        print("\n❌ Fix the JSON errors above.")
        sys.exit(1)
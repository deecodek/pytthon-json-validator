import sys
import re

def find_unclosed_string(filepath):
    print(f"🔍 Scanning {filepath} for unclosed strings...")

    in_string = False
    string_start_line = 0
    string_start_col = 0
    escape_next = False

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                for col_num, char in enumerate(line, 1):
                    if escape_next:
                        escape_next = False
                        continue

                    if char == '\\':
                        escape_next = True
                        continue

                    if char == '"' and not in_string:
                        in_string = True
                        string_start_line = line_num
                        string_start_col = col_num
                    elif char == '"' and in_string:
                        in_string = False

                
                if in_string and not (line.rstrip().endswith('\\')):
                    
                    
                    pass

            
            if in_string:
                print(f"\n❌ FOUND UNCLOSDED STRING!")
                print(f"   String started at Line {string_start_line}, Column {string_start_col}")
                print(f"   Still open at EOF (Line {line_num})")
                print(f"   Preview around start:")

                
                with open(filepath, 'r', encoding='utf-8') as f2:
                    lines = f2.readlines()
                    start = max(0, string_start_line - 3)
                    end = min(len(lines), string_start_line + 3)
                    for i in range(start, end):
                        marker = ">> " if i + 1 == string_start_line else "   "
                        print(f"{marker}{i+1:6}: {lines[i].rstrip()}")

                return string_start_line

        print("✅ No unclosed strings found.")
        return None

    except Exception as e:
        print(f"❌ Error scanning file: {e}")
        return None


if __name__ == "__main__":
    filepath = r"C:\fyntune\agent_onboarding_backend\database\seeders\jsons\ifsc3.json"
    find_unclosed_string(filepath)
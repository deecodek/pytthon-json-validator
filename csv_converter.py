import csv
import json
import os
import sys
from pathlib import Path

class UniversalCSVToJSONConverter:
    def __init__(self):
        self.csv_headers = []
        self.db_schema = {}  # {custom_key: {csv_column: str, data_type: str}}
        self.input_path = ""
        self.output_path = ""
        
    def show_help(self):
        """Display help information"""
        help_text = """
=====================================
    Universal CSV to JSON Converter
=====================================

USAGE:
    python csv_converter.py [OPTIONS]
    python csv_converter.py --help

DESCRIPTION:
    A universal tool to convert any CSV file to JSON format with custom
    key names and data types. The converter follows this workflow:
    
    1. Automatically detects all CSV headers
    2. For each header, you specify a custom key name
    3. For each custom key, you specify the data type
    4. Converts the CSV to JSON with proper data typing

WORKFLOW:
    CSV Headers → Custom Key Names → Data Types → JSON Output

DATA TYPES:
    - string:  Text data (default)
    - integer: Whole numbers (e.g., 123, -456)
    - float:   Decimal numbers (e.g., 123.45, -67.89)
    - boolean: True/False values (true, 1, yes, on = True)

SKIPPING COLUMNS:
    - Leave custom key name blank to skip a CSV column
    - Leave data type blank to skip a custom key

EXAMPLE:
    CSV Headers: name,age,salary,active,department
    Custom Keys: employee_name,employee_age,monthly_salary,is_active,dept_name
    Data Types:  string,integer,float,boolean,string

OPTIONS:
    --help, -h    Show this help message

TIPS:
    - All CSV columns are shown - nothing is hidden
    - You can skip any column by leaving fields blank
    - Press Ctrl+C to cancel at any time
    - Preview data before final conversion
"""
        print(help_text)
        sys.exit(0)
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_user_input(self, prompt, default=None):
        """Get user input with optional default value"""
        if default is not None:
            prompt = f"{prompt} [{default}]: "
        else:
            prompt = f"{prompt}: "
        
        try:
            user_input = input(prompt).strip()
            return user_input if user_input else default
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user.")
            sys.exit(0)
    
    def get_file_paths(self):
        """Get input and output file paths"""
        self.clear_screen()
        print("=== File Configuration ===")
        
        # Input file
        while True:
            self.input_path = self.get_user_input("Enter CSV file path", "data.csv")
            if os.path.exists(self.input_path):
                break
            else:
                print(f"File not found: {self.input_path}")
                retry = self.get_user_input("Try again? (y/n)", "y")
                if retry.lower() != 'y':
                    return False
        
        # Output file
        default_output = str(Path(self.input_path).with_suffix('.json'))
        self.output_path = self.get_user_input("Enter output JSON file path", default_output)
        return True
    
    def read_csv_headers(self):
        """Read CSV headers"""
        with open(self.input_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            self.csv_headers = next(reader)
    
    def create_key_mapping(self):
        """Interactive key mapping - show headers, get custom keys, then data types"""
        self.clear_screen()
        print("=== Key Mapping ===")
        print("Available CSV columns:")
        for i, header in enumerate(self.csv_headers, 1):
            print(f"  {i}. {header}")
        
        print("\nFor each CSV column, enter a custom key name (or leave blank to skip):")
        
        self.db_schema = {}
        
        for header in self.csv_headers:
            while True:
                custom_key = self.get_user_input(f"CSV column '{header}' → Custom key name")
                
                if not custom_key:
                    print(f"Column '{header}' will be skipped")
                    break
                elif custom_key in self.db_schema:
                    print(f"Key '{custom_key}' already used. Please choose a different name.")
                    continue
                else:
                    # Get data type for this key
                    data_type = self.get_data_type(custom_key)
                    if data_type is not None:  # Not skipped
                        self.db_schema[custom_key] = {
                            'csv_column': header,
                            'data_type': data_type
                        }
                        print(f"Mapped: '{header}' → '{custom_key}' ({data_type})")
                    break
    
    def get_data_type(self, key_name):
        """Get data type for a key"""
        while True:
            data_type = self.get_user_input(f"Data type for '{key_name}'", "string")
            
            if not data_type:
                print(f"Key '{key_name}' will be skipped")
                return None
            elif data_type.lower() in ['string', 'integer', 'float', 'boolean']:
                return data_type.lower()
            else:
                print(f"Invalid data type: {data_type}")
                print("Valid types: string, integer, float, boolean")
                retry = self.get_user_input("Try again? (y/n)", "y")
                if retry.lower() != 'y':
                    return None
    
    def convert_value(self, value, data_type):
        """Convert value to specified data type"""
        if not value or value.strip() == '':
            return None
            
        value = value.strip()
        
        try:
            if data_type == 'string':
                return value
            elif data_type == 'integer':
                return int(float(value))  # Handle cases like "123.0"
            elif data_type == 'float':
                return float(value)
            elif data_type == 'boolean':
                return value.lower() in ['true', '1', 'yes', 'on', 't', 'y']
        except (ValueError, TypeError):
            print(f"Warning: Could not convert '{value}' to {data_type}")
            return None
    
    def convert_data(self):
        """Convert CSV data to JSON with proper data types"""
        self.clear_screen()
        print("=== Converting Data ===")
        
        data = []
        with open(self.input_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_num, row in enumerate(reader, 2):
                mapped_row = {}
                
                # Process each mapped key
                for custom_key, mapping_info in self.db_schema.items():
                    csv_column = mapping_info['csv_column']
                    data_type = mapping_info['data_type']
                    
                    raw_value = row.get(csv_column, '')
                    mapped_row[custom_key] = self.convert_value(raw_value, data_type)
                
                data.append(mapped_row)
        
        return data
    
    def preview_data(self, data, sample_size=3):
        """Show preview of converted data"""
        self.clear_screen()
        print("=== Data Preview ===")
        print(f"Total records: {len(data)}")
        print(f"Processed keys: {len(self.db_schema)}")
        print("\nKey mapping:")
        for custom_key, mapping_info in self.db_schema.items():
            csv_column = mapping_info['csv_column']
            data_type = mapping_info['data_type']
            print(f"  {csv_column} → {custom_key} ({data_type})")
        
        print(f"\nShowing first {min(sample_size, len(data))} records:")
        print("-" * 50)
        
        for i, record in enumerate(data[:sample_size]):
            print(f"Record {i + 1}:")
            for key, value in record.items():
                data_type = self.db_schema[key]['data_type']
                print(f"  {key} ({data_type}): {value}")
            print()
        
        if len(data) > sample_size:
            print(f"... and {len(data) - sample_size} more records")
        
        return self.get_user_input("Continue with conversion? (y/n)", "y").lower() == 'y'
    
    def save_json(self, data):
        """Save data to JSON file"""
        with open(self.output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✅ Conversion completed successfully!")
        print(f"📊 Records processed: {len(data)}")
        print(f"💾 JSON file saved to: {self.output_path}")
    
    def show_summary(self):
        """Show conversion summary"""
        self.clear_screen()
        print("=== Conversion Summary ===")
        print(f"Input file: {self.input_path}")
        print(f"Output file: {self.output_path}")
        print(f"Total CSV columns: {len(self.csv_headers)}")
        print(f"Processed keys: {len(self.db_schema)}")
        print("\nKey mapping:")
        for custom_key, mapping_info in self.db_schema.items():
            csv_column = mapping_info['csv_column']
            data_type = mapping_info['data_type']
            print(f"  {csv_column} → {custom_key} ({data_type})")
        
        processed_columns = {info['csv_column'] for info in self.db_schema.values()}
        skipped_columns = set(self.csv_headers) - processed_columns
        if skipped_columns:
            print(f"\nSkipped columns: {len(skipped_columns)}")
            for column in skipped_columns:
                print(f"  {column} (skipped)")
    
    def run(self):
        """Main execution flow"""
        try:
            # Get file paths
            if not self.get_file_paths():
                return
            
            # Read CSV headers
            self.read_csv_headers()
            
            # Create key mapping
            self.create_key_mapping()
            
            # Show summary
            if self.db_schema:  # Only proceed if some columns were mapped
                self.show_summary()
                if self.get_user_input("\nProceed with conversion? (y/n)", "y").lower() != 'y':
                    print("Conversion cancelled.")
                    return
                
                # Convert data
                data = self.convert_data()
                
                # Preview data
                if not self.preview_data(data):
                    print("Conversion cancelled.")
                    return
                
                # Save JSON
                self.save_json(data)
                
                # Ask to open file
                if self.get_user_input("Open the output file? (y/n)", "n").lower() == 'y':
                    try:
                        os.startfile(self.output_path) if os.name == 'nt' else os.system(f'open "{self.output_path}"')
                    except:
                        print("Could not open file automatically.")
            else:
                print("No columns were mapped. Conversion cancelled.")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user.")
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            import traceback
            if self.get_user_input("Show detailed error? (y/n)", "n").lower() == 'y':
                traceback.print_exc()

def main():
    """Main application with command line argument support"""
    
    # Check for help arguments
    if '--help' in sys.argv or '-h' in sys.argv:
        converter = UniversalCSVToJSONConverter()
        converter.show_help()
        return
    
    # Run the converter
    converter = UniversalCSVToJSONConverter()
    
    while True:
        converter.clear_screen()
        print("=====================================")
        print("    Universal CSV to JSON Converter")
        print("=====================================")
        print("1. Start conversion")
        print("2. Show help")
        print("3. Exit")
        print("-------------------------------------")
        
        choice = converter.get_user_input("Select option", "1")
        
        if choice == "1":
            converter.run()
            input("\nPress Enter to continue...")
        elif choice == "2":
            converter.show_help()
        elif choice == "3":
            print("Goodbye! 👋")
            break
        else:
            print("Invalid option. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
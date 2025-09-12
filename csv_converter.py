import csv
import json
import os
from pathlib import Path

class UniversalCSVToJSONConverter:
    def __init__(self):
        self.csv_headers = []
        self.db_schema = {}  
        self.input_path = ""
        self.output_path = ""
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_user_input(self, prompt, default=None):
        """Get user input with optional default value"""
        if default is not None:
            prompt = f"{prompt} [{default}]: "
        else:
            prompt = f"{prompt}: "
        
        user_input = input(prompt).strip()
        return user_input if user_input else default
    
    def get_file_paths(self):
        """Get input and output file paths"""
        self.clear_screen()
        print("=== File Configuration ===")
        
        
        while True:
            self.input_path = self.get_user_input("Enter CSV file path", "data.csv")
            if os.path.exists(self.input_path):
                break
            else:
                print(f"File not found: {self.input_path}")
                retry = self.get_user_input("Try again? (y/n)", "y")
                if retry.lower() != 'y':
                    return False
        
        
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
                    
                    data_type = self.get_data_type(custom_key)
                    if data_type is not None:  
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
                return int(float(value))  
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
            
            if not self.get_file_paths():
                return
            
            
            self.read_csv_headers()
            
            
            self.create_key_mapping()
            
            
            if self.db_schema:  
                self.show_summary()
                if self.get_user_input("\nProceed with conversion? (y/n)", "y").lower() != 'y':
                    print("Conversion cancelled.")
                    return
                
                
                data = self.convert_data()
                
                
                if not self.preview_data(data):
                    print("Conversion cancelled.")
                    return
                
                
                self.save_json(data)
                
                
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
    """Main application"""
    converter = UniversalCSVToJSONConverter()
    
    while True:
        converter.clear_screen()
        print("=====================================")
        print("    Universal CSV to JSON Converter")
        print("=====================================")
        print("1. Start conversion")
        print("2. Exit")
        print("-------------------------------------")
        
        choice = converter.get_user_input("Select option", "1")
        
        if choice == "1":
            converter.run()
            input("\nPress Enter to continue...")
        elif choice == "2":
            print("Goodbye! 👋")
            break
        else:
            print("Invalid option. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
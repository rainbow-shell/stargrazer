#!/usr/bin/env python3
"""
Convert stargazers JSON to CSV for Excel
"""
import json
import csv
import sys
import os
from datetime import datetime

def convert_json_to_csv(json_file, csv_file=None):
    """Convert the stargazers JSON file to CSV format"""
    
    # Generate default CSV filename if not provided
    if csv_file is None:
        base_name = os.path.splitext(json_file)[0]
        csv_file = f"{base_name}.csv"
    
    print(f"Converting {json_file} to {csv_file}...")
    
    try:
        # Read the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print("No data found in JSON file.")
            return False
            
        # Get the fieldnames from the first record
        fieldnames = list(data[0].keys())
        
        # Write to CSV
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write each record
            for record in data:
                # Handle potential encoding issues for Excel
                for key, value in record.items():
                    if isinstance(value, str):
                        # Replace any characters that might cause issues in Excel
                        record[key] = value.replace('\n', ' ').replace('\r', '')
                writer.writerow(record)
        
        print(f"Successfully converted {len(data)} records to CSV.")
        print(f"CSV file saved at: {csv_file}")
        return True
    
    except Exception as e:
        print(f"Error converting JSON to CSV: {e}")
        return False

def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python json_to_csv.py <json_file> [csv_file]")
        return
    
    json_file = sys.argv[1]
    
    # Optional CSV output file
    csv_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Convert JSON to CSV
    convert_json_to_csv(json_file, csv_file)

if __name__ == "__main__":
    main()
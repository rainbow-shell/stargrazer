#!/usr/bin/env python3
"""
Extract LinkedIn URLs from existing stargazers data
"""
import json
import re
import sys
import csv
import os

def extract_linkedin_url(bio, blog, company):
    """
    Extract LinkedIn URL from user bio, blog, or company field
    Returns the first LinkedIn URL found or None
    """
    # Common patterns for LinkedIn URLs
    linkedin_patterns = [
        r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?',
        r'https?://(?:www\.)?linkedin\.com/company/[a-zA-Z0-9_-]+/?',
        r'linkedin\.com/in/[a-zA-Z0-9_-]+/?',
        r'linkedin\.com/company/[a-zA-Z0-9_-]+/?'
    ]
    
    # Check all fields for LinkedIn URLs
    for field in [bio, blog, company]:
        if not field:
            continue
            
        for pattern in linkedin_patterns:
            match = re.search(pattern, field)
            if match:
                url = match.group(0)
                # Ensure it has the https:// prefix
                if not url.startswith('http'):
                    url = 'https://' + url
                return url
                
    return None

def process_json_file(json_file, output_file=None):
    """Process the JSON file to add LinkedIn URLs"""
    
    # Generate default output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(json_file)[0]
        output_file = f"{base_name}_with_linkedin.json"
    
    print(f"Processing {json_file} to extract LinkedIn URLs...")
    
    try:
        # Read the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print("No data found in JSON file.")
            return False
        
        # Count how many LinkedIn URLs we find
        linkedin_count = 0
        
        # Add LinkedIn URL field to each record
        for record in data:
            bio = record.get('bio', '')
            blog = record.get('blog', '')
            company = record.get('company', '')
            
            linkedin_url = extract_linkedin_url(bio, blog, company)
            record['linkedin_url'] = linkedin_url
            
            if linkedin_url:
                linkedin_count += 1
        
        # Write the updated data to the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Found LinkedIn URLs for {linkedin_count} out of {len(data)} users ({(linkedin_count/len(data))*100:.2f}%).")
        print(f"Updated data saved to {output_file}")
        
        # Also create a CSV version
        csv_file = f"{os.path.splitext(output_file)[0]}.csv"
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            if data:
                fieldnames = list(data[0].keys())
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
                
                print(f"CSV file with LinkedIn URLs saved to {csv_file}")
            else:
                print("No data to write to CSV.")
        
        return True
    
    except Exception as e:
        print(f"Error processing JSON file: {e}")
        return False

def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python linkedin_extractor.py <json_file> [output_file]")
        return
    
    json_file = sys.argv[1]
    
    # Optional output file
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Process the JSON file
    process_json_file(json_file, output_file)

if __name__ == "__main__":
    main()
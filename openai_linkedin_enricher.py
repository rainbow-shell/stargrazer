#!/usr/bin/env python3
"""
Enrich stargazers data with LinkedIn URLs using OpenAI API
"""
import json
import csv
import time
import os
import argparse
import re
from datetime import datetime
import requests

# OpenAI API configuration
import os
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")  # Get API key from environment variable
OPENAI_MODEL = "gpt-4.1-2025-04-14"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

def load_prompt_template(file_path="linkedin_prompt.txt"):
    """Load the prompt template from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error loading prompt template: {e}")
        # Fallback to a simple prompt if file can't be loaded
        return "Find the LinkedIn profile URL for {{name}} who works at {{company}}."

def format_prompt(template, name, company):
    """Format the prompt template with name and company"""
    return template.replace("{{name}}", name or "").replace("{{company}}", company or "")

def find_linkedin_url(name, company, prompt_template):
    """
    Use OpenAI API to find LinkedIn URL for a person
    
    Args:
        name: Person's name
        company: Company name
        prompt_template: The prompt template to use
        
    Returns:
        LinkedIn URL or None if not found
    """
    if not name:
        return None
        
    formatted_prompt = format_prompt(prompt_template, name, company or "")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    data = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert researcher who finds LinkedIn Profile URLs."},
            {"role": "user", "content": formatted_prompt}
        ],
        "temperature": 0.2,  # Lower temperature for more focused results
        "max_tokens": 200    # Limit response length
    }
    
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
        
        # Extract LinkedIn URL from the response
        linkedin_url_match = re.search(r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?', content)
        if linkedin_url_match:
            return linkedin_url_match.group(0)
        elif "No LinkedIn profile found" in content:
            return None
        else:
            # If no URL pattern found but response isn't "no profile found", 
            # it might be just the URL without https://
            linkedin_handle_match = re.search(r'linkedin\.com/in/[a-zA-Z0-9_-]+/?', content)
            if linkedin_handle_match:
                return "https://" + linkedin_handle_match.group(0)
            return None
            
    except Exception as e:
        print(f"Error calling OpenAI API for {name}: {e}")
        return None

def enrich_stargazers_with_linkedin(input_file, output_file=None, limit=None, skip_existing=True):
    """
    Enrich stargazers data with LinkedIn URLs
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file (generated if not provided)
        limit: Maximum number of records to process
        skip_existing: Whether to skip records that already have LinkedIn URLs
    """
    # Generate default output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_with_openai_linkedin.json"
    
    print(f"Enriching stargazers data from {input_file} with LinkedIn URLs using OpenAI API...")
    
    # Load the prompt template
    prompt_template = load_prompt_template()
    
    try:
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print("No data found in input file.")
            return False
        
        total_records = len(data)
        print(f"Found {total_records} records in the input file.")
        
        processed_count = 0
        linkedin_found_count = 0
        
        # Process each record
        for i, record in enumerate(data):
            # Check if we've hit the limit
            if limit and processed_count >= limit:
                print(f"Reached processing limit of {limit} records.")
                break
            
            # Skip records that already have LinkedIn URLs
            if skip_existing and (record.get('linkedin_url') or record.get('linkedin_url_guess')):
                print(f"Skipping {record.get('name')} - already has LinkedIn URL: {record.get('linkedin_url') or record.get('linkedin_url_guess')}")
                continue
            
            name = record.get('name')
            company = record.get('company')
            
            if name:  # Only process records with names
                processed_count += 1
                print(f"Processing {name} at {company} ({i+1}/{total_records})...")
                
                # Find LinkedIn URL
                linkedin_url = find_linkedin_url(name, company, prompt_template)
                
                if linkedin_url:
                    record['linkedin_url_openai'] = linkedin_url
                    linkedin_found_count += 1
                    print(f"Found LinkedIn URL: {linkedin_url}")
                else:
                    record['linkedin_url_openai'] = ""
                    print(f"No LinkedIn URL found.")
                
                # Save intermediate results every 10 processed records
                if processed_count % 10 == 0:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    temp_file = f"stargazers_openai_temp_{timestamp}.json"
                    
                    try:
                        with open(temp_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2)
                        print(f"Saved intermediate data to {temp_file}")
                    except Exception as e:
                        print(f"Error saving intermediate data: {e}")
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.5)
        
        # Save the final enriched data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        # Generate CSV output
        csv_file = f"{os.path.splitext(output_file)[0]}.csv"
        if data:
            with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write each record
                for record in data:
                    # Handle potential encoding issues
                    for key, value in record.items():
                        if isinstance(value, str):
                            record[key] = value.replace('\n', ' ').replace('\r', '')
                    writer.writerow(record)
        
        print(f"\nEnrichment complete:")
        print(f"Total records: {total_records}")
        print(f"Records processed: {processed_count}")
        print(f"LinkedIn URLs found: {linkedin_found_count}")
        if processed_count > 0:
            print(f"Success rate: {(linkedin_found_count/processed_count)*100:.2f}%")
        
        print(f"\nEnriched data saved to:")
        print(f"- JSON: {output_file}")
        print(f"- CSV: {csv_file}")
        
        return True
        
    except Exception as e:
        print(f"Error enriching data: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Enrich stargazers data with LinkedIn URLs using OpenAI API')
    parser.add_argument('input_file', help='Input JSON file with stargazers data')
    parser.add_argument('--output', '-o', help='Output JSON file (default: input_file_with_openai_linkedin.json)')
    parser.add_argument('--limit', '-l', type=int, help='Maximum number of records to process')
    parser.add_argument('--include-existing', '-i', action='store_true', 
                        help='Process records that already have LinkedIn URLs')
    
    args = parser.parse_args()
    
    enrich_stargazers_with_linkedin(
        args.input_file,
        args.output,
        args.limit,
        not args.include_existing
    )

if __name__ == "__main__":
    main()
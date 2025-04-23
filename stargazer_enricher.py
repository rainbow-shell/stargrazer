#!/usr/bin/env python3
"""
Stargazer Enricher - A tool to capture and enrich GitHub repository stargazers
<<<<<<< HEAD

This tool fetches stargazers for a GitHub repository and enriches the data with
additional user information from the GitHub API. The enriched data is saved in
both JSON and CSV formats for further analysis.
=======
>>>>>>> 8c5765c7ea4b4bc8ee68dcee8a278102324ac737
"""
import requests
import json
import time
import argparse
import sys
import os
<<<<<<< HEAD
import re
import csv
=======
>>>>>>> 8c5765c7ea4b4bc8ee68dcee8a278102324ac737
from datetime import datetime

def fetch_stargazers(repo_owner, repo_name, token=None, limit=None, skip=0, use_existing=None):
    """
    Fetch stargazers for a given repository with optional limit and skip
    
    Args:
        repo_owner: Owner of the repository
        repo_name: Name of the repository
        token: GitHub personal access token
        limit: Maximum number of stargazers to fetch
        skip: Number of stargazers to skip
        use_existing: Path to existing raw stargazers file to use instead of fetching
        
    Returns:
        List of stargazers
    """
    # If use_existing is provided, load stargazers from file
    if use_existing and os.path.exists(use_existing):
        try:
            print(f"Loading stargazers from existing file: {use_existing}")
            with open(use_existing, 'r', encoding='utf-8') as f:
                all_stargazers = json.load(f)
            
            total = len(all_stargazers)
            print(f"Loaded {total} stargazers from file")
            
            # Apply skip and limit if provided
            start_idx = min(skip, total)
            end_idx = min(skip + limit, total) if limit else total
            
            return all_stargazers[start_idx:end_idx]
        except Exception as e:
            print(f"Error loading stargazers from file: {e}")
            print("Falling back to fetching from GitHub API")
    
    all_stargazers = []
    page = 1
    per_page = 100
    base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/stargazers"
    
    headers = {
        'Accept': 'application/vnd.github.v3.star+json'  # This gives us starring timestamps
    }
    
    if token:
        headers['Authorization'] = f"token {token}"
    
    # Calculate which page to start from based on skip
    if skip > 0:
        page = (skip // per_page) + 1
        skip_remainder = skip % per_page
    else:
        skip_remainder = 0
    
    try:
        stargazers_count = 0  # Total count of stargazers processed (including skipped)
        while True:
            if limit and len(all_stargazers) >= limit:
                print(f"Reached requested limit of {limit} stargazers")
                break
                
            params = {
                'page': page,
                'per_page': per_page
            }
            
            print(f"Fetching page {page} of stargazers...")
            response = requests.get(base_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                stargazers_batch = response.json()
                if not stargazers_batch:
                    break
                
                # Skip remainder stargazers from the first page if needed
                if page == (skip // per_page) + 1 and skip_remainder > 0:
                    stargazers_batch = stargazers_batch[skip_remainder:]
                
                stargazers_count += len(stargazers_batch)
                all_stargazers.extend(stargazers_batch)
                page += 1
                
                limit_info = f" (limit: {limit})" if limit else ""
                skip_info = f" (skipped: {skip})" if skip > 0 else ""
                print(f"Fetched {len(all_stargazers)} stargazers so far{limit_info}{skip_info}")
                
                # Check if we have enough stargazers based on limit
                if limit and len(all_stargazers) >= limit:
                    print(f"Reached requested limit of {limit} stargazers")
                    break
                
                # GitHub API rate limiting
                if response.headers.get('X-RateLimit-Remaining') == '0':
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    sleep_time = max(reset_time - time.time(), 0) + 1
                    print(f"Rate limit reached. Sleeping for {sleep_time:.0f} seconds...")
                    time.sleep(sleep_time)
                
                # Be nice to the API
                time.sleep(0.5)
            elif response.status_code == 401:
                sys.exit("Error: Invalid token or unauthorized access.")
            elif response.status_code == 404:
                sys.exit(f"Error: Repository {repo_owner}/{repo_name} not found.")
            else:
                sys.exit(f"Error: API returned status code {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        print(f"Continuing with {len(all_stargazers)} stargazers fetched so far...")
    
    return all_stargazers

def enrich_stargazer_data(stargazers, token=None, batch_name=None):
    """Enrich stargazer data with additional user information"""
    enriched_data = []
    headers = {}
<<<<<<< HEAD
    linkedin_count = 0
=======
>>>>>>> 8c5765c7ea4b4bc8ee68dcee8a278102324ac737
    
    if token:
        headers['Authorization'] = f"token {token}"
    
    total = len(stargazers)
    batch_info = f" (batch: {batch_name})" if batch_name else ""
    
    for i, stargazer in enumerate(stargazers):
        try:
            user = stargazer.get('user', {})
            username = user.get('login')
            if not username:
                continue
                
            print(f"Enriching data for user {username} ({i+1}/{total}){batch_info}...")
            
            user_url = f"https://api.github.com/users/{username}"
            response = requests.get(user_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                starred_at = stargazer.get('starred_at')
                
<<<<<<< HEAD
                # Extract bio, blog, and company for LinkedIn URL extraction
                bio = user_data.get('bio', '')
                blog = user_data.get('blog', '')
                company = user_data.get('company', '')
                
                # Extract LinkedIn URL if present in any of these fields
                linkedin_url = extract_linkedin_url(bio, blog, company, username)
                if linkedin_url:
                    linkedin_count += 1
                
                enriched_user = {
                    'username': username,
                    'name': user_data.get('name'),
                    'company': company,
                    'blog': blog,
                    'location': user_data.get('location'),
                    'email': user_data.get('email'),
                    'bio': bio,
=======
                enriched_user = {
                    'username': username,
                    'name': user_data.get('name'),
                    'company': user_data.get('company'),
                    'blog': user_data.get('blog'),
                    'location': user_data.get('location'),
                    'email': user_data.get('email'),
                    'bio': user_data.get('bio'),
>>>>>>> 8c5765c7ea4b4bc8ee68dcee8a278102324ac737
                    'twitter_username': user_data.get('twitter_username'),
                    'public_repos': user_data.get('public_repos'),
                    'followers': user_data.get('followers'),
                    'following': user_data.get('following'),
                    'created_at': user_data.get('created_at'),
                    'starred_at': starred_at,
                    'avatar_url': user_data.get('avatar_url'),
<<<<<<< HEAD
                    'html_url': user_data.get('html_url'),
                    'linkedin_url': linkedin_url
=======
                    'html_url': user_data.get('html_url')
>>>>>>> 8c5765c7ea4b4bc8ee68dcee8a278102324ac737
                }
                
                enriched_data.append(enriched_user)
                
                # Save intermediate results every 10 users
                if len(enriched_data) % 10 == 0:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    batch_suffix = f"_{batch_name}" if batch_name else ""
                    temp_file = f"stargazers_temp{batch_suffix}_{timestamp}.json"
                    try:
                        with open(temp_file, 'w', encoding='utf-8') as f:
                            json.dump(enriched_data, f, indent=2)
                        print(f"Saved intermediate data to {temp_file}")
                    except Exception as e:
                        print(f"Failed to save intermediate data: {e}")
                
                # GitHub API rate limiting
                if response.headers.get('X-RateLimit-Remaining') == '0':
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    sleep_time = max(reset_time - time.time(), 0) + 1
                    print(f"Rate limit reached. Sleeping for {sleep_time:.0f} seconds...")
                    time.sleep(sleep_time)
                
                # Be nice to the API
                time.sleep(0.5)
            else:
                print(f"Could not fetch data for user {username}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Network error while processing user {username}: {e}")
            print("Continuing with next user...")
            time.sleep(1)  # Wait a bit before continuing
        except Exception as e:
            print(f"Error processing user {username}: {e}")
            print("Continuing with next user...")
    
    return enriched_data

<<<<<<< HEAD
def extract_linkedin_url(bio, blog, company, username=None):
    """Extract social URLs from profile data"""
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
    
    # If no LinkedIn URL found in API fields and username is provided,
    # try to fetch the HTML profile page
    if username:
        try:
            # First, check the main profile page
            profile_url = f"https://github.com/{username}"
            response = requests.get(profile_url, timeout=10)
            if response.status_code == 200:
                html_content = response.text
                
                # Check for LinkedIn URLs in the HTML content
                for pattern in linkedin_patterns:
                    matches = re.findall(pattern, html_content)
                    if matches:
                        url = matches[0]
                        # Ensure it has the https:// prefix
                        if not url.startswith('http'):
                            url = 'https://' + url
                        return url
            
            # Next, check the profile README.md if it exists
            readme_url = f"https://github.com/{username}/{username}"
            response = requests.get(readme_url, timeout=10)
            if response.status_code == 200:
                readme_html = response.text
                
                # Check for LinkedIn URLs in the README content
                for pattern in linkedin_patterns:
                    matches = re.findall(pattern, readme_html)
                    if matches:
                        url = matches[0]
                        # Ensure it has the https:// prefix
                        if not url.startswith('http'):
                            url = 'https://' + url
                        return url
                        
        except Exception as e:
            print(f"Error fetching profile data for {username}: {e}")
                
    return None

=======
>>>>>>> 8c5765c7ea4b4bc8ee68dcee8a278102324ac737
def extract_repo_info(repo_url):
    """Extract owner and repo name from GitHub URL"""
    # Handle various GitHub URL formats
    if 'github.com' not in repo_url:
        return None, None
        
    parts = repo_url.strip('/').split('/')
    if 'stargazers' in parts:
        parts.remove('stargazers')
    
    # Handle URLs of form github.com/owner/repo
    if len(parts) >= 3 and parts[-3] == 'github.com':
        return parts[-2], parts[-1]
        
    # Try to locate github.com in the URL
    try:
        owner_index = parts.index('github.com') + 1
        if owner_index >= len(parts):
            return None, None
            
        owner = parts[owner_index]
        repo_name = parts[owner_index + 1] if owner_index + 1 < len(parts) else None
        
        return owner, repo_name
    except (ValueError, IndexError):
        return None, None

def merge_enriched_files(output_prefix, pattern="stargazers_enriched_batch_*.json"):
    """Merge multiple enriched files into a single file"""
    import glob
    
    merged_data = []
    files = glob.glob(pattern)
    
    if not files:
        print(f"No files found matching pattern: {pattern}")
        return
    
    print(f"Found {len(files)} files to merge")
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                merged_data.extend(data)
                print(f"Added {len(data)} records from {file_path}")
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
    
    if merged_data:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"{output_prefix}_merged_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2)
        
        print(f"Merged {len(merged_data)} records into {output_file}")
    else:
        print("No data to merge")

def main():
<<<<<<< HEAD
    # Simplify the command-line interface to the old style
    parser = argparse.ArgumentParser(description='Fetch and enrich GitHub repository stargazers.')
    
    # Main command arguments
    parser.add_argument('repo_url', nargs='?', help='GitHub repository URL or owner/repo format')
=======
    parser = argparse.ArgumentParser(description='Fetch and enrich GitHub repository stargazers.')
    parser.add_argument('repo_url', help='GitHub repository URL or owner/repo format')
>>>>>>> 8c5765c7ea4b4bc8ee68dcee8a278102324ac737
    parser.add_argument('--token', '-t', help='GitHub personal access token')
    parser.add_argument('--output', '-o', default='stargazers', help='Output JSON file prefix')
    parser.add_argument('--limit', '-l', type=int, help='Maximum number of stargazers to fetch')
    parser.add_argument('--skip', type=int, default=0, help='Number of stargazers to skip')
    parser.add_argument('--batch-size', '-b', type=int, default=100, 
                        help='Batch size for processing stargazers (default: 100)')
    parser.add_argument('--batch-number', '-n', type=int, help='Batch number to process (1-based)')
    parser.add_argument('--use-existing', '-e', help='Use existing raw stargazers file instead of fetching')
    parser.add_argument('--skip-enrichment', '-s', action='store_true', 
                        help='Skip enrichment step, only fetch stargazers')
<<<<<<< HEAD
    
    # Mode-specific arguments
=======
>>>>>>> 8c5765c7ea4b4bc8ee68dcee8a278102324ac737
    parser.add_argument('--merge-files', '-m', action='store_true',
                        help='Merge multiple enriched batch files into a single file')
    parser.add_argument('--merge-pattern', default='stargazers_enriched_batch_*.json',
                        help='File pattern for merging (default: stargazers_enriched_batch_*.json)')
<<<<<<< HEAD
    parser.add_argument('--linkedin-only', action='store_true',
                        help='Process existing data without fetching new data (requires existing JSON file)')
    parser.add_argument('--existing-file', help='Path to existing enriched JSON file (for --linkedin-only)')
    parser.add_argument('--specific-users', help='Comma-separated list of usernames to process')
    
    args = parser.parse_args()
    
    # Determine the mode based on flags
    if args.merge_files:
        args.mode = 'merge'
    elif args.linkedin_only:
        args.mode = 'linkedin'
    else:
        args.mode = 'normal'
    
    # Handle merge mode
    if args.mode == 'merge' or args.merge_files:
        merge_pattern = args.merge_pattern
        merge_enriched_files(args.output, merge_pattern)
        return
        
    # Handle LinkedIn-only mode
    if args.mode == 'linkedin' or args.linkedin_only:
        if not args.existing_file:
            sys.exit("Error: --existing-file is required for LinkedIn-only mode")
            
        try:
            with open(args.existing_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                
            print(f"Loaded {len(existing_data)} records from {args.existing_file}")
            
            # Filter to specific users if provided
            if args.specific_users:
                usernames = args.specific_users.split(',')
                print(f"Filtering to {len(usernames)} specific users: {', '.join(usernames)}")
                filtered_data = [user for user in existing_data if user.get('username') in usernames]
                if not filtered_data:
                    print("No matching users found!")
                    return
                existing_data = filtered_data
                print(f"Found {len(existing_data)} matching records")
            
            # Limit the number of users to process if requested
            if args.limit and args.limit > 0 and args.limit < len(existing_data):
                print(f"Limiting to {args.limit} users")
                existing_data = existing_data[:args.limit]
            
            linkedin_count = 0
            updated_data = []
            
            for i, user in enumerate(existing_data):
                username = user.get('username')
                bio = user.get('bio', '')
                blog = user.get('blog', '')
                company = user.get('company', '')
                
                # Keep progress indication but remove LinkedIn-specific messaging
                print(f"Processing {i+1}/{len(existing_data)}: {username}")
                
                linkedin_url = extract_linkedin_url(bio, blog, company, username)
                user['linkedin_url'] = linkedin_url
                
                if linkedin_url:
                    linkedin_count += 1
                    
                updated_data.append(user)
            
            # Save updated data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"stargazers_linkedin_updated_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, indent=2)
                
            # Create CSV version
            csv_file = f"stargazers_linkedin_updated_{timestamp}.csv"
            with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                fieldnames = list(updated_data[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write each record
                for record in updated_data:
                    # Handle potential encoding issues for Excel
                    for key, value in record.items():
                        if isinstance(value, str):
                            # Replace any characters that might cause issues in Excel
                            record[key] = value.replace('\n', ' ').replace('\r', '')
                    writer.writerow(record)
            
            print(f"Updated data saved to {output_file}")
            print(f"CSV file saved to {csv_file}")
            
            return
        except Exception as e:
            sys.exit(f"Error processing existing file: {e}")
    
    # Handle normal mode (fetch and enrich)
    if args.mode == 'normal':
        # Check if repo_url is provided
        if not args.repo_url:
            sys.exit("Error: Repository URL is required in normal mode. Use 'owner/repo' or a GitHub repository URL.")
            
        # Check if input is a URL or owner/repo format
        if '/' in args.repo_url and ('github.com' in args.repo_url or 'http' in args.repo_url):
            owner, repo_name = extract_repo_info(args.repo_url)
        else:
            parts = args.repo_url.split('/')
            if len(parts) == 2:
                owner, repo_name = parts
            else:
                sys.exit("Error: Invalid repository format. Use 'owner/repo' or a GitHub repository URL.")
        
        if not owner or not repo_name:
            sys.exit("Error: Could not extract owner and repository name from the provided URL.")
    
        # If batch_number is provided, calculate skip and limit
        if args.batch_number is not None:
            batch_num = max(1, args.batch_number)  # Ensure batch number is at least 1
            args.skip = (batch_num - 1) * args.batch_size
            args.limit = args.batch_size
            batch_name = f"batch_{batch_num}"
        else:
            batch_name = f"skip_{args.skip}_limit_{args.limit}" if args.skip or args.limit else None
        
        # Show what we're doing
        action = "Fetching"
        if args.use_existing:
            action = "Processing"
        
        print(f"{action} stargazers for {owner}/{repo_name}..." + 
              (f" (skip: {args.skip}, limit: {args.limit})" if args.skip or args.limit else ""))
              
        start_time = time.time()
        try:
            # Fetch or load stargazers
            stargazers = fetch_stargazers(owner, repo_name, args.token, args.limit, args.skip, args.use_existing)
            print(f"Found {len(stargazers)} stargazers for processing")
            
            # Save raw stargazers data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            batch_suffix = f"_batch_{args.batch_number}" if args.batch_number is not None else ""
            raw_output_file = f"{args.output}_raw{batch_suffix}_{timestamp}.json"
            with open(raw_output_file, 'w', encoding='utf-8') as f:
                json.dump(stargazers, f, indent=2)
            print(f"Raw stargazer data saved to {raw_output_file}")
            
            if not args.skip_enrichment:
                print("Enriching stargazer data...")
                enriched_data = enrich_stargazer_data(stargazers, args.token, batch_name)
                
                enriched_output_file = f"{args.output}_enriched{batch_suffix}_{timestamp}.json"
                with open(enriched_output_file, 'w', encoding='utf-8') as f:
                    json.dump(enriched_data, f, indent=2)
                
                print(f"Enriched data for {len(enriched_data)} stargazers saved to {enriched_output_file}")
                
                # Also create a CSV version
                csv_output_file = f"{args.output}_enriched{batch_suffix}_{timestamp}.csv"
                with open(csv_output_file, 'w', encoding='utf-8', newline='') as f:
                    if enriched_data:
                        fieldnames = list(enriched_data[0].keys())
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        
                        # Write each record
                        for record in enriched_data:
                            # Handle potential encoding issues for Excel
                            for key, value in record.items():
                                if isinstance(value, str):
                                    # Replace any characters that might cause issues in Excel
                                    record[key] = value.replace('\n', ' ').replace('\r', '')
                            writer.writerow(record)
                        
                        print(f"CSV file with enriched data saved to {csv_output_file}")
                    else:
                        print("No data to write to CSV.")
            
            elapsed_time = time.time() - start_time
            print(f"Total execution time: {elapsed_time:.2f} seconds")
                
        except KeyboardInterrupt:
            print("\nOperation interrupted by user. Saving data collected so far...")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            batch_suffix = f"_batch_{args.batch_number}" if args.batch_number is not None else ""
            interrupted_file = f"{args.output}_interrupted{batch_suffix}_{timestamp}.json"
            try:
                with open(interrupted_file, 'w', encoding='utf-8') as f:
                    json.dump(locals().get('enriched_data', []) or locals().get('stargazers', []), f, indent=2)
                print(f"Partial data saved to {interrupted_file}")
            except Exception as e:
                print(f"Failed to save partial data: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)
=======
    
    args = parser.parse_args()
    
    # If merge option is selected, merge files and exit
    if args.merge_files:
        merge_enriched_files(args.output, args.merge_pattern)
        return
    
    # Check if input is a URL or owner/repo format
    if '/' in args.repo_url and ('github.com' in args.repo_url or 'http' in args.repo_url):
        owner, repo_name = extract_repo_info(args.repo_url)
    else:
        parts = args.repo_url.split('/')
        if len(parts) == 2:
            owner, repo_name = parts
        else:
            sys.exit("Error: Invalid repository format. Use 'owner/repo' or a GitHub repository URL.")
    
    if not owner or not repo_name:
        sys.exit("Error: Could not extract owner and repository name from the provided URL.")
    
    # If batch_number is provided, calculate skip and limit
    if args.batch_number is not None:
        batch_num = max(1, args.batch_number)  # Ensure batch number is at least 1
        args.skip = (batch_num - 1) * args.batch_size
        args.limit = args.batch_size
        batch_name = f"batch_{batch_num}"
    else:
        batch_name = f"skip_{args.skip}_limit_{args.limit}" if args.skip or args.limit else None
    
    # Show what we're doing
    action = "Fetching"
    if args.use_existing:
        action = "Processing"
    
    print(f"{action} stargazers for {owner}/{repo_name}..." + 
          (f" (skip: {args.skip}, limit: {args.limit})" if args.skip or args.limit else ""))
          
    start_time = time.time()
    try:
        # Fetch or load stargazers
        stargazers = fetch_stargazers(owner, repo_name, args.token, args.limit, args.skip, args.use_existing)
        print(f"Found {len(stargazers)} stargazers for processing")
        
        # Save raw stargazers data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        batch_suffix = f"_batch_{args.batch_number}" if args.batch_number is not None else ""
        raw_output_file = f"{args.output}_raw{batch_suffix}_{timestamp}.json"
        with open(raw_output_file, 'w', encoding='utf-8') as f:
            json.dump(stargazers, f, indent=2)
        print(f"Raw stargazer data saved to {raw_output_file}")
        
        if not args.skip_enrichment:
            print("Enriching stargazer data...")
            enriched_data = enrich_stargazer_data(stargazers, args.token, batch_name)
            
            enriched_output_file = f"{args.output}_enriched{batch_suffix}_{timestamp}.json"
            with open(enriched_output_file, 'w', encoding='utf-8') as f:
                json.dump(enriched_data, f, indent=2)
            
            print(f"Enriched data for {len(enriched_data)} stargazers saved to {enriched_output_file}")
        
        elapsed_time = time.time() - start_time
        print(f"Total execution time: {elapsed_time:.2f} seconds")
            
    except KeyboardInterrupt:
        print("\nOperation interrupted by user. Saving data collected so far...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        batch_suffix = f"_batch_{args.batch_number}" if args.batch_number is not None else ""
        interrupted_file = f"{args.output}_interrupted{batch_suffix}_{timestamp}.json"
        try:
            with open(interrupted_file, 'w', encoding='utf-8') as f:
                json.dump(locals().get('enriched_data', []) or locals().get('stargazers', []), f, indent=2)
            print(f"Partial data saved to {interrupted_file}")
        except Exception as e:
            print(f"Failed to save partial data: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
>>>>>>> 8c5765c7ea4b4bc8ee68dcee8a278102324ac737

if __name__ == "__main__":
    main()
# Stargazer Enricher

A tool to capture and enrich GitHub repository stargazers. This script fetches all users who have starred a GitHub repository and enriches their profiles with additional information, including LinkedIn URLs when available.

## Features

- Fetches all stargazers for a GitHub repository
- Records when each user starred the repository
- Enriches stargazer data with user profile information
- Extracts LinkedIn URLs from user profiles when available
- Exports data to both JSON and CSV formats for Excel analysis
- Handles GitHub API rate limiting
- Saves intermediate results to prevent data loss
- Supports batch processing for large repositories
- Processes stargazers in configurable batches
- Re-uses existing data to avoid unnecessary API calls
- Merges multiple batch files into a single file

## Requirements

- Python 3.6+
- `requests` library

## Installation

```bash
pip install requests
```

## Basic Usage

With a repository URL:

```bash
python stargazer_enricher.py https://github.com/owner/repo
```

With a GitHub personal access token (recommended to avoid rate limiting):

```bash
python stargazer_enricher.py owner/repo --token YOUR_GITHUB_TOKEN
```

## Complete Workflow

### 1. Fetch and Process Stargazers

For repositories with many stars, process them in batches:

```bash
# First, fetch all raw stargazers to get the complete list
python stargazer_enricher.py owner/repo --token YOUR_TOKEN --skip-enrichment

# Process the data in batches of 100 using the raw data file
python stargazer_enricher.py owner/repo --token YOUR_TOKEN --batch-size 100 --batch-number 1 --use-existing stargazers_raw_YYYYMMDD_HHMMSS.json
python stargazer_enricher.py owner/repo --token YOUR_TOKEN --batch-size 100 --batch-number 2 --use-existing stargazers_raw_YYYYMMDD_HHMMSS.json
# ... continue for all batches

# Merge all the batch files into a single complete dataset
python stargazer_enricher.py owner/repo --merge-files
```

### 2. Convert to CSV for Excel

```bash
python json_to_csv.py stargazers_merged_YYYYMMDD_HHMMSS.json
```

### 3. Extract LinkedIn URLs

To extract LinkedIn URLs from user profiles and add them to the dataset:

```bash
python linkedin_extractor.py stargazers_merged_YYYYMMDD_HHMMSS.json
```

This will create:
- An enhanced JSON file with LinkedIn URLs: `stargazers_merged_YYYYMMDD_HHMMSS_with_linkedin.json`
- A CSV file ready for Excel with LinkedIn URLs: `stargazers_merged_YYYYMMDD_HHMMSS_with_linkedin.csv`

## Advanced Options

### Batch Processing Options

You can process stargazers in batches using batch numbers:

```bash
# Process first 50 stargazers (batch 1)
python stargazer_enricher.py owner/repo --token YOUR_TOKEN --batch-size 50 --batch-number 1

# Process next 50 stargazers (batch 2)
python stargazer_enricher.py owner/repo --token YOUR_TOKEN --batch-size 50 --batch-number 2
```

Or using skip and limit parameters directly:

```bash
# Process stargazers 0-99
python stargazer_enricher.py owner/repo --token YOUR_TOKEN --limit 100 --skip 0

# Process stargazers 100-199
python stargazer_enricher.py owner/repo --token YOUR_TOKEN --limit 100 --skip 100
```

### Re-using Raw Data

To avoid re-fetching the stargazers list for each batch:

```bash
# First, fetch all raw stargazers (skip enrichment)
python stargazer_enricher.py owner/repo --token YOUR_TOKEN --skip-enrichment

# Then process batches using the raw data file
python stargazer_enricher.py owner/repo --token YOUR_TOKEN --batch-size 100 --batch-number 1 --use-existing stargazers_raw_YYYYMMDD_HHMMSS.json
```

### Merging Batch Files

After processing all batches, merge them into a single file:

```bash
python stargazer_enricher.py owner/repo --merge-files
```

Specify a different pattern if needed:

```bash
python stargazer_enricher.py owner/repo --merge-files --merge-pattern "stargazers_*.json"
```

### Other Options

Specify a custom output file prefix:

```bash
python stargazer_enricher.py owner/repo --output my_stargazers
```

Skip the enrichment step and only fetch basic stargazer data:

```bash
python stargazer_enricher.py owner/repo --skip-enrichment
```

## GitHub API Rate Limiting

Without authentication, GitHub API limits to 60 requests per hour. With authentication (using a token), this increases to 5,000 requests per hour. For repositories with many stargazers, using a token is highly recommended.

To create a GitHub personal access token:
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token with the `public_repo` scope

## Output Data Format

The enriched dataset contains the following information for each stargazer:

- Username
- Name
- Company
- Blog
- Location
- Email (if public)
- Bio
- Twitter username
- LinkedIn URL (extracted from bio, blog, or company fields when available)
- Public repositories count
- Followers count
- Following count
- Account creation date
- Date when they starred the repository
- Avatar URL
- GitHub profile URL

## File Descriptions

- `stargazer_enricher.py`: Main script to fetch and enrich stargazer data
- `json_to_csv.py`: Converts JSON data to CSV format for Excel
- `linkedin_extractor.py`: Extracts LinkedIn URLs from user profiles
- `linkedin_searcher.py`: Searches for LinkedIn profiles for users who don't have LinkedIn URLs

## LinkedIn Profile Searcher

For users who don't have LinkedIn URLs in their profiles, you can use the LinkedIn Profile Searcher to find their LinkedIn profiles based on their name and company:

```bash
python linkedin_searcher.py stargazers_merged_YYYYMMDD_HHMMSS.csv --manual-login --limit 10
```

### Features

- Searches Google for LinkedIn profiles based on user name and company
- Extracts profile text from LinkedIn profile pages
- Captures connection degree between you and the profile
- Handles manual LinkedIn login with CAPTCHA support
- Maintains session for reliable profile access
- Saves intermediate results to prevent data loss
- Adds random delays to avoid rate limiting
- Has robust error handling for temporary issues

### Requirements

For the LinkedIn searcher, you'll need:

```bash
pip install playwright
playwright install
```

### Options

```
usage: linkedin_searcher.py [-h] [--output OUTPUT] [--limit LIMIT]
                           [--linkedin-username LINKEDIN_USERNAME]
                           [--linkedin-password LINKEDIN_PASSWORD]
                           [--headless] [--no-interactive]
                           [--manual-login]
                           input_file

positional arguments:
  input_file            Input CSV file with stargazers data

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output CSV file (default: input_file_enriched_linkedin.csv)
  --limit LIMIT, -l LIMIT
                        Limit the number of records to process
  --linkedin-username LINKEDIN_USERNAME
                        LinkedIn username/email for logging in
  --linkedin-password LINKEDIN_PASSWORD
                        LinkedIn password for logging in
  --headless            Run in headless mode (default: interactive for login, headless for processing)
  --no-interactive      Disable interactive mode for handling verification
  --manual-login        Use manual login instead of automated login
```

### Manual Login (Recommended)

The `--manual-login` option is the most reliable method, as it gives you full control over the login process, including handling CAPTCHA:

```bash
python linkedin_searcher.py stargazers_merged_YYYYMMDD_HHMMSS.csv --manual-login
```

A browser window will open for you to manually log in to LinkedIn. After logging in, return to the terminal and type 'done' to continue.
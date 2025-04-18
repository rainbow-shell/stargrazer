# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Run stargazer enricher: `python stargazer_enricher.py <repo_url> --token <token>`
- Convert JSON to CSV: `python json_to_csv.py <json_file> [csv_file]`
- Extract LinkedIn info: `python linkedin_extractor.py <json_file> [output_file]`
- Run a specific batch: `python stargazer_enricher.py <repo_url> --batch-size <size> --batch-number <num>`
- Merge batch files: `python stargazer_enricher.py <repo_url> --merge-files`
- Search LinkedIn profiles: `python linkedin_searcher.py <csv_file> --manual-login [--output output.csv] [--limit N]`

## Dependencies

- Python 3.6+
- requests
- playwright (for LinkedIn searcher): `pip install playwright && playwright install`

## LinkedIn Searcher Workflow

The LinkedIn searcher workflow is:
1. Run the script on a CSV file containing stargazer data
2. Use the `--manual-login` option for reliable authentication
3. Browser window opens and waits for user to log in manually
4. After login, user types 'done' in terminal to continue
5. Script processes each record to find LinkedIn profiles
6. Results saved to new CSV with original data + LinkedIn fields

Example for running LinkedIn searcher:
```bash
python linkedin_searcher.py stargazers_merged_20250417_114816.csv --manual-login --limit 10
```

The LinkedIn searcher adds these fields to the CSV:
- `linkedin_url_guess`: The LinkedIn profile URL found by the script
- `linkedin_profile_text`: Text extracted from the profile "About" section
- `linkedin_connection_degree`: Connection degree (1st, 2nd, 3rd) between profiles

## Code Style

- Use Python 3.6+ compatible code
- Follow PEP 8 style guidelines
- Include docstrings for all functions and modules
- Import order: standard library -> third-party -> local
- Use meaningful variable and function names
- Error handling: wrap API calls and file operations in try/except blocks
- Gracefully handle rate limiting and network interruptions
- Use f-strings for string formatting
- Use snake_case for variables and functions
- For async code, use asyncio and proper async/await patterns

## Data Structures

The enriched stargazer data structure includes:
- username: GitHub username
- name: Full name from GitHub profile
- company: Company name if provided
- blog: Website/blog URL if provided
- location: Location if provided
- email: Public email if available
- bio: User's bio/description
- twitter_username: Twitter handle if linked
- public_repos: Number of public repositories
- followers: Number of followers
- following: Number of users they follow
- created_at: Account creation date
- starred_at: When they starred the repository
- avatar_url: Profile picture URL
- html_url: GitHub profile URL
- linkedin_url: LinkedIn URL if found in profile
- linkedin_url_guess: LinkedIn URL found by the searcher
- linkedin_profile_text: Text from LinkedIn profile
- linkedin_connection_degree: Connection level (1st, 2nd, etc.)
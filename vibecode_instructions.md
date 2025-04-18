# Vibecode Instructions

This file provides guidance when working with code in this repository.

## Commands

- Run stargazer enricher: `python stargazer_enricher.py <repo_url> --token <token>`
- Convert JSON to CSV: `python json_to_csv.py <json_file> [csv_file]`
- Extract LinkedIn info: `python linkedin_extractor.py <json_file> [output_file]`
- Run a specific batch: `python stargazer_enricher.py <repo_url> --batch-size <size> --batch-number <num>`
- Merge batch files: `python stargazer_enricher.py <repo_url> --merge-files`

## Dependencies

- Python 3.6+
- requests

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
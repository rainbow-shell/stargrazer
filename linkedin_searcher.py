#!/usr/bin/env python3
"""
LinkedIn Profile Searcher - Enriches stargazers data with LinkedIn profiles for users without LinkedIn URLs
Using Playwright for headless browser automation
"""
import json
import csv
import sys
import os
import time
import re
import random
import argparse
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

def clean_company_name(company):
    """
    Clean the company name by removing @ symbol and other non-alphanumeric characters
    """
    if not company:
        return ""
    
    # Remove @ symbol and special characters
    cleaned = re.sub(r'@', '', company)
    cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def create_search_query(name, company):
    """
    Create a search query for LinkedIn based on name and company
    """
    query_parts = []
    
    if name:
        query_parts.append(name)
    
    cleaned_company = clean_company_name(company)
    if cleaned_company:
        query_parts.append(cleaned_company)
    
    return " ".join(query_parts)

async def setup_browser(headless=True):
    """
    Set up and return a browser instance using Playwright
    
    Args:
        headless: Whether to run the browser in headless mode
    """
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        return playwright, browser, context
    except Exception as e:
        print(f"Error setting up browser: {e}")
        print("Make sure you have Playwright installed. Run: pip install playwright && playwright install")
        return None, None, None

async def manual_linkedin_login(context):
    """
    Opens LinkedIn and waits for the user to manually log in with full control of the process
    
    Args:
        context: Browser context
        
    Returns:
        True if login confirmed by user, False otherwise
    """
    try:
        print("\n==================================================")
        print("MANUAL LINKEDIN LOGIN")
        print("==================================================")
        print("A browser window will open for you to log in to LinkedIn.")
        print("Please:")
        print("1. Enter your credentials")
        print("2. Complete any verification steps and CAPTCHA")
        print("3. Make sure you're fully logged in")
        print()
        print("The browser window will REMAIN OPEN during the entire process.")
        print("IMPORTANT: Login to your account manually and leave the window open.")
        print("The browser window will stay active throughout the entire process.")
        print()
        print("Press Enter when you're ready to open the browser...")
        print("==================================================\n")
        
        input()  # Wait for user to press Enter to start
        
        # Create a persistent page that will stay open
        page = await context.new_page()
        await page.goto("https://www.linkedin.com/", wait_until="domcontentloaded")
        
        print("\nBrowser window opened. Please log in to LinkedIn now...\n")
        print("IMPORTANT INSTRUCTIONS:")
        print("1. Complete the entire login process in the browser window")
        print("2. Solve any CAPTCHA or verification challenges")
        print("3. WAIT until you can see your LinkedIn homepage/feed")
        print("4. After you are fully logged in, RETURN TO THIS TERMINAL")
        print("5. Type 'done' and press Enter ONLY when completely logged in")
        print("\nThe browser window will remain open throughout this process.")
        print("Take as much time as you need to complete the login.\n")
        
        # Loop until user confirms they're done or wants to abort
        while True:
            print("When finished login, type 'done' and press Enter, or 'abort' to quit: ", end="")
            user_response = input().strip().lower()
            
            if user_response == 'abort':
                print("Login aborted by user.")
                await page.close()
                return False
                
            if user_response == 'done':
                break
                
            print("Invalid input. Please type 'done' when finished or 'abort' to quit.")
        
        # After user confirms, check login status
        logged_in = await is_linkedin_logged_in(page)
        
        if logged_in:
            print("\nLinkedIn login confirmed! The script will continue with processing...")
            print("The login browser window will remain open for the entire process.")
        else:
            print("\nWarning: Could not automatically verify that you're logged in to LinkedIn.")
            print("This may happen if LinkedIn's page layout has changed.")
            print("Do you want to proceed anyway? (Type 'yes' to continue, anything else to abort): ", end="")
            
            response = input().strip().lower()
            if response != 'yes':
                print("Aborting at user request.")
                await page.close()
                return False
                
            print("Continuing at user request...")
        
        # Store the login page in the context for later reference
        context.login_page = page
        
        return True
            
    except Exception as e:
        print(f"Error during manual LinkedIn login: {e}")
        try:
            await page.close()
        except:
            pass
        return False

async def is_linkedin_logged_in(page):
    """
    Check if the current page shows a logged-in state on LinkedIn
    """
    try:
        # Look for elements that indicate logged-in state
        is_logged_in = await page.evaluate("""
            () => {
                // Check for various elements that would indicate a logged-in state
                const feedContainer = document.querySelector('div.feed-container');
                const globalNav = document.querySelector('.global-nav');
                const profileNav = document.querySelector('.profile-rail-card');
                
                return !!(feedContainer || globalNav || profileNav);
            }
        """)
        return is_logged_in
    except Exception:
        return False

async def login_to_linkedin(context, username, password, interactive=True):
    """
    Automated login to LinkedIn with username and password
    
    Args:
        context: Browser context
        username: LinkedIn username/email
        password: LinkedIn password
        interactive: Whether to allow manual interaction for verification
    
    Returns:
        True if login successful, False otherwise
    """
    try:
        page = await context.new_page()
        await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
        
        print("\nAttempting automated LinkedIn login...")
        
        # Enter username and password
        await page.fill("input#username", username)
        await page.fill("input#password", password)
        await page.click("button[type='submit']")
        
        # Allow time for login to complete
        await asyncio.sleep(3)
        
        # Check for CAPTCHA or verification challenges
        verification_needed = await page.query_selector(".captcha-container") is not None
        pin_verification = await page.query_selector("input#pin") is not None
        
        if verification_needed or pin_verification or interactive:
            print("\nVerification or CAPTCHA detected, or interactive mode enabled.")
            print("Please complete any verification steps manually...")
            print("Browser window is now visible for you to interact with.")
            
            # Keep waiting until user confirms they're done
            print("\nOnce you have completed login and can see your LinkedIn homepage:")
            print("Type 'done' and press Enter to continue, or 'abort' to quit: ", end="")
            
            while True:
                user_response = input().strip().lower()
                
                if user_response == 'abort':
                    print("Login aborted by user.")
                    await page.close()
                    return False
                    
                if user_response == 'done':
                    break
                    
                print("Invalid input. Please type 'done' when finished or 'abort' to quit: ", end="")
        
        # After user interaction or automated login, check if we're logged in
        logged_in = await is_linkedin_logged_in(page)
        
        if logged_in:
            print("LinkedIn login successful!")
            # Store the page for later use
            context.login_page = page
            return True
        else:
            print("LinkedIn login failed. Please check your credentials or try manual login.")
            await page.close()
            return False
            
    except Exception as e:
        print(f"Error during LinkedIn login: {e}")
        try:
            await page.close()
        except:
            pass
        return False

async def extract_linkedin_profile_info(page, linkedin_url):
    """
    Visit the LinkedIn profile page and extract the profile text and connection degree
    Returns a tuple of (profile_text, connection_degree)
    """
    try:
        await page.goto(linkedin_url, wait_until="domcontentloaded")
        
        # Allow time for page to fully load
        await asyncio.sleep(2)
        
        profile_text = "Profile text not found"
        connection_degree = "Not connected"
        
        # Extract profile text
        try:
            # Wait for and extract the profile text from the specific div class
            await page.wait_for_selector("div.text-body-medium.break-words", timeout=5000)
            profile_element = await page.query_selector("div.text-body-medium.break-words")
            
            if profile_element:
                profile_text = await profile_element.inner_text()
            else:
                # Try an alternative selector if the specific one isn't found
                about_section = await page.query_selector("section.about-section")
                if about_section:
                    profile_text = await about_section.inner_text()
        except Exception as e:
            print(f"Error extracting profile text: {e}")
        
        # Extract connection degree
        try:
            # Try to find the connection degree element
            connection_element = await page.query_selector("span.dist-value")
            if connection_element:
                connection_text = await connection_element.inner_text()
                # Clean up the text (remove extra whitespace)
                connection_degree = connection_text.strip()
            else:
                # Alternative selectors to try
                connection_element = await page.query_selector("[data-test-id='relationship-degree-text']")
                if connection_element:
                    connection_degree = await connection_element.inner_text()
                    connection_degree = connection_degree.strip()
        except Exception as e:
            print(f"Error extracting connection degree: {e}")
            
        return profile_text, connection_degree
            
    except Exception as e:
        print(f"Error extracting profile information: {e}")
        return "Error extracting profile text", "Unknown"

async def search_linkedin_profile(query, context, is_logged_in=False):
    """
    Search for LinkedIn profile using the query with Playwright
    Returns a tuple of (linkedin_url, profile_text, connection_degree)
    """
    if not context:
        return None, None, None
        
    # Check if we have a persisted login page
    has_login_page = hasattr(context, 'login_page')
        
    try:
        # Create a new page for Google search
        search_page = await context.new_page()
        
        # Step 1: Search Google for the LinkedIn profile
        escaped_query = query.replace(' ', '+')
        search_url = f"https://www.google.com/search?q={escaped_query}+site:linkedin.com/in"
        
        try:
            # Go to Google search and wait for it to load
            await search_page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            
            # Try multiple possible selectors for Google search results
            selectors = ["div[jscontroller]", "div.g", "#search", "div.main"]
            
            # Wait for any of the selectors to appear
            for selector in selectors:
                try:
                    await search_page.wait_for_selector(selector, timeout=5000)
                    break  # If selector is found, break the loop
                except:
                    continue  # Try next selector if this one times out
            
            # Wait a bit for any dynamic content to load
            await asyncio.sleep(2)
            
            # Find LinkedIn links in search results
            linkedin_links = await search_page.query_selector_all("a[href*='linkedin.com/in/']")
            
            if not linkedin_links or len(linkedin_links) == 0:
                print(f"No LinkedIn profile found for query: '{query}'")
                await search_page.close()
                return None, None, None
            
            # Get the href attribute from the first link
            linkedin_url = await linkedin_links[0].get_attribute("href")
            
            # Remove UTM parameters and other tracking from the URL
            linkedin_url = re.sub(r'\?.*$', '', linkedin_url)
            
            # Close the search page, we don't need it anymore
            await search_page.close()
            
            profile_text = "Profile text unavailable - Not logged in to LinkedIn"
            connection_degree = "Not logged in"
            
            # Step 2: If logged in, visit the LinkedIn profile and extract info
            if is_logged_in:
                print(f"Visiting LinkedIn profile: {linkedin_url}")
                
                # If we have a login page, use that for profile viewing to maintain session
                if has_login_page:
                    # Use the existing logged-in page to navigate to the profile
                    try:
                        await context.login_page.goto(linkedin_url, wait_until="domcontentloaded", timeout=30000)
                        profile_text, connection_degree = await extract_linkedin_profile_info(context.login_page, linkedin_url)
                    except Exception as e:
                        print(f"Error using login page to view profile: {e}")
                        print("Creating a new page for profile viewing...")
                        
                        # If there's an error with the login page, fall back to creating a new page
                        profile_page = await context.new_page()
                        profile_text, connection_degree = await extract_linkedin_profile_info(profile_page, linkedin_url)
                        await profile_page.close()
                else:
                    # Create a new page for viewing the profile
                    profile_page = await context.new_page()
                    profile_text, connection_degree = await extract_linkedin_profile_info(profile_page, linkedin_url)
                    await profile_page.close()
            
            # Sleep to avoid rate limiting
            await asyncio.sleep(2)
            
            return linkedin_url, profile_text, connection_degree
            
        except Exception as e:
            print(f"Error during search for '{query}': {e}")
            
            # Take a screenshot of the failed search for debugging
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                screenshot_path = f"search_error_{timestamp}.png"
                await search_page.screenshot(path=screenshot_path)
                print(f"Saved error screenshot to {screenshot_path}")
            except:
                pass
                
            await search_page.close()
            return None, None, None
            
    except Exception as e:
        print(f"Error creating search page for '{query}': {e}")
        try:
            if 'search_page' in locals():
                await search_page.close()
        except:
            pass
        return None, None, None

async def process_records(records, context, is_logged_in=False, limit=None):
    """
    Process records asynchronously
    """
    enriched_records = []
    total_processed = 0
    total_found = 0
    consecutive_errors = 0
    MAX_CONSECUTIVE_ERRORS = 5
    
    for i, record in enumerate(records):
        # Check if we've hit the limit
        if limit and total_processed >= limit:
            break
            
        # Check if we've had too many consecutive errors
        if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
            print(f"\nWARNING: {consecutive_errors} consecutive errors detected.")
            print("Google search may be temporarily blocking requests.")
            print("Do you want to continue processing? Type 'yes' to continue or anything else to stop: ", end="")
            response = input().strip().lower()
            if response != 'yes':
                print("Processing stopped at user request.")
                break
            consecutive_errors = 0  # Reset error counter
        
        # Skip records that already have a LinkedIn URL
        if record.get('linkedin_url'):
            enriched_records.append(record)
            continue
        
        name = record.get('name', '')
        company = record.get('company', '')
        
        # Skip if no name is available
        if not name:
            enriched_records.append(record)
            continue
        
        total_processed += 1
        print(f"Processing {name} at {company} ({i+1}/{len(records)})...")
        
        try:
            # Create search query and search for LinkedIn profile
            query = create_search_query(name, company)
            linkedin_url, profile_text, connection_degree = await search_linkedin_profile(query, context, is_logged_in)
            
            # Update the record with the LinkedIn data
            record['linkedin_url_guess'] = linkedin_url or ''
            record['linkedin_profile_text'] = profile_text or ''
            record['linkedin_connection_degree'] = connection_degree or ''
            
            if linkedin_url:
                total_found += 1
                consecutive_errors = 0  # Reset error counter on success
            else:
                consecutive_errors += 1  # Increment error counter if no profile found
                
            enriched_records.append(record)
            
            # Save intermediate results every 5 processed records
            if total_processed % 5 == 0:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                temp_file = f"linkedin_enrichment_temp_{timestamp}.csv"
                
                # Get field names from the first record
                fieldnames = list(enriched_records[0].keys())
                
                try:
                    with open(temp_file, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(enriched_records)
                        
                    print(f"Saved intermediate data to {temp_file}")
                except Exception as e:
                    print(f"Error saving intermediate data: {e}")
            
            # Add a random delay between requests to avoid being blocked
            delay = 2 + random.random() * 3  # Random delay between 2-5 seconds
            await asyncio.sleep(delay)
            
        except Exception as e:
            print(f"Error processing record {i+1}: {e}")
            consecutive_errors += 1
            
            # Add the record with error information
            record['linkedin_url_guess'] = ''
            record['linkedin_profile_text'] = f"Error: {str(e)}"
            record['linkedin_connection_degree'] = ''
            enriched_records.append(record)
            
            # Wait a bit longer after an error
            await asyncio.sleep(5)
    
    return enriched_records, total_processed, total_found

async def enrich_linkedin_data_async(input_file, output_file=None, linkedin_username=None, 
                               linkedin_password=None, limit=None, headless=True, interactive=True,
                               manual_login=False):
    """
    Enrich the CSV data with LinkedIn profiles for users who have a name but no LinkedIn URL
    
    Args:
        input_file: Path to the input CSV file
        output_file: Path to the output CSV file (generated if not provided)
        linkedin_username: LinkedIn username/email for login
        linkedin_password: LinkedIn password for login
        limit: Maximum number of records to process
        headless: Whether to run the browser in headless mode
        interactive: Whether to allow manual interaction for verification
        manual_login: Whether to use manual login instead of automated login
    """
    # Generate default output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_enriched_linkedin.csv"
    
    print(f"Enriching LinkedIn data from {input_file}...")
    
    try:
        # Load the CSV file
        records = []
        with open(input_file, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                records.append(row)
        
        if not records:
            print("No data found in CSV file.")
            return False
        
        # Get field names and add new fields for LinkedIn data
        fieldnames = list(records[0].keys())
        if 'linkedin_url_guess' not in fieldnames:
            fieldnames.append('linkedin_url_guess')
        if 'linkedin_profile_text' not in fieldnames:
            fieldnames.append('linkedin_profile_text')
        if 'linkedin_connection_degree' not in fieldnames:
            fieldnames.append('linkedin_connection_degree')
        
        # Always use visible browser for manual login
        login_headless = False if manual_login else headless
        if interactive and linkedin_username and linkedin_password and not manual_login:
            login_headless = False
            print("Using interactive mode for LinkedIn login - a browser window will open.")
        
        # Set up the browser - non-headless for login if interactive or manual
        playwright, browser, context = await setup_browser(headless=login_headless)
        if not context:
            return False
        
        try:
            # Handle login
            is_logged_in = False
            
            if manual_login:
                # Use manual login
                is_logged_in = await manual_linkedin_login(context)
            elif linkedin_username and linkedin_password:
                # Use automated login with credentials
                is_logged_in = await login_to_linkedin(context, linkedin_username, linkedin_password, interactive)
            else:
                print("No login method provided. Will only extract profile URLs, not profile text or connection degree.")
            
            # If visible browser was used for login, and we need to switch to headless
            if is_logged_in and not login_headless and headless:
                print("Login successful. Switching to headless mode for processing...")
                # Save cookies
                cookies = await context.cookies()
                # Close old browser
                await context.close()
                await browser.close()
                
                # Start new headless browser
                playwright, browser, context = await setup_browser(headless=True)
                # Restore cookies
                await context.add_cookies(cookies)
            
            # Process the records
            enriched_records, total_processed, total_found = await process_records(
                records, context, is_logged_in, limit
            )
            
            # Write the final enriched data to the output file
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(enriched_records)
            
            # Print statistics
            print(f"\nEnrichment complete:")
            print(f"Total records: {len(records)}")
            print(f"Records processed: {total_processed}")
            print(f"LinkedIn profiles found: {total_found}")
            if total_processed > 0:
                print(f"Success rate: {(total_found/total_processed)*100:.2f}% (of processed records)")
            print(f"\nEnriched data saved to {output_file}")
            
            return True
        
        finally:
            # Clean up, but carefully to avoid errors with the login page
            try:
                # If we have a login page attribute, close it separately
                if hasattr(context, 'login_page'):
                    print("Closing login browser window...")
                    await context.login_page.close()
                
                # Close the rest of the browser resources
                await context.close()
                await browser.close()
                await playwright.stop()
            except Exception as e:
                print(f"Error during cleanup: {e}")
                # Try to force close the browser if possible
                try:
                    await browser.close()
                    await playwright.stop()
                except:
                    pass
    
    except Exception as e:
        print(f"Error enriching LinkedIn data: {e}")
        return False

def enrich_linkedin_data(input_file, output_file=None, linkedin_username=None, linkedin_password=None, 
                        limit=None, headless=True, interactive=True, manual_login=False):
    """
    Synchronous wrapper for the async enrichment function
    """
    return asyncio.run(enrich_linkedin_data_async(
        input_file, output_file, linkedin_username, linkedin_password, limit, headless, interactive, manual_login
    ))

def main():
    parser = argparse.ArgumentParser(description='Enrich stargazers data with LinkedIn profiles')
    parser.add_argument('input_file', help='Input CSV file with stargazers data')
    parser.add_argument('--output', '-o', help='Output CSV file (default: input_file_enriched_linkedin.csv)')
    parser.add_argument('--limit', '-l', type=int, help='Limit the number of records to process')
    parser.add_argument('--linkedin-username', help='LinkedIn username/email for logging in')
    parser.add_argument('--linkedin-password', help='LinkedIn password for logging in')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode (default: interactive for login, headless for processing)')
    parser.add_argument('--no-interactive', dest='interactive', action='store_false', help='Disable interactive mode for handling verification')
    parser.add_argument('--manual-login', action='store_true', help='Use manual login instead of automated login')
    parser.set_defaults(headless=False, interactive=True, manual_login=False)
    
    args = parser.parse_args()
    
    # Enrich the data
    enrich_linkedin_data(
        args.input_file, 
        args.output, 
        args.linkedin_username, 
        args.linkedin_password, 
        args.limit,
        args.headless,
        args.interactive,
        args.manual_login
    )

if __name__ == "__main__":
    main()
# Automated Work Logger - Migrated from Selenium to Playwright with Jira Integration
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import base64
import json
import argparse

load_dotenv()


class AutomatedWorkLogger:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.ensure_screenshots_directory()
    
    def ensure_screenshots_directory(self):
        """Create screenshots directory if it doesn't exist"""
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
            print("📁 Created screenshots directory")
        
    def get_jira_issues(self):
        """Fetch recent Jira issues assigned to the user"""
        # Jira API configuration
        jira_url = os.getenv("JIRA_URL")
        jira_username = os.getenv("JIRA_USERNAME")  # Ticket assignee
        jira_svc_account = os.getenv("JIRA_SVC_ACCOUNT")  # Service account
        jira_api_token = os.getenv("JIRA_API_TOKEN")  # Service account API token
        jira_project = os.getenv("JIRA_PROJECT")
        
        if not jira_username:
            raise ValueError("JIRA_USERNAME environment variable is required but not set")
        if not jira_svc_account:
            raise ValueError("JIRA_SVC_ACCOUNT environment variable is required but not set")
        if not jira_api_token:
            raise ValueError("JIRA_API_TOKEN environment variable is required but not set")
        if not jira_url:
            raise ValueError("JIRA_URL environment variable is required but not set")
        if not jira_project:
            raise ValueError("JIRA_PROJECT environment variable is required but not set")
        
        # Create authentication header
        auth_string = f"{jira_svc_account}:{jira_api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        # JQL query - same as n8n automation
        jql = f'project = {jira_project} AND assignee = "{jira_username}" AND updated >= -5d AND type IN standardIssueTypes()'
        
        # API endpoint
        url = f"{jira_url}/rest/api/2/search"
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        params = {
            "jql": jql,
            "maxResults": 10,
            "fields": "key,summary"
        }
        
        print(f"Querying Jira for recent tickets...")
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Jira API: {str(e)}")
        
        if response.status_code == 401:
            raise ValueError(f"Jira authentication failed. Please check your JIRA_USERNAME and JIRA_API_TOKEN credentials.")
        elif response.status_code == 403:
            raise ValueError(f"Jira access forbidden. Your account may not have permission to access the {jira_project} project.")
        elif response.status_code != 200:
            raise ValueError(f"Jira API error: {response.status_code} - {response.text}")
        
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Jira API: {str(e)}")
        
        issues = data.get('issues', [])
        
        if not issues:
            raise ValueError(f"No recent tickets found for {jira_username} in {jira_project} project (last 5 days). Please verify your Jira username and that you have assigned tickets.")
        
        issue_keys = [issue['key'] for issue in issues]
        print(f"Found {len(issue_keys)} tickets: {', '.join(issue_keys)}")
        
        # Format tasks same as n8n automation
        tasks = f"Daily Standup, Retro, Planning, Refinement, Code Reviews, help to team, and work on the tickets {', '.join(issue_keys)}"
        return tasks
    
    def get_current_weekday(self):
        """Get current weekday abbreviation"""
        weekdays = {0: "Mo", 1: "Tu", 2: "We", 3: "Th", 4: "Fr", 5: "Sa", 6: "Su"}
        today = datetime.now().weekday()
        return weekdays.get(today)
    
    def get_weekday_full_name(self, day_abbr):
        """Convert day abbreviation to full name"""
        day_names = {
            "Mo": "Monday", "Tu": "Tuesday", "We": "Wednesday", 
            "Th": "Thursday", "Fr": "Friday", "Sa": "Saturday", "Su": "Sunday"
        }
        return day_names.get(day_abbr, day_abbr)
    
    def setup_browser(self, headless=True):
        """Initialize browser and page"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        # Set viewport size to meet site requirements (at least 1366px)
        self.context = self.browser.new_context(viewport={'width': 1366, 'height': 768})
        self.page = self.context.new_page()
    
    def teardown_browser(self):
        """Clean up browser resources"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def login(self):
        """Handle login to the work logging system"""
        print("Navigating to login page...")
        self.page.goto("https://service-management.coderfull.com/login")
        
        # Check if submit button exists (login required)
        submit_buttons = self.page.locator("button:has-text('Login')")
        has_submit = submit_buttons.count() == 1
        
        if has_submit:
            print("Login required. Authenticating...")
            # Fill in credentials
            self.page.locator("input[label='Username']").fill(os.getenv("SYSTEM_USERNAME"))
            self.page.locator("input[label='Password']").fill(os.getenv("SYSTEM_PASSWORD"))
            self.page.locator("button[type='submit']").click()
            
            # Wait for navigation after login
            self.page.wait_for_load_state("networkidle")
            print("Login successful!")
        else:
            print("Already logged in.")
    
    def log_hours_for_day(self, day, tasks):
        """Log hours for a specific day"""
        try:
            day_name = self.get_weekday_full_name(day)
            print(f"Logging hours for {day_name} ({day})...")
            
            # Wait for the page to load and try different selectors for the current day
            try:
                # Try the original selector first
                self.page.locator(f"span:has-text('{day}')").click(timeout=10000)
            except:
                try:
                    # Alternative selector - might be in a different structure
                    self.page.locator(f"text={day}").click(timeout=10000)
                except:
                    # If still not found, take a screenshot for debugging
                    debug_screenshot = f"screenshots/debug_screenshot_{day}.png"
                    self.page.screenshot(path=debug_screenshot)
                    raise Exception(f"Could not find {day} element. Screenshot saved as {debug_screenshot}")
            
            # Fill in task details
            self.page.locator("input[name='task']").fill(tasks)
            self.page.locator("input[name='time']").fill("8h")
            
            # Submit the hours
            self.page.locator("button:has-text('Log Hours')").click()
            
            # Wait a moment for processing
            self.page.wait_for_timeout(1000)
            print(f"✅ Successfully logged 8 hours for {day_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error logging hours for {day}: {str(e)}")
            return False
    
    def log_hours_for_week(self, tasks, days=None):
        """Log hours for specified days or full week"""
        if days is None:
            # Default: full work week
            days = ["Mo", "Tu", "We", "Th", "Fr"]
        elif isinstance(days, str):
            # Single day passed as string
            days = [days]
        
        success_count = 0
        total_days = len(days)
        
        # Loop through each specified day
        for day in days:
            if self.log_hours_for_day(day, tasks):
                success_count += 1
            
            # Brief pause between days (except for the last one)
            if day != days[-1]:
                self.page.wait_for_timeout(500)
        
        # Take a final screenshot to verify logged hours
        print(f"\n📸 Taking verification screenshot...")
        
        # Wait for loading to complete using multiple strategies
        try:            
            print("⏳ Checking for loading spinner...")
            try:
                self.page.wait_for_selector('svg.tw-animate-spin', timeout=10000, state="hidden")
            except:
                print("⚠️  Warning: Could not find loading spinner")
                print("⏳ Adding fallback wait...")
                self.page.wait_for_timeout(3000)  # Fallback wait
            
            print("✅ Page loading completed and UI is ready")
        except Exception as e:
            print(f"⚠️  Warning: Could not fully confirm page loading completion: {str(e)}")
            print("⏳ Adding fallback wait...")
            self.page.wait_for_timeout(3000)  # Fallback wait
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"screenshots/hours_logged_verification_{timestamp}.png"
        self.page.screenshot(path=screenshot_path)
        print(f"Screenshot saved as '{screenshot_path}'")
        
        # Summary
        if success_count == total_days:
            print(f"✅ Successfully logged hours for all {total_days} day(s)!")
        else:
            print(f"⚠️  Logged hours for {success_count}/{total_days} day(s)")
        
        return success_count == total_days
    
    def run(self, mode="week", specific_day=None):
        """Main execution method"""
        try:
            print(f"=== Automated Work Logger Started at {datetime.now()} ===")
            
            # Determine what days to log
            if mode == "today":
                current_day = self.get_current_weekday()
                if current_day in ["Sa", "Su"]:
                    print(f"🗓️  Today is {self.get_weekday_full_name(current_day)} (weekend). No work hours to log.")
                    return
                days_to_log = [current_day]
                print(f"🗓️  Mode: Single day (Today - {self.get_weekday_full_name(current_day)})")
            elif mode == "day" and specific_day:
                if specific_day not in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
                    print(f"❌ Invalid day: {specific_day}. Use Mo, Tu, We, Th, Fr, Sa, Su")
                    return
                days_to_log = [specific_day]
                print(f"🗓️  Mode: Single day ({self.get_weekday_full_name(specific_day)})")
            else:
                days_to_log = ["Mo", "Tu", "We", "Th", "Fr"]
                print(f"🗓️  Mode: Full work week (Monday-Friday)")
            
            # Step 1: Get dynamic tasks from Jira
            tasks = self.get_jira_issues()
            print(f"📝 Task description: {tasks}")
            
            # Step 2: Setup browser (headless for cronjob, visible for manual testing)
            is_manual = mode in ["today", "day"]
            self.setup_browser(headless=not is_manual)  # Show browser for manual runs
            
            # Step 3: Login to system
            self.login()
            
            # Step 4: Log hours for specified days
            success = self.log_hours_for_week(tasks, days_to_log)
            
            if success:
                print("\n🎉 Work logging completed successfully!")
            else:
                print("\n⚠️  Work logging completed with some errors.")
            
        except Exception as e:
            print(f"❌ Error in main execution: {str(e)}")
            # Take screenshot for debugging
            if self.page:
                error_screenshot = f"screenshots/error_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.page.screenshot(path=error_screenshot)
                print(f"Error screenshot saved as '{error_screenshot}'")
        finally:
            # Always cleanup browser resources
            self.teardown_browser()


def main():
    """Parse command line arguments and run the work logger"""
    parser = argparse.ArgumentParser(
        description="Automated Work Logger with Jira Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python loghours.py                    # Log full week (Mon-Fri) - for cronjob
  python loghours.py --today           # Log only today's hours
  python loghours.py --day Mo          # Log hours for Monday
  python loghours.py --day We          # Log hours for Wednesday
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--today", 
                      action="store_true",
                      help="Log hours only for today (for testing)")
    group.add_argument("--day", 
                      choices=["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
                      help="Log hours for a specific day (Mo, Tu, We, Th, Fr, Sa, Su)")
    
    args = parser.parse_args()
    
    # Create and run the logger
    logger = AutomatedWorkLogger()
    
    if args.today:
        logger.run(mode="today")
    elif args.day:
        logger.run(mode="day", specific_day=args.day)
    else:
        logger.run(mode="week")


if __name__ == "__main__":
    main()
  

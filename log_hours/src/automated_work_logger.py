import base64
import json
import logging
import os
from datetime import datetime

import requests
from playwright.sync_api import sync_playwright

from .constants import WEEKDAYS, BUSINESS_DAYS

logger = logging.getLogger(__name__)


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
            logger.info("📁 Created screenshots directory")

    def parse_day_interval(self, interval):
        """Parse day interval like 'Tu-Fr' and return list of days"""
        try:
            # Split the interval
            parts = interval.split("-")
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid interval format. Expected 'Day-Day' (e.g., 'Tu-Fr'), got '{interval}'"
                )

            start_day, end_day = parts[0].strip(), parts[1].strip()

            # Validate day abbreviations
            if start_day not in WEEKDAYS or end_day not in WEEKDAYS:
                raise ValueError(
                    f"Invalid day abbreviation. Use: {', '.join(WEEKDAYS)}"
                )

            # Map days to indices
            day_to_index = {day: i for i, day in enumerate(WEEKDAYS)}
            start_index = day_to_index[start_day]
            end_index = day_to_index[end_day]

            # Generate the range of days
            days = []
            if start_index <= end_index:
                # Normal range (e.g., Tu-Fr)
                for i in range(start_index, end_index + 1):
                    days.append(WEEKDAYS[i])
            else:
                # Wrap around range (e.g., Fr-Mo)
                for i in range(start_index, len(WEEKDAYS)):
                    days.append(WEEKDAYS[i])
                for i in range(0, end_index + 1):
                    days.append(WEEKDAYS[i])

            return days

        except Exception as e:
            raise ValueError(f"Error parsing interval '{interval}': {str(e)}") from e

    def get_jira_issues(self):
        """Fetch recent Jira issues assigned to the user"""
        # Jira API configuration
        jira_url = os.getenv("JIRA_URL")
        jira_username = os.getenv("JIRA_USERNAME")  # Ticket assignee
        jira_svc_account = os.getenv("JIRA_SVC_ACCOUNT")  # Service account
        jira_api_token = os.getenv("JIRA_API_TOKEN")  # Service account API token
        jira_project = os.getenv("JIRA_PROJECT")

        if not jira_username:
            raise ValueError(
                "JIRA_USERNAME environment variable is required but not set"
            )
        if not jira_svc_account:
            raise ValueError(
                "JIRA_SVC_ACCOUNT environment variable is required but not set"
            )
        if not jira_api_token:
            raise ValueError(
                "JIRA_API_TOKEN environment variable is required but not set"
            )
        if not jira_url:
            raise ValueError("JIRA_URL environment variable is required but not set")
        if not jira_project:
            raise ValueError(
                "JIRA_PROJECT environment variable is required but not set"
            )

        # Create authentication header
        auth_string = f"{jira_svc_account}:{jira_api_token}"
        auth_bytes = auth_string.encode("ascii")
        auth_b64 = base64.b64encode(auth_bytes).decode("ascii")

        # JQL query - same as n8n automation
        jql = f'project = {jira_project} AND assignee = "{jira_username}" AND updated >= -5d AND type IN standardIssueTypes()'

        # API endpoint
        url = f"{jira_url}/rest/api/2/search"

        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        params = {"jql": jql, "maxResults": 10, "fields": "key,summary"}

        logger.info("Querying Jira for recent tickets...")

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Jira API: {str(e)}") from e

        if response.status_code == 401:
            raise ValueError(
                f"Jira authentication failed. Please check your JIRA_USERNAME and JIRA_API_TOKEN credentials."
            )
        elif response.status_code == 403:
            raise ValueError(
                f"Jira access forbidden. Your account may not have permission to access the {jira_project} project."
            )
        elif response.status_code != 200:
            raise ValueError(
                f"Jira API error: {response.status_code} - {response.text}"
            )

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Jira API: {str(e)}") from e

        issues = data.get("issues", [])

        if not issues:
            raise ValueError(
                f"No recent tickets found for {jira_username} in {jira_project} project (last 5 days). Please verify your Jira username and that you have assigned tickets."
            )

        issue_keys = [issue["key"] for issue in issues]
        logger.info(f"Found {len(issue_keys)} tickets: {', '.join(issue_keys)}")

        # Format tasks same as n8n automation
        tasks = f"Daily Standup, Retro, Planning, Refinement, Code Reviews, help to team, and work on the tickets {', '.join(issue_keys)}"
        return tasks

    def get_current_weekday(self):
        """Get current weekday abbreviation"""
        today = datetime.now().weekday()
        return WEEKDAYS[today]

    def get_weekday_full_name(self, day_abbr):
        """Convert day abbreviation to full name"""
        day_names = {
            "Mo": "Monday",
            "Tu": "Tuesday",
            "We": "Wednesday",
            "Th": "Thursday",
            "Fr": "Friday",
            "Sa": "Saturday",
            "Su": "Sunday",
        }
        return day_names.get(day_abbr, day_abbr)

    def setup_browser(self, headless=True):
        """Initialize browser and page"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        # Set viewport size to meet site requirements (at least 1366px)
        self.context = self.browser.new_context(viewport={"width": 1366, "height": 768})
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
        logger.info("Navigating to login page...")
        self.page.goto("https://service-management.coderfull.com")

        # Check if submit button exists (login required)
        submit_buttons = self.page.locator("button[type='submit']:has-text('Login')")
        has_submit = submit_buttons.count() == 1

        if has_submit:
            try:
                logger.info("Login required. Authenticating...")
                # Fill in credentials
                self.page.locator("input[label='Username']").fill(
                    os.getenv("SYSTEM_USERNAME")
                )
                self.page.locator("input[label='Password']").fill(
                    os.getenv("SYSTEM_PASSWORD")
                )
                submit_buttons.click()
                logger.info("Waiting for login to complete...")

                self.page.wait_for_selector(
                    "button:has-text('Log Hours')", timeout=10000
                )
                logger.info("Login successful!")
            except Exception as e:
                logger.error(
                    f"❌ Error logging in: {str(e)}, will try to continue without login..."
                )
        else:
            logger.info("Already logged in.")

    def check_if_hours_logged(self, day):
        """Check if hours are already logged for a specific day"""
        try:
            day_name = self.get_weekday_full_name(day)
            logger.info(
                f"🔍 Checking if hours are already logged for {day_name} ({day})..."
            )

            # Click on the day to see if hours are already logged
            try:
                self.page.locator(f"span:has-text('{day}')").click(timeout=20000)
            except:
                try:
                    self.page.locator(f"text={day}").click(timeout=15000)
                except:
                    logger.warning(f"⚠️  Could not find {day} element to check hours")
                    return False

            # Wait a moment for the form to load
            self.page.wait_for_timeout(1000)

            # Check if task and time inputs have values
            task_input = self.page.locator("input[name='task']")
            time_input = self.page.locator("input[name='time']")

            # Get current values
            task_value = task_input.input_value() if task_input.count() > 0 else ""
            time_value = time_input.input_value() if time_input.count() > 0 else ""

            # Consider hours logged if both task and time have values
            has_hours = bool(task_value.strip() and time_value.strip())

            if has_hours:
                logger.info(
                    f"✅ Hours already logged for {day_name}: {time_value} - {task_value[:50]}..."
                )
                return True
            else:
                logger.info(f"⭕ No hours logged yet for {day_name}")
                return False

        except Exception as e:
            logger.warning(f"⚠️  Error checking hours for {day}: {str(e)}")
            return False

    def log_hours_for_day(self, day, tasks, override=False):
        """Log hours for a specific day"""
        try:
            day_name = self.get_weekday_full_name(day)

            # Check if hours are already logged (unless this is part of the check itself)
            if not override:
                if self.check_if_hours_logged(day):
                    logger.info(
                        f"⏭️  Skipping {day_name} - hours already logged (use --override to relog)"
                    )
                    return True  # Consider this a success since hours exist

            logger.info(f"📝 Logging hours for {day_name} ({day})...")

            # Navigate to the day (click might have happened in check, but ensure we're there)
            try:
                # Try the original selector first
                self.page.locator(f"span:has-text('{day}')").click(timeout=20000)
            except:
                try:
                    # Alternative selector - might be in a different structure
                    self.page.locator(f"text={day}").click(timeout=10000)
                except:
                    # If still not found, take a screenshot for debugging
                    debug_screenshot = f"screenshots/debug_screenshot_{day}.png"
                    self.page.screenshot(path=debug_screenshot)
                    raise Exception(
                        f"Could not find {day} element. Screenshot saved as {debug_screenshot}"
                    )

            # Fill in task details
            self.page.locator("input[name='task']").fill(tasks)
            self.page.locator("input[name='time']").fill("8h")

            # Submit the hours
            self.page.locator("button:has-text('Log Hours')").click()

            # Wait a moment for processing
            self.page.wait_for_timeout(1000)

            action = "Updated" if override else "Logged"
            logger.info(f"✅ Successfully {action.lower()} 8 hours for {day_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Error logging hours for {day}: {str(e)}")
            return False

    def log_hours_for_week(self, tasks, days=None, override=False):
        """Log hours for specified days or full week"""
        if days is None:
            # Default: full work week
            days = BUSINESS_DAYS
        elif isinstance(days, str):
            # Single day passed as string
            days = [days]

        success_count = 0
        total_days = len(days)

        mode_msg = (
            "Override existing hours" if override else "Skip days with existing hours"
        )
        logger.info(f"🔄 Mode: {mode_msg}")

        # Loop through each specified day
        for day in days:
            if self.log_hours_for_day(day, tasks, override=override):
                success_count += 1

            # Brief pause between days (except for the last one)
            if day != days[-1]:
                self.page.wait_for_timeout(500)

        # Take a final screenshot to verify logged hours
        logger.info("📸 Taking verification screenshot...")

        # Wait for loading to complete using multiple strategies
        try:
            logger.info("⏳ Checking for loading spinner...")
            try:
                self.page.wait_for_selector(
                    "svg.tw-animate-spin", timeout=10000, state="hidden"
                )
            except:
                logger.warning("⚠️  Warning: Could not find loading spinner")
                logger.info("⏳ Adding fallback wait...")
                self.page.wait_for_timeout(3000)  # Fallback wait

            logger.info("✅ Page loading completed and UI is ready")
        except Exception as e:
            logger.warning(
                f"⚠️  Warning: Could not fully confirm page loading completion: {str(e)}"
            )
            logger.info("⏳ Adding fallback wait...")
            self.page.wait_for_timeout(3000)  # Fallback wait

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"screenshots/hours_logged_verification_{timestamp}.png"
        self.page.screenshot(path=screenshot_path)
        logger.info(f"Screenshot saved as '{screenshot_path}'")

        # Summary
        if success_count == total_days:
            logger.info(f"✅ Successfully processed hours for all {total_days} day(s)!")
        else:
            logger.warning(
                f"⚠️  Processed hours for {success_count}/{total_days} day(s)"
            )

        return success_count == total_days

    def run(
        self,
        mode="week",
        specific_day=None,
        interval=None,
        headless=True,
        override=False,
    ):
        """Main execution method"""
        try:
            logger.info(f"=== Automated Work Logger Started at {datetime.now()} ===")

            # Determine what days to log
            if mode == "today":
                current_day = self.get_current_weekday()
                if current_day in ["Sa", "Su"]:
                    logger.info(
                        f"🗓️  Today is {self.get_weekday_full_name(current_day)} (weekend). No work hours to log."
                    )
                    return
                days_to_log = [current_day]
                logger.info(
                    f"🗓️  Mode: Single day (Today - {self.get_weekday_full_name(current_day)})"
                )
            elif mode == "day" and specific_day:
                if specific_day not in WEEKDAYS:
                    logger.error(
                        f"❌ Invalid day: {specific_day}. Use {', '.join(WEEKDAYS)}"
                    )
                    return
                days_to_log = [specific_day]
                logger.info(
                    f"🗓️  Mode: Single day ({self.get_weekday_full_name(specific_day)})"
                )
            elif mode == "interval" and interval:
                days_to_log = self.parse_day_interval(interval)
                day_names = [self.get_weekday_full_name(day) for day in days_to_log]
                logger.info(f"🗓️  Mode: Interval ({interval}) - {', '.join(day_names)}")
            else:
                days_to_log = BUSINESS_DAYS
                logger.info("🗓️  Mode: Full work week (Monday-Friday)")

            # Step 1: Get dynamic tasks from Jira
            tasks = self.get_jira_issues()
            logger.info(f"📝 Task description: {tasks}")

            # Step 2: Setup browser with specified headless mode
            browser_mode = "headless" if headless else "visible"
            logger.info(f"🌐 Browser mode: {browser_mode}")
            self.setup_browser(headless=headless)

            # Step 3: Login to system
            self.login()

            # Step 4: Log hours for specified days
            success = self.log_hours_for_week(tasks, days_to_log, override=override)

            if success:
                logger.info("🎉 Work logging completed successfully!")
            else:
                logger.warning("⚠️  Work logging completed with some errors.")

        except Exception as e:
            logger.error(f"❌ Error in main execution: {str(e)}")
            # Take screenshot for debugging
            if self.page:
                error_screenshot = f"screenshots/error_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.page.screenshot(path=error_screenshot)
                logger.error(f"Error screenshot saved as '{error_screenshot}'")
        finally:
            # Always cleanup browser resources
            self.teardown_browser()

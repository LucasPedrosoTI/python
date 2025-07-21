# Automated Work Logger 🤖

A Python automation tool that integrates with Jira to dynamically fetch your recent tickets and automatically log work hours for the entire week. Perfect for those who need to log hours consistently across all weekdays.

## Features ✨

- **🎯 Dynamic Jira Integration**: Automatically queries your assigned tickets from the last 5 days
- **📅 Full Week Logging**: Logs 8 hours for Monday through Friday
- **🤖 Automated Scheduling**: Runs every Friday at 10am via cronjob
- **📸 Verification Screenshots**: Takes screenshots to verify successful logging
- **🔄 Headless Operation**: Runs silently in the background
- **🛡️ Error Handling**: Robust error handling with fallback options

## Quick Start 🚀

### 1. Install Dependencies

```bash
# Install Python dependencies
poetry install

# Install Playwright browsers
poetry run playwright install chromium
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# System login credentials for work logging platform
SYSTEM_USERNAME=your_username_here
SYSTEM_PASSWORD=your_password_here

# Jira API credentials for dynamic task fetching
JIRA_URL=https://your_jira_url.atlassian.net
JIRA_USERNAME=your_email@mail.com
JIRA_API_TOKEN=your_jira_api_token_here
JIRA_PROJECT=your_jira_project_here
```

### 3. Get Your Jira API Token

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Label it "Work Logger" and copy the token
4. Add it to your `.env` file as `JIRA_API_TOKEN`

### 4. Set Up Automated Scheduling

```bash
# Run the setup script to configure the cronjob
python src/setup_cronjob.py
```

This will:
- ✅ Check your environment configuration
- ⚙️ Set up a cronjob to run every Friday at 10am
- 📁 Configure logging to `cronjob.log`

## Manual Usage 📋

### Testing Modes (New! 🆕)

The script supports flexible testing with different modes:

```bash
# 🧪 Test with today only
python src/loghours.py --today

# 🎯 Test a specific day
python src/loghours.py --day Mo     # Monday
python src/loghours.py --day We     # Wednesday  
python src/loghours.py --day Fr     # Friday

# 📅 Full week (default - for cronjob)
python src/loghours.py

# ❓ See all options
python src/loghours.py --help
```

### What Each Mode Does

**🧪 Today Mode (`--today`)**:
- Perfect for testing and development
- Shows browser window so you can watch it work
- Logs hours only for the current day
- Automatically skips weekends
- Quick and safe for testing

**🎯 Specific Day Mode (`--day [Mo|Tu|We|Th|Fr|Sa|Su]`)**:
- Test any specific day
- Shows browser window for visibility
- Great for testing edge cases
- Useful for catching up missed days

**📅 Full Week Mode (default)**:
- Production mode for cronjob automation
- Runs headless (invisible browser)
- Logs Monday through Friday
- Takes longer but covers the entire week

### Complete Process

When you run the automation, it will:
1. 📡 Query Jira for your recent tickets (defined project, updated in last 5 days)
2. 📝 Format task description: "Daily Standup, Retro, Planning, Refinement, Code Reviews, help to team, and work on the tickets PROJECT-XXX, PROJECT-YYY"
3. 🕐 Log 8 hours for each specified day
4. 📸 Take a verification screenshot

## Task Description Format 📝

The automation generates task descriptions like:

```
Daily Standup, Retro, Planning, Refinement, Code Reviews, help to team, and work on the tickets PROJECT-830, PROJECT-804, PROJECT-765, PROJECT-725, PROJECT-270
```

## Monitoring & Troubleshooting 🔧

### Check Cronjob Status
```bash
# View current cronjobs
crontab -l

# Check recent logs
tail -f cronjob.log

# Test manually (recommended testing approach)
python src/loghours.py --today    # Quick test with today only
python src/loghours.py --day We   # Test specific day
python src/loghours.py            # Full week test
```

### Common Issues

**Jira API Error**: Check your API token and username in `.env`
**Login Failed**: Verify `SYSTEM_USERNAME` and `SYSTEM_PASSWORD`
**Element Not Found**: The website UI may have changed - check debug screenshots

### Screenshots

The automation saves timestamped screenshots:
- `hours_logged_verification_YYYYMMDD_HHMMSS.png` - Success verification
- `error_screenshot_YYYYMMDD_HHMMSS.png` - Error debugging
- `debug_screenshot_[Day].png` - Day-specific debugging

## Project Structure 📁

```
log_hours/
├── src/
│   ├── loghours.py           # Main automation script
│   ├── setup_cronjob.py      # Cronjob configuration helper
│   └── __init__.py
├── pyproject.toml            # Dependencies and configuration
├── poetry.lock              # Locked dependencies
├── .env                     # Environment variables (create this)
├── cronjob.log              # Automation logs (auto-created)
└── README.md                # This file
```

## Development 🛠️

### Running Tests
```bash
poetry run pytest src/loghours.py -v
```

### Debugging Tips
- **Use `--today` for development**: Shows browser window and only affects one day
- **Check screenshots**: All modes save verification screenshots
- **Watch the console**: Detailed logging shows exactly what's happening

## Advanced Configuration ⚙️

### Custom Jira Query
You can modify the JQL query in `src/loghours.py`:
```python
jql = f'project = YOUR_PROJECT AND assignee = "{jira_username}" AND updated >= -5d'
```

### Different Schedule
Modify the cron expression in `src/setup_cronjob.py`:
```python
# Current: Every Friday at 10am
cron_command = f"0 10 * * 5 ..."

# Examples:
# Every day at 10am: "0 10 * * *"
# Every Monday at 9am: "0 9 * * 1"
# Twice a week: "0 10 * * 1,5"
```

## Security Notes 🔐

- Never commit your `.env` file to version control
- Use API tokens instead of passwords where possible
- Regularly rotate your Jira API tokens
- Run with headless mode in production (default)

## License 📄

This project is for personal automation use. Ensure compliance with your company's automation policies.

---

**Made with ❤️ for automated productivity** 
#!/usr/bin/env python3
"""
Setup script for configuring the Automated Work Logger cronjob.
This script helps configure the system to run the work logger every Friday at 9am.
"""

import os
import subprocess
import sys
from pathlib import Path

def get_project_root():
    """Get the absolute path to the project root directory"""
    return Path(__file__).parent.parent.absolute()

def get_python_path():
    """Get the Python executable path"""
    return sys.executable

def create_cronjob_command():
    """Create the cronjob command"""
    project_root = get_project_root()
    python_path = get_python_path()
    script_path = project_root / "src" / "loghours.py"
    log_path = project_root / "cronjob.log"
    
    # Create the cron command
    # 0 10 * * 5 means: minute=0, hour=10, any day of month, any month, day 5 (Friday)
    cron_command = f"0 10 * * 5 cd {project_root} && {python_path} {script_path} >> {log_path} 2>&1"
    
    return cron_command

def setup_cronjob():
    """Setup the cronjob for automated work logging"""
    print("=== Automated Work Logger Cronjob Setup ===\n")
    
    # Get current crontab
    try:
        current_crontab = subprocess.run(['crontab', '-l'], 
                                       capture_output=True, 
                                       text=True, 
                                       check=False)
        existing_jobs = current_crontab.stdout if current_crontab.returncode == 0 else ""
    except FileNotFoundError:
        print("Error: crontab command not found. Please install cron.")
        return False
    
    # Create the new cron command
    cron_command = create_cronjob_command()
    job_comment = "# Automated Work Logger - Runs every Friday at 9am"
    
    # Check if the job already exists
    if "loghours.py" in existing_jobs:
        print("⚠️  A work logger cronjob already exists.")
        response = input("Do you want to replace it? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return False
        
        # Remove existing work logger jobs
        lines = existing_jobs.split('\n')
        filtered_lines = [line for line in lines 
                         if 'loghours.py' not in line and 
                            'Automated Work Logger' not in line]
        existing_jobs = '\n'.join(filtered_lines).strip()
    
    # Add the new job
    if existing_jobs:
        new_crontab = f"{existing_jobs}\n{job_comment}\n{cron_command}"
    else:
        new_crontab = f"{job_comment}\n{cron_command}"
    
    # Write the new crontab
    try:
        process = subprocess.run(['crontab', '-'], 
                               input=new_crontab, 
                               text=True, 
                               check=True)
        print("✅ Cronjob successfully configured!")
        print(f"📅 The work logger will run every Friday at 10:00 AM")
        print(f"📁 Logs will be saved to: {get_project_root()}/cronjob.log")
        print(f"🔧 Command: {cron_command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error setting up cronjob: {e}")
        return False

def show_manual_setup():
    """Show manual cronjob setup instructions"""
    print("\n=== Manual Cronjob Setup ===")
    print("If automatic setup failed, you can manually add this cronjob:")
    print(f"\n1. Run: crontab -e")
    print("2. Add these lines:")
    print(f"   # Automated Work Logger - Runs every Friday at 10am")
    print(f"   {create_cronjob_command()}")
    print("3. Save and exit")

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...")
    
    issues = []
    
    # Check if .env file exists
    env_file = get_project_root() / ".env"
    if not env_file.exists():
        issues.append("❌ .env file not found")
    else:
        print("✅ .env file found")
    
    # Check required environment variables
    required_vars = [
        'SYSTEM_USERNAME',
        'SYSTEM_PASSWORD',
        'JIRA_USERNAME',
        'JIRA_API_TOKEN',
        'JIRA_URL',
        'JIRA_PROJECT'
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            issues.append(f"❌ Environment variable {var} not set")
        else:
            print(f"✅ {var} configured")
    
    if issues:
        print("\n⚠️  Environment issues found:")
        for issue in issues:
            print(f"   {issue}")
        print("\nPlease create a .env file with the following variables:")
        print("   SYSTEM_USERNAME=your_username")
        print("   SYSTEM_PASSWORD=your_password")
        print("   JIRA_USERNAME=your_email@mail.com")
        print("   JIRA_API_TOKEN=your_jira_api_token")
        print("   JIRA_URL=https://your_jira_url.atlassian.net")
        print("   JIRA_PROJECT=your_jira_project")
        return False
    else:
        print("✅ Environment properly configured!")
        return True

def main():
    """Main setup function"""
    print("🤖 Automated Work Logger Setup\n")
    
    # Check environment first
    if not check_environment():
        print("\n❌ Please fix environment issues before setting up cronjob.")
        return
    
    print("\nThis will set up a cronjob to automatically log your work hours")
    print("every Friday at 10:00 AM by:")
    print("• Querying Jira for your recent tickets")
    print("• Logging 8 hours for Monday-Friday")
    print("• Taking a screenshot for verification")
    
    response = input("\nContinue with setup? (Y/n): ").strip().lower()
    if response == 'n':
        print("Setup cancelled.")
        return
    
    # Setup cronjob
    if setup_cronjob():
        print("\n🎉 Setup complete! Your work hours will be automatically logged every Friday.")
        print("\n📝 Next steps:")
        print("• Test the script manually: python src/loghours.py")
        print("• Check logs: tail -f cronjob.log")
        print("• View current cronjobs: crontab -l")
    else:
        show_manual_setup()

if __name__ == "__main__":
    main() 
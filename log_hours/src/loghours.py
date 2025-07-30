# Automated Work Logger - Migrated from Selenium to Playwright with Jira Integration
import argparse
import logging

from dotenv import load_dotenv

from .automated_work_logger import AutomatedWorkLogger
from .constants import WEEKDAYS

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    """Parse command line arguments and run the work logger"""
    parser = argparse.ArgumentParser(
        description="Automated Work Logger with Jira Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python loghours.py                           # Log full week (Mon-Fri) - for cronjob
  python loghours.py -t/--today                 # Log only today's hours
  python loghours.py -d Mo/--day Mo             # Log hours for Monday
  python loghours.py -d We/--day We             # Log hours for Wednesday
  python loghours.py -i Tu-Fr/--interval Tu-Fr  # Log hours for Tuesday through Friday
  python loghours.py -i Mo-We          # Log hours for Monday through Wednesday
  python loghours.py -i Fr-Mo          # Log hours for Friday through Monday (wrap around)
  python loghours.py -t --override        # Log today's hours, overriding existing entries
  python loghours.py -d Fr -v    # Log Friday's hours with visible browser
  python loghours.py -o                        # Log full week, overriding any existing hours
        """,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-t",
        "--today",
        action="store_true",
        help="Log hours only for today (for testing)",
    )
    group.add_argument(
        "-d",
        "--day",
        choices=WEEKDAYS,
        help=f"Log hours for a specific day ({', '.join(WEEKDAYS)})",
    )
    group.add_argument(
        "-i",
        "--interval",
        type=str,
        help="Log hours for a range of days (e.g., 'Tu-Fr', 'Mo-We')",
    )

    # Override argument
    parser.add_argument(
        "-o",
        "--override",
        action="store_true",
        help="Override existing hours (default: skip days with existing hours)",
    )

    # Browser mode arguments
    browser_group = parser.add_mutually_exclusive_group()
    browser_group.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default for all modes)",
    )
    browser_group.add_argument(
        "-v",
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Run browser in visible mode (for local debugging)",
    )

    # Logging level argument
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Set logging level based on argument
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Create and run the logger
    work_logger = AutomatedWorkLogger()

    try:
        if args.today:
            work_logger.run(
                mode="today", headless=args.headless, override=args.override
            )
        elif args.day:
            work_logger.run(
                mode="day",
                specific_day=args.day,
                headless=args.headless,
                override=args.override,
            )
        elif args.interval:
            work_logger.run(
                mode="interval",
                interval=args.interval,
                headless=args.headless,
                override=args.override,
            )
        else:
            work_logger.run(mode="week", headless=args.headless, override=args.override)
    except ValueError as e:
        logger.error(f"❌ {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    main()

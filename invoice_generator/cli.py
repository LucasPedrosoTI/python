#!/usr/bin/env python3
"""
Invoice Generator CLI
A command-line interface for generating PDF invoices.
"""

import argparse
import sys
import os
from datetime import datetime

# Add the current directory to the path so we can import our modules
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from invoice_generator import InvoiceGenerator


def get_default_output_dir():
    """Get the default output directory, handling both development and bundled environments."""
    if getattr(sys, 'frozen', False):
        # Running in a bundled executable
        return os.path.join(os.path.dirname(sys.executable), 'output')
    else:
        # Running in development
        return os.path.join(os.path.dirname(__file__), 'output')


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate PDF invoices for monthly work hours",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Generate invoice for current month
  %(prog)s --year 2024 --month 1     # Generate invoice for January 2024
  %(prog)s --hours-per-day 6         # Generate with 6 hours per day
  %(prog)s --output ./invoices       # Save to custom directory
        """
    )
    
    parser.add_argument('--year', '-y', type=int, 
                       help='Invoice year (default: current year)')
    parser.add_argument('--month', '-m', type=int, choices=range(1, 13),
                       help='Invoice month 1-12 (default: previous month)')
    parser.add_argument('--hours-per-day', '-H', type=int, default=8,
                       help='Hours per business day (default: 8)')
    parser.add_argument('--output', '-o', type=str,
                       help='Output directory (default: ./output)')
    parser.add_argument('--version', action='version', version='Invoice Generator 1.0')
    
    args = parser.parse_args()
    
    try:
        print("🧾 Invoice Generator")
        print("=" * 40)
        
        # Create invoice generator
        generator = InvoiceGenerator(
            year=args.year,
            month=args.month,
            hours_per_day=args.hours_per_day
        )
        
        print(f"📅 Generating invoice for: {generator.year}-{generator.month:02d}")
        print(f"⏰ Hours per day: {generator.hours_calculator.hours_per_day}")
        print(f"📊 Total hours: {generator.monthly_hours}")
        print(f"💰 Total amount: ${generator.total_amount:,.2f}")
        
        # Use provided output directory or default
        output_dir = args.output if args.output else get_default_output_dir()
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate the invoice
        output_file = generator.generate_invoice(output_dir)
        
        print(f"✅ Invoice generated successfully!")
        print(f"📁 File saved to: {os.path.abspath(output_file)}")
        
        # Try to open the file (Windows)
        if sys.platform.startswith('win'):
            try:
                os.startfile(output_file)
                print("📖 Opening PDF...")
            except:
                pass
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating invoice: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 
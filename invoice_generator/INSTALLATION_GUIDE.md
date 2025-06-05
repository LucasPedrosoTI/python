# Invoice Generator - Installation Guide

## 🚀 Quick Setup (Executable Version)

### Prerequisites
- Windows 10/11
- A `.env` file with your configuration (see Configuration section below)

### Installation Steps

1. **Copy the executable**:
   ```cmd
   mkdir C:\InvoiceGenerator
   copy dist\InvoiceGenerator.exe C:\InvoiceGenerator\
   ```

2. **Create desktop shortcuts**:
   ```powershell
   powershell -ExecutionPolicy Bypass -File create_desktop_shortcut.ps1
   ```

3. **Set up your configuration** (see Configuration section below)

## ⚙️ Configuration

Create a `.env` file in the `C:\InvoiceGenerator\` directory with your business information:

```env
# Client Information
CLIENT_NAME=Your Client Company Name
CLIENT_ADDRESS=Client Address Line 1\nClient Address Line 2
CLIENT_EMAIL=client@company.com
CLIENT_TAX_ID=Tax ID: 12345678

# Company Information (Your Business)
COMPANY_NAME=Your Company Name
COMPANY_ADDRESS=Your Address Line 1
COMPANY_CITY_STATE=Your City, State ZIP
COMPANY_COUNTRY=Your Country
COMPANY_EMAIL=your-email@company.com

# Invoice Settings
HOURLY_RATE=50
FONT_FAMILY=Courier
```

## 🖥️ Usage

### Using the Desktop Shortcut
- **Double-click** the "Invoice Generator" shortcut on your desktop
- This will generate an invoice for the current month with default settings

### Using Command Line
Open Command Prompt and use these commands:

```cmd
# Generate invoice for current month
C:\InvoiceGenerator\InvoiceGenerator.exe

# Generate invoice for specific month/year
C:\InvoiceGenerator\InvoiceGenerator.exe --year 2024 --month 3

# Generate with custom hours per day
C:\InvoiceGenerator\InvoiceGenerator.exe --hours-per-day 6

# Save to custom directory
C:\InvoiceGenerator\InvoiceGenerator.exe --output C:\MyInvoices

# View all options
C:\InvoiceGenerator\InvoiceGenerator.exe --help
```

### Command Line Options
- `--year, -y`: Invoice year (default: current year)
- `--month, -m`: Invoice month 1-12 (default: previous month)
- `--hours-per-day, -H`: Hours per business day (default: 8)
- `--output, -o`: Output directory (default: ./output)
- `--version`: Show version information
- `--help`: Show help message

## 📁 File Locations

- **Executable**: `C:\InvoiceGenerator\InvoiceGenerator.exe`
- **Configuration**: `C:\InvoiceGenerator\.env`
- **Generated PDFs**: `C:\InvoiceGenerator\output\` (by default)
- **Desktop Shortcut**: `%USERPROFILE%\Desktop\Invoice Generator.lnk`
- **Start Menu**: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Invoice Generator.lnk`

## 🧮 How It Works

The Invoice Generator automatically:
1. Calculates business days (Monday-Friday) for the specified month
2. Multiplies business days × hours per day to get total hours
3. Calculates total amount (total hours × hourly rate)
4. Generates a professional PDF invoice
5. Automatically opens the PDF when complete

### Example Calculations
- **January 2024**: 23 business days × 8 hours = 184 hours
- **February 2024**: 21 business days × 8 hours = 168 hours
- **March 2024**: 21 business days × 8 hours = 168 hours

## 🔧 Troubleshooting

### "Error generating invoice: [Errno 2] No such file or directory"
- Make sure you have a `.env` file in `C:\InvoiceGenerator\`
- Check that all required environment variables are set

### "ModuleNotFoundError" or Import Errors
- The executable should be self-contained. If you see these errors, try rebuilding:
  ```cmd
  pyinstaller --onefile --name "InvoiceGenerator" cli.py --clean
  ```

### PDF doesn't open automatically
- This is normal on some systems. The PDF is still generated in the output directory
- Navigate to the output folder and open the PDF manually

### Configuration not loading
- Ensure the `.env` file is in the same directory as the executable
- Check that there are no syntax errors in your `.env` file
- Use the exact format shown in the Configuration section

## 📋 Business Day Calculation

The tool calculates business days as Monday through Friday, excluding weekends. It handles:
- Month boundaries correctly
- Leap years
- Different month lengths
- Year transitions (December to January)

## 💡 Tips

1. **Monthly Workflow**: Run the tool at the beginning of each month for the previous month
2. **Backup Configuration**: Keep a backup of your `.env` file
3. **Custom Output**: Use `--output` to organize invoices by year or client
4. **Batch Processing**: You can run multiple commands to generate several months at once

## 🆘 Support

If you encounter issues:
1. Check this guide first
2. Verify your `.env` configuration
3. Test with the command line version to see detailed error messages
4. Check the Windows Event Viewer for system-level errors

## 🔄 Updates

To update the Invoice Generator:
1. Replace `C:\InvoiceGenerator\InvoiceGenerator.exe` with the new version
2. Keep your existing `.env` file
3. Shortcuts will continue to work with the new version 
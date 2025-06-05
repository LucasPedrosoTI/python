from fpdf import FPDF
from datetime import datetime
try:
    from invoice_generator.monthly_hours_calculator import MonthlyHoursCalculator
except ImportError:
    from monthly_hours_calculator import MonthlyHoursCalculator
from os import path
import os
from dotenv import load_dotenv


class InvoiceGenerator:
    """
    A class to generate invoices in PDF format.
    Handles configuration loading, invoice data calculation, and PDF generation.
    """
    
    def __init__(self, year=None, month=None, hours_per_day=8):
        """
        Initialize the InvoiceGenerator with configuration and invoice data.
        
        Args:
            year (int, optional): Invoice year. Defaults to current year.
            month (int, optional): Invoice month. Defaults to previous month.
            hours_per_day (int, optional): Hours per business day. Defaults to 8.
        """
        # Load environment variables
        load_dotenv()
        
        # Load configuration from environment variables
        self._load_config()
        
        # Initialize the hours calculator
        self.hours_calculator = MonthlyHoursCalculator(hours_per_day)
        
        # Set invoice date
        now = datetime.now()
        self.year = year or now.year
        self.month = month or (now.month - 1 if now.month > 1 else 12)
        
        # Calculate invoice data
        self._calculate_invoice_data()
        
        # Initialize PDF
        self.pdf = None
    
    def _load_config(self):
        """Load configuration from environment variables."""
        # Client configuration
        self.client_name = os.getenv('CLIENT_NAME')
        self.client_address = os.getenv('CLIENT_ADDRESS')
        self.client_email = os.getenv('CLIENT_EMAIL')
        self.client_tax_id = os.getenv('CLIENT_TAX_ID')
        
        # Company configuration
        self.company_name = os.getenv('COMPANY_NAME')
        self.company_address = os.getenv('COMPANY_ADDRESS')
        self.company_city_state = os.getenv('COMPANY_CITY_STATE')
        self.company_country = os.getenv('COMPANY_COUNTRY')
        self.company_email = os.getenv('COMPANY_EMAIL')
        
        # Invoice configuration
        self.font_family = os.getenv('FONT_FAMILY', 'Courier')
        self.hourly_rate = int(os.getenv('HOURLY_RATE', '16'))
    
    def _calculate_invoice_data(self):
        """Calculate invoice-specific data like dates, hours, and totals."""
        self.invoice_number = f"{self.year}-{self.month:02d}"
        self.invoice_date = f"{self.invoice_number}-01"
        
        self.monthly_hours = self.hours_calculator.calc_monthly_hours(self.year, self.month)
        self.total_amount = self.hourly_rate * self.monthly_hours
    
    def _create_pdf(self):
        """Initialize a new PDF document."""
        self.pdf = FPDF()
        self.pdf.add_page()
    
    def _add_header(self):
        """Add the invoice header."""
        self.pdf.set_font(self.font_family, "B", 16)
        self.pdf.cell(200, 10, "Invoice", ln=True, align="C")
    
    def _add_company_info(self):
        """Add company information section."""
        self.pdf.set_font(self.font_family, "B", 12)
        self.pdf.cell(100, 10, "INVOICE FROM:", ln=True)
        
        self.pdf.set_font(self.font_family, "", 12)
        self.pdf.cell(100, 10, self.company_name, ln=True)
        self.pdf.cell(100, 10, self.company_address, ln=True)
        self.pdf.cell(100, 10, self.company_city_state, ln=True)
        self.pdf.cell(100, 10, self.company_country, ln=True)
        self.pdf.cell(100, 10, self.company_email, ln=True)
        
        self.pdf.ln(10)
    
    def _add_client_info(self):
        """Add client information section."""
        self.pdf.set_font(self.font_family, "B", 12)
        self.pdf.cell(100, 10, "INVOICE TO:", ln=True)
        
        self.pdf.set_font(self.font_family, "", 12)
        self.pdf.multi_cell(0, 10, 
            f"{self.client_name}\n"
            f"{self.client_address}\n"
            f"{self.client_tax_id}\n"
            f"{self.client_email}"
        )
        
        self.pdf.ln(10)
    
    def _add_invoice_details(self):
        """Add invoice number and date."""
        self.pdf.cell(100, 10, f"INVOICE NUMBER: {self.invoice_number}", ln=True)
        self.pdf.cell(100, 10, f"INVOICE DATE: {self.invoice_date}", ln=True)
        
        self.pdf.ln(10)
    
    def _add_amounts(self):
        """Add amount calculations section."""
        self.pdf.cell(100, 10, f"AMOUNT DUE: $ {self.total_amount:,.2f}", ln=True)
        self.pdf.cell(100, 10, f"SUBTOTAL: $ {self.total_amount:,.2f}", ln=True)
        self.pdf.cell(100, 10, "TAX (0.0%): $ 0,00", ln=True)
        self.pdf.cell(100, 10, f"TOTAL: $ {self.total_amount:,.2f}", ln=True)
        
        self.pdf.ln(10)
    
    def _add_items_table(self):
        """Add the items table."""
        # Table header
        self.pdf.cell(40, 10, "Item", border=1)
        self.pdf.cell(80, 10, "Description", border=1)
        self.pdf.cell(30, 10, "Quantity", border=1)
        self.pdf.cell(40, 10, "Unit Cost", border=1, ln=True)
        
        # Table row
        self.pdf.cell(40, 10, "01", border=1)
        self.pdf.cell(80, 10, "IT SERVICES", border=1)
        self.pdf.cell(30, 10, "1,0", border=1)
        self.pdf.cell(40, 10, f"$ {self.total_amount:,.2f}", border=1)
    
    def generate_invoice(self, output_dir=None):
        """
        Generate the complete invoice PDF.
        
        Args:
            output_dir (str, optional): Output directory. Defaults to './output'.
            
        Returns:
            str: Path to the generated PDF file.
        """
        # Create PDF
        self._create_pdf()
        
        # Add all sections
        self._add_header()
        self._add_company_info()
        self._add_client_info()
        self._add_invoice_details()
        self._add_amounts()
        self._add_items_table()
        
        # Save PDF
        if output_dir is None:
            output_dir = path.join(path.dirname(__file__), "output")
        
        filename = f"invoice_{self.invoice_number}.pdf"
        output_path = path.join(output_dir, filename)
        
        self.pdf.output(output_path)
        
        return output_path


# For backward compatibility and direct script execution
if __name__ == "__main__":
    generator = InvoiceGenerator()
    output_file = generator.generate_invoice()
    print(f"Invoice generated: {output_file}")
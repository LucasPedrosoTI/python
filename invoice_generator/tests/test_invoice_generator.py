import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import os
from datetime import datetime
from fpdf import FPDF

# Import the module under test
from invoice_generator.invoice_generator import InvoiceGenerator


class TestInvoiceGenerator(unittest.TestCase):
    """Test cases for the InvoiceGenerator class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock environment variables
        self.mock_env_vars = {
            'CLIENT_NAME': 'Test Client Corp',
            'CLIENT_ADDRESS': '123 Client St, Client City, CC 12345',
            'CLIENT_EMAIL': 'client@testcorp.com',
            'CLIENT_TAX_ID': 'TAX123456789',
            'COMPANY_NAME': 'Test Company LLC',
            'COMPANY_ADDRESS': '456 Company Ave',
            'COMPANY_CITY_STATE': 'Company City, CS 67890',
            'COMPANY_COUNTRY': 'Test Country',
            'COMPANY_EMAIL': 'billing@testcompany.com',
            'FONT_FAMILY': 'Arial',
            'HOURLY_RATE': '25'
        }
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    @patch('invoice_generator.invoice_generator.datetime')
    def test_init_with_defaults(self, mock_datetime, mock_getenv, mock_load_dotenv):
        """Test initialization with default year and month."""
        # Setup mocks
        mock_now = Mock()
        mock_now.year = 2024
        mock_now.month = 3
        mock_datetime.now.return_value = mock_now
        
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        # Create instance
        generator = InvoiceGenerator()
        
        # Assertions
        mock_load_dotenv.assert_called_once()
        self.assertEqual(generator.year, 2024)
        self.assertEqual(generator.month, 2)  # Previous month
        self.assertEqual(generator.client_name, 'Test Client Corp')
        self.assertEqual(generator.hourly_rate, 25)
        # February 2024 has 21 business days * 8 hours = 168 hours
        self.assertEqual(generator.monthly_hours, 168)
        self.assertEqual(generator.total_amount, 4200)  # 25 * 168
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    @patch('invoice_generator.invoice_generator.datetime')
    def test_init_with_january_defaults_to_december_previous_year(self, mock_datetime, mock_getenv, mock_load_dotenv):
        """Test initialization when current month is January, should default to December of previous year."""
        # Setup mocks
        mock_now = Mock()
        mock_now.year = 2024
        mock_now.month = 1
        mock_datetime.now.return_value = mock_now
        
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        # Create instance
        generator = InvoiceGenerator()
        
        # Assertions
        self.assertEqual(generator.year, 2024)
        self.assertEqual(generator.month, 12)  # Previous month wraps to December
        # December 2024 has 22 business days * 8 hours = 176 hours
        self.assertEqual(generator.monthly_hours, 176)
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_init_with_custom_year_month(self, mock_getenv, mock_load_dotenv):
        """Test initialization with custom year and month."""
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        # Create instance with custom values
        generator = InvoiceGenerator(year=2023, month=5)
        
        # Assertions
        self.assertEqual(generator.year, 2023)
        self.assertEqual(generator.month, 5)
        # May 2023 has 23 business days * 8 hours = 184 hours
        self.assertEqual(generator.monthly_hours, 184)
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_init_with_custom_hours_per_day(self, mock_getenv, mock_load_dotenv):
        """Test initialization with custom hours per day."""
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        # Create instance with custom hours per day
        generator = InvoiceGenerator(year=2024, month=1, hours_per_day=6)
        
        # Assertions
        self.assertEqual(generator.year, 2024)
        self.assertEqual(generator.month, 1)
        # January 2024 has 23 business days * 6 hours = 138 hours
        self.assertEqual(generator.monthly_hours, 138)
        self.assertEqual(generator.total_amount, 3450)  # 25 * 138
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_load_config_with_defaults(self, mock_getenv, mock_load_dotenv):
        """Test configuration loading with default values."""
        # Mock getenv to return None for most values, defaults should be used
        def mock_getenv_func(key, default=None):
            if key == 'FONT_FAMILY':
                return default or 'Courier'
            elif key == 'HOURLY_RATE':
                return default or '16'
            return None
        
        mock_getenv.side_effect = mock_getenv_func
        
        generator = InvoiceGenerator(year=2024, month=1)
        
        # Check defaults are applied
        self.assertEqual(generator.font_family, 'Courier')
        self.assertEqual(generator.hourly_rate, 16)
        self.assertIsNone(generator.client_name)
        self.assertIsNone(generator.company_name)
        # January 2024 has 23 business days * 8 hours = 184 hours
        self.assertEqual(generator.monthly_hours, 184)
        self.assertEqual(generator.total_amount, 2944)  # 16 * 184
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_calculate_invoice_data(self, mock_getenv, mock_load_dotenv):
        """Test invoice data calculation."""
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        generator = InvoiceGenerator(year=2024, month=3)
        
        # Assertions
        self.assertEqual(generator.invoice_number, "2024-03")
        self.assertEqual(generator.invoice_date, "2024-03-01")
        # March 2024 has 21 business days * 8 hours = 168 hours
        self.assertEqual(generator.monthly_hours, 168)
        self.assertEqual(generator.total_amount, 4200)  # 25 * 168
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_create_pdf(self, mock_getenv, mock_load_dotenv):
        """Test PDF creation."""
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        generator = InvoiceGenerator(year=2024, month=1)
        generator._create_pdf()
        
        # Check PDF is created and configured
        self.assertIsInstance(generator.pdf, FPDF)
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_add_header(self, mock_getenv, mock_load_dotenv):
        """Test adding header to PDF."""
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        generator = InvoiceGenerator(year=2024, month=1)
        generator._create_pdf()
        
        # Mock PDF methods
        generator.pdf.set_font = Mock()
        generator.pdf.cell = Mock()
        
        generator._add_header()
        
        # Verify font and cell calls
        generator.pdf.set_font.assert_called_with('Arial', "B", 16)
        generator.pdf.cell.assert_called_with(200, 10, "Invoice", ln=True, align="C")
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_add_company_info(self, mock_getenv, mock_load_dotenv):
        """Test adding company information to PDF."""
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        generator = InvoiceGenerator(year=2024, month=1)
        generator._create_pdf()
        
        # Mock PDF methods
        generator.pdf.set_font = Mock()
        generator.pdf.cell = Mock()
        generator.pdf.ln = Mock()
        
        generator._add_company_info()
        
        # Verify company info is added
        self.assertIn(unittest.mock.call('Arial', "B", 12), generator.pdf.set_font.call_args_list)
        self.assertIn(unittest.mock.call('Arial', "", 12), generator.pdf.set_font.call_args_list)
        generator.pdf.ln.assert_called_with(10)
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_add_client_info(self, mock_getenv, mock_load_dotenv):
        """Test adding client information to PDF."""
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        generator = InvoiceGenerator(year=2024, month=1)
        generator._create_pdf()
        
        # Mock PDF methods
        generator.pdf.set_font = Mock()
        generator.pdf.cell = Mock()
        generator.pdf.multi_cell = Mock()
        generator.pdf.ln = Mock()
        
        generator._add_client_info()
        
        # Verify client info is added
        self.assertIn(unittest.mock.call('Arial', "B", 12), generator.pdf.set_font.call_args_list)
        self.assertIn(unittest.mock.call('Arial', "", 12), generator.pdf.set_font.call_args_list)
        generator.pdf.cell.assert_called_with(100, 10, "INVOICE TO:", ln=True)
        generator.pdf.ln.assert_called_with(10)
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_add_invoice_details(self, mock_getenv, mock_load_dotenv):
        """Test adding invoice details to PDF."""
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        generator = InvoiceGenerator(year=2024, month=6)
        generator._create_pdf()
        
        # Mock PDF methods
        generator.pdf.cell = Mock()
        generator.pdf.ln = Mock()
        
        generator._add_invoice_details()
        
        # Verify invoice details are added
        expected_calls = [
            unittest.mock.call(100, 10, "INVOICE NUMBER: 2024-06", ln=True),
            unittest.mock.call(100, 10, "INVOICE DATE: 2024-06-01", ln=True)
        ]
        generator.pdf.cell.assert_has_calls(expected_calls)
        generator.pdf.ln.assert_called_with(10)
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_add_amounts(self, mock_getenv, mock_load_dotenv):
        """Test adding amounts to PDF."""
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        generator = InvoiceGenerator(year=2024, month=1)
        generator._create_pdf()
        
        # Mock PDF methods
        generator.pdf.cell = Mock()
        generator.pdf.ln = Mock()
        
        generator._add_amounts()
        
        # Verify amounts are added (January 2024: 23 business days * 8 hours * $25 = $4600)
        expected_total = 4600
        expected_calls = [
            unittest.mock.call(100, 10, f"AMOUNT DUE: $ {expected_total:,.2f}", ln=True),
            unittest.mock.call(100, 10, f"SUBTOTAL: $ {expected_total:,.2f}", ln=True),
            unittest.mock.call(100, 10, "TAX (0.0%): $ 0,00", ln=True),
            unittest.mock.call(100, 10, f"TOTAL: $ {expected_total:,.2f}", ln=True)
        ]
        generator.pdf.cell.assert_has_calls(expected_calls)
        generator.pdf.ln.assert_called_with(10)
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_add_items_table(self, mock_getenv, mock_load_dotenv):
        """Test adding items table to PDF."""
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        generator = InvoiceGenerator(year=2024, month=1)
        generator._create_pdf()
        
        # Mock PDF methods
        generator.pdf.cell = Mock()
        
        generator._add_items_table()
        
        # Verify table headers and content are added
        # January 2024: 23 business days * 8 hours * $25 = $4600
        expected_calls = [
            # Table headers
            unittest.mock.call(40, 10, "Item", border=1),
            unittest.mock.call(80, 10, "Description", border=1),
            unittest.mock.call(30, 10, "Quantity", border=1),
            unittest.mock.call(40, 10, "Unit Cost", border=1, ln=True),
            # Table row
            unittest.mock.call(40, 10, "01", border=1),
            unittest.mock.call(80, 10, "IT SERVICES", border=1),
            unittest.mock.call(30, 10, "1,0", border=1),
            unittest.mock.call(40, 10, "$ 4,600.00", border=1)
        ]
        generator.pdf.cell.assert_has_calls(expected_calls)
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    @patch('invoice_generator.invoice_generator.path.join')
    @patch('invoice_generator.invoice_generator.path.dirname')
    def test_generate_invoice_default_output_dir(self, mock_dirname, mock_join, mock_getenv, mock_load_dotenv):
        """Test invoice generation with default output directory."""
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        # Mock path operations
        mock_dirname.return_value = "/test/dir"
        mock_join.return_value = "/test/dir/output/invoice_2024-03.pdf"
        
        generator = InvoiceGenerator(year=2024, month=3)
        
        # Mock PDF output method
        generator.pdf = Mock()
        generator.pdf.output = Mock()
        
        # Mock all PDF creation methods
        generator._create_pdf = Mock()
        generator._add_header = Mock()
        generator._add_company_info = Mock()
        generator._add_client_info = Mock()
        generator._add_invoice_details = Mock()
        generator._add_amounts = Mock()
        generator._add_items_table = Mock()
        
        output_path = generator.generate_invoice()
        
        # Verify methods were called
        generator._create_pdf.assert_called_once()
        generator._add_header.assert_called_once()
        generator._add_company_info.assert_called_once()
        generator._add_client_info.assert_called_once()
        generator._add_invoice_details.assert_called_once()
        generator._add_amounts.assert_called_once()
        generator._add_items_table.assert_called_once()
        
        # Verify output path
        self.assertEqual(output_path, "/test/dir/output/invoice_2024-03.pdf")
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_generate_invoice_custom_output_dir(self, mock_getenv, mock_load_dotenv):
        """Test invoice generation with custom output directory."""
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        generator = InvoiceGenerator(year=2024, month=5)
        
        # Mock PDF output method
        generator.pdf = Mock()
        generator.pdf.output = Mock()
        
        # Mock all PDF creation methods
        generator._create_pdf = Mock()
        generator._add_header = Mock()
        generator._add_company_info = Mock()
        generator._add_client_info = Mock()
        generator._add_invoice_details = Mock()
        generator._add_amounts = Mock()
        generator._add_items_table = Mock()
        
        custom_output_dir = "/custom/output"
        output_path = generator.generate_invoice(custom_output_dir)
        
        # Verify output path (normalize path separators for cross-platform compatibility)
        expected_path = "/custom/output/invoice_2024-05.pdf"
        self.assertEqual(os.path.normpath(output_path), os.path.normpath(expected_path))
        generator.pdf.output.assert_called_once_with(output_path)
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_invoice_number_formatting(self, mock_getenv, mock_load_dotenv):
        """Test invoice number formatting with different months."""
        mock_getenv.side_effect = lambda key, default=None: self.mock_env_vars.get(key, default)
        
        # Test different month formats
        test_cases = [
            (2024, 1, "2024-01"),
            (2024, 12, "2024-12"),
            (2023, 6, "2023-06")
        ]
        
        for year, month, expected_number in test_cases:
            with self.subTest(year=year, month=month):
                generator = InvoiceGenerator(year=year, month=month)
                self.assertEqual(generator.invoice_number, expected_number)
    
    @patch('invoice_generator.invoice_generator.load_dotenv')
    @patch('invoice_generator.invoice_generator.os.getenv')
    def test_hourly_rate_string_conversion(self, mock_getenv, mock_load_dotenv):
        """Test that hourly rate is correctly converted from string to int."""
        # Set up mock to return string value for HOURLY_RATE
        mock_env_vars = self.mock_env_vars.copy()
        mock_env_vars['HOURLY_RATE'] = '30'  # String value
        
        mock_getenv.side_effect = lambda key, default=None: mock_env_vars.get(key, default)
        
        generator = InvoiceGenerator(year=2024, month=1)
        
        # Verify that hourly_rate is converted to int
        self.assertEqual(generator.hourly_rate, 30)
        self.assertIsInstance(generator.hourly_rate, int)
        # January 2024: 23 business days * 8 hours * $30 = $5520
        self.assertEqual(generator.total_amount, 5520)


if __name__ == '__main__':
    unittest.main() 
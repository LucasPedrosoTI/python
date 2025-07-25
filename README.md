# Python Repo

This repo will be used to save all python related project.

## Contents:
1. [Utilities](/utils)
2. [Invoice Generator](/invoice_generator)
3. [Log Hours](/log_hours)

## CI/CD

This repository uses GitHub Actions for automated testing and deployment. Each project has its own workflow that only triggers when files in that specific project are changed:

- **Log Hours**: `.github/workflows/log-hours.yml` - Triggers on changes to `log_hours/**`

## Projects

### 📧 Invoice Generator

A Python application that automatically generates professional PDF invoices with configurable business information and automatic business day calculations.

**Features:**
- 🎯 **Automatic Business Day Calculation** - Calculates work days (Mon-Fri) for any month/year
- 📄 **Professional PDF Generation** - Creates clean, formatted invoices using FPDF2
- ⚙️ **Configurable Settings** - Environment-based configuration for client/company info
- 🧪 **Well Tested** - Comprehensive test suite with 20+ test cases
- 🐍 **Poetry Support** - Modern Python dependency management
- 💻 **CLI Interface** - Command-line interface with flexible options
- 📦 **Executable Version** - Windows executable for non-technical users

For detailed installation instructions, configuration options, and usage examples, see the [Installation Guide](/invoice_generator/INSTALLATION_GUIDE.md).

### 📅 Log Hours

A Python application that automatically logs hours to the service management system using Playwright automation.

**Features:**
- 🎯 **Automated Hour Logging** - Automatically logs work hours to service management system
- 🎭 **Playwright Integration** - Modern, reliable web automation (migrated from Selenium)
- 🐳 **Docker Support** - Containerized deployment with Docker and Docker Compose
- 🚀 **CI/CD Pipeline** - GitHub Actions workflow for automated testing and deployment
- ⚙️ **VPS Deployment** - Automated deployment to VPS via DockerHub
- 📱 **Responsive Design** - Handles different screen resolutions automatically
- 🛡️ **Error Handling** - Smart error handling with debug screenshots

**Tech Stack:**
- Python 3.11+
- Playwright for web automation
- Poetry for dependency management
- Docker for containerization
- GitHub Actions for CI/CD

For detailed installation instructions, configuration options, and usage examples, see the [README](/log_hours/README.md).
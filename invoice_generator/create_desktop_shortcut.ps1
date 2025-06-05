# PowerShell script to create a desktop shortcut for Invoice Generator
Write-Host "Creating desktop shortcut for Invoice Generator..." -ForegroundColor Green

# Get desktop path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Invoice Generator.lnk"

# Define executable path
$ExecutablePath = "C:\InvoiceGenerator\InvoiceGenerator.exe"

# Check if executable exists
if (-not (Test-Path $ExecutablePath)) {
    Write-Host "Error: Executable not found at $ExecutablePath" -ForegroundColor Red
    Write-Host "Please make sure the Invoice Generator is installed in C:\InvoiceGenerator\" -ForegroundColor Red
    exit 1
}

# Create shortcut
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ExecutablePath
$Shortcut.WorkingDirectory = "C:\InvoiceGenerator"
$Shortcut.Description = "Generate PDF invoices for monthly work hours"
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Shortcut location: $ShortcutPath" -ForegroundColor Cyan

# Also create a Start Menu shortcut
$StartMenuPath = [Environment]::GetFolderPath("Programs")
$StartMenuShortcutPath = Join-Path $StartMenuPath "Invoice Generator.lnk"

$StartMenuShortcut = $WshShell.CreateShortcut($StartMenuShortcutPath)
$StartMenuShortcut.TargetPath = $ExecutablePath
$StartMenuShortcut.WorkingDirectory = "C:\InvoiceGenerator"
$StartMenuShortcut.Description = "Generate PDF invoices for monthly work hours"
$StartMenuShortcut.Save()

Write-Host "Start Menu shortcut created successfully!" -ForegroundColor Green
Write-Host "Start Menu location: $StartMenuShortcutPath" -ForegroundColor Cyan

Write-Host "`nInvoice Generator installation complete!" -ForegroundColor Yellow
Write-Host "You can now:" -ForegroundColor White
Write-Host "- Double-click the desktop shortcut to run with default settings" -ForegroundColor White
Write-Host "- Open Command Prompt and run: C:\InvoiceGenerator\InvoiceGenerator.exe --help" -ForegroundColor White
Write-Host "- Find it in the Start Menu" -ForegroundColor White 
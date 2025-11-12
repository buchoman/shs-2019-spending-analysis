# PowerShell script to run the Streamlit app
Set-Location $PSScriptRoot
Write-Host "Starting Survey of Household Spending 2019 Application..." -ForegroundColor Green
Write-Host ""
python -m streamlit run app.py
Read-Host "Press Enter to exit"


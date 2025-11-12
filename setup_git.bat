@echo off
echo Setting up Git repository for Streamlit Cloud deployment...
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git is installed.
echo.
echo This script will help you set up your GitHub repository.
echo.
echo You need to:
echo 1. Create a GitHub repository at https://github.com
echo 2. Get the repository URL (e.g., https://github.com/YOUR_USERNAME/REPO_NAME.git)
echo.
set /p REPO_URL="Enter your GitHub repository URL: "

if "%REPO_URL%"=="" (
    echo ERROR: Repository URL is required
    pause
    exit /b 1
)

echo.
echo Initializing git repository...
git init

echo.
echo Adding all files...
git add .

echo.
echo Creating initial commit...
git commit -m "Initial commit - Survey of Household Spending 2019 Application"

echo.
echo Setting main branch...
git branch -M main

echo.
echo Adding remote repository...
git remote add origin %REPO_URL%

echo.
echo Pushing to GitHub...
echo NOTE: You may be prompted for your GitHub username and Personal Access Token
echo (Create a token at: https://github.com/settings/tokens)
echo.
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Your code has been pushed to GitHub.
    echo.
    echo Next steps:
    echo 1. Go to https://share.streamlit.io
    echo 2. Sign in with your GitHub account
    echo 3. Click "New app"
    echo 4. Select your repository and deploy!
) else (
    echo.
    echo ERROR: Failed to push to GitHub
    echo.
    echo Common issues:
    echo - Authentication: Use a Personal Access Token, not your password
    echo - Large files: May need Git LFS for files over 100MB
    echo.
    echo See DEPLOY_NOW.md for detailed instructions.
)

pause


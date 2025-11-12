# Quick Deployment Guide - Survey of Household Spending 2019

## Prerequisites
- GitHub account (free at https://github.com)
- Git installed on your computer

## Step 1: Create GitHub Repository

1. Go to https://github.com and sign in
2. Click the **"+"** icon (top right) → **"New repository"**
3. Name: `shs-2019-spending-analysis` (or your preferred name)
4. Make it **PUBLIC** ✅ (required for free Streamlit Cloud)
5. **DO NOT** check any boxes (no README, .gitignore, license)
6. Click **"Create repository"**
7. Copy the repository URL (e.g., `https://github.com/yourusername/shs-2019-spending-analysis.git`)

## Step 2: Push Code to GitHub

### Option A: Use the batch file (Windows)
1. Double-click `setup_git.bat`
2. Enter your GitHub repository URL when prompted
3. Follow the prompts

### Option B: Use command line

Open PowerShell or Command Prompt in this folder and run:

```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Survey of Household Spending 2019 Application"

# Set main branch
git branch -M main

# Add remote (replace with your actual URL)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push (you'll need a Personal Access Token, not password)
git push -u origin main
```

**Authentication:**
- GitHub no longer accepts passwords
- Create a Personal Access Token at: https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Select scope: `repo` (full control)
- Use the token as your password when pushing

## Step 3: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in:
   - **Repository**: Select your repository from the dropdown
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom name (optional)
5. Click **"Deploy"**

## Step 4: Wait for Deployment

- First deployment takes 2-5 minutes
- Streamlit Cloud will:
  - Install dependencies from `requirements.txt`
  - Load your data files
  - Start the app
- Watch the build logs for progress
- Your app will be live at: `https://your-app-name.streamlit.app`

## Troubleshooting

### Large Files (>100MB)
If your SAS data files are large:
- We may need to use Git LFS (Large File Storage)
- Streamlit Cloud free tier has a 1GB limit
- Contact me if you get file size errors

### Build Errors
- Check the build logs in Streamlit Cloud
- Common issues:
  - Missing dependencies (check `requirements.txt`)
  - Data file paths incorrect
  - Memory issues

### Authentication Errors
- Use a Personal Access Token, not your password
- Make sure the token has `repo` scope

## Your App is Live! 🎉

Once deployed, your app will:
- ✅ Be accessible from anywhere
- ✅ Auto-update when you push to GitHub
- ✅ Have free HTTPS
- ✅ No server management needed

## Need Help?

Just tell me:
1. Your GitHub username
2. The repository name you created

And I'll help you complete the setup!


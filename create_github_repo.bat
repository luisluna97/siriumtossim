@echo off
echo ========================================
echo Creating GitHub Repository
echo TS Schedule to SSIM Converter
echo ========================================

echo.
echo Step 1: Initializing Git repository...
git init

echo.
echo Step 2: Adding all files...
git add .

echo.
echo Step 3: Creating initial commit...
git commit -m "Initial commit: TS Schedule to SSIM Converter by Dnata Brasil"

echo.
echo Step 4: Creating GitHub repository...
echo Please choose one option:
echo.
echo OPTION A - If you have GitHub CLI installed:
echo gh repo create ts-schedule-ssim-converter --public --description "Professional TS Schedule to SSIM converter by Dnata Brasil"
echo git remote add origin https://github.com/[YOUR-USERNAME]/ts-schedule-ssim-converter.git
echo git branch -M main
echo git push -u origin main
echo.
echo OPTION B - Manual GitHub creation:
echo 1. Go to https://github.com/new
echo 2. Repository name: ts-schedule-ssim-converter
echo 3. Description: Professional TS Schedule to SSIM converter by Dnata Brasil
echo 4. Make it Public
echo 5. DO NOT initialize with README (we already have files)
echo 6. Click "Create repository"
echo 7. Then run these commands:
echo    git remote add origin https://github.com/[YOUR-USERNAME]/ts-schedule-ssim-converter.git
echo    git branch -M main
echo    git push -u origin main

echo.
echo Repository setup completed!
echo.
echo Next step: Deploy on Streamlit Cloud
echo 1. Go to https://share.streamlit.io/
echo 2. Connect with GitHub
echo 3. Select repository: ts-schedule-ssim-converter
echo 4. Branch: main
echo 5. Main file: app.py
echo 6. Click Deploy!
echo.
pause

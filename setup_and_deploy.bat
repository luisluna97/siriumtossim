@echo off
echo ========================================
echo TS Schedule to SSIM Converter - Setup
echo ========================================

echo.
echo 1. Installing Python dependencies...
python -m pip install streamlit pandas openpyxl xlrd --upgrade

echo.
echo 2. Initializing Git repository...
git init

echo.
echo 3. Adding files to Git...
git add .

echo.
echo 4. Creating initial commit...
git commit -m "Initial commit: TS Schedule to SSIM Converter by Dnata Brasil"

echo.
echo 5. Setting up GitHub repository...
echo Please run this command to create the GitHub repository:
echo gh repo create ts-schedule-ssim-converter --public --description "Professional TS Schedule to SSIM converter by Dnata Brasil"

echo.
echo 6. To push to GitHub, run:
echo git remote add origin https://github.com/[YOUR-USERNAME]/ts-schedule-ssim-converter.git
echo git branch -M main
echo git push -u origin main

echo.
echo 7. To run locally:
echo streamlit run app.py

echo.
echo Setup completed! Check above for next steps.
pause

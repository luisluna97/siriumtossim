@echo off
echo Uploading SIRIUM to GitHub...

git init
git add app.py
git add sirium_to_ssim_converter.py
git add requirements.txt
git add README.md
git add airport.csv
git add "ACT TYPE.xlsx"
git add .streamlit/config.toml
git add .gitignore
git add DEPLOY.md

git commit -m "Initial SIRIUM to SSIM Converter - Professional Airline Operations Tool"

git branch -M main
git remote add origin https://github.com/luisluna97/siriumtossim.git
git push -u origin main

echo Upload completed!
pause

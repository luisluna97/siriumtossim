@echo off
echo Deploying v1.1.0 updates...

git add app.py
git add sirium_to_ssim_converter.py
git add version.py
git add README.md
git add upload_to_github.bat

git commit -m "v1.1.0 Major Updates"

git push origin main

echo Deploy completed!
echo.
echo Updates included:
echo - Fixed date operation periods (Eff Date to Disc Date)
echo - All Companies mode for processing all airlines
echo - Enhanced preview with 50 lines
echo - Optimized layout with compact information
echo.
echo App should be updated at: https://siriumtossim.streamlit.app/
pause

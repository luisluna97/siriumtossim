@echo off
echo ========================================
echo Starting TS Schedule to SSIM Converter
echo ========================================

echo Checking if Streamlit is installed...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Installing Streamlit and dependencies...
    python -m pip install streamlit pandas openpyxl xlrd
)

echo.
echo Starting the application...
echo The app will open in your browser at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py

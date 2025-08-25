# 🚀 SIRIUM Deployment Guide

## GitHub Repository
**Repository URL:** [https://github.com/luisluna97/siriumtossim](https://github.com/luisluna97/siriumtossim)

## 📁 Files Structure
```
├── app.py                          # Main Streamlit application
├── sirium_to_ssim_converter.py     # Core converter module
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── airport.csv                     # Airport timezone mapping
├── ACT TYPE.xlsx                   # Aircraft type mapping
├── .streamlit/config.toml          # Streamlit configuration
├── .gitignore                      # Git ignore rules
└── DEPLOY.md                       # This deployment guide
```

## 🌐 Streamlit Cloud Deployment

### Step 1: Upload to GitHub
Run the upload script:
```bash
upload_to_github.bat
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [https://share.streamlit.io/](https://share.streamlit.io/)
2. Sign in with GitHub account
3. Click "New app"
4. Select repository: `luisluna97/siriumtossim`
5. Main file path: `app.py`
6. Click "Deploy!"

### Step 3: App Configuration
- **App URL:** Will be `https://siriumtossim.streamlit.app/`
- **Python version:** 3.9+
- **Dependencies:** Automatically installed from `requirements.txt`

## 🧪 Local Testing

### Run Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py
```

Or use the batch file:
```bash
run_streamlit.bat
```

### Test URL
Local app will be available at: `http://localhost:8501`

## 📋 Dependencies
- `streamlit>=1.28.0`
- `pandas>=1.5.0`
- `openpyxl>=3.0.0`

## ✅ Deployment Checklist
- [ ] Repository created and uploaded
- [ ] All required files present
- [ ] Dependencies specified in requirements.txt
- [ ] Streamlit Cloud app deployed
- [ ] App tested with sample data
- [ ] Documentation updated

## 🔧 Configuration Files

### .streamlit/config.toml
```toml
[server]
maxUploadSize = 200

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

## 📞 Support
Developed by **Capacity Dnata Brasil** for professional airline operations.

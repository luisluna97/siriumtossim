# ✈️ SIRIUM to SSIM Converter

**Professional airline schedule converter developed by Capacity Dnata Brasil**

## 🎯 Overview

SIRIUM is a powerful converter that transforms airline schedules from SIRIUM format (based on SFO Schedule Extract Reports) to SSIM (Standard Schedules Information Manual) format, following IATA standards.

## ✨ Key Features

- 🏢 **Multiple Airlines Support**: Process multiple airlines in the same file
- 🎯 **Airline Selection**: Choose specific airline after file upload
- ✅ **SSIM Standard**: Generates IATA-compatible 200-character line format
- 🔍 **Data Validation**: Complete integrity checks and format validation
- 📊 **Real-time Preview**: View data before conversion
- 📥 **Instant Download**: Download generated SSIM files immediately

## 🚀 Quick Start

### Web Application
```bash
streamlit run app.py
```

### Command Line
```python
from sirium_to_ssim_converter import gerar_ssim_sirium

result = gerar_ssim_sirium(
    excel_path="schedule.xlsx",
    codigo_iata_selecionado="AI",
    output_file="AI_schedule.ssim"
)
```

## 📊 Input Format

The Excel file should have:
- **Header on row 5** (index 4)
- **Required columns**:
  - `Mkt Al` or `Op Al`: Airline code (2 letters)
  - `Orig`: Origin airport (IATA code)
  - `Dest`: Destination airport (IATA code)
  - `Flight`: Flight number
  - `Eff Date`: Effective date
  - `Disc Date`: Discontinue date
  - `Op Days`: Operating days (1234567 format)

## 📄 Output Format

Generates standard SSIM files with:
- **200-character lines**: IATA standard format
- **Complete structure**: Header, Carrier Info, Flight Records, Footer
- **Proper formatting**: Correct line breaks and spacing
- **Sequential numbering**: Each line properly numbered

### Sample SSIM Output:
```
1AIRLINE STANDARD SCHEDULE DATA SET                                 00000001
2UAI  0008    19JUL2505SEP2525AUG25Created by Capacity Dnata Brasil 00000006
3 AI 01730101J01AUG2501AUG251234567 DEL0000+0530  SFO0000-0800  320 00000011
5 AI 25AUG25                                                        000022E000023
```

## 🏢 Supported Airlines

Supports any airline present in the input file, including:
- **AI** (Air India)
- **BA** (British Airways)
- **EK** (Emirates)
- **LH** (Lufthansa)
- **QF** (Qantas)
- And many more...

## 🛠️ Installation

```bash
git clone <repository-url>
cd sirium-converter
pip install -r requirements.txt
```

## 📋 Dependencies

- `streamlit>=1.28.0`
- `pandas>=1.5.0`
- `openpyxl>=3.0.0`

## 🔧 Technical Features

- **Timezone Support**: Automatic timezone mapping for airports
- **Aircraft Mapping**: ICAO to IATA aircraft code conversion
- **Data Validation**: Comprehensive checks before conversion
- **Error Handling**: Robust error handling and user feedback
- **Memory Efficient**: Optimized for large schedule files

## 📁 Project Structure

```
├── app.py                          # Main Streamlit application
├── sirium_to_ssim_converter.py     # Core converter module
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── airport.csv                     # Airport timezone mapping
└── ACT TYPE.xlsx                   # Aircraft type mapping
```

## 🎮 How to Use

1. **Upload** your Excel file with SIRIUM schedule
2. **Preview** available airlines and data structure
3. **Select** the specific airline for conversion
4. **Convert** to SSIM format with validation
5. **Download** the generated SSIM file

## ✅ Validation Features

The converter includes comprehensive validation:
- ✅ **Line Length**: Ensures 200-character lines
- ✅ **SSIM Structure**: Validates Header, Carrier, Flights, Footer
- ✅ **Data Integrity**: Checks required fields and formats
- ✅ **Format Compliance**: IATA standard compliance

## 📞 Support

Developed by **Capacity Dnata Brasil** for professional airline operations.

For technical support or questions, please contact the development team.

## 🏆 Why SIRIUM?

SIRIUM combines the best of both worlds:
- ✅ **Reliability** of proven SSIM standards
- ✅ **Flexibility** of modern file processing
- ✅ **Validation** with real-time feedback
- ✅ **User Experience** with intuitive interface

---

*Version 1.0 - Professional Airline Operations Tool*
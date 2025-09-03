# ✈️ CIRIUM to SSIM Converter

**Professional airline schedule converter developed by Capacity Dnata Brasil**

## 📋 Executive Summary

The CIRIUM to SSIM Converter is a production-ready application that transforms airline schedule data from CIRIUM format (SFO Schedule Extract Reports) into IATA-compliant SSIM (Standard Schedules Information Manual) files. The system supports three conversion modes: single airline, multiple selected airlines, and all companies processing, generating standardized 200-character SSIM records suitable for industry-standard airline operations systems.

## 🔧 Core Capabilities

### **Conversion Modes**
- **Single Airline**: Process individual airline schedules
- **Multiple Airlines**: Custom selection of specific airlines (e.g., EK + AI + CZ)
- **All Companies**: Batch processing of all airlines in one SSIM file

### **Data Intelligence**
- **Flight Type Detection**: Automatic cargo (F) vs passenger (J) classification based on seat count
- **Equipment Mapping**: Real aircraft types from CIRIUM Equip column (388, 359, 77X, 74Y, etc.)
- **Date Period Accuracy**: Full seasonal coverage using Eff Date to Disc Date ranges
- **Timezone Processing**: Automatic IATA airport timezone mapping

### **SSIM Compliance**
- **200-character lines**: Strict IATA formatting compliance
- **Complete structure**: Header (1), Carrier (2U), Flight records (3), Footer (5)
- **Sequential numbering**: Proper line numbering throughout file
- **Data validation**: Comprehensive integrity checks before output

## 🏗️ Technical Architecture

### **Core Engine** (`sirium_to_ssim_converter.py`)

The conversion engine implements three main functions:

#### `gerar_ssim_sirium(excel_path, codigo_iata, output_file=None)`
Processes single airline schedules with complete data validation and SSIM formatting.

#### `gerar_ssim_multiplas_companias(excel_path, companias_list, output_file=None)`
Generates unified SSIM files for custom airline selections, maintaining single header/footer structure.

#### `gerar_ssim_todas_companias(excel_path, output_file=None)`
Batch processes all valid airlines into one consolidated SSIM file.

### **Data Processing Pipeline**

1. **Input Validation**: Excel file parsing with header detection (row 5)
2. **Airline Filtering**: IATA code validation (2-letter alphabetic codes only)
3. **Data Cleaning**: Remove invalid records, NaN values, and system text
4. **Type Classification**: Flight type determination based on seat configuration
5. **Equipment Mapping**: Aircraft type resolution from CIRIUM codes to IATA standard
6. **Date Processing**: Seasonal period calculation using effective/discontinue dates
7. **SSIM Generation**: 200-character line formatting with proper structure

### **Key Algorithms**

- **Flight Type Logic**: `Seats == 0 → 'F' (Cargo)`, `Seats > 0 → 'J' (Passenger)`
- **Date Parsing**: Robust datetime conversion with multiple format support
- **Equipment Mapping**: Comprehensive aircraft code translation (388→388, A320→320, etc.)
- **Timezone Calculation**: Airport-based offset determination from `airport.csv`

## 🚀 Quick Start

### Web Application
```bash
streamlit run app.py
```

### Programmatic Usage
```python
from sirium_to_ssim_converter import gerar_ssim_sirium, gerar_ssim_multiplas_companias

# Single airline
result = gerar_ssim_sirium("schedule.xlsx", "EK", "emirates.ssim")

# Multiple airlines
result = gerar_ssim_multiplas_companias("schedule.xlsx", ["EK", "AI"], "multi.ssim")
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

## 📁 Technical Implementation

### **Project Structure**
```
├── app.py                          # Streamlit web interface
├── sirium_to_ssim_converter.py     # Core conversion engine
├── version.py                      # Version management system
├── airport.csv                     # IATA airport timezone database
├── ACT TYPE.xlsx                   # Aircraft type mapping table
├── requirements.txt                # Python dependencies
├── CHANGELOG.md                    # Complete project history
└── README.md                       # Technical documentation
```

### **Code Architecture**

#### **Main Interface** (`app.py`)
- **Streamlit Framework**: Professional web interface with gradient design
- **File Upload**: Multi-format Excel support with validation
- **Data Preview**: Real-time airline and flight statistics
- **Conversion Control**: Three-mode selection system (Single/Multiple/All)
- **Result Validation**: SSIM structure verification and 50-line preview

#### **Conversion Engine** (`sirium_to_ssim_converter.py`)
- **Data Pipeline**: Excel → Pandas → Validation → SSIM Generation
- **Flight Processing**: Individual record transformation with error handling
- **Type Detection**: Intelligent cargo/passenger classification
- **Equipment Resolution**: CIRIUM to IATA aircraft code mapping
- **Date Calculation**: Seasonal period extraction and formatting

#### **Core Functions**

```python
def gerar_ssim_sirium(excel_path, codigo_iata, output_file=None):
    """Single airline processing with complete SSIM structure"""

def gerar_ssim_multiplas_companias(excel_path, companias_list, output_file=None):
    """Multiple airline processing with unified SSIM output"""

def gerar_ssim_todas_companias(excel_path, output_file=None):
    """Batch processing for all valid airlines"""

def determinar_status_sfo(seats=None, service_type=None):
    """Flight type classification: F (cargo) or J (passenger)"""

def get_aircraft_type_sfo(equipment=None):
    """Aircraft code mapping with fallback logic"""
```

## 🎮 How to Use

1. **Upload** your Excel file with CIRIUM schedule
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

## 📞 Technical Support

**Developed by**: Capacity Dnata Brasil  
**Lead Developer**: Luis Luna  
**Contact**: 
- luis.luna@ufpe.br
- luis.evaristo@dnata.com.br

For technical support, feature requests, or integration questions, please contact the development team or open an issue on GitHub.

## 🏆 Why CIRIUM Converter?

This converter provides enterprise-grade reliability with modern flexibility:
- ✅ **IATA Compliance**: Strict adherence to SSIM standards
- ✅ **Production Ready**: Handles large-scale airline operations data
- ✅ **Intelligent Processing**: Automatic flight type and equipment detection
- ✅ **Flexible Output**: Single, multiple, or all-airline processing modes
- ✅ **Data Integrity**: Comprehensive validation and error handling

## 📈 Version History

### v1.2.0 (2025-08-03) - Multiple Selection
- 🎯 **MULTIPLE SELECT**: Custom airline combinations (e.g., EK + AI + CZ)
- 🔘 **Three Modes**: Single, Multiple, All Companies with radio button selection
- 📦 **Unified Output**: Single SSIM file for multiple airlines with proper structure
- 🧪 **Tested**: EK (13 flights) + CZ (6 flights) = 19 combined flights

### v1.1.4 (2025-08-03) - Cargo Logic
- 📦 **CARGO DETECTION**: Seats = 0 → Cargo (F), Seats > 0 → Passenger (J)
- ✅ **Validated**: 9 cargo flights + 25 passenger flights detected correctly

### v1.1.3 (2025-08-03) - Real Equipment Types
- ✈️ **EQUIPMENT MAPPING**: Uses real CIRIUM Equip column values
- 🔧 **Aircraft Codes**: 388, 359, 332, 77X, 74Y, 333, 789, 77W (instead of default 320)

### v1.1.2 (2025-08-03) - Professional Design
- 🎨 **CIRIUM Name**: Corrected spelling throughout application
- 🎨 **Professional Layout**: Gradient headers, fixed help sections
- 📋 **Enhanced UX**: Release notes and help always visible at top

### v1.1.1 (2025-08-03) - All Companies Fix
- 🔧 **CRITICAL FIX**: All Companies generates single SSIM file (not concatenated)
- 🧹 **BUG FIX**: Filtered invalid airline codes (removes system text)

### v1.1.0 (2025-08-03) - Major Updates  
- 📅 **DATE FIX**: Flight lines use complete Eff Date to Disc Date periods
- 🌍 **ALL COMPANIES**: Process all airlines in single file
- 👀 **ENHANCED PREVIEW**: 50-line SSIM preview

### v1.0.1.1 (2025-08-25) - Rebrand
- 🎭 **REBRAND**: SIRIUM → CIRIUM naming correction

### v1.0.0 - Initial Release
- 🚀 **CORE**: Basic CIRIUM to SSIM conversion functionality

---

*Professional Airline Operations Tool - [GitHub Repository](https://github.com/luisluna97/siriumtossim)*
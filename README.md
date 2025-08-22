# ✈️ TS Schedule to SSIM Converter

A professional web application for converting airline schedules from TS format to SSIM (Standard Schedules Information Manual) format.

**Developed by Capacity Dnata Brasil**

## 🚀 Features

- **Smart Flight Connections**: Extracts real next flights from "Onward Flight" column
- **Order Preservation**: Maintains original flight sequence from schedule
- **Complex Processing**: Handles values like "TS840/1" correctly
- **Industry Standard**: Generates IATA-compatible SSIM files
- **User-friendly Interface**: Professional Streamlit web application
- **Data Validation**: Comprehensive integrity checks before conversion

## 📋 How It Works

1. Upload your Excel file containing the TS schedule
2. Enter the airline IATA code (2 letters)
3. Preview and validate your data
4. Convert to SSIM format
5. Download the generated SSIM file

## 🔧 Technical Specifications

### Input Format (TS Schedule)
The Excel file must contain these columns:
- `Flight-Number`: Flight number
- `Route`: Route in format "ORIGIN / DESTINATION"
- `Date-LT`: Local date
- `Std-LT`: Departure time local
- `Sta-LT`: Arrival time local
- `Onward Flight`: Next connecting flight (format: "TSxxx")
- `Aircraft-Type`: Aircraft type code
- `Type`: Service type (J=Passenger, F=Freight)

### Output Format (SSIM)
- Standard IATA SSIM format
- 200-character fixed-width lines
- Type 3 records for flight data
- Proper timezone handling
- Sequential line numbering

## 🌐 Live Demo

Access the application at: [Your Streamlit Cloud URL]

## 💻 Local Development

### Prerequisites
- Python 3.8+
- pip

### Installation
```bash
git clone [repository-url]
cd ts-schedule-converter
pip install -r requirements.txt
```

### Run locally
```bash
streamlit run app.py
```

## 📁 Project Structure

```
ts-schedule-converter/
├── app.py                      # Main Streamlit application
├── ts09_to_ssim_converter.py   # Core conversion logic
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── airport.csv                 # Airport codes and timezones
├── ACT TYPE.xlsx              # Aircraft type mappings
└── iata_airlines.csv          # Airline codes reference
```

## 🔍 Key Improvements Over Standard Converters

1. **Real Connection Logic**: Instead of repeating the same flight number, extracts actual next flight from schedule data
2. **Original Order Preservation**: Maintains the flight sequence as defined in the original schedule
3. **Robust Data Processing**: Handles edge cases like "TS840/1" format in onward flights
4. **Professional Interface**: Clean, intuitive web interface for non-technical users

## 📊 Supported Data

- **Airlines**: Any IATA-coded airline
- **Routes**: International and domestic
- **Aircraft Types**: All standard IATA aircraft codes
- **Schedules**: Daily, weekly, or custom patterns
- **Timezones**: Automatic UTC conversion

## 🛠️ Support Files

The converter uses reference files for enhanced accuracy:
- `airport.csv`: Airport codes, names, and timezone data
- `ACT TYPE.xlsx`: Aircraft type code mappings (ICAO to IATA)
- `iata_airlines.csv`: Airline reference data

## 📈 Performance

- Processes 1000+ flight records in seconds
- Memory efficient for large schedules
- Real-time validation and feedback
- Automatic error handling and recovery

## 🔒 Data Security

- Files processed locally (no external data transmission)
- Temporary files automatically cleaned up
- No data retention on server
- GDPR compliant processing

## 📞 Support

For technical support or feature requests, contact the **Capacity Dnata Brasil** team.

## 📄 License

This project is proprietary software developed by Dnata Brasil for internal airline operations.

---

**Dnata Brasil** - Professional Aviation Solutions
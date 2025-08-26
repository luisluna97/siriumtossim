import streamlit as st
import pandas as pd
from datetime import datetime
import os
from sirium_to_ssim_converter import gerar_ssim_sirium
from version import get_version_info

def main():
    st.set_page_config(
        page_title="CIRUIM to SSIM Converter - Dnata Brasil", 
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Header
    version_info = get_version_info()
    st.title("✈️ CIRUIM to SSIM Converter")
    st.markdown("**Developed by Capacity Dnata Brasil**")
    st.markdown(f"*Version {version_info['version']} - {version_info['date']}*")
    st.markdown("---")
    
    st.markdown("""
    ### 📋 About CIRUIM Converter
    
    This converter transforms airline schedules from **CIRUIM format** (based on SFO Schedule Extract Reports) 
    to **SSIM** (Standard Schedules Information Manual) format.
    
    **Key Features:**
    - ✅ **Multiple Airlines Support**: Process multiple airlines in the same file
    - ✅ **Airline Selection**: Choose specific airline after upload
    - ✅ **SSIM Standard**: Generates IATA-compatible files
    - ✅ **Data Validation**: Integrity checks before conversion
    - ✅ **200-Character Lines**: Proper SSIM formatting
    - ✅ **Complete Structure**: Header, Carrier Info, Flight Records, Footer
    """)
    
    st.markdown("---")
    
    # File Upload Section
    st.subheader("📁 Upload Schedule File")
    uploaded_file = st.file_uploader(
        "Select Excel file with CIRUIM schedule:",
        type=['xlsx', 'xls'],
        help="Upload Excel file containing schedule in CIRUIM format (header on row 5)"
    )
    
    if uploaded_file is not None:
        st.markdown("---")
        
        try:
            # Save temporary file
            temp_file_path = f"temp_{uploaded_file.name}"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Read and analyze data
            df = pd.read_excel(temp_file_path, header=4)
            
            st.subheader("👀 Data Preview")
            
            # Find airline column
            airline_col = None
            for col in ['Mkt Al', 'Op Al', 'Airline', 'Carrier']:
                if col in df.columns:
                    airline_col = col
                    break
            
            if airline_col:
                # Get available airlines
                # Ultra-safe: evitar erro de sorted() com float/string
                try:
                    unique_values = df[airline_col].astype(str)
                    unique_values = unique_values[
                        (unique_values != 'nan') & 
                        (unique_values != '') & 
                        (unique_values.notna())
                    ].unique()
                    available_airlines = sorted([str(x) for x in unique_values if str(x) not in ['nan', '', 'None']])
                except Exception as e:
                    st.error(f"⚠️ Erro ao processar companhias: {e}")
                    available_airlines = [str(x) for x in df[airline_col].dropna().unique()]
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total Records", len(df))
                with col2:
                    st.metric("🏢 Airlines Available", len(available_airlines))
                with col3:
                    if 'Flight' in df.columns:
                        st.metric("✈️ Total Flights", df['Flight'].nunique())
                    else:
                        st.metric("✈️ Records", len(df))
                
                # Show available airlines
                st.subheader("🏢 Available Airlines")
                airline_cols = st.columns(min(len(available_airlines), 5))
                for i, airline in enumerate(available_airlines):
                    with airline_cols[i % 5]:
                        airline_count = len(df[df[airline_col] == airline])
                        st.info(f"**{airline}**\n{airline_count} flights")
                
                # Airline Selection
                st.markdown("---")
                st.subheader("⚙️ Conversion Settings")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_airline = st.selectbox(
                        "Select Airline for Conversion:",
                        options=available_airlines,
                        help="Choose the airline to convert to SSIM format"
                    )
                
                with col2:
                    output_filename = st.text_input(
                        "Output filename (optional):",
                        placeholder="Auto-generated if empty",
                        help="Leave empty for automatic naming"
                    )
                
                # Filter data by selected airline
                df_filtered = df[df[airline_col] == selected_airline]
                
                # Show filtered data preview
                st.subheader(f"📋 {selected_airline} Schedule Preview")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✈️ Flights", len(df_filtered))
                with col2:
                    if 'Flight' in df_filtered.columns:
                        st.metric("🔢 Unique Flights", df_filtered['Flight'].nunique())
                with col3:
                    if 'Orig' in df_filtered.columns and 'Dest' in df_filtered.columns:
                        routes = df_filtered[['Orig', 'Dest']].drop_duplicates()
                        st.metric("🗺️ Routes", len(routes))
                
                # Show sample data
                if len(df_filtered) > 0:
                    cols_to_show = []
                    for col in ['Flight', 'Orig', 'Dest', 'Eff Date', 'Disc Date', 'Op Days']:
                        if col in df_filtered.columns:
                            cols_to_show.append(col)
                    
                    if cols_to_show:
                        st.dataframe(
                            df_filtered[cols_to_show].head(10),
                            use_container_width=True
                        )
                    else:
                        st.dataframe(df_filtered.head(10), use_container_width=True)
                
                # Data Integrity Check
                st.subheader("🔍 Data Integrity Check")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Check required columns
                    required_columns = ['Orig', 'Dest']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    
                    if missing_columns:
                        st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                    else:
                        st.success("✅ All required columns present")
                
                with col2:
                    # Check selected airline data
                    if len(df_filtered) > 0:
                        st.success(f"✅ {len(df_filtered)} flights found for {selected_airline}")
                    else:
                        st.error(f"❌ No flights found for {selected_airline}")
                
                st.markdown("---")
                
                # Conversion Button
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col2:
                    if st.button("🚀 Convert to SSIM", type="primary", use_container_width=True):
                        
                        if len(df_filtered) == 0:
                            st.error(f"❌ Cannot convert: no flights found for {selected_airline}")
                            return
                        
                        with st.spinner(f"Converting {selected_airline} schedule to SSIM..."):
                            try:
                                # Determine output filename
                                if output_filename:
                                    output_file = output_filename if output_filename.endswith('.ssim') else output_filename + '.ssim'
                                else:
                                    output_file = None
                                
                                # Execute conversion
                                result = gerar_ssim_sirium(temp_file_path, selected_airline, output_file)
                                
                                if result:
                                    st.success("✅ SSIM conversion completed successfully!")
                                    st.info(f"📄 Generated file: {result}")
                                    
                                    # Offer download
                                    with open(result, 'rb') as file:
                                        st.download_button(
                                            label="📥 Download SSIM File",
                                            data=file.read(),
                                            file_name=os.path.basename(result),
                                            mime="text/plain",
                                            type="primary",
                                            use_container_width=True
                                        )
                                    
                                    # Conversion Statistics
                                    st.subheader("📊 Conversion Statistics")
                                    
                                    # Read generated file for stats
                                    with open(result, 'r') as f:
                                        ssim_lines = f.readlines()
                                    
                                    flight_lines = [line for line in ssim_lines if line.startswith('3 ')]
                                    
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("📄 SSIM Lines", len(ssim_lines))
                                    with col2:
                                        st.metric("✈️ Flight Records", len(flight_lines))
                                    with col3:
                                        st.metric("🏢 Airline", selected_airline)
                                    with col4:
                                        st.metric("📁 File Size", f"{os.path.getsize(result)} bytes")
                                    
                                    # SSIM Validation
                                    st.subheader("✅ SSIM Format Validation")
                                    
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.write("**Line Length Validation:**")
                                        valid_lines = 0
                                        for line in ssim_lines[:10]:  # Check first 10 lines
                                            if len(line.rstrip()) == 200:
                                                valid_lines += 1
                                        
                                        if valid_lines == len(ssim_lines[:10]):
                                            st.success(f"✅ All lines have correct length (200 chars)")
                                        else:
                                            st.warning(f"⚠️ {valid_lines}/{len(ssim_lines[:10])} lines have correct length")
                                    
                                    with col2:
                                        st.write("**SSIM Structure:**")
                                        has_header = any(line.startswith('1') for line in ssim_lines)
                                        has_carrier = any(line.startswith('2U') for line in ssim_lines)
                                        has_flights = any(line.startswith('3 ') for line in ssim_lines)
                                        has_footer = any(line.startswith('5 ') for line in ssim_lines)
                                        
                                        st.write(f"Header (1): {'✅' if has_header else '❌'}")
                                        st.write(f"Carrier (2U): {'✅' if has_carrier else '❌'}")
                                        st.write(f"Flights (3): {'✅' if has_flights else '❌'}")
                                        st.write(f"Footer (5): {'✅' if has_footer else '❌'}")
                                    
                                    # Show SSIM preview
                                    st.subheader("👀 SSIM File Preview")
                                    
                                    # Show first few flight lines for preview
                                    preview_lines = []
                                    line_count = 0
                                    for line in ssim_lines:
                                        if line_count < 5 or line.startswith('3 ') or line.startswith('5 '):
                                            preview_lines.append(line.rstrip())
                                            if line.startswith('3 '):
                                                line_count += 1
                                                if line_count > 8:  # Show max 5 flight lines
                                                    break
                                    
                                    st.code("\\n".join(preview_lines), language="text")
                                    
                                else:
                                    st.error("❌ Conversion failed. Please check your data and try again.")
                                
                            except Exception as e:
                                st.error(f"❌ Conversion error: {str(e)}")
                                st.exception(e)
                            
                            finally:
                                # Clean up temporary file
                                if os.path.exists(temp_file_path):
                                    os.remove(temp_file_path)
            
            else:
                st.error("❌ Could not identify airline column in the file")
                st.info("Expected columns: 'Mkt Al', 'Op Al', 'Airline', or 'Carrier'")
                st.subheader("Available Columns:")
                st.write(df.columns.tolist())
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            
            # Clean up temporary file on error
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    # Help Section
    st.markdown("---")
    with st.expander("❓ Help & Technical Information"):
        st.markdown("""
        ### 📖 How to use:
        
        1. **Upload**: Upload your Excel file with CIRUIM schedule
        2. **Preview**: Review available airlines and data
        3. **Select**: Choose the airline for conversion
        4. **Convert**: Click "Convert to SSIM"
        5. **Validate**: Check the SSIM structure
        6. **Download**: Download the generated SSIM file
        
        ### 📋 Expected CIRUIM Format:
        
        The file must contain these columns (starting from row 5):
        - `Mkt Al` or `Op Al`: Airline code (2 letters)
        - `Orig`: Origin airport (IATA code)
        - `Dest`: Destination airport (IATA code)
        - `Flight`: Flight number
        - `Eff Date`: Effective date
        - `Disc Date`: Discontinue date
        - `Op Days`: Operating days (format: 1234567)
        
        ### 🔧 Technical Features:
        
        - **200-Character Lines**: Proper SSIM formatting
        - **Complete Structure**: Header, Carrier Info, Flight Records, Footer
        - **Timezone Support**: Automatic timezone mapping
        - **Aircraft Mapping**: ICAO to IATA conversion
        - **Data Validation**: Integrity checks and format validation
        - **Multiple Airlines**: Support for various airlines in same file
        
        ### 📞 Support:
        Developed by **Capacity Dnata Brasil** for professional airline operations.
        """)
        
        # Add version info separately to avoid formatting issues
        version_info = get_version_info()
        st.markdown("### 📋 Version Information:")
        st.markdown(f"""
        - **Version:** {version_info['version']}
        - **Release Date:** {version_info['date']}
        - **Latest Changes:** {version_info['notes']}
        """)

if __name__ == "__main__":
    main()
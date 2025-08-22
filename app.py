import streamlit as st
import pandas as pd
from datetime import datetime
import os
from ts09_to_ssim_converter import gerar_ssim_ts09

def main():
    st.set_page_config(
        page_title="TS Schedule to SSIM Converter - Dnata Brasil", 
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Header
    st.title("✈️ TS Schedule to SSIM Converter")
    st.markdown("**Developed by Capacity Dnata Brasil**")
    st.markdown("---")
    
    st.markdown("""
    ### 📋 About This Converter
    
    This converter transforms airline schedules from **TS Schedule format** (Excel) 
    to **SSIM** (Standard Schedules Information Manual) format.
    
    **Key Features:**
    - ✅ Preserves original flight order from schedule
    - ✅ Correctly extracts next flights from "Onward Flight" column
    - ✅ Processes complex connections (including values with "/")
    - ✅ Generates SSIM file compatible with industry standards
    - ✅ Professional-grade output for airline operations
    """)
    
    st.markdown("---")
    
    # Upload and Settings
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 Upload TS Schedule")
        uploaded_file = st.file_uploader(
            "Select Excel file with TS schedule:",
            type=['xlsx', 'xls'],
            help="Upload Excel file containing schedule in TS format"
        )
    
    with col2:
        st.subheader("⚙️ Settings")
        codigo_iata = st.text_input(
            "Airline IATA Code:",
            value="TS",
            max_chars=2,
            help="2-letter IATA code"
        ).upper()
        
        nome_arquivo = st.text_input(
            "Output filename (optional):",
            placeholder="Auto-generated if empty",
            help="Leave empty for automatic naming"
        )
    
    # Validation
    if not codigo_iata or len(codigo_iata) != 2:
        st.warning("⚠️ Please enter a valid 2-character IATA code.")
        return
    
    if uploaded_file is not None:
        st.markdown("---")
        
        try:
            # Save temporary file
            temp_file_path = f"temp_{uploaded_file.name}"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Read and preview data
            df = pd.read_excel(temp_file_path)
            
            st.subheader("👀 Data Preview")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Rows", len(df))
            with col2:
                st.metric("✈️ Unique Flights", df['Flight-Number'].nunique())
            with col3:
                st.metric("📅 Period", f"{df['Date-LT'].min()} - {df['Date-LT'].max()}")
            
            # Show sample data
            st.dataframe(
                df[['Flight-Number', 'Route', 'Date-LT', 'Std-LT', 'Sta-LT', 'Onward Flight']].head(10),
                use_container_width=True
            )
            
            # Data integrity check
            st.subheader("🔍 Data Integrity Check")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Check required columns
                required_columns = ['Flight-Number', 'Route', 'Date-LT', 'Std-LT', 'Sta-LT', 'Onward Flight']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"❌ Missing columns: {', '.join(missing_columns)}")
                else:
                    st.success("✅ All required columns present")
            
            with col2:
                # Check onward flight values
                problematic_values = []
                for _, row in df.iterrows():
                    onward = row['Onward Flight']
                    if pd.notna(onward) and isinstance(onward, str):
                        clean_onward = onward.replace('TS', '').strip()
                        if not clean_onward.isdigit() and '/' not in clean_onward:
                            problematic_values.append(onward)
                
                if problematic_values:
                    st.warning(f"⚠️ {len(set(problematic_values))} atypical Onward Flight values")
                else:
                    st.success("✅ Onward Flight values OK")
            
            st.markdown("---")
            
            # Convert button
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("🚀 Convert to SSIM", type="primary", use_container_width=True):
                    
                    with st.spinner("Converting TS schedule to SSIM..."):
                        try:
                            # Determine output filename
                            if nome_arquivo:
                                output_file = nome_arquivo if nome_arquivo.endswith('.ssim') else nome_arquivo + '.ssim'
                            else:
                                output_file = None
                            
                            # Execute conversion
                            resultado = gerar_ssim_ts09(temp_file_path, codigo_iata, output_file)
                            
                            st.success("✅ Conversion completed successfully!")
                            st.info(f"📄 Generated file: {resultado}")
                            
                            # Offer download
                            with open(resultado, 'rb') as file:
                                st.download_button(
                                    label="📥 Download SSIM File",
                                    data=file.read(),
                                    file_name=os.path.basename(resultado),
                                    mime="text/plain",
                                    type="primary",
                                    use_container_width=True
                                )
                            
                            # Conversion statistics
                            st.subheader("📊 Conversion Statistics")
                            
                            # Read generated file for stats
                            with open(resultado, 'r') as f:
                                ssim_lines = f.readlines()
                            
                            flight_lines = [line for line in ssim_lines if line.startswith('3 ')]
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("📄 Total SSIM Lines", len(ssim_lines))
                            with col2:
                                st.metric("✈️ Flight Records", len(flight_lines))
                            with col3:
                                st.metric("🔗 Connections Processed", df['Onward Flight'].notna().sum())
                            with col4:
                                st.metric("📁 File Size", f"{os.path.getsize(resultado)} bytes")
                                
                            # Show SSIM preview
                            st.subheader("👀 SSIM File Preview")
                            
                            preview_lines = ssim_lines[:10] + ["...\n"] + ssim_lines[-5:] if len(ssim_lines) > 15 else ssim_lines
                            st.code("".join(preview_lines), language="text")
                            
                        except Exception as e:
                            st.error(f"❌ Conversion error: {str(e)}")
                            st.exception(e)
                        
                        finally:
                            # Clean up temporary file
                            if os.path.exists(temp_file_path):
                                os.remove(temp_file_path)
            
        except Exception as e:
            st.error(f"❌ File processing error: {str(e)}")
            
            # Clean up temporary file on error
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    # Help section
    st.markdown("---")
    with st.expander("❓ Help & Technical Information"):
        st.markdown("""
        ### 📖 How to use:
        
        1. **Upload**: Upload your Excel file with TS schedule
        2. **Settings**: Enter airline IATA code
        3. **Preview**: Check loaded data
        4. **Convert**: Click "Convert to SSIM"
        5. **Download**: Download generated SSIM file
        
        ### 📋 Expected TS Format:
        
        The file must contain these columns:
        - `Flight-Number`: Flight number
        - `Route`: Route (format: "ORIGIN / DESTINATION")
        - `Date-LT`: Local date
        - `Std-LT`: Departure time local
        - `Sta-LT`: Arrival time local
        - `Onward Flight`: Next flight (format: "TSxxx")
        - `Aircraft-Type`: Aircraft type
        - `Type`: Service type (J/F)
        
        ### 🔧 Technical Features:
        
        - **Order Preservation**: Original flight order is maintained
        - **Smart Connections**: Correctly processes values like "TS840/1"
        - **Data Validation**: Checks integrity before conversion
        - **Standard SSIM**: Generates IATA-compatible files
        
        ### 📞 Support:
        Developed by **Capacity Dnata Brasil** for professional airline operations.
        """)

if __name__ == "__main__":
    main()

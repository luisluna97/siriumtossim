import streamlit as st
import pandas as pd
from datetime import datetime
import os
from sirium_to_ssim_converter import gerar_ssim_sirium, gerar_ssim_todas_companias
from version import get_version_info

def main():
    st.set_page_config(
        page_title="CIRUIM to SSIM Converter - Dnata Brasil", 
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Header compacto
    version_info = get_version_info()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("✈️ CIRUIM to SSIM Converter")
        st.markdown("**Developed by Capacity Dnata Brasil**")
    
    with col2:
        st.markdown("### 🔗 Links")
        st.markdown("[📱 GitHub](https://github.com/luisluna97/siriumtossim)")
        st.markdown(f"**v{version_info['version']}** • {version_info['date']}")
    
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
                    # Adicionar opção "All Companies"
                    airline_options = ["ALL_COMPANIES"] + available_airlines
                    airline_labels = ["🌍 All Companies"] + [f"✈️ {airline}" for airline in available_airlines]
                    
                    selected_option = st.selectbox(
                        "Select Conversion Option:",
                        options=airline_options,
                        format_func=lambda x: airline_labels[airline_options.index(x)],
                        help="Choose specific airline or all companies in one file"
                    )
                    
                    selected_airline = selected_option
                
                with col2:
                    output_filename = st.text_input(
                        "Output filename (optional):",
                        placeholder="Auto-generated if empty",
                        help="Leave empty for automatic naming"
                    )
                
                # Filter data by selected airline
                if selected_airline == "ALL_COMPANIES":
                    df_filtered = df  # Usar todos os dados
                    display_airline = "ALL"
                else:
                    df_filtered = df[df[airline_col] == selected_airline]
                    display_airline = selected_airline
                
                # Show filtered data preview
                if selected_airline == "ALL_COMPANIES":
                    st.subheader(f"📋 All Companies Schedule Preview ({len(available_airlines)} airlines)")
                else:
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
                        if selected_airline == "ALL_COMPANIES":
                            st.success(f"✅ {len(df_filtered)} flights found for all companies")
                        else:
                            st.success(f"✅ {len(df_filtered)} flights found for {selected_airline}")
                    else:
                        if selected_airline == "ALL_COMPANIES":
                            st.error(f"❌ No flights found for any company")
                        else:
                            st.error(f"❌ No flights found for {selected_airline}")
                
                st.markdown("---")
                
                # Conversion Button
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col2:
                    if st.button("🚀 Convert to SSIM", type="primary", use_container_width=True):
                        
                        if len(df_filtered) == 0:
                            if selected_airline == "ALL_COMPANIES":
                                st.error(f"❌ Cannot convert: no flights found for any company")
                            else:
                                st.error(f"❌ Cannot convert: no flights found for {selected_airline}")
                            return
                        
                        conversion_label = "all companies" if selected_airline == "ALL_COMPANIES" else selected_airline
                        with st.spinner(f"Converting {conversion_label} schedule to SSIM..."):
                            try:
                                # Determine output filename
                                if output_filename:
                                    output_file = output_filename if output_filename.endswith('.ssim') else output_filename + '.ssim'
                                else:
                                    output_file = None
                                
                                # Execute conversion
                                if selected_airline == "ALL_COMPANIES":
                                    result = gerar_ssim_todas_companias(temp_file_path, output_file)
                                else:
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
                                        if selected_airline == "ALL_COMPANIES":
                                            st.metric("🏢 Airlines", f"{len(available_airlines)} companies")
                                        else:
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
                                    
                                    # Show first 50 lines for preview
                                    preview_lines = []
                                    line_count = 0
                                    for line in ssim_lines:
                                        preview_lines.append(line.rstrip())
                                        line_count += 1
                                        if line_count >= 50:  # Show max 50 lines
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
    
    # Footer compacto
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.expander("❓ Help & Format Info"):
            st.markdown("""
            **📖 How to use:** Upload Excel → Select airline/All Companies → Convert → Download
            
            **📋 Required columns (row 5):** `Mkt Al/Op Al`, `Orig`, `Dest`, `Flight`, `Eff Date`, `Disc Date`, `Op Days`
            
            **🔧 Output:** IATA-standard SSIM files with 200-character lines
            """)
    
    with col2:
        with st.expander("📋 Version Updates"):
            version_info = get_version_info()
            st.markdown(f"""
            **v{version_info['version']}** - {version_info['date']}
            
            {version_info['notes']}
            
            **Previous versions:**
            - v1.0.1.1 - SIRIUM → CIRUIM rebrand
            - v1.0.0 - Initial release
            """)

if __name__ == "__main__":
    main()
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Importar os conversores
try:
    from ts09_to_ssim_converter import gerar_ssim_ts09
    TS09_AVAILABLE = True
except ImportError:
    TS09_AVAILABLE = False

try:
    from sfo_to_ssim_converter import gerar_ssim_sfo
    SFO_AVAILABLE = True
except ImportError:
    SFO_AVAILABLE = False

def detect_file_type(uploaded_file):
    """Detecta o tipo de arquivo baseado no conteúdo"""
    try:
        # Salvar arquivo temporário
        temp_file_path = f"temp_detect_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Tentar ler como TS.09 (header padrão)
        try:
            df_ts09 = pd.read_excel(temp_file_path)
            if 'Flight-Number' in df_ts09.columns and 'Onward Flight' in df_ts09.columns:
                os.remove(temp_file_path)
                return "TS09"
        except:
            pass
        
        # Tentar ler como SFO (header=4)
        try:
            df_sfo = pd.read_excel(temp_file_path, header=4)
            if any(col in df_sfo.columns for col in ['Mkt Al', 'Op Al']) and 'Orig' in df_sfo.columns:
                os.remove(temp_file_path)
                return "SFO"
        except:
            pass
        
        # Limpar arquivo temporário
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        return "UNKNOWN"
        
    except Exception as e:
        return "ERROR"

def main():
    st.set_page_config(
        page_title="Multi Schedule to SSIM Converter - Dnata Brasil", 
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Header
    st.title("✈️ Multi Schedule to SSIM Converter")
    st.markdown("**Desenvolvido pela Capacity Dnata Brasil**")
    st.markdown("---")
    
    st.markdown("""
    ### 📋 Sobre Este Conversor
    
    Este conversor suporta múltiplos formatos de malhas aéreas para **SSIM** (Standard Schedules Information Manual):
    
    **Formatos Suportados:**
    - ✅ **TS.09 Format**: Malhas TS com coluna "Onward Flight"
    - ✅ **SFO Format**: SFO Schedule Weekly Extract Reports
    
    **Características principais:**
    - 🤖 **Detecção Automática**: Identifica automaticamente o formato do arquivo
    - 🏢 **Múltiplas Companhias**: Suporte para seleção de companhia aérea específica
    - ✅ **Validação de Dados**: Verificação de integridade antes da conversão
    - 📄 **SSIM Padrão**: Gera arquivos compatíveis com padrões IATA
    """)
    
    # Mostrar status dos conversores
    col1, col2 = st.columns(2)
    with col1:
        if TS09_AVAILABLE:
            st.success("✅ Conversor TS.09 disponível")
        else:
            st.error("❌ Conversor TS.09 não disponível")
    
    with col2:
        if SFO_AVAILABLE:
            st.success("✅ Conversor SFO disponível")
        else:
            st.error("❌ Conversor SFO não disponível")
    
    st.markdown("---")
    
    # Upload
    st.subheader("📁 Upload da Malha")
    uploaded_file = st.file_uploader(
        "Selecione o arquivo Excel com a malha:",
        type=['xlsx', 'xls'],
        help="Upload do arquivo Excel (TS.09 ou SFO format)"
    )
    
    if uploaded_file is not None:
        # Detectar tipo de arquivo
        with st.spinner("Analisando formato do arquivo..."):
            file_type = detect_file_type(uploaded_file)
        
        st.markdown("---")
        
        if file_type == "TS09":
            st.success("🎯 **Formato Detectado: TS.09**")
            if TS09_AVAILABLE:
                handle_ts09_conversion(uploaded_file)
            else:
                st.error("❌ Conversor TS.09 não está disponível")
                
        elif file_type == "SFO":
            st.success("🎯 **Formato Detectado: SFO Schedule**")
            if SFO_AVAILABLE:
                handle_sfo_conversion(uploaded_file)
            else:
                st.error("❌ Conversor SFO não está disponível")
                
        elif file_type == "UNKNOWN":
            st.warning("⚠️ **Formato não reconhecido**")
            st.info("Por favor, selecione manualmente o tipo de arquivo:")
            
            format_choice = st.radio(
                "Escolha o formato:",
                ["TS.09 Format", "SFO Format"],
                help="Selecione o formato correto do seu arquivo"
            )
            
            if format_choice == "TS.09 Format" and TS09_AVAILABLE:
                handle_ts09_conversion(uploaded_file)
            elif format_choice == "SFO Format" and SFO_AVAILABLE:
                handle_sfo_conversion(uploaded_file)
            else:
                st.error("❌ Conversor selecionado não está disponível")
                
        else:
            st.error("❌ Erro ao analisar o arquivo")
    
    # Seção de ajuda
    st.markdown("---")
    with st.expander("❓ Ajuda & Informações Técnicas"):
        st.markdown("""
        ### 📖 Formatos Suportados:
        
        #### **TS.09 Format**
        - Arquivo Excel com colunas: `Flight-Number`, `Route`, `Date-LT`, `Std-LT`, `Sta-LT`, `Onward Flight`
        - Suporte para conexões via coluna "Onward Flight"
        - Preserva ordem original dos voos
        
        #### **SFO Format**  
        - SFO Schedule Weekly Extract Report
        - Header na linha 5
        - Colunas: `Mkt Al`, `Op Al`, `Orig`, `Dest`, `Flight`, `Eff Date`, `Disc Date`
        - Suporte para múltiplas companhias aéreas
        
        ### 🔧 Como usar:
        
        1. **Upload**: Faça upload do arquivo Excel
        2. **Detecção**: O sistema detecta automaticamente o formato
        3. **Configuração**: Configure parâmetros específicos
        4. **Conversão**: Execute a conversão para SSIM
        5. **Download**: Baixe o arquivo SSIM gerado
        
        ### 📞 Suporte:
        Desenvolvido pela **Capacity Dnata Brasil** para operações aéreas profissionais.
        """)

def handle_ts09_conversion(uploaded_file):
    """Manipula conversão de arquivos TS.09"""
    st.subheader("⚙️ Configuração TS.09")
    
    col1, col2 = st.columns(2)
    
    with col1:
        codigo_iata = st.text_input(
            "Código IATA da Companhia:",
            value="TS",
            max_chars=2,
            help="Código IATA de 2 letras"
        ).upper()
    
    with col2:
        nome_arquivo = st.text_input(
            "Nome do arquivo (opcional):",
            placeholder="Gerado automaticamente se vazio"
        )
    
    if not codigo_iata or len(codigo_iata) != 2:
        st.warning("⚠️ Por favor, insira um código IATA válido de 2 caracteres.")
        return
    
    # Prévia dos dados
    try:
        temp_file_path = f"temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        df = pd.read_excel(temp_file_path)
        
        st.subheader("👀 Prévia dos Dados TS.09")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total de Voos", len(df))
        with col2:
            st.metric("✈️ Voos Únicos", df['Flight-Number'].nunique())
        with col3:
            if 'Date-LT' in df.columns:
                st.metric("📅 Período", f"{df['Date-LT'].min()} - {df['Date-LT'].max()}")
        
        # Mostrar amostra
        cols_to_show = ['Flight-Number', 'Route', 'Date-LT', 'Std-LT', 'Sta-LT', 'Onward Flight']
        available_cols = [col for col in cols_to_show if col in df.columns]
        st.dataframe(df[available_cols].head(10), use_container_width=True)
        
        # Botão de conversão
        if st.button("🚀 Converter TS.09 para SSIM", type="primary", use_container_width=True):
            with st.spinner("Convertendo TS.09 para SSIM..."):
                try:
                    output_file = nome_arquivo if nome_arquivo else None
                    resultado = gerar_ssim_ts09(temp_file_path, codigo_iata, output_file)
                    
                    if resultado:
                        st.success("✅ Conversão TS.09 realizada com sucesso!")
                        
                        with open(resultado, 'rb') as file:
                            st.download_button(
                                label="📥 Baixar Arquivo SSIM",
                                data=file.read(),
                                file_name=os.path.basename(resultado),
                                mime="text/plain",
                                type="primary"
                            )
                    else:
                        st.error("❌ Falha na conversão TS.09")
                        
                except Exception as e:
                    st.error(f"❌ Erro na conversão TS.09: {str(e)}")
        
        # Limpar arquivo temporário
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo TS.09: {str(e)}")

def handle_sfo_conversion(uploaded_file):
    """Manipula conversão de arquivos SFO"""
    st.subheader("⚙️ Configuração SFO")
    
    # Primeiro, ler arquivo para obter companhias disponíveis
    companhias_disponiveis = []
    try:
        temp_file_path = f"temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        df_preview = pd.read_excel(temp_file_path, header=4)
        
        airline_col = None
        for col in ['Mkt Al', 'Op Al', 'Airline', 'Carrier']:
            if col in df_preview.columns:
                airline_col = col
                break
        
        if airline_col:
            companhias_disponiveis = sorted(df_preview[airline_col].unique())
        
    except Exception as e:
        st.error(f"Erro ao ler arquivo SFO: {e}")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if companhias_disponiveis:
            codigo_iata = st.selectbox(
                "Selecione a Companhia Aérea:",
                options=companhias_disponiveis,
                help="Escolha a companhia aérea para conversão"
            )
        else:
            codigo_iata = st.text_input(
                "Código IATA da Companhia:",
                value="XX",
                max_chars=2,
                help="Código IATA de 2 letras"
            ).upper()
    
    with col2:
        nome_arquivo = st.text_input(
            "Nome do arquivo (opcional):",
            placeholder="Gerado automaticamente se vazio"
        )
    
    # Prévia dos dados
    try:
        if airline_col:
            df_filtered = df_preview[df_preview[airline_col] == codigo_iata]
        else:
            df_filtered = df_preview
        
        st.subheader("👀 Prévia dos Dados SFO")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total de Linhas", len(df_preview))
        with col2:
            st.metric("✈️ Voos da Companhia", len(df_filtered))
        with col3:
            if 'Flight' in df_filtered.columns:
                st.metric("🔢 Voos Únicos", df_filtered['Flight'].nunique())
        
        if len(df_filtered) > 0:
            # Mostrar amostra
            cols_to_show = ['Mkt Al', 'Op Al', 'Orig', 'Dest', 'Flight', 'Eff Date', 'Disc Date']
            available_cols = [col for col in cols_to_show if col in df_filtered.columns]
            st.dataframe(df_filtered[available_cols].head(10), use_container_width=True)
            
            # Botão de conversão
            if st.button("🚀 Converter SFO para SSIM", type="primary", use_container_width=True):
                with st.spinner("Convertendo SFO para SSIM..."):
                    try:
                        output_file = nome_arquivo if nome_arquivo else None
                        resultado = gerar_ssim_sfo(temp_file_path, codigo_iata, output_file)
                        
                        if resultado:
                            st.success("✅ Conversão SFO realizada com sucesso!")
                            
                            with open(resultado, 'rb') as file:
                                st.download_button(
                                    label="📥 Baixar Arquivo SSIM",
                                    data=file.read(),
                                    file_name=os.path.basename(resultado),
                                    mime="text/plain",
                                    type="primary"
                                )
                        else:
                            st.error("❌ Falha na conversão SFO")
                            
                    except Exception as e:
                        st.error(f"❌ Erro na conversão SFO: {str(e)}")
        else:
            st.warning(f"⚠️ Nenhum voo encontrado para {codigo_iata}")
            if companhias_disponiveis:
                st.info(f"Companhias disponíveis: {', '.join(companhias_disponiveis)}")
    
    # Limpar arquivo temporário
    if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
        os.remove(temp_file_path)

if __name__ == "__main__":
    main()

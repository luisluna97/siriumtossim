import streamlit as st
import pandas as pd
from datetime import datetime
import os
from sfo_to_ssim_converter import gerar_ssim_sfo

def main():
    st.set_page_config(
        page_title="SFO Schedule to SSIM Converter - Dnata Brasil", 
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Header
    st.title("✈️ SFO Schedule to SSIM Converter")
    st.markdown("**Desenvolvido pela Capacity Dnata Brasil**")
    st.markdown("---")
    
    st.markdown("""
    ### 📋 Sobre Este Conversor
    
    Este conversor transforma malhas aéreas do formato **SFO Schedule Extract Report** (Excel) 
    para **SSIM** (Standard Schedules Information Manual).
    
    **Características principais:**
    - ✅ Suporte para múltiplas companhias aéreas
    - ✅ Seleção de companhia específica
    - ✅ Processamento de dados SFO padrão
    - ✅ Geração de arquivo SSIM compatível com padrões da indústria
    - ✅ Interface profissional para operações aéreas
    """)
    
    st.markdown("---")
    
    # Upload e Configurações
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 Upload da Malha SFO")
        uploaded_file = st.file_uploader(
            "Selecione o arquivo Excel com a malha SFO:",
            type=['xlsx', 'xls'],
            help="Upload do arquivo Excel contendo malha no formato SFO"
        )
    
    with col2:
        st.subheader("⚙️ Configurações")
        
        # Primeiro, vamos verificar se há arquivo carregado para mostrar as companhias
        companhias_disponiveis = []
        if uploaded_file is not None:
            try:
                # Salvar arquivo temporário
                temp_file_path = f"temp_{uploaded_file.name}"
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Ler para obter companhias
                df_preview = pd.read_excel(temp_file_path, header=4)
                
                # Procurar coluna de companhia aérea
                airline_col = None
                for col in ['Mkt Al', 'Op Al', 'Airline', 'Carrier']:
                    if col in df_preview.columns:
                        airline_col = col
                        break
                
                if airline_col:
                    companhias_disponiveis = sorted(df_preview[airline_col].unique())
                
                # Limpar arquivo temporário
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")
        
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
                help="Código IATA de 2 letras da companhia"
            ).upper()
        
        nome_arquivo = st.text_input(
            "Nome do arquivo (opcional):",
            placeholder="Gerado automaticamente se vazio",
            help="Deixe vazio para nomenclatura automática"
        )
    
    # Validação
    if not codigo_iata or len(codigo_iata) != 2:
        st.warning("⚠️ Por favor, insira um código IATA válido de 2 caracteres.")
        return
    
    if uploaded_file is not None:
        st.markdown("---")
        
        try:
            # Salvar arquivo temporário
            temp_file_path = f"temp_{uploaded_file.name}"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Ler e prévia dos dados
            df = pd.read_excel(temp_file_path, header=4)
            
            st.subheader("👀 Prévia dos Dados")
            
            # Encontrar coluna de companhia
            airline_col = None
            for col in ['Mkt Al', 'Op Al', 'Airline', 'Carrier']:
                if col in df.columns:
                    airline_col = col
                    break
            
            # Filtrar dados pela companhia selecionada
            if airline_col:
                df_filtered = df[df[airline_col] == codigo_iata]
            else:
                df_filtered = df
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total de Linhas", len(df))
            with col2:
                st.metric("✈️ Voos da Companhia", len(df_filtered))
            with col3:
                if 'Flight' in df_filtered.columns:
                    st.metric("🔢 Voos Únicos", df_filtered['Flight'].nunique())
                else:
                    st.metric("🔢 Registros", len(df_filtered))
            
            # Mostrar dados de amostra
            if len(df_filtered) > 0:
                # Selecionar colunas relevantes para mostrar
                cols_to_show = []
                for col in ['Mkt Al', 'Op Al', 'Orig', 'Dest', 'Flight', 'Eff Date', 'Disc Date', 'Op Days']:
                    if col in df_filtered.columns:
                        cols_to_show.append(col)
                
                if cols_to_show:
                    st.dataframe(
                        df_filtered[cols_to_show].head(10),
                        use_container_width=True
                    )
                else:
                    st.dataframe(df_filtered.head(10), use_container_width=True)
            else:
                st.warning(f"⚠️ Nenhum voo encontrado para a companhia {codigo_iata}")
                st.info("Companhias disponíveis no arquivo:")
                if airline_col:
                    for comp in sorted(df[airline_col].unique()):
                        st.write(f"- {comp}")
            
            # Verificação de integridade dos dados
            st.subheader("🔍 Verificação de Integridade")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Verificar colunas obrigatórias
                required_columns = ['Orig', 'Dest']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"❌ Colunas obrigatórias ausentes: {', '.join(missing_columns)}")
                else:
                    st.success("✅ Colunas obrigatórias presentes")
            
            with col2:
                # Verificar dados da companhia selecionada
                if len(df_filtered) > 0:
                    st.success(f"✅ {len(df_filtered)} voos encontrados para {codigo_iata}")
                else:
                    st.error(f"❌ Nenhum voo encontrado para {codigo_iata}")
            
            st.markdown("---")
            
            # Botão de conversão
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("🚀 Converter para SSIM", type="primary", use_container_width=True):
                    
                    if len(df_filtered) == 0:
                        st.error(f"❌ Não é possível converter: nenhum voo encontrado para {codigo_iata}")
                        return
                    
                    with st.spinner("Convertendo malha SFO para SSIM..."):
                        try:
                            # Determinar nome do arquivo de saída
                            if nome_arquivo:
                                output_file = nome_arquivo if nome_arquivo.endswith('.ssim') else nome_arquivo + '.ssim'
                            else:
                                output_file = None
                            
                            # Executar conversão
                            resultado = gerar_ssim_sfo(temp_file_path, codigo_iata, output_file)
                            
                            if resultado:
                                st.success("✅ Conversão realizada com sucesso!")
                                st.info(f"📄 Arquivo gerado: {resultado}")
                                
                                # Oferecer download
                                with open(resultado, 'rb') as file:
                                    st.download_button(
                                        label="📥 Baixar Arquivo SSIM",
                                        data=file.read(),
                                        file_name=os.path.basename(resultado),
                                        mime="text/plain",
                                        type="primary",
                                        use_container_width=True
                                    )
                                
                                # Estatísticas da conversão
                                st.subheader("📊 Estatísticas da Conversão")
                                
                                # Ler arquivo gerado para estatísticas
                                with open(resultado, 'r') as f:
                                    ssim_lines = f.readlines()
                                
                                flight_lines = [line for line in ssim_lines if line.startswith('3 ')]
                                
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("📄 Linhas SSIM", len(ssim_lines))
                                with col2:
                                    st.metric("✈️ Registros de Voo", len(flight_lines))
                                with col3:
                                    st.metric("🏢 Companhia", codigo_iata)
                                with col4:
                                    st.metric("📁 Tamanho", f"{os.path.getsize(resultado)} bytes")
                                    
                                # Mostrar prévia do arquivo SSIM
                                st.subheader("👀 Prévia do Arquivo SSIM")
                                
                                preview_lines = ssim_lines[:10] + ["...\\n"] + ssim_lines[-5:] if len(ssim_lines) > 15 else ssim_lines
                                st.code("".join(preview_lines), language="text")
                                
                                # Limpar arquivo gerado após download (opcional)
                                # os.remove(resultado)
                                
                            else:
                                st.error("❌ Falha na conversão. Verifique os dados e tente novamente.")
                            
                        except Exception as e:
                            st.error(f"❌ Erro na conversão: {str(e)}")
                            st.exception(e)
                        
                        finally:
                            # Limpar arquivo temporário
                            if os.path.exists(temp_file_path):
                                os.remove(temp_file_path)
            
        except Exception as e:
            st.error(f"❌ Erro no processamento do arquivo: {str(e)}")
            
            # Limpar arquivo temporário em caso de erro
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    # Seção de ajuda
    st.markdown("---")
    with st.expander("❓ Ajuda & Informações Técnicas"):
        st.markdown("""
        ### 📖 Como usar:
        
        1. **Upload**: Faça upload do arquivo Excel com malha SFO
        2. **Seleção**: Escolha a companhia aérea desejada
        3. **Prévia**: Verifique os dados carregados
        4. **Conversão**: Clique em "Converter para SSIM"
        5. **Download**: Baixe o arquivo SSIM gerado
        
        ### 📋 Formato SFO Esperado:
        
        O arquivo deve conter estas colunas (a partir da linha 5):
        - `Mkt Al` ou `Op Al`: Código da companhia aérea
        - `Orig`: Aeroporto de origem (código IATA)
        - `Dest`: Aeroporto de destino (código IATA)
        - `Flight`: Número do voo
        - `Eff Date`: Data de início da operação
        - `Disc Date`: Data de fim da operação
        - `Op Days`: Dias operacionais (formato: 1234567)
        
        ### 🔧 Características Técnicas:
        
        - **Múltiplas Companhias**: Suporte para várias companhias no mesmo arquivo
        - **Seleção Inteligente**: Interface para escolher companhia específica
        - **Validação de Dados**: Verificação de integridade antes da conversão
        - **SSIM Padrão**: Gera arquivos compatíveis com padrão IATA
        - **Preservação de Dados**: Mantém informações originais de horários e frequências
        
        ### 📞 Suporte:
        Desenvolvido pela **Capacity Dnata Brasil** para operações aéreas profissionais.
        """)

if __name__ == "__main__":
    main()

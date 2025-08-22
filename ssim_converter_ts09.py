import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import os

def ajustar_linha(line, comprimento=200):
    """Ajusta o comprimento da linha para exatamente 200 caracteres"""
    return line.ljust(comprimento)[:comprimento]

def determinar_dia_semana(weekday_num):
    """
    Converte o número do dia da semana (1-7) para o formato SSIM
    1 = Segunda, 2 = Terça, ..., 7 = Domingo
    """
    frequencia = [" "] * 7
    if 1 <= weekday_num <= 7:
        frequencia[weekday_num - 1] = str(weekday_num)
    return "".join(frequencia)

def determinar_status(tipo):
    """Determina o status do voo baseado no tipo"""
    tipo_lower = str(tipo).lower()
    if "j" in tipo_lower:
        return "J"  # Passageiro
    else:
        return "F"  # Carga

def format_timezone_offset(offset_str):
    """Formata o offset de timezone para o padrão SSIM"""
    try:
        offset = float(offset_str)
        hours = int(offset)
        minutes = int(abs(offset - hours) * 60)
        if offset >= 0:
            sign = '+'
        else:
            sign = '-'
            hours = -hours
        offset_formatted = f"{sign}{abs(hours):02}{minutes:02}"
        return offset_formatted
    except (ValueError, TypeError):
        return '+0000'

def parse_datetime(date_str, time_str):
    """Converte data e hora do formato TS.09 para datetime"""
    try:
        # Formato esperado: '01SEP25' e '22:45'
        date_part = pd.to_datetime(date_str, format='%d%b%y')
        time_part = pd.to_datetime(time_str, format='%H:%M').time()
        return datetime.combine(date_part.date(), time_part)
    except:
        return None

def extract_airport_codes(route):
    """Extrai códigos de aeroportos da rota (formato: 'YYZ / LGW')"""
    try:
        parts = route.split(' / ')
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        return None, None
    except:
        return None, None

def gerar_ssim_ts09(excel_path, codigo_iata, output_file=None):
    """
    Gera arquivo SSIM a partir do arquivo TS.09 com casamento correto de voos
    """
    try:
        # Ler o arquivo TS.09
        df = pd.read_excel(excel_path)
        
        st.info(f"Arquivo carregado com {len(df)} registros")
        
        # Carregar arquivos de referência
        try:
            airport_df = pd.read_csv('airport.csv')
            airport_df['IATA'] = airport_df['IATA'].str.strip().str.upper()
            airport_df['Timezone'] = airport_df['Timezone'].replace('\\\\N', '0')
            airport_df['Timezone'] = pd.to_numeric(airport_df['Timezone'], errors='coerce').fillna(0)
            iata_to_timezone = dict(zip(airport_df['IATA'], airport_df['Timezone']))
        except:
            st.warning("Arquivo airport.csv não encontrado. Usando timezone padrão.")
            iata_to_timezone = {}
        
        try:
            aircraft_df = pd.read_excel('ACT TYPE.xlsx')
            aircraft_df['ICAO'] = aircraft_df['ICAO'].str.strip().str.upper()
            aircraft_df['IATA'] = aircraft_df['IATA'].str.strip()
            icao_to_iata_aircraft = dict(zip(aircraft_df['ICAO'], aircraft_df['IATA']))
        except:
            st.warning("Arquivo ACT TYPE.xlsx não encontrado. Usando códigos originais.")
            icao_to_iata_aircraft = {}
        
        # Processar dados do TS.09
        processed_flights = []
        
        for _, row in df.iterrows():
            # Extrair informações básicas
            aircraft_type = str(row['Aircraft-Type']).strip()
            acv = str(row['ACV']).strip()
            date_lt = str(row['Date-LT']).strip()
            weekday = int(row['Week-Day-LT'])
            flight_type = str(row['Type']).strip()
            carrier = str(row['Flight-Carrier']).strip()
            flight_number = int(row['Flight-Number'])
            std_utc = str(row['Std-UTC']).strip()
            std_lt = str(row['Std-LT']).strip()
            route = str(row['Route']).strip()
            sta_utc = str(row['Sta-UTC']).strip()
            sta_lt = str(row['Sta-LT']).strip()
            duration = str(row['Duration']).strip()
            
            # Processar próximo voo (conexão correta!)
            onward_flight = row['Onward Flight']
            next_flight = None
            if pd.notna(onward_flight):
                # Remover prefixo da companhia se existir
                next_flight = str(onward_flight).replace(carrier, '').strip()
                try:
                    next_flight = int(next_flight)
                except:
                    next_flight = None
            
            # Extrair aeroportos da rota
            origem, destino = extract_airport_codes(route)
            
            # Converter datas e horários
            partida_dt = parse_datetime(date_lt, std_lt)
            chegada_dt = parse_datetime(date_lt, sta_lt)
            
            # Ajustar data de chegada se for no dia seguinte
            if chegada_dt and partida_dt and chegada_dt < partida_dt:
                chegada_dt += timedelta(days=1)
            
            if not partida_dt or not chegada_dt or not origem or not destino:
                continue
            
            # Obter timezones
            origem_tz = iata_to_timezone.get(origem, 0)
            destino_tz = iata_to_timezone.get(destino, 0)
            
            # Converter código de aeronave
            aircraft_iata = icao_to_iata_aircraft.get(aircraft_type, aircraft_type)
            
            processed_flights.append({
                'aircraft_type': aircraft_iata,
                'acv': acv,
                'flight_number': flight_number,
                'carrier': carrier,
                'type': flight_type,
                'weekday': weekday,
                'partida_dt': partida_dt,
                'chegada_dt': chegada_dt,
                'origem': origem,
                'destino': destino,
                'origem_tz': origem_tz,
                'destino_tz': destino_tz,
                'next_flight': next_flight,  # CONEXÃO CORRETA!
                'duration': duration
            })
        
        if not processed_flights:
            st.error("Nenhum voo válido foi processado!")
            return
        
        # Determinar período de dados
        all_dates = [f['partida_dt'] for f in processed_flights] + [f['chegada_dt'] for f in processed_flights]
        data_min = min(all_dates).strftime("%d%b%y").upper()
        data_max = max(all_dates).strftime("%d%b%y").upper()
        data_emissao = datetime.now().strftime("%d%b%y").upper()
        data_emissao2 = datetime.now().strftime("%Y%m%d")
        
        # Criar nome do arquivo
        if output_file is None:
            output_file = f"{codigo_iata}_{data_emissao2}_{data_min}-{data_max}.ssim"
        
        # Gerar arquivo SSIM
        with open(output_file, 'w') as file:
            numero_linha = 1
            
            # Linha 1 - Header
            linha_1 = ajustar_linha("1AIRLINE STANDARD SCHEDULE DATA SET" + " " * 157 + f"{numero_linha:08}")
            file.write(linha_1 + "\\n")
            numero_linha += 1
            
            # Linhas de zeros
            for _ in range(4):
                file.write("0" * 200 + "\\n")
                numero_linha += 1
            
            # Linha 2 - Carrier info
            linha_2_conteudo = f"2U{codigo_iata}  0008    {data_min}{data_max}{data_emissao}Created by dnata capacity"
            posicao_p = 72
            espacos_antes_p = posicao_p - len(linha_2_conteudo) - 1
            linha_2_base = linha_2_conteudo + (' ' * espacos_antes_p) + 'P'
            numero_linha_str = f" EN08{numero_linha:08}"
            espacos_restantes = 200 - len(linha_2_base) - len(numero_linha_str)
            linha_2 = linha_2_base + (' ' * espacos_restantes) + numero_linha_str
            file.write(linha_2 + "\\n")
            numero_linha += 1
            
            # Linhas de zeros
            for _ in range(4):
                file.write("0" * 200 + "\\n")
                numero_linha += 1
            
            # Ordenar voos por número e data
            processed_flights.sort(key=lambda x: (x['flight_number'], x['partida_dt']))
            
            # Linhas 3 - Dados dos voos
            flight_date_counter = {}
            
            for flight in processed_flights:
                flight_num = flight['flight_number']
                partida_dt = flight['partida_dt']
                chegada_dt = flight['chegada_dt']
                
                # Determinar date counter
                if flight_num not in flight_date_counter:
                    flight_date_counter[flight_num] = 1
                else:
                    flight_date_counter[flight_num] += 1
                
                date_counter = flight_date_counter[flight_num]
                
                # Formatar campos
                frequencia = determinar_dia_semana(flight['weekday'])
                status = determinar_status(flight['type'])
                
                # Datas
                data_partida = partida_dt.strftime("%d%b%y").upper()
                data_chegada = chegada_dt.strftime("%d%b%y").upper()
                
                # Horários
                partida = partida_dt.strftime("%H%M")
                chegada = chegada_dt.strftime("%H%M")
                
                # Timezones
                origem_tz_fmt = format_timezone_offset(str(flight['origem_tz']))
                destino_tz_fmt = format_timezone_offset(str(flight['destino_tz']))
                
                # Identificador do voo (8 caracteres)
                flight_id = f"{flight_num:04d}{date_counter:02d}01"
                
                # Número do voo para exibição (igual ao projeto original)
                flight_display = str(flight_num).rjust(5)
                
                # PRÓXIMO VOO - CORREÇÃO: não repetir voo atual, só incluir se diferente
                next_flight_field = ""
                if flight['next_flight'] and flight['next_flight'] != flight_num:
                    next_flight_field = f"{codigo_iata}{flight['next_flight']:>5d}"
                
                # Construir linha 3
                linha_3 = (
                    f"3 "                           # Tipo de registro
                    f"{codigo_iata:<2} "            # Código da companhia
                    f"{flight_id}"                  # ID do voo (8 chars)
                    f"{status}"                     # Status
                    f"{data_partida}"              # Data partida
                    f"{data_chegada}"              # Data chegada  
                    f"{frequencia}"                # Frequência (7 chars)
                    f" "                           # Espaço
                    f"{flight['origem']:<3}"       # Aeroporto origem
                    f"{partida}"                   # Horário partida
                    f"{partida}"                   # Horário partida (repetido)
                    f"{origem_tz_fmt}"             # Timezone origem
                    f"  "                          # Espaços
                    f"{flight['destino']:<3}"      # Aeroporto destino
                    f"{chegada}"                   # Horário chegada
                    f"{chegada}"                   # Horário chegada (repetido)
                    f"{destino_tz_fmt}"            # Timezone destino
                    f"  "                          # Espaços
                    f"{flight['aircraft_type']:<3}" # Tipo de aeronave
                    f"{' ':53}"                    # Espaços reservados
                    f"{codigo_iata:<2}"            # Companhia operadora
                    f"{' ':7}"                     # Espaços
                    f"{codigo_iata:<2}"            # Companhia de marketing
                    f"{flight_display}"            # Número do voo
                    f"{' ':28}"                    # Espaços (reduzir duplicação)
                    f"{next_flight_field:<6}"      # PRÓXIMO VOO CORRETO!
                    f"{' ':5}"                     # Espaços restantes
                    f"{numero_linha:08}"           # Número da linha
                )
                
                # Garantir 200 caracteres
                linha_3 = ajustar_linha(linha_3)
                file.write(linha_3 + "\\n")
                numero_linha += 1
            
            # Linhas de zeros finais
            for _ in range(4):
                file.write("0" * 200 + "\\n")
                numero_linha += 1
            
            # Linha 5 - Footer
            linha_5 = ajustar_linha(f"5 {codigo_iata} {data_emissao}" + " " * 175 + f"{numero_linha:06}E{numero_linha+1:06}")
            file.write(linha_5 + "\\n")
        
        st.success(f"Arquivo SSIM gerado com sucesso: {output_file}")
        st.info(f"Processados {len(processed_flights)} voos com conexões corretas!")
        
        # Estatísticas das conexões
        with_connections = sum(1 for f in processed_flights if f['next_flight'])
        st.info(f"Voos com próximo voo definido: {with_connections}/{len(processed_flights)}")
        
        # Oferecer download
        with open(output_file, 'rb') as f:
            st.download_button(
                label="📥 Baixar Arquivo SSIM",
                data=f,
                file_name=output_file,
                mime='text/plain'
            )
        
        # Limpar arquivo temporário
        if os.path.exists(output_file):
            os.remove(output_file)
            
    except Exception as e:
        st.error(f"Erro ao gerar arquivo SSIM: {str(e)}")
        import traceback
        st.error(traceback.format_exc())

# Interface Streamlit
def main():
    st.set_page_config(
        page_title="Conversor SSIM TS.09", 
        page_icon="✈️",
        layout="wide"
    )
    
    st.title("✈️ Conversor SSIM - Baseado em TS.09")
    st.markdown("### Gerador de arquivo SSIM com casamento correto de voos")
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Carregar lista de companhias aéreas
        try:
            airlines_df = pd.read_csv('iata_airlines.csv')
            
            # Método de seleção da companhia
            metodo_selecao = st.radio(
                "Método de seleção:",
                ("Selecionar por lista", "Inserir código manualmente")
            )
            
            if metodo_selecao == "Selecionar por lista":
                paises = sorted(airlines_df['Country / Territory'].dropna().unique())
                pais_selecionado = st.selectbox("País / Território:", ["Todos"] + paises)
                
                if pais_selecionado != "Todos":
                    airlines_filtrado = airlines_df[airlines_df['Country / Territory'] == pais_selecionado]
                else:
                    airlines_filtrado = airlines_df
                
                companhias = sorted(airlines_filtrado['Airline Name'].dropna().unique())
                companhia_selecionada = st.selectbox("Companhia Aérea:", companhias)
                
                codigo_iata = airlines_filtrado[
                    airlines_filtrado['Airline Name'] == companhia_selecionada
                ]['IATA Designator'].values[0]
                
                st.success(f"Código IATA: **{codigo_iata}**")
            else:
                codigo_iata = st.text_input("Código IATA (2 caracteres):").upper()
                if codigo_iata and len(codigo_iata) == 2:
                    st.success(f"Código inserido: **{codigo_iata}**")
                elif codigo_iata:
                    st.error("Código deve ter exatamente 2 caracteres!")
                    
        except FileNotFoundError:
            st.error("Arquivo 'iata_airlines.csv' não encontrado!")
            codigo_iata = st.text_input("Código IATA (2 caracteres):").upper()
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 Upload do Arquivo")
        excel_file = st.file_uploader(
            "Selecione o arquivo TS.09 (Excel):",
            type=['xlsx', 'xls'],
            help="Arquivo no formato TS.09 com dados de malha aérea"
        )
        
        if excel_file:
            st.success(f"Arquivo carregado: **{excel_file.name}**")
    
    with col2:
        st.header("ℹ️ Informações")
        st.info("""
        **Melhorias desta versão:**
        - ✅ Casamento correto de voos
        - ✅ Baseado em dados TS.09
        - ✅ Conexões bidirecionais
        - ✅ Validação de rotas
        """)
    
    # Botão de geração
    if st.button("🚀 Gerar Arquivo SSIM", type="primary", use_container_width=True):
        if not excel_file:
            st.error("Por favor, faça o upload do arquivo TS.09!")
        elif not codigo_iata or len(codigo_iata) != 2:
            st.error("Por favor, informe um código IATA válido!")
        else:
            # Salvar arquivo temporariamente
            temp_path = f"temp_{excel_file.name}"
            with open(temp_path, 'wb') as f:
                f.write(excel_file.getbuffer())
            
            try:
                with st.spinner("Gerando arquivo SSIM..."):
                    gerar_ssim_ts09(temp_path, codigo_iata)
            finally:
                # Limpar arquivo temporário
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Desenvolvido com ❤️ usando Streamlit** | "
        "Baseado no padrão IATA SSIM | "
        f"Versão 2.0 - {datetime.now().year}"
    )

if __name__ == "__main__":
    main()
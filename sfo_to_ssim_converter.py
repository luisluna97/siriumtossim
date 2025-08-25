#!/usr/bin/env python3
"""
Conversor SFO Schedule to SSIM - Dnata Brasil
Converte arquivo SFO_Schedule_Weekly_Extract_Report para formato SSIM
"""

import pandas as pd
from datetime import datetime, timedelta
import os

def ajustar_linha(line, comprimento=200):
    """Ajusta uma linha para ter exatamente o comprimento especificado"""
    return line.ljust(comprimento)[:comprimento]

def parse_op_days(op_days_str):
    """
    Converte string de dias operacionais para formato SSIM
    Exemplo: '1234567' = todos os dias, '12..56.' = Seg, Ter, Sex, Sab
    """
    if pd.isna(op_days_str):
        return "1234567"  # Default: todos os dias
    
    op_days = str(op_days_str).strip()
    
    # Se já está no formato correto (7 caracteres)
    if len(op_days) == 7:
        return op_days
    
    # Fallback: todos os dias
    return "1234567"

def format_timezone_offset(offset_str):
    """Formata offset de timezone para padrão SSIM"""
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

def parse_date_sfo(date_str):
    """Converte data SFO para formato SSIM (DDMMMYY)"""
    try:
        if pd.isna(date_str):
            return datetime.now().strftime("%d%b%y").upper()
        
        # Se já está no formato datetime
        if isinstance(date_str, datetime):
            return date_str.strftime("%d%b%y").upper()
        
        # Tentar diferentes formatos
        date_str = str(date_str).strip()
        
        # Formato YYYY-MM-DD
        if '-' in date_str and len(date_str) == 10:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%d%b%y").upper()
        
        # Formato DD/MM/YYYY
        if '/' in date_str:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            return dt.strftime("%d%b%y").upper()
        
        # Fallback
        return datetime.now().strftime("%d%b%y").upper()
        
    except Exception as e:
        print(f"Erro ao converter data {date_str}: {e}")
        return datetime.now().strftime("%d%b%y").upper()

def parse_time_sfo(time_str):
    """Converte horário SFO para formato SSIM (HHMM)"""
    try:
        if pd.isna(time_str):
            return "0000"
        
        # Se é um objeto time
        if hasattr(time_str, 'strftime'):
            return time_str.strftime("%H%M")
        
        # Se é string
        time_str = str(time_str).strip()
        
        # Formato HH:MM
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) >= 2:
                hours = int(parts[0])
                minutes = int(parts[1])
                return f"{hours:02d}{minutes:02d}"
        
        # Formato HHMM
        if len(time_str) == 4 and time_str.isdigit():
            return time_str
        
        # Formato HMM
        if len(time_str) == 3 and time_str.isdigit():
            return '0' + time_str
        
        return "0000"
        
    except Exception as e:
        print(f"Erro ao converter horário {time_str}: {e}")
        return "0000"

def determinar_status_voo(service_type=None):
    """Determina o status do voo - assumindo passageiro por padrão"""
    return "J"  # Scheduled passenger service

def get_aircraft_type(equipment=None):
    """Obtém tipo de aeronave - usar código IATA se disponível"""
    if pd.isna(equipment):
        return "320"  # Default
    
    equipment = str(equipment).strip().upper()
    
    # Mapeamento comum de códigos
    aircraft_map = {
        'A320': '320',
        'A321': '321',
        'A330': '330',
        'A350': '350',
        'B737': '737',
        'B777': '777',
        'B787': '787',
        '777': '777',
        '787': '787',
        '320': '320',
        '321': '321',
        '330': '330',
        '350': '350'
    }
    
    return aircraft_map.get(equipment, equipment[:3])

def gerar_ssim_sfo(excel_path, codigo_iata_selecionado, output_file=None):
    """
    Gera arquivo SSIM a partir da malha SFO em Excel
    """
    try:
        print(f"🔄 GERANDO SSIM SFO PARA {codigo_iata_selecionado}")
        print("=" * 60)
        
        # Ler o arquivo Excel SFO (header na linha 5)
        df = pd.read_excel(excel_path, header=4)
        print(f"✅ Arquivo lido: {len(df)} linhas")
        print(f"📋 Colunas: {df.columns.tolist()}")
        
        # Filtrar pela companhia aérea selecionada
        # Verificar se há coluna de companhia aérea
        airline_col = None
        for col in ['Mkt Al', 'Op Al', 'Airline', 'Carrier']:
            if col in df.columns:
                airline_col = col
                break
        
        if airline_col:
            # Mostrar companhias disponíveis
            companhias_disponiveis = df[airline_col].unique()
            print(f"🏢 Companhias disponíveis: {companhias_disponiveis}")
            
            # Filtrar pela companhia selecionada
            df_filtered = df[df[airline_col] == codigo_iata_selecionado]
            
            if len(df_filtered) == 0:
                print(f"⚠️  Nenhum voo encontrado para {codigo_iata_selecionado}")
                print(f"   Companhias disponíveis: {companhias_disponiveis}")
                return None
            
            print(f"✅ Voos filtrados para {codigo_iata_selecionado}: {len(df_filtered)}")
        else:
            print("⚠️  Coluna de companhia aérea não encontrada, usando todos os dados")
            df_filtered = df
        
        # Carregar arquivos de apoio
        try:
            airport_df = pd.read_csv('airport.csv')
            airport_df['IATA'] = airport_df['IATA'].str.strip().str.upper()
            airport_df['Timezone'] = airport_df['Timezone'].replace('\\N', '0')
            airport_df['Timezone'] = pd.to_numeric(airport_df['Timezone'], errors='coerce').fillna(0)
            iata_to_timezone = dict(zip(airport_df['IATA'], airport_df['Timezone']))
            print(f"✅ Aeroportos carregados: {len(airport_df)}")
        except Exception as e:
            print(f"⚠️  Erro ao carregar aeroportos: {e}")
            iata_to_timezone = {}
        
        try:
            aircraft_df = pd.read_excel('ACT TYPE.xlsx')
            aircraft_df['ICAO'] = aircraft_df['ICAO'].str.strip().str.upper()
            aircraft_df['IATA'] = aircraft_df['IATA'].str.strip()
            icao_to_iata_aircraft = dict(zip(aircraft_df['ICAO'], aircraft_df['IATA']))
            print(f"✅ Aeronaves carregadas: {len(aircraft_df)}")
        except Exception as e:
            print(f"⚠️  Erro ao carregar aeronaves: {e}")
            icao_to_iata_aircraft = {}
        
        # Processar dados dos voos
        processed_flights = []
        
        for idx, row in df_filtered.iterrows():
            try:
                # Extrair dados básicos
                origem = str(row.get('Orig', 'SFO')).strip().upper()
                destino = str(row.get('Dest', 'SFO')).strip().upper()
                flight_number = int(row.get('Flight', 1))
                
                # Datas e horários
                eff_date = row.get('Eff Date', datetime.now())
                disc_date = row.get('Disc Date', datetime.now() + timedelta(days=30))
                
                # Horários de partida e chegada (assumindo que existem)
                dep_time = row.get('Dep Time', '12:00')
                arr_time = row.get('Arr Time', '14:00')
                
                # Dias operacionais
                op_days = row.get('Op Days', '1234567')
                frequencia = parse_op_days(op_days)
                
                # Equipamento
                equipment = row.get('Equipment', 'A320')
                aircraft_type = get_aircraft_type(equipment)
                
                # Status do voo
                status = determinar_status_voo()
                
                # Timezone offsets
                origem_tz = iata_to_timezone.get(origem, 0.0)
                destino_tz = iata_to_timezone.get(destino, 0.0)
                
                processed_flights.append({
                    'flight_number': flight_number,
                    'origem': origem,
                    'destino': destino,
                    'eff_date': eff_date,
                    'disc_date': disc_date,
                    'dep_time': dep_time,
                    'arr_time': arr_time,
                    'frequencia': frequencia,
                    'aircraft_type': aircraft_type,
                    'status': status,
                    'origem_tz': origem_tz,
                    'destino_tz': destino_tz,
                })
                
            except Exception as e:
                print(f"⚠️  Erro ao processar linha {idx}: {e}")
                continue
        
        print(f"✅ Processados {len(processed_flights)} voos válidos")
        
        if len(processed_flights) == 0:
            print("❌ Nenhum voo válido encontrado")
            return None
        
        # Determinar período de dados
        if processed_flights:
            data_min = min([f['eff_date'] for f in processed_flights])
            data_max = max([f['disc_date'] for f in processed_flights])
            
            if isinstance(data_min, datetime):
                data_min_str = data_min.strftime("%d%b%y").upper()
            else:
                data_min_str = parse_date_sfo(data_min)
                
            if isinstance(data_max, datetime):
                data_max_str = data_max.strftime("%d%b%y").upper()
            else:
                data_max_str = parse_date_sfo(data_max)
        else:
            data_min_str = datetime.now().strftime("%d%b%y").upper()
            data_max_str = (datetime.now() + timedelta(days=30)).strftime("%d%b%y").upper()
        
        data_emissao = datetime.now().strftime("%d%b%y").upper()
        data_emissao2 = datetime.now().strftime("%Y%m%d")
        
        # Nome do arquivo de saída
        if output_file is None:
            output_file = f"SFO_{codigo_iata_selecionado}_{data_emissao2}_{data_min_str}-{data_max_str}.ssim"
        
        print(f"📝 Gerando arquivo: {output_file}")
        
        # Gerar arquivo SSIM
        with open(output_file, 'w') as file:
            numero_linha = 1
            
            # Linha 1 - Header
            linha_1_conteudo = "1AIRLINE STANDARD SCHEDULE DATA SET"
            numero_linha_str = f"{numero_linha:08}"
            espacos_necessarios = 200 - len(linha_1_conteudo) - len(numero_linha_str)
            linha_1 = linha_1_conteudo + (' ' * espacos_necessarios) + numero_linha_str
            file.write(linha_1 + "\\n")
            numero_linha += 1
            
            # 4 linhas de zeros
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\\n")
                numero_linha += 1
            
            # Linha 2 - Carrier info
            linha_2_conteudo = f"2U{codigo_iata_selecionado}  0008    {data_min_str}{data_max_str}{data_emissao}Created by Capacity Dnata Brasil"
            posicao_p = 72
            espacos_antes_p = posicao_p - len(linha_2_conteudo) - 1
            linha_2 = linha_2_conteudo + (' ' * espacos_antes_p) + 'P'
            
            numero_linha_str = f" EN08{numero_linha:08}"
            espacos_restantes = 200 - len(linha_2) - len(numero_linha_str)
            linha_2 += (' ' * espacos_restantes) + numero_linha_str
            file.write(linha_2 + "\\n")
            numero_linha += 1
            
            # 4 linhas de zeros
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\\n")
                numero_linha += 1
            
            # Ordenar voos por número
            processed_flights.sort(key=lambda x: x['flight_number'])
            
            # Contador de datas por voo
            flight_date_counter = {}
            
            print("🔄 Escrevendo linhas de voos...")
            
            # Linhas 3 - Dados dos voos
            for flight_idx, flight in enumerate(processed_flights):
                flight_num = flight['flight_number']
                
                # Date counter
                if flight_num not in flight_date_counter:
                    flight_date_counter[flight_num] = 0
                flight_date_counter[flight_num] += 1
                date_counter = flight_date_counter[flight_num]
                
                # Formatar campos
                data_partida = parse_date_sfo(flight['eff_date'])
                data_chegada = parse_date_sfo(flight['eff_date'])  # Mesmo dia por simplicidade
                
                partida = parse_time_sfo(flight['dep_time'])
                chegada = parse_time_sfo(flight['arr_time'])
                
                origem_tz_fmt = format_timezone_offset(str(flight['origem_tz']))
                destino_tz_fmt = format_timezone_offset(str(flight['destino_tz']))
                
                # Número do voo preenchido com zeros
                numero_voo_padded = str(flight_num).zfill(4)
                etapa = "01"
                eight_char_field = f"{numero_voo_padded}{str(date_counter).zfill(2)}{etapa}"
                numero_voo_display = str(flight_num).rjust(5)
                
                # Número da linha
                numero_linha_str = f"{numero_linha:08}"
                
                # Construir linha 3 (formato SSIM padrão)
                linha_3 = (
                    f"3 "                                    # Tipo de registro
                    f"{codigo_iata_selecionado:<2} "         # Código da companhia  
                    f"{eight_char_field}"                    # ID do voo (8 chars)
                    f"{flight['status']}"                    # Status (J/F)
                    f"{data_partida}"                       # Data partida (7 chars)
                    f"{data_chegada}"                       # Data chegada (7 chars)
                    f"{flight['frequencia']}"               # Frequência (7 chars)
                    f" "                                    # Espaço
                    f"{flight['origem']:<3}"                # Aeroporto origem (3 chars)
                    f"{partida}"                           # Horário partida (4 chars)
                    f"{partida}"                           # Horário partida repetido (4 chars)
                    f"{origem_tz_fmt}"                     # Timezone origem (5 chars)
                    f"  "                                  # Espaços (2 chars)
                    f"{flight['destino']:<3}"              # Aeroporto destino (3 chars)
                    f"{chegada}"                           # Horário chegada (4 chars)
                    f"{chegada}"                           # Horário chegada repetido (4 chars)
                    f"{destino_tz_fmt}"                    # Timezone destino (5 chars)
                    f"  "                                  # Espaços (2 chars)
                    f"{flight['aircraft_type']:<3}"        # Tipo de aeronave (3 chars)
                    f"{' ':53}"                           # Espaços reservados (53 chars)
                    f"{codigo_iata_selecionado:<2}"        # Companhia operadora (2 chars)
                    f"{' ':7}"                            # Espaços (7 chars)
                    f"{codigo_iata_selecionado:<2}"        # Companhia de marketing (2 chars)
                    f"{numero_voo_display}"               # Número do voo (5 chars)
                    f"{' ':34}"                           # Espaços restantes (34 chars)
                    f"{numero_linha_str}"                 # Número da linha (8 chars)
                )
                
                # Garantir exatamente 200 caracteres
                linha_3 = ajustar_linha(linha_3)
                file.write(linha_3 + "\\n")
                numero_linha += 1
                
                # Mostrar alguns exemplos
                if flight_idx < 5:
                    print(f"  Voo {flight_num}: {flight['origem']} → {flight['destino']} ({partida}-{chegada})")
            
            # 4 linhas de zeros finais
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\\n")
                numero_linha += 1
            
            # Linha 5 - Footer
            numero_linha_str = f"{numero_linha + 1:06}"
            linha_5_conteudo = f"5 {codigo_iata_selecionado} {data_emissao}"
            numero_linha_str2 = f"{numero_linha:06}E"
            espacos_necessarios = 200 - len(linha_5_conteudo) - len(numero_linha_str) - len(numero_linha_str2)
            linha_5 = linha_5_conteudo + (' ' * espacos_necessarios) + numero_linha_str2 + numero_linha_str
            file.write(linha_5 + "\\n")
            numero_linha += 1
        
        print(f"✅ Arquivo SSIM SFO gerado: {output_file}")
        print(f"📊 Total de linhas: {numero_linha}")
        print(f"📁 Tamanho: {os.path.getsize(output_file)} bytes")
        print(f"✈️  Voos processados: {len(processed_flights)}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Função principal para teste"""
    excel_path = 'SFO_Schedule_Weekly_Extract_Report_32370.xlsx'
    
    print("🎯 CONVERSOR SFO TO SSIM")
    print("Desenvolvido por Capacity Dnata Brasil")
    print("=" * 60)
    
    if not os.path.exists(excel_path):
        print(f"❌ Arquivo não encontrado: {excel_path}")
        return
    
    # Mostrar companhias disponíveis
    try:
        df_preview = pd.read_excel(excel_path, header=4)
        airline_col = None
        for col in ['Mkt Al', 'Op Al', 'Airline', 'Carrier']:
            if col in df_preview.columns:
                airline_col = col
                break
        
        if airline_col:
            companhias = df_preview[airline_col].unique()
            print(f"🏢 Companhias disponíveis: {companhias}")
            
            # Para teste, usar a primeira companhia
            codigo_iata = companhias[0]
            print(f"🧪 Testando com: {codigo_iata}")
        else:
            codigo_iata = "XX"
            print("⚠️  Usando código genérico XX")
        
        output_file = gerar_ssim_sfo(excel_path, codigo_iata)
        
        if output_file:
            print("\\n🎉 CONVERSÃO CONCLUÍDA COM SUCESSO!")
            print(f"📁 Arquivo gerado: {output_file}")
        else:
            print("❌ FALHA NA CONVERSÃO!")
            
    except Exception as e:
        print(f"❌ Erro na execução: {e}")

if __name__ == "__main__":
    main()

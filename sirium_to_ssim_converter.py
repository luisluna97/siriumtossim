#!/usr/bin/env python3
"""
Conversor SIRIUM (SFO Schedule) para SSIM - Dnata Brasil
Baseado no padrão do old_project, corrigido e adaptado para formato SFO
"""

import pandas as pd
from datetime import datetime, timedelta
import os

def ajustar_linha(line, comprimento=200):
    """Ajusta uma linha para ter exatamente o comprimento especificado"""
    return line.ljust(comprimento)[:comprimento]

def determinar_dia_semana_sfo(op_days_str):
    """
    Converte string de dias operacionais SFO para formato SSIM
    Exemplo SFO: '1234567' = todos os dias, '12..56.' = Seg, Ter, Sex, Sab
    """
    if pd.isna(op_days_str):
        return "1234567"  # Default: todos os dias
    
    op_days = str(op_days_str).strip()
    
    # Se já está no formato correto (7 caracteres)
    if len(op_days) == 7:
        return op_days.replace('.', ' ')  # Converter pontos para espaços
    
    # Fallback: todos os dias
    return "1234567"

def determinar_status_sfo(seats=None, service_type=None):
    """
    Determina o status do voo baseado na coluna Seats:
    - Seats = 0 → Cargo (F)
    - Seats > 0 → Passageiro (J)
    """
    try:
        # Verificar se temos informação de assentos
        if pd.notna(seats):
            seats_num = float(seats)
            if seats_num == 0:
                return "F"  # Scheduled cargo service
            else:
                return "J"  # Scheduled passenger service
        else:
            return "J"  # Default: passenger service
    except (ValueError, TypeError):
        return "J"  # Default: passenger service

def format_timezone_offset(offset_str):
    """Formata offset de timezone para padrão SSIM (igual ao old_project)"""
    try:
        offset = float(offset_str)
        hours = int(offset)
        minutes = int(abs(offset - hours) * 60)
        if offset >= 0:
            sign = '+'
        else:
            sign = '-'
            hours = -hours  # tornar horas positivas
        offset_formatted = f"{sign}{abs(hours):02}{minutes:02}"
        return offset_formatted
    except (ValueError, TypeError):
        return '+0000'

def parse_date_sfo(date_value):
    """Converte data SFO para formato SSIM (DDMMMYY) - baseado no old_project"""
    try:
        if pd.isna(date_value):
            return datetime.now().strftime("%d%b%y").upper()
        
        # Se já é datetime
        if isinstance(date_value, datetime):
            return date_value.strftime("%d%b%y").upper()
        
        # Se é string, tentar converter
        date_str = str(date_value).strip()
        
        # Formato YYYY-MM-DD
        if '-' in date_str and len(date_str) >= 8:
            dt = pd.to_datetime(date_str)
            return dt.strftime("%d%b%y").upper()
        
        # Tentar parse direto
        dt = pd.to_datetime(date_value)
        return dt.strftime("%d%b%y").upper()
        
    except Exception as e:
        print(f"Erro ao converter data {date_value}: {e}")
        return datetime.now().strftime("%d%b%y").upper()

def parse_time_sfo(time_value):
    """Converte horário SFO para formato SSIM (HHMM) - baseado no old_project"""
    try:
        if pd.isna(time_value):
            return "0000"
        
        # Se é um objeto time ou datetime
        if hasattr(time_value, 'strftime'):
            return time_value.strftime("%H%M")
        
        # Se é número (int ou float) - NOVO TRATAMENTO PARA SFO
        if isinstance(time_value, (int, float)):
            # Converter para inteiro e formatar como HHMM
            time_int = int(time_value)
            
            # Se é menor que 100, assumir formato HMM (ex: 45 = 00:45)
            if time_int < 100:
                return f"{time_int:04d}"
            
            # Se tem 3 dígitos, assumir HMM (ex: 235 = 02:35)  
            elif time_int < 1000:
                return f"{time_int:04d}"
            
            # Se tem 4 dígitos, assumir HHMM (ex: 1730 = 17:30)
            elif time_int < 2400:
                return f"{time_int:04d}"
            
            else:
                return "0000"
        
        # Se é string
        time_str = str(time_value).strip()
        
        # Remover .0 se presente (ex: "1730.0" -> "1730")
        if time_str.endswith('.0'):
            time_str = time_str[:-2]
        
        # Formato HH:MM
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) >= 2:
                hours = int(float(parts[0]))
                minutes = int(float(parts[1]))
                return f"{hours:02d}{minutes:02d}"
        
        # Formato numérico como string
        if time_str.replace('.', '').isdigit():
            time_int = int(float(time_str))
            
            # Aplicar mesma lógica de números
            if time_int < 100:
                return f"{time_int:04d}"
            elif time_int < 1000:
                return f"{time_int:04d}"
            elif time_int < 2400:
                return f"{time_int:04d}"
        
        return "0000"
        
    except Exception as e:
        print(f"Erro ao converter horário {time_value}: {e}")
        return "0000"

def get_aircraft_type_sfo(equipment=None):
    """Obtém tipo de aeronave - usar código IATA se disponível"""
    if pd.isna(equipment) or equipment == 'N/A':
        return "320"  # Default
    
    equipment = str(equipment).strip().upper()
    
    # Se está vazio ou é N/A, usar default
    if equipment in ['', 'N/A', 'NAN', 'NONE']:
        return "320"
    
    # Mapeamento comum de códigos (expandido com códigos reais do CIRIUM)
    aircraft_map = {
        # Airbus
        'A320': '320', 'A321': '321', 'A330': '330', 'A350': '350',
        'A319': '319', 'A380': '380', 'A340': '340',
        # Boeing
        'B737': '737', 'B777': '777', 'B787': '787', 'B747': '747',
        'B767': '767', 'B757': '757', 'B717': '717',
        # Códigos diretos
        '777': '777', '787': '787', '320': '320', '321': '321',
        '330': '330', '350': '350', '319': '319', '380': '380',
        '737': '737', '747': '747', '767': '767', '757': '757',
        # Códigos específicos do CIRIUM (baseado nos dados reais)
        '388': '388', '359': '359', '332': '332', '333': '333', '789': '789',
        '77X': '77X', '77W': '77W', '74Y': '74Y',
        # Embraer
        'E190': '190', 'E170': '170', 'E175': '175', 'E195': '195',
        # Outros
        'ATR72': 'AT7', 'ATR42': 'AT4', 'CRJ900': 'CR9', 'CRJ700': 'CR7'
    }
    
    # Tentar mapeamento direto primeiro
    if equipment in aircraft_map:
        return aircraft_map[equipment]
    
    # Se tem números, tentar extrair (ex: "A320-200" -> "320")
    import re
    match = re.search(r'(\d{3})', equipment)
    if match:
        return match.group(1)
    
    # Fallback: primeiros 3 caracteres ou default
    if len(equipment) >= 3:
        return equipment[:3]
    else:
        return "320"

def gerar_ssim_multiplas_companias(excel_path, companias_selecionadas, output_file=None):
    """
    Gera arquivo SSIM com companhias específicas selecionadas
    """
    try:
        print(f"🔄 GERANDO SSIM PARA COMPANHIAS SELECIONADAS: {', '.join(companias_selecionadas)}")
        print("=" * 60)
        
        # Ler o arquivo Excel CIRIUM (header na linha 5)
        df = pd.read_excel(excel_path, header=4)
        print(f"✅ Arquivo lido: {len(df)} linhas")
        
        # Filtrar apenas linhas válidas
        df_clean = df.dropna(subset=['Orig', 'Dest'])
        df_clean = df_clean[
            (df_clean['Orig'].astype(str).str.strip() != '') & 
            (df_clean['Dest'].astype(str).str.strip() != '') &
            (df_clean['Orig'].astype(str).str.strip() != 'nan') & 
            (df_clean['Dest'].astype(str).str.strip() != 'nan')
        ]
        
        if 'Flight' in df_clean.columns:
            df_clean = df_clean[pd.to_numeric(df_clean['Flight'], errors='coerce').notna()]
        
        print(f"🧹 Limpeza concluída: {len(df_clean)} linhas válidas")
        df = df_clean
        
        # Filtrar apenas companhias selecionadas
        airline_col = None
        for col in ['Mkt Al', 'Op Al', 'Airline', 'Carrier']:
            if col in df.columns:
                airline_col = col
                break
        
        if not airline_col:
            print("❌ Coluna de companhia aérea não encontrada")
            return None
            
        # Filtrar dados para as companhias selecionadas
        df = df[df[airline_col].isin(companias_selecionadas)]
        print(f"✅ Dados filtrados para {len(companias_selecionadas)} companhias: {len(df)} voos")
        
        # Determinar período global
        data_min = datetime.now()
        data_max = datetime.now() + timedelta(days=30)
        
        if 'Eff Date' in df.columns and 'Disc Date' in df.columns:
            try:
                eff_dates_str = df['Eff Date'].astype(str)
                disc_dates_str = df['Disc Date'].astype(str)
                
                eff_dates_valid = eff_dates_str[
                    (eff_dates_str != 'nan') & 
                    (eff_dates_str != '') & 
                    (eff_dates_str.notna())
                ]
                
                disc_dates_valid = disc_dates_str[
                    (disc_dates_str != 'nan') & 
                    (disc_dates_str != '') & 
                    (disc_dates_str.notna())
                ]
                
                if len(eff_dates_valid) > 0 and len(disc_dates_valid) > 0:
                    eff_dt_list = []
                    for date_str in eff_dates_valid:
                        try:
                            dt = pd.to_datetime(date_str, errors='coerce')
                            if pd.notna(dt):
                                eff_dt_list.append(dt)
                        except:
                            continue
                    
                    disc_dt_list = []
                    for date_str in disc_dates_valid:
                        try:
                            dt = pd.to_datetime(date_str, errors='coerce')
                            if pd.notna(dt):
                                disc_dt_list.append(dt)
                        except:
                            continue
                    
                    if eff_dt_list and disc_dt_list:
                        data_min = min(eff_dt_list)
                        data_max = max(disc_dt_list)
                        print(f"✅ Período global: {data_min.date()} a {data_max.date()}")
            except Exception as e:
                print(f"⚠️ Erro ao processar datas globais: {e}")
        
        data_min_str = parse_date_sfo(data_min)
        data_max_str = parse_date_sfo(data_max)
        data_emissao = datetime.now().strftime("%d%b%y").upper()
        data_emissao2 = datetime.now().strftime("%Y%m%d")
        
        # Nome do arquivo de saída
        if output_file is None:
            airlines_str = "_".join(companias_selecionadas)
            output_file = f"MULTIPLE_{airlines_str}_{data_emissao2}_{data_min_str}-{data_max_str}.ssim"
        
        print(f"📝 Gerando arquivo: {output_file}")
        
        # Carregar arquivos de apoio
        try:
            airport_df = pd.read_csv('airport.csv')
            airport_df['ICAO'] = airport_df['ICAO'].str.strip().str.upper()
            airport_df['IATA'] = airport_df['IATA'].str.strip().str.upper()
            airport_df['Timezone'] = airport_df['Timezone'].replace('\\N', '0')
            airport_df['Timezone'] = airport_df['Timezone'].astype(float)
            
            iata_to_timezone = dict(zip(airport_df['IATA'], airport_df['Timezone']))
            print(f"✅ Aeroportos carregados: {len(airport_df)}")
        except Exception as e:
            print(f"⚠️ Erro ao carregar aeroportos: {e}")
            iata_to_timezone = {}
        
        # Gerar arquivo SSIM ÚNICO com companhias selecionadas
        with open(output_file, 'w') as file:
            numero_linha = 1
            
            # UM ÚNICO HEADER
            numero_linha_str = f"{numero_linha:08}"
            linha_1_conteudo = "1AIRLINE STANDARD SCHEDULE DATA SET"
            espacos_necessarios = 200 - len(linha_1_conteudo) - len(numero_linha_str)
            linha_1 = linha_1_conteudo + (' ' * espacos_necessarios) + numero_linha_str
            file.write(linha_1 + "\n")
            numero_linha += 1
            
            # 4 linhas de zeros
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\n")
                numero_linha += 1
            
            # UM ÚNICO CARRIER RECORD para múltiplas companhias
            airlines_code = "MIX" if len(companias_selecionadas) > 1 else companias_selecionadas[0]
            linha_2_conteudo = f"2U{airlines_code}  0008    {data_min_str}{data_max_str}{data_emissao}Created by Capacity Dnata Brasil"
            posicao_p = 72
            espacos_antes_p = posicao_p - len(linha_2_conteudo) - 1
            linha_2 = linha_2_conteudo + (' ' * espacos_antes_p) + 'P'
            
            numero_linha_str = f" EN08{numero_linha:08}"
            espacos_restantes = 200 - len(linha_2) - len(numero_linha_str)
            linha_2 += (' ' * espacos_restantes) + numero_linha_str
            file.write(linha_2 + "\n")
            numero_linha += 1
            
            # 4 linhas de zeros
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\n")
                numero_linha += 1
            
            # TODAS as linhas de voo das companhias selecionadas
            flight_date_counter = {}
            
            # Processar cada companhia selecionada
            for companhia in companias_selecionadas:
                print(f"🔄 Processando companhia: {companhia}")
                
                df_companhia = df[df[airline_col] == companhia]
                if len(df_companhia) == 0:
                    continue
                
                # Processar voos desta companhia
                try:
                    if 'Flight' in df_companhia.columns:
                        df_companhia['Flight_num'] = pd.to_numeric(df_companhia['Flight'], errors='coerce')
                        
                        if 'Eff Date' in df_companhia.columns:
                            df_companhia['Eff Date_dt'] = pd.to_datetime(df_companhia['Eff Date'], errors='coerce')
                            df_sorted = df_companhia.sort_values(by=['Flight_num', 'Eff Date_dt'])
                        else:
                            df_sorted = df_companhia.sort_values(by=['Flight_num'])
                    else:
                        df_sorted = df_companhia
                except Exception as e:
                    print(f"⚠️ Erro ao ordenar dados para {companhia}: {e}")
                    df_sorted = df_companhia
                
                # Linhas 3 - voos desta companhia
                for idx, row in df_sorted.iterrows():
                    try:
                        # Extrair dados básicos
                        if 'Flight' in row and pd.notna(row['Flight']):
                            try:
                                numero_voo = str(int(float(row['Flight']))).strip()
                            except (ValueError, TypeError):
                                numero_voo = "001"
                        else:
                            numero_voo = "001"
                        
                        origem = str(row.get('Orig', 'SFO')).strip().upper()
                        destino = str(row.get('Dest', 'SFO')).strip().upper()
                        
                        # Frequência
                        if 'Op Days' in row:
                            frequencia = determinar_dia_semana_sfo(row['Op Days'])
                        else:
                            frequencia = "1234567"
                        
                        # Status do voo baseado em Seats (cargo vs passageiro)
                        seats = row.get('Seats', None)
                        status = determinar_status_sfo(seats)
                        
                        # Datas (usar Eff Date e Disc Date para período completo)
                        if 'Eff Date' in row and pd.notna(row['Eff Date']):
                            data_partida = parse_date_sfo(row['Eff Date'])
                        else:
                            data_partida = data_min_str
                        
                        if 'Disc Date' in row and pd.notna(row['Disc Date']):
                            data_chegada = parse_date_sfo(row['Disc Date'])
                        else:
                            data_chegada = data_max_str
                        
                        # Horários
                        dep_time = row.get('Dep Time', '12:00')
                        arr_time = row.get('Arr Time', '14:00')
                        partida = parse_time_sfo(dep_time)
                        chegada = parse_time_sfo(arr_time)
                        
                        # Equipamento (usar coluna Equip se disponível)
                        equipment = row.get('Equip', row.get('Equipment', 'A320'))
                        equipamento = get_aircraft_type_sfo(equipment)
                        
                        # Timezone offsets
                        origem_timezone_offset = iata_to_timezone.get(origem, 0.0)
                        destino_timezone_offset = iata_to_timezone.get(destino, 0.0)
                        origem_timezone_formatted = format_timezone_offset(str(origem_timezone_offset))
                        destino_timezone_formatted = format_timezone_offset(str(destino_timezone_offset))
                        
                        # Lógica de date_counter (global para todas as companhias)
                        voo_key = f"{companhia}_{numero_voo}"
                        if voo_key not in flight_date_counter:
                            flight_date_counter[voo_key] = 0
                        flight_date_counter[voo_key] += 1
                        date_counter = flight_date_counter[voo_key]
                        
                        # Construir linha 3
                        numero_voo_padded = numero_voo.zfill(4)
                        etapa = "01"
                        eight_char_field = f"{numero_voo_padded}{str(date_counter).zfill(2)}{etapa}"
                        numero_voo_display = numero_voo.rjust(5)
                        numero_linha_str = f"{numero_linha:08}"
                        
                        linha_3 = (
                            f"3 "
                            f"{companhia:<2} "
                            f"{eight_char_field}"
                            f"{status}"
                            f"{data_partida}"
                            f"{data_chegada}"
                            f"{frequencia}"
                            f" "
                            f"{origem:<3}"
                            f"{partida}"
                            f"{partida}"
                            f"{origem_timezone_formatted}"
                            f"  "
                            f"{destino:<3}"
                            f"{chegada}"
                            f"{chegada}"
                            f"{destino_timezone_formatted}"
                            f"  "
                            f"{equipamento:<3}"
                            f"{' ':53}"
                            f"{companhia:<2}"
                            f"{' ':7}"
                            f"{companhia:<2}"
                            f"{numero_voo_display}"
                            f"{' ':28}"
                            f"{' ':6}"
                            f"{' ':5}"
                            f"{' ':9}"
                            f"{numero_linha_str}"
                        )
                        
                        linha_3 = linha_3.ljust(200)
                        file.write(linha_3 + "\n")
                        numero_linha += 1
                        
                    except Exception as e:
                        print(f"⚠️ Erro ao processar linha {idx} da companhia {companhia}: {e}")
                        continue
                
                print(f"✅ Companhia {companhia} processada: {len(df_companhia)} voos")
            
            # UM ÚNICO FOOTER no final
            # 4 linhas de zeros finais
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\n")
                numero_linha += 1
            
            # Footer para múltiplas companhias
            airlines_code = "MIX" if len(companias_selecionadas) > 1 else companias_selecionadas[0]
            numero_linha_str = f"{numero_linha + 1:06}"
            linha_5_conteudo = f"5 {airlines_code} {data_emissao}"
            numero_linha_str2 = f"{numero_linha:06}E"
            espacos_necessarios = 200 - len(linha_5_conteudo) - len(numero_linha_str) - len(numero_linha_str2)
            linha_5 = linha_5_conteudo + (' ' * espacos_necessarios) + numero_linha_str2 + numero_linha_str
            file.write(linha_5 + "\n")
            numero_linha += 1
        
        print(f"✅ Arquivo SSIM MÚLTIPLAS COMPANHIAS gerado: {output_file}")
        print(f"📊 Total de linhas: {numero_linha}")
        print(f"🏢 Companhias processadas: {len(companias_selecionadas)}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None

def gerar_ssim_todas_companias(excel_path, output_file=None):
    """
    Gera arquivo SSIM com TODAS as companhias em um único arquivo
    """
    try:
        print(f"🔄 GERANDO SSIM PARA TODAS AS COMPANHIAS")
        print("=" * 60)
        
        # Ler o arquivo Excel SIRIUM (header na linha 5)
        df = pd.read_excel(excel_path, header=4)
        print(f"✅ Arquivo lido: {len(df)} linhas")
        
        # Filtrar apenas linhas válidas
        df_clean = df.dropna(subset=['Orig', 'Dest'])
        df_clean = df_clean[
            (df_clean['Orig'].astype(str).str.strip() != '') & 
            (df_clean['Dest'].astype(str).str.strip() != '') &
            (df_clean['Orig'].astype(str).str.strip() != 'nan') & 
            (df_clean['Dest'].astype(str).str.strip() != 'nan')
        ]
        
        if 'Flight' in df_clean.columns:
            df_clean = df_clean[pd.to_numeric(df_clean['Flight'], errors='coerce').notna()]
        
        print(f"🧹 Limpeza concluída: {len(df_clean)} linhas válidas")
        df = df_clean
        
        # Obter todas as companhias (filtrar textos inválidos)
        airline_col = None
        for col in ['Mkt Al', 'Op Al', 'Airline', 'Carrier']:
            if col in df.columns:
                airline_col = col
                break
        
        if not airline_col:
            print("❌ Coluna de companhia aérea não encontrada")
            return None
            
        unique_values = df[airline_col].astype(str)
        unique_values = unique_values[
            (unique_values != 'nan') & 
            (unique_values != '') & 
            (unique_values.notna())
        ].unique()
        
        # Filtrar apenas códigos IATA válidos (2 caracteres, letras)
        todas_companias = []
        for x in unique_values:
            x_str = str(x).strip().upper()
            if (len(x_str) == 2 and 
                x_str.isalpha() and 
                x_str not in ['nan', '', 'None', 'NA'] and
                'Schedule' not in x_str and
                'Extract' not in x_str and
                'Report' not in x_str):
                todas_companias.append(x_str)
        
        todas_companias = sorted(todas_companias)
        print(f"🏢 Processando companhias válidas: {todas_companias}")
        
        # Determinar período global
        data_min = datetime.now()
        data_max = datetime.now() + timedelta(days=30)
        
        if 'Eff Date' in df.columns and 'Disc Date' in df.columns:
            try:
                eff_dates_str = df['Eff Date'].astype(str)
                disc_dates_str = df['Disc Date'].astype(str)
                
                eff_dates_valid = eff_dates_str[
                    (eff_dates_str != 'nan') & 
                    (eff_dates_str != '') & 
                    (eff_dates_str.notna())
                ]
                
                disc_dates_valid = disc_dates_str[
                    (disc_dates_str != 'nan') & 
                    (disc_dates_str != '') & 
                    (disc_dates_str.notna())
                ]
                
                if len(eff_dates_valid) > 0 and len(disc_dates_valid) > 0:
                    eff_dt_list = []
                    for date_str in eff_dates_valid:
                        try:
                            dt = pd.to_datetime(date_str, errors='coerce')
                            if pd.notna(dt):
                                eff_dt_list.append(dt)
                        except:
                            continue
                    
                    disc_dt_list = []
                    for date_str in disc_dates_valid:
                        try:
                            dt = pd.to_datetime(date_str, errors='coerce')
                            if pd.notna(dt):
                                disc_dt_list.append(dt)
                        except:
                            continue
                    
                    if eff_dt_list and disc_dt_list:
                        data_min = min(eff_dt_list)
                        data_max = max(disc_dt_list)
                        print(f"✅ Período global: {data_min.date()} a {data_max.date()}")
            except Exception as e:
                print(f"⚠️ Erro ao processar datas globais: {e}")
        
        data_min_str = parse_date_sfo(data_min)
        data_max_str = parse_date_sfo(data_max)
        data_emissao = datetime.now().strftime("%d%b%y").upper()
        data_emissao2 = datetime.now().strftime("%Y%m%d")
        
        # Nome do arquivo de saída
        if output_file is None:
            output_file = f"ALL_COMPANIES_{data_emissao2}_{data_min_str}-{data_max_str}.ssim"
        
        print(f"📝 Gerando arquivo: {output_file}")
        
        # Carregar arquivos de apoio
        try:
            airport_df = pd.read_csv('airport.csv')
            airport_df['ICAO'] = airport_df['ICAO'].str.strip().str.upper()
            airport_df['IATA'] = airport_df['IATA'].str.strip().str.upper()
            airport_df['Timezone'] = airport_df['Timezone'].replace('\\N', '0')
            airport_df['Timezone'] = airport_df['Timezone'].astype(float)
            
            iata_to_timezone = dict(zip(airport_df['IATA'], airport_df['Timezone']))
            print(f"✅ Aeroportos carregados: {len(airport_df)}")
        except Exception as e:
            print(f"⚠️ Erro ao carregar aeroportos: {e}")
            iata_to_timezone = {}
        
        # Gerar arquivo SSIM ÚNICO com TODAS as companhias
        with open(output_file, 'w') as file:
            numero_linha = 1
            
            # UM ÚNICO HEADER para todas as companhias
            numero_linha_str = f"{numero_linha:08}"
            linha_1_conteudo = "1AIRLINE STANDARD SCHEDULE DATA SET"
            espacos_necessarios = 200 - len(linha_1_conteudo) - len(numero_linha_str)
            linha_1 = linha_1_conteudo + (' ' * espacos_necessarios) + numero_linha_str
            file.write(linha_1 + "\n")
            numero_linha += 1
            
            # 4 linhas de zeros
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\n")
                numero_linha += 1
            
            # UM ÚNICO CARRIER RECORD para "ALL" 
            linha_2_conteudo = f"2UALL 0008    {data_min_str}{data_max_str}{data_emissao}Created by Capacity Dnata Brasil"
            posicao_p = 72
            espacos_antes_p = posicao_p - len(linha_2_conteudo) - 1
            linha_2 = linha_2_conteudo + (' ' * espacos_antes_p) + 'P'
            
            numero_linha_str = f" EN08{numero_linha:08}"
            espacos_restantes = 200 - len(linha_2) - len(numero_linha_str)
            linha_2 += (' ' * espacos_restantes) + numero_linha_str
            file.write(linha_2 + "\n")
            numero_linha += 1
            
            # 4 linhas de zeros
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\n")
                numero_linha += 1
            
            # TODAS as linhas de voo de TODAS as companhias juntas
            flight_date_counter = {}
            
            # Processar cada companhia
            for companhia in todas_companias:
                print(f"🔄 Processando companhia: {companhia}")
                
                df_companhia = df[df[airline_col] == companhia]
                if len(df_companhia) == 0:
                    continue
                
                # Processar voos desta companhia
                try:
                    if 'Flight' in df_companhia.columns:
                        df_companhia['Flight_num'] = pd.to_numeric(df_companhia['Flight'], errors='coerce')
                        
                        if 'Eff Date' in df_companhia.columns:
                            df_companhia['Eff Date_dt'] = pd.to_datetime(df_companhia['Eff Date'], errors='coerce')
                            df_sorted = df_companhia.sort_values(by=['Flight_num', 'Eff Date_dt'])
                        else:
                            df_sorted = df_companhia.sort_values(by=['Flight_num'])
                    else:
                        df_sorted = df_companhia
                except Exception as e:
                    print(f"⚠️ Erro ao ordenar dados para {companhia}: {e}")
                    df_sorted = df_companhia
                
                # Linhas 3 - voos desta companhia (SEM headers/footers separados)
                for idx, row in df_sorted.iterrows():
                    try:
                        # Extrair dados básicos
                        if 'Flight' in row and pd.notna(row['Flight']):
                            try:
                                numero_voo = str(int(float(row['Flight']))).strip()
                            except (ValueError, TypeError):
                                numero_voo = "001"
                        else:
                            numero_voo = "001"
                        
                        origem = str(row.get('Orig', 'SFO')).strip().upper()
                        destino = str(row.get('Dest', 'SFO')).strip().upper()
                        
                        # Frequência
                        if 'Op Days' in row:
                            frequencia = determinar_dia_semana_sfo(row['Op Days'])
                        else:
                            frequencia = "1234567"
                        
                        # Status do voo baseado em Seats (cargo vs passageiro)
                        seats = row.get('Seats', None)
                        status = determinar_status_sfo(seats)
                        
                        # Datas (usar Eff Date e Disc Date para período completo)
                        if 'Eff Date' in row and pd.notna(row['Eff Date']):
                            data_partida = parse_date_sfo(row['Eff Date'])
                        else:
                            data_partida = data_min_str
                        
                        if 'Disc Date' in row and pd.notna(row['Disc Date']):
                            data_chegada = parse_date_sfo(row['Disc Date'])
                        else:
                            data_chegada = data_max_str
                        
                        # Horários
                        dep_time = row.get('Dep Time', '12:00')
                        arr_time = row.get('Arr Time', '14:00')
                        partida = parse_time_sfo(dep_time)
                        chegada = parse_time_sfo(arr_time)
                        
                        # Equipamento (usar coluna Equip se disponível)
                        equipment = row.get('Equip', row.get('Equipment', 'A320'))
                        equipamento = get_aircraft_type_sfo(equipment)
                        
                        # Timezone offsets
                        origem_timezone_offset = iata_to_timezone.get(origem, 0.0)
                        destino_timezone_offset = iata_to_timezone.get(destino, 0.0)
                        origem_timezone_formatted = format_timezone_offset(str(origem_timezone_offset))
                        destino_timezone_formatted = format_timezone_offset(str(destino_timezone_offset))
                        
                        # Lógica de date_counter (global para todas as companhias)
                        voo_key = f"{companhia}_{numero_voo}"
                        if voo_key not in flight_date_counter:
                            flight_date_counter[voo_key] = 0
                        flight_date_counter[voo_key] += 1
                        date_counter = flight_date_counter[voo_key]
                        
                        # Construir linha 3
                        numero_voo_padded = numero_voo.zfill(4)
                        etapa = "01"
                        eight_char_field = f"{numero_voo_padded}{str(date_counter).zfill(2)}{etapa}"
                        numero_voo_display = numero_voo.rjust(5)
                        numero_linha_str = f"{numero_linha:08}"
                        
                        linha_3 = (
                            f"3 "
                            f"{companhia:<2} "
                            f"{eight_char_field}"
                            f"{status}"
                            f"{data_partida}"
                            f"{data_chegada}"
                            f"{frequencia}"
                            f" "
                            f"{origem:<3}"
                            f"{partida}"
                            f"{partida}"
                            f"{origem_timezone_formatted}"
                            f"  "
                            f"{destino:<3}"
                            f"{chegada}"
                            f"{chegada}"
                            f"{destino_timezone_formatted}"
                            f"  "
                            f"{equipamento:<3}"
                            f"{' ':53}"
                            f"{companhia:<2}"
                            f"{' ':7}"
                            f"{companhia:<2}"
                            f"{numero_voo_display}"
                            f"{' ':28}"
                            f"{' ':6}"
                            f"{' ':5}"
                            f"{' ':9}"
                            f"{numero_linha_str}"
                        )
                        
                        linha_3 = linha_3.ljust(200)
                        file.write(linha_3 + "\n")
                        numero_linha += 1
                        
                    except Exception as e:
                        print(f"⚠️ Erro ao processar linha {idx} da companhia {companhia}: {e}")
                        continue
                
                print(f"✅ Companhia {companhia} processada: {len(df_companhia)} voos")
            
            # UM ÚNICO FOOTER no final para todas as companhias
            # 4 linhas de zeros finais
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\n")
                numero_linha += 1
            
            # Footer único para ALL
            numero_linha_str = f"{numero_linha + 1:06}"
            linha_5_conteudo = f"5 ALL {data_emissao}"
            numero_linha_str2 = f"{numero_linha:06}E"
            espacos_necessarios = 200 - len(linha_5_conteudo) - len(numero_linha_str) - len(numero_linha_str2)
            linha_5 = linha_5_conteudo + (' ' * espacos_necessarios) + numero_linha_str2 + numero_linha_str
            file.write(linha_5 + "\n")
            numero_linha += 1
        
        print(f"✅ Arquivo SSIM TODAS COMPANHIAS gerado: {output_file}")
        print(f"📊 Total de linhas: {numero_linha}")
        print(f"🏢 Companhias processadas: {len(todas_companias)}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None

def gerar_ssim_sirium(excel_path, codigo_iata_selecionado, output_file=None):
    """
    Gera arquivo SSIM a partir da malha SIRIUM (SFO) em Excel
    Baseado no padrão do old_project
    """
    try:
        print(f"🔄 GERANDO SSIM SIRIUM PARA {codigo_iata_selecionado}")
        print("=" * 60)
        
        # Ler o arquivo Excel SIRIUM (header na linha 5)
        df = pd.read_excel(excel_path, header=4)
        print(f"✅ Arquivo lido: {len(df)} linhas")
        print(f"📋 Colunas: {df.columns.tolist()}")
        
        # Filtrar apenas linhas válidas (que têm dados de voo)
        print("🧹 Iniciando limpeza de dados...")
        
        # Remove linhas onde Orig ou Dest são NaN/vazios
        df_clean = df.dropna(subset=['Orig', 'Dest'])
        print(f"   Após remover NaN: {len(df_clean)} linhas")
        
        # Remove linhas onde Orig ou Dest são strings vazias
        df_clean = df_clean[
            (df_clean['Orig'].astype(str).str.strip() != '') & 
            (df_clean['Dest'].astype(str).str.strip() != '') &
            (df_clean['Orig'].astype(str).str.strip() != 'nan') & 
            (df_clean['Dest'].astype(str).str.strip() != 'nan')
        ]
        print(f"   Após remover strings vazias: {len(df_clean)} linhas")
        
        # Filtro adicional: remover linhas onde Flight não é válido
        if 'Flight' in df_clean.columns:
            df_clean = df_clean[pd.to_numeric(df_clean['Flight'], errors='coerce').notna()]
            print(f"   Após filtrar Flight inválidos: {len(df_clean)} linhas")
        
        print(f"🧹 Limpeza concluída: {len(df_clean)} linhas válidas (removidas {len(df) - len(df_clean)} linhas inválidas)")
        df = df_clean
        
        # Filtrar pela companhia aérea selecionada
        airline_col = None
        for col in ['Mkt Al', 'Op Al', 'Airline', 'Carrier']:
            if col in df.columns:
                airline_col = col
                break
        
        if airline_col:
            # Filtrar apenas códigos IATA válidos
            try:
                unique_values = df[airline_col].astype(str)
                unique_values = unique_values[
                    (unique_values != 'nan') & 
                    (unique_values != '') & 
                    (unique_values.notna())
                ].unique()
                
                # Filtrar apenas códigos IATA válidos (2 caracteres, letras)
                companhias_disponiveis = []
                for x in unique_values:
                    x_str = str(x).strip().upper()
                    if (len(x_str) == 2 and 
                        x_str.isalpha() and 
                        x_str not in ['nan', '', 'None', 'NA'] and
                        'Schedule' not in x_str and
                        'Extract' not in x_str and
                        'Report' not in x_str):
                        companhias_disponiveis.append(x_str)
                
                companhias_disponiveis = sorted(companhias_disponiveis)
                print(f"🏢 Companhias válidas disponíveis: {companhias_disponiveis}")
            except Exception as e:
                print(f"⚠️  Erro ao listar companhias, usando valores brutos: {e}")
                companhias_disponiveis = df[airline_col].unique()
                print(f"🏢 Companhias disponíveis (bruto): {companhias_disponiveis}")
            
            df_filtered = df[df[airline_col] == codigo_iata_selecionado]
            
            if len(df_filtered) == 0:
                print(f"⚠️  Nenhum voo encontrado para {codigo_iata_selecionado}")
                return None
            
            print(f"✅ Voos filtrados para {codigo_iata_selecionado}: {len(df_filtered)}")
        else:
            print("⚠️  Coluna de companhia aérea não encontrada, usando todos os dados")
            df_filtered = df
        
        # Carregar arquivos de apoio (igual ao old_project)
        try:
            airport_df = pd.read_csv('airport.csv')
            airport_df['ICAO'] = airport_df['ICAO'].str.strip().str.upper()
            airport_df['IATA'] = airport_df['IATA'].str.strip().str.upper()
            airport_df['Timezone'] = airport_df['Timezone'].replace('\\N', '0')
            airport_df['Timezone'] = airport_df['Timezone'].astype(float)
            
            icao_to_iata_airport = dict(zip(airport_df['ICAO'], airport_df['IATA']))
            icao_to_timezone = dict(zip(airport_df['ICAO'], airport_df['Timezone']))
            iata_to_timezone = dict(zip(airport_df['IATA'], airport_df['Timezone']))
            print(f"✅ Aeroportos carregados: {len(airport_df)}")
        except Exception as e:
            print(f"⚠️  Erro ao carregar aeroportos: {e}")
            icao_to_iata_airport = {}
            icao_to_timezone = {}
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
        
        # Determinar período de dados - versão ultra robusta
        try:
            print("📅 Determinando período de dados...")
            
            # Usar datas fixas como fallback seguro
            data_min = datetime.now()
            data_max = datetime.now() + timedelta(days=30)
            
            if 'Eff Date' in df_filtered.columns and 'Disc Date' in df_filtered.columns:
                try:
                    # Converter todas as datas para string primeiro, depois datetime
                    eff_dates_str = df_filtered['Eff Date'].astype(str)
                    disc_dates_str = df_filtered['Disc Date'].astype(str)
                    
                    # Filtrar strings válidas
                    eff_dates_valid = eff_dates_str[
                        (eff_dates_str != 'nan') & 
                        (eff_dates_str != '') & 
                        (eff_dates_str.notna())
                    ]
                    
                    disc_dates_valid = disc_dates_str[
                        (disc_dates_str != 'nan') & 
                        (disc_dates_str != '') & 
                        (disc_dates_str.notna())
                    ]
                    
                    if len(eff_dates_valid) > 0 and len(disc_dates_valid) > 0:
                        # Converter para datetime sem comparações diretas
                        eff_dt_list = []
                        for date_str in eff_dates_valid:
                            try:
                                dt = pd.to_datetime(date_str, errors='coerce')
                                if pd.notna(dt):
                                    eff_dt_list.append(dt)
                            except:
                                continue
                        
                        disc_dt_list = []
                        for date_str in disc_dates_valid:
                            try:
                                dt = pd.to_datetime(date_str, errors='coerce')
                                if pd.notna(dt):
                                    disc_dt_list.append(dt)
                            except:
                                continue
                        
                        if eff_dt_list and disc_dt_list:
                            data_min = min(eff_dt_list)
                            data_max = max(disc_dt_list)
                            print(f"   ✅ Período extraído: {data_min.date()} a {data_max.date()}")
                        else:
                            print(f"   ⚠️  Usando datas padrão (não foi possível converter)")
                    else:
                        print(f"   ⚠️  Usando datas padrão (dados inválidos)")
                        
                except Exception as e:
                    print(f"   ⚠️  Erro ao processar datas, usando padrão: {e}")
            else:
                print(f"   ⚠️  Colunas de data não encontradas, usando padrão")
            
            data_min_str = parse_date_sfo(data_min)
            data_max_str = parse_date_sfo(data_max)
            
        except Exception as e:
            print(f"⚠️  Erro geral ao determinar período: {e}")
            data_min_str = datetime.now().strftime("%d%b%y").upper()
            data_max_str = (datetime.now() + timedelta(days=30)).strftime("%d%b%y").upper()
        
        # Data de emissão (igual ao old_project)
        data_emissao = datetime.now().strftime("%d%b%y").upper()
        data_emissao2 = datetime.now().strftime("%Y%m%d")
        
        # Nome do arquivo de saída (igual ao old_project)
        if output_file is None:
            output_file = f"{codigo_iata_selecionado} {data_emissao2} {data_min_str}-{data_max_str}.ssim"
        
        print(f"📝 Gerando arquivo: {output_file}")
        
        # Gerar arquivo SSIM (FORMATO EXATO DO OLD_PROJECT)
        with open(output_file, 'w') as file:
            numero_linha = 1
            
            # Linha 1 (EXATAMENTE IGUAL AO OLD_PROJECT)
            numero_linha_str = f"{numero_linha:08}"
            linha_1_conteudo = "1AIRLINE STANDARD SCHEDULE DATA SET"
            espacos_necessarios = 200 - len(linha_1_conteudo) - len(numero_linha_str)
            linha_1 = linha_1_conteudo + (' ' * espacos_necessarios) + numero_linha_str
            file.write(linha_1 + "\n")
            numero_linha += 1
            
            # 4 linhas de zeros (IGUAL AO OLD_PROJECT)
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\n")
                numero_linha += 1
            
            # Linha 2 (EXATAMENTE IGUAL AO OLD_PROJECT)
            linha_2_conteudo = f"2U{codigo_iata_selecionado}  0008    {data_min_str}{data_max_str}{data_emissao}Created by Capacity Dnata Brasil"
            posicao_p = 72
            espacos_antes_p = posicao_p - len(linha_2_conteudo) - 1
            linha_2 = linha_2_conteudo + (' ' * espacos_antes_p) + 'P'
            
            numero_linha_str = f" EN08{numero_linha:08}"
            espacos_restantes = 200 - len(linha_2) - len(numero_linha_str)
            linha_2 += (' ' * espacos_restantes) + numero_linha_str
            file.write(linha_2 + "\n")
            numero_linha += 1
            
            # 4 linhas de zeros (IGUAL AO OLD_PROJECT)
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\n")
                numero_linha += 1
            
            # Inicializar contador de datas por voo (IGUAL AO OLD_PROJECT)
            flight_date_counter = {}
            
            # Ordenar o DataFrame (similar ao old_project) - com proteção para tipos mistos
            try:
                if 'Flight' in df_filtered.columns:
                    # Converter Flight para numérico antes de ordenar
                    df_filtered['Flight_num'] = pd.to_numeric(df_filtered['Flight'], errors='coerce')
                    
                    if 'Eff Date' in df_filtered.columns:
                        # Converter datas para datetime antes de ordenar
                        df_filtered['Eff Date_dt'] = pd.to_datetime(df_filtered['Eff Date'], errors='coerce')
                        df_sorted = df_filtered.sort_values(by=['Flight_num', 'Eff Date_dt'])
                    else:
                        df_sorted = df_filtered.sort_values(by=['Flight_num'])
                else:
                    df_sorted = df_filtered
            except Exception as e:
                print(f"⚠️  Erro ao ordenar dados: {e}")
                df_sorted = df_filtered  # Usar sem ordenação se falhar
            
            print("🔄 Escrevendo linhas de voos...")
            
            # Linhas 3 - Dados dos voos (FORMATO EXATO DO OLD_PROJECT)
            for idx, row in df_sorted.iterrows():
                try:
                    # Extrair dados básicos
                    if 'Flight' in row and pd.notna(row['Flight']):
                        try:
                            numero_voo = str(int(float(row['Flight']))).strip()
                        except (ValueError, TypeError):
                            numero_voo = "001"
                    else:
                        numero_voo = "001"
                    
                    origem = str(row.get('Orig', 'SFO')).strip().upper()
                    destino = str(row.get('Dest', 'SFO')).strip().upper()
                    
                    # Determinar frequência
                    if 'Op Days' in row:
                        frequencia = determinar_dia_semana_sfo(row['Op Days'])
                    else:
                        frequencia = "1234567"
                    
                    # Status do voo baseado em Seats (cargo vs passageiro)
                    seats = row.get('Seats', None)
                    status = determinar_status_sfo(seats)
                    
                    # Datas (usar Eff Date e Disc Date para período completo)
                    if 'Eff Date' in row and pd.notna(row['Eff Date']):
                        data_partida = parse_date_sfo(row['Eff Date'])
                    else:
                        data_partida = data_min_str
                    
                    if 'Disc Date' in row and pd.notna(row['Disc Date']):
                        data_chegada = parse_date_sfo(row['Disc Date'])
                    else:
                        data_chegada = data_max_str
                    
                    # Horários (assumir padrão se não disponível)
                    dep_time = row.get('Dep Time', '12:00')
                    arr_time = row.get('Arr Time', '14:00')
                    partida = parse_time_sfo(dep_time)
                    chegada = parse_time_sfo(arr_time)
                    
                    # Equipamento (usar coluna Equip se disponível)
                    equipment = row.get('Equip', row.get('Equipment', 'A320'))
                    equipamento = get_aircraft_type_sfo(equipment)
                    
                    # Timezone offsets (usar mapeamento se disponível)
                    origem_timezone_offset = iata_to_timezone.get(origem, 0.0)
                    destino_timezone_offset = iata_to_timezone.get(destino, 0.0)
                    origem_timezone_formatted = format_timezone_offset(str(origem_timezone_offset))
                    destino_timezone_formatted = format_timezone_offset(str(destino_timezone_offset))
                    
                    # Lógica de date_counter (IGUAL AO OLD_PROJECT)
                    if numero_voo not in flight_date_counter:
                        flight_date_counter[numero_voo] = 0
                    flight_date_counter[numero_voo] += 1
                    date_counter = flight_date_counter[numero_voo]
                    
                    # Número do voo preenchido com zeros (IGUAL AO OLD_PROJECT)
                    numero_voo_padded = numero_voo.zfill(4)
                    
                    # Etapa sempre "01" (simplificado)
                    etapa = "01"
                    
                    # Campo de 8 caracteres (IGUAL AO OLD_PROJECT)
                    eight_char_field = f"{numero_voo_padded}{str(date_counter).zfill(2)}{etapa}"
                    
                    # Número do voo para exibição (IGUAL AO OLD_PROJECT)
                    numero_voo_display = numero_voo.rjust(5)
                    
                    # Número da linha (IGUAL AO OLD_PROJECT)
                    numero_linha_str = f"{numero_linha:08}"
                    
                    # Construção da linha 3 (FORMATO EXATO DO OLD_PROJECT)
                    linha_3 = (
                        f"3 "
                        f"{codigo_iata_selecionado:<2} "
                        f"{eight_char_field}"
                        f"{status}"
                        f"{data_partida}"
                        f"{data_chegada}"
                        f"{frequencia}"
                        f" "
                        f"{origem:<3}"
                        f"{partida}"
                        f"{partida}"
                        f"{origem_timezone_formatted}"
                        f"  "
                        f"{destino:<3}"
                        f"{chegada}"
                        f"{chegada}"
                        f"{destino_timezone_formatted}"
                        f"  "
                        f"{equipamento:<3}"
                        f"{' ':53}"
                        f"{codigo_iata_selecionado:<2}"
                        f"{' ':7}"
                        f"{codigo_iata_selecionado:<2}"
                        f"{numero_voo_display}"
                        f"{' ':28}"
                        f"{' ':6}"
                        f"{' ':5}"
                        f"{' ':9}"
                        f"{numero_linha_str}"
                    )
                    
                    # Garantir que a linha tenha exatamente 200 caracteres (IGUAL AO OLD_PROJECT)
                    linha_3 = linha_3.ljust(200)
                    
                    file.write(linha_3 + "\n")
                    numero_linha += 1
                    
                    # Mostrar alguns exemplos
                    if idx < 5:
                        print(f"  Voo {numero_voo}: {origem} → {destino} ({partida}-{chegada})")
                
                except Exception as e:
                    print(f"⚠️  Erro ao processar linha {idx}: {e}")
                    continue
            
            # 4 linhas de zeros finais (IGUAL AO OLD_PROJECT)
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\n")
                numero_linha += 1
            
            # Linha 5 - Footer (EXATAMENTE IGUAL AO OLD_PROJECT)
            numero_linha_str = f"{numero_linha + 1:06}"
            linha_5_conteudo = f"5 {codigo_iata_selecionado} {data_emissao}"
            numero_linha_str2 = f"{numero_linha:06}E"
            espacos_necessarios = 200 - len(linha_5_conteudo) - len(numero_linha_str) - len(numero_linha_str2)
            linha_5 = linha_5_conteudo + (' ' * espacos_necessarios) + numero_linha_str2 + numero_linha_str
            file.write(linha_5 + "\n")
            numero_linha += 1
        
        print(f"✅ Arquivo SSIM SIRIUM gerado: {output_file}")
        print(f"📊 Total de linhas: {numero_linha}")
        print(f"📁 Tamanho: {os.path.getsize(output_file)} bytes")
        print(f"✈️  Voos processados: {len(df_sorted)}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Função principal para teste"""
    excel_path = 'SFO_Schedule_Weekly_Extract_Report_32370.xlsx'
    
    print("🎯 CONVERSOR SIRIUM TO SSIM")
    print("Baseado no padrão do old_project")
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
            
            # Para teste, usar AI
            codigo_iata = "AI"
            print(f"🧪 Testando com: {codigo_iata}")
        else:
            codigo_iata = "XX"
            print("⚠️  Usando código genérico XX")
        
        output_file = gerar_ssim_sirium(excel_path, codigo_iata)
        
        if output_file:
            print("\\n🎉 CONVERSÃO CONCLUÍDA COM SUCESSO!")
            print(f"📁 Arquivo gerado: {output_file}")
        else:
            print("❌ FALHA NA CONVERSÃO!")
            
    except Exception as e:
        print(f"❌ Erro na execução: {e}")

if __name__ == "__main__":
    main()

import pandas as pd
from datetime import datetime, timedelta
import os

def ajustar_linha(line, comprimento=200):
    """Ajusta uma linha para ter exatamente o comprimento especificado"""
    return line.ljust(comprimento)[:comprimento]

def determinar_dia_semana(week_day_lt):
    """Converte o dia da semana numérico para formato SSIM"""
    # TS.09 usa 1=Segunda, 2=Terça, etc.
    # SSIM usa posições: [1,2,3,4,5,6,7] para Segunda a Domingo
    frequencia = [" "] * 7
    if 1 <= week_day_lt <= 7:
        frequencia[week_day_lt - 1] = str(week_day_lt)
    return "".join(frequencia)

def determinar_status(tipo):
    """Determina o status do voo baseado no tipo"""
    tipo_upper = str(tipo).upper()
    if tipo_upper == "J":
        return "J"  # Scheduled passenger service
    else:
        return "F"  # Freight service

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

def parse_route(route_str):
    """Extrai origem e destino da string de rota"""
    try:
        parts = route_str.split(' / ')
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        else:
            return "YYZ", "YYZ"  # Fallback
    except:
        return "YYZ", "YYZ"

def parse_time(time_str):
    """Converte string de tempo para formato SSIM (HHMM)"""
    try:
        # Remove ':' e formata para 4 dígitos
        time_clean = str(time_str).replace(':', '')
        if len(time_clean) == 3:
            time_clean = '0' + time_clean
        return time_clean[:4]
    except:
        return "0000"

def parse_date(date_str):
    """Converte data para formato SSIM (DDMMMYY)"""
    try:
        # TS.09 formato: 01SEP25
        return str(date_str).upper()[:7]
    except:
        return "01JAN25"

def get_next_flight_number(onward_flight):
    """Extrai número do próximo voo da string Onward Flight"""
    try:
        if pd.isna(onward_flight):
            return ""
        
        onward_str = str(onward_flight).strip()
        if onward_str.startswith('TS'):
            # Remove 'TS' e pega só a parte numérica
            flight_part = onward_str[2:].strip()
            # Se contém '/', pega só a primeira parte e adiciona '/1' no final
            if '/' in flight_part:
                parts = flight_part.split('/')
                if len(parts) >= 2 and parts[0].isdigit():
                    # Para casos como "840/1", retornamos "840" com formatação especial
                    return parts[0].zfill(3)
            # Verifica se é numérico
            elif flight_part.isdigit():
                return flight_part.zfill(3)  # Preenche com zeros até 3 dígitos
        return ""
    except:
        return ""

def gerar_ssim_ts09(excel_path, codigo_iata, output_file=None):
    """
    Gera arquivo SSIM a partir da malha TS.09 em Excel
    """
    try:
        # Ler o arquivo Excel TS.09
        df = pd.read_excel(excel_path)
        
        print(f"Arquivo lido com sucesso: {len(df)} linhas")
        
        # Carregar arquivos de apoio (usando os mesmos do projeto antigo)
        try:
            airport_df = pd.read_csv('airport.csv')
            airport_df['ICAO'] = airport_df['ICAO'].str.strip().str.upper()
            airport_df['IATA'] = airport_df['IATA'].str.strip().str.upper()
            airport_df['Timezone'] = airport_df['Timezone'].replace('\\N', '0')
            airport_df['Timezone'] = airport_df['Timezone'].astype(float)
            
            icao_to_iata_airport = dict(zip(airport_df['ICAO'], airport_df['IATA']))
            icao_to_timezone = dict(zip(airport_df['ICAO'], airport_df['Timezone']))
            iata_to_timezone = dict(zip(airport_df['IATA'], airport_df['Timezone']))
        except Exception as e:
            print(f"Aviso: Erro ao carregar airport.csv: {e}")
            icao_to_iata_airport = {}
            icao_to_timezone = {}
            iata_to_timezone = {}
        
        try:
            aircraft_df = pd.read_excel('ACT TYPE.xlsx')
            aircraft_df['ICAO'] = aircraft_df['ICAO'].str.strip().str.upper()
            aircraft_df['IATA'] = aircraft_df['IATA'].str.strip()
            icao_to_iata_aircraft = dict(zip(aircraft_df['ICAO'], aircraft_df['IATA']))
        except Exception as e:
            print(f"Aviso: Erro ao carregar ACT TYPE.xlsx: {e}")
            icao_to_iata_aircraft = {}
        
        # Determinar datas mínima e máxima
        dates = df['Date-LT'].unique()
        data_min = min(dates)
        data_max = max(dates)
        
        # Data de emissão
        data_emissao = datetime.now().strftime("%d%b%y").upper()
        data_emissao2 = datetime.now().strftime("%Y%m%d")
        
        # Nome do arquivo de saída
        if output_file is None:
            output_file = f"{codigo_iata}_{data_emissao2}_{data_min}-{data_max}.ssim"
        
        # Criar arquivo SSIM
        with open(output_file, 'w') as file:
            numero_linha = 1
            
            # Linha 1 - Header
            linha_1_conteudo = "1AIRLINE STANDARD SCHEDULE DATA SET"
            numero_linha_str = f"{numero_linha:08}"
            espacos_necessarios = 200 - len(linha_1_conteudo) - len(numero_linha_str)
            linha_1 = linha_1_conteudo + (' ' * espacos_necessarios) + numero_linha_str
            file.write(linha_1 + "\n")
            numero_linha += 1
            
            # 4 linhas de zeros
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\n")
                numero_linha += 1
            
            # Linha 2 - Carrier info
            linha_2_conteudo = f"2U{codigo_iata}  0008    {data_min}{data_max}{data_emissao}Created by Capacity Dnata Brasil"
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
            
            # Contador de voos por número de voo
            flight_date_counter = {}
            
            # Manter a ordem original do arquivo (não ordenar)
            df_sorted = df
            
            # Linhas 3 - Flight records
            for _, row in df_sorted.iterrows():
                # Extrair dados básicos
                flight_number = int(row['Flight-Number'])
                route = row['Route']
                date_lt = row['Date-LT']
                week_day = int(row['Week-Day-LT'])
                std_lt = row['Std-LT']
                sta_lt = row['Sta-LT']
                aircraft_type = row['Aircraft-Type']
                flight_type = row['Type']
                onward_flight = row['Onward Flight']
                
                # Parse route
                origem, destino = parse_route(route)
                
                # Formatar tempos
                partida = parse_time(std_lt)
                chegada = parse_time(sta_lt)
                
                # Determinar frequência (dia da semana)
                frequencia = determinar_dia_semana(week_day)
                
                # Status do voo
                status = determinar_status(flight_type)
                
                # Data formatada
                data_partida = parse_date(date_lt)
                data_chegada = parse_date(date_lt)  # Assumindo mesmo dia
                
                # Equipamento - usar mapeamento se disponível
                equipamento = icao_to_iata_aircraft.get(aircraft_type, aircraft_type[:3])
                
                # Timezone offsets - usar mapeamento se disponível
                origem_timezone = iata_to_timezone.get(origem, 0.0)
                destino_timezone = iata_to_timezone.get(destino, 0.0)
                origem_timezone_formatted = format_timezone_offset(str(origem_timezone))
                destino_timezone_formatted = format_timezone_offset(str(destino_timezone))
                
                # Lógica de date_counter (similar ao projeto antigo)
                if flight_number not in flight_date_counter:
                    flight_date_counter[flight_number] = 0
                flight_date_counter[flight_number] += 1
                date_counter = flight_date_counter[flight_number]
                
                # Número do voo formatado
                numero_voo_padded = str(flight_number).zfill(4)
                
                # Campo de 8 caracteres (flight + date_counter + occurrence)
                eight_char_field = f"{numero_voo_padded}{str(date_counter).zfill(2)}01"
                
                # Número do voo para exibição
                numero_voo_display = str(flight_number).rjust(5)
                
                # Próximo voo - AQUI É A DIFERENÇA PRINCIPAL!
                next_flight_number = get_next_flight_number(onward_flight)
                
                # Número da linha
                numero_linha_str = f"{numero_linha:08}"
                
                # Construir linha 3 (formato exato do projeto original)
                linha_3 = (
                    f"3 "
                    f"{codigo_iata:<2} "
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
                    f"{codigo_iata:<2}"
                    f"{' ':7}"
                    f"{codigo_iata:<2}"
                    f"{numero_voo_display}"
                    f"{' ':21}"
                    f"{codigo_iata:<2}"
                    f"  "
                    f"{next_flight_number:>3}"  # Próximo voo da malha!
                    f"{' ':11}"
                    f"{numero_linha_str}"
                )
                
                # Garantir que a linha tenha exatamente 200 caracteres
                linha_3 = ajustar_linha(linha_3, 200)
                
                file.write(linha_3 + "\n")
                numero_linha += 1
            
            # 4 linhas de zeros finais
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\n")
                numero_linha += 1
            
            # Linha 5 - Final
            numero_linha_str = f"{numero_linha + 1:06}"
            linha_5_conteudo = f"5 {codigo_iata} {data_emissao}"
            numero_linha_str2 = f"{numero_linha:06}E"
            espacos_necessarios = 200 - len(linha_5_conteudo) - len(numero_linha_str) - len(numero_linha_str2)
            linha_5 = linha_5_conteudo + (' ' * espacos_necessarios) + numero_linha_str2 + numero_linha_str
            file.write(linha_5 + "\n")
        
        print(f"Arquivo SSIM gerado com sucesso: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Erro ao gerar arquivo SSIM: {e}")
        raise e

if __name__ == "__main__":
    # Teste do conversor
    excel_file = "TS.09 VERSION 01 - SEPT 2025 - YYZ.xls"
    codigo_iata = "TS"
    
    try:
        output_file = gerar_ssim_ts09(excel_file, codigo_iata)
        print(f"Conversão concluída! Arquivo gerado: {output_file}")
    except Exception as e:
        print(f"Erro na conversão: {e}")

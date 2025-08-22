#!/usr/bin/env python3
"""
Conversor SSIM corrigido - baseado no padrão IATA e projeto original
"""

import pandas as pd
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

def gerar_ssim_corrigido(excel_path, codigo_iata, max_flights=100):
    """
    Gera arquivo SSIM corrigido baseado no padrão IATA
    """
    try:
        print("🔄 GERANDO SSIM CORRIGIDO")
        print("=" * 60)
        
        # Ler o arquivo TS.09
        df = pd.read_excel(excel_path)
        print(f"✅ Carregados {len(df)} voos do TS.09")
        
        # Limitar para teste
        if len(df) > max_flights:
            df = df.head(max_flights)
            print(f"⚠️  Limitando a {max_flights} voos para análise")
        
        # Carregar arquivos de referência
        try:
            airport_df = pd.read_csv('airport.csv')
            airport_df['IATA'] = airport_df['IATA'].str.strip().str.upper()
            airport_df['Timezone'] = airport_df['Timezone'].replace('\\\\N', '0')
            airport_df['Timezone'] = pd.to_numeric(airport_df['Timezone'], errors='coerce').fillna(0)
            iata_to_timezone = dict(zip(airport_df['IATA'], airport_df['Timezone']))
            print(f"✅ Aeroportos: {len(airport_df)} registros")
        except Exception as e:
            print(f"⚠️  Erro ao carregar aeroportos: {e}")
            iata_to_timezone = {}
        
        try:
            aircraft_df = pd.read_excel('ACT TYPE.xlsx')
            aircraft_df['ICAO'] = aircraft_df['ICAO'].str.strip().str.upper()
            aircraft_df['IATA'] = aircraft_df['IATA'].str.strip()
            icao_to_iata_aircraft = dict(zip(aircraft_df['ICAO'], aircraft_df['IATA']))
            print(f"✅ Aeronaves: {len(aircraft_df)} registros")
        except Exception as e:
            print(f"⚠️  Erro ao carregar aeronaves: {e}")
            icao_to_iata_aircraft = {}
        
        # Processar dados do TS.09
        print("🔄 Processando dados dos voos...")
        processed_flights = []
        connections_count = 0
        
        for idx, row in df.iterrows():
            aircraft_type = str(row['Aircraft-Type']).strip()
            flight_number = int(row['Flight-Number'])
            carrier = str(row['Flight-Carrier']).strip()
            date_lt = str(row['Date-LT']).strip()
            weekday = int(row['Week-Day-LT'])
            flight_type = str(row['Type']).strip()
            std_lt = str(row['Std-LT']).strip()
            sta_lt = str(row['Sta-LT']).strip()
            route = str(row['Route']).strip()
            
            # CONEXÃO CORRETA - usar coluna "Onward Flight"
            onward_flight = row['Onward Flight']
            next_flight = None
            if pd.notna(onward_flight):
                next_flight = str(onward_flight).replace(carrier, '').strip()
                try:
                    next_flight = int(next_flight)
                    connections_count += 1
                except:
                    next_flight = None
            
            origem, destino = extract_airport_codes(route)
            partida_dt = parse_datetime(date_lt, std_lt)
            chegada_dt = parse_datetime(date_lt, sta_lt)
            
            if chegada_dt and partida_dt and chegada_dt < partida_dt:
                chegada_dt += timedelta(days=1)
            
            if not partida_dt or not chegada_dt or not origem or not destino:
                continue
            
            origem_tz = iata_to_timezone.get(origem, 0)
            destino_tz = iata_to_timezone.get(destino, 0)
            aircraft_iata = icao_to_iata_aircraft.get(aircraft_type, aircraft_type)
            
            processed_flights.append({
                'aircraft_type': aircraft_iata,
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
            })
            
            if (idx + 1) % 20 == 0:
                print(f"  Processados {idx + 1} voos...")
        
        print(f"✅ Processados {len(processed_flights)} voos válidos")
        print(f"🔗 Conexões encontradas: {connections_count}/{len(processed_flights)} ({connections_count/len(processed_flights)*100:.1f}%)")
        
        # Determinar período de dados
        all_dates = [f['partida_dt'] for f in processed_flights] + [f['chegada_dt'] for f in processed_flights]
        data_min = min(all_dates).strftime("%d%b%y").upper()
        data_max = max(all_dates).strftime("%d%b%y").upper()
        data_emissao = datetime.now().strftime("%d%b%y").upper()
        data_emissao2 = datetime.now().strftime("%Y%m%d")
        
        output_file = f"{codigo_iata}_{data_emissao2}_{data_min}-{data_max}_CORRIGIDO.ssim"
        print(f"📝 Gerando arquivo: {output_file}")
        
        # Gerar arquivo SSIM
        with open(output_file, 'w') as file:
            numero_linha = 1
            
            # Linha 1 - Header (igual ao projeto original)
            numero_linha_str = f"{numero_linha:08}"
            linha_1_conteudo = "1AIRLINE STANDARD SCHEDULE DATA SET"
            espacos_necessarios = 200 - len(linha_1_conteudo) - len(numero_linha_str)
            linha_1 = linha_1_conteudo + (' ' * espacos_necessarios) + numero_linha_str
            file.write(linha_1 + "\\n")
            numero_linha += 1
            
            # Linhas de zeros
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\\n")
                numero_linha += 1
            
            # Linha 2 - Carrier info (CABEÇALHO IGUAL AO PROJETO ORIGINAL)
            linha_2_conteudo = f"2U{codigo_iata}  0008    {data_min}{data_max}{data_emissao}Created by dnata capacity"
            posicao_p = 72
            espacos_antes_p = posicao_p - len(linha_2_conteudo) - 1
            linha_2 = linha_2_conteudo + (' ' * espacos_antes_p) + 'P'
            
            numero_linha_str = f" EN08{numero_linha:08}"
            espacos_restantes = 200 - len(linha_2) - len(numero_linha_str)
            linha_2 += (' ' * espacos_restantes) + numero_linha_str
            file.write(linha_2 + "\\n")
            numero_linha += 1
            
            # Linhas de zeros
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\\n")
                numero_linha += 1
            
            # Ordenar voos
            processed_flights.sort(key=lambda x: (x['flight_number'], x['partida_dt']))
            
            # Inicializar contador de datas por voo
            flight_date_counter = {}
            
            print("🔄 Escrevendo linhas de voos...")
            
            # Linhas 3 - Dados dos voos (FORMATO CORRETO)
            for flight_idx, flight in enumerate(processed_flights):
                flight_num = flight['flight_number']
                partida_dt = flight['partida_dt']
                chegada_dt = flight['chegada_dt']
                
                # Determinar date counter (igual ao projeto original)
                if flight_num not in flight_date_counter:
                    flight_date_counter[flight_num] = 0
                flight_date_counter[flight_num] += 1
                date_counter = flight_date_counter[flight_num]
                
                # Formatar campos
                frequencia = determinar_dia_semana(flight['weekday'])
                status = determinar_status(flight['type'])
                
                data_partida = partida_dt.strftime("%d%b%y").upper()
                data_chegada = chegada_dt.strftime("%d%b%y").upper()
                
                partida = partida_dt.strftime("%H%M")
                chegada = chegada_dt.strftime("%H%M")
                
                origem_tz_fmt = format_timezone_offset(str(flight['origem_tz']))
                destino_tz_fmt = format_timezone_offset(str(flight['destino_tz']))
                
                # Número do voo preenchido com zeros à esquerda até 4 dígitos
                numero_voo_padded = str(flight_num).zfill(4)
                
                # Etapa sempre "01" para simplificar
                etapa = "01"
                
                # Campo de 8 caracteres (igual ao projeto original)
                eight_char_field = f"{numero_voo_padded}{str(date_counter).zfill(2)}{etapa}"
                
                # Número do voo para exibição
                numero_voo_display = str(flight_num).rjust(5)
                
                # Número da linha formatado
                numero_linha_str = f"{numero_linha:08}"
                
                # CONSTRUÇÃO DA LINHA 3 - BASEADA NO PROJETO ORIGINAL MAS CORRIGIDA
                linha_3 = (
                    f"3 "                           # Tipo de registro
                    f"{codigo_iata:<2} "            # Código da companhia  
                    f"{eight_char_field}"           # ID do voo (8 chars)
                    f"{status}"                     # Status (J/F)
                    f"{data_partida}"              # Data partida (7 chars)
                    f"{data_chegada}"              # Data chegada (7 chars)
                    f"{frequencia}"                # Frequência (7 chars)
                    f" "                           # Espaço
                    f"{flight['origem']:<3}"       # Aeroporto origem (3 chars)
                    f"{partida}"                   # Horário partida (4 chars)
                    f"{partida}"                   # Horário partida repetido (4 chars)
                    f"{origem_tz_fmt}"             # Timezone origem (5 chars)
                    f"  "                          # Espaços (2 chars)
                    f"{flight['destino']:<3}"      # Aeroporto destino (3 chars)
                    f"{chegada}"                   # Horário chegada (4 chars)
                    f"{chegada}"                   # Horário chegada repetido (4 chars)
                    f"{destino_tz_fmt}"            # Timezone destino (5 chars)
                    f"  "                          # Espaços (2 chars)
                    f"{flight['aircraft_type']:<3}" # Tipo de aeronave (3 chars)
                    f"{' ':53}"                    # Espaços reservados (53 chars)
                    f"{codigo_iata:<2}"            # Companhia operadora (2 chars)
                    f"{' ':7}"                     # Espaços (7 chars)
                    f"{codigo_iata:<2}"            # Companhia de marketing (2 chars)
                    f"{numero_voo_display}"        # Número do voo (5 chars)
                    f"{' ':28}"                    # Espaços (28 chars)
                )
                
                # ADICIONAR PRÓXIMO VOO NA POSIÇÃO CORRETA (SEM REPETIR O VOO ATUAL)
                if flight['next_flight']:
                    # Só adicionar o próximo voo, não repetir o atual
                    next_flight_str = f"{codigo_iata}{flight['next_flight']:>5d}"
                    linha_3 += f"{next_flight_str:<6}"  # Próximo voo (6 chars)
                else:
                    linha_3 += f"{' ':6}"              # Espaços se não há próximo voo
                
                linha_3 += f"{' ':5}"                  # Espaços finais (5 chars)
                linha_3 += f"{numero_linha_str}"       # Número da linha (8 chars)
                
                # Garantir exatamente 200 caracteres
                linha_3 = ajustar_linha(linha_3)
                file.write(linha_3 + "\\n")
                numero_linha += 1
                
                # Mostrar alguns exemplos
                if flight_idx < 5:
                    next_info = f" → {flight['next_flight']}" if flight['next_flight'] else ""
                    print(f"  Voo {flight_num}: {flight['origem']} → {flight['destino']}{next_info}")
            
            # Linhas de zeros finais
            for _ in range(4):
                zeros_line = "0" * 200
                file.write(zeros_line + "\\n")
                numero_linha += 1
            
            # Linha 5 - Footer (igual ao projeto original)
            numero_linha_str = f"{numero_linha + 1:06}"
            linha_5_conteudo = f"5 {codigo_iata} {data_emissao}"
            numero_linha_str2 = f"{numero_linha:06}E"
            espacos_necessarios = 200 - len(linha_5_conteudo) - len(numero_linha_str) - len(numero_linha_str2)
            linha_5 = linha_5_conteudo + (' ' * espacos_necessarios) + numero_linha_str2 + numero_linha_str
            file.write(linha_5 + "\\n")
            numero_linha += 1
        
        print(f"✅ Arquivo SSIM corrigido gerado: {output_file}")
        print(f"📊 Total de linhas: {numero_linha}")
        print(f"📁 Tamanho: {os.path.getsize(output_file)} bytes")
        
        # Mostrar estatísticas das conexões
        print(f"\\n📈 ESTATÍSTICAS:")
        print(f"   Voos processados: {len(processed_flights)}")
        print(f"   Voos com conexões: {connections_count}")
        print(f"   Taxa de conexão: {connections_count/len(processed_flights)*100:.1f}%")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Função principal"""
    excel_path = 'TS.09 VERSION 01 - SEPT 2025 - YYZ.xls'
    codigo_iata = "TS"
    max_flights = 50  # Para análise detalhada
    
    print("🎯 CONVERSOR SSIM CORRIGIDO")
    print("Baseado no padrão IATA e projeto original")
    print("=" * 60)
    
    if not os.path.exists(excel_path):
        print(f"❌ Arquivo não encontrado: {excel_path}")
        return
    
    output_file = gerar_ssim_corrigido(excel_path, codigo_iata, max_flights)
    
    if output_file:
        print("\\n🎉 CONVERSÃO CONCLUÍDA COM SUCESSO!")
        print(f"📁 Arquivo gerado: {output_file}")
        
        # Mostrar algumas linhas do arquivo
        print("\\n📄 PRIMEIRAS LINHAS DE VOOS:")
        print("-" * 60)
        try:
            with open(output_file, 'r') as f:
                lines = f.readlines()
                flight_lines = [line.rstrip() for line in lines if line.startswith('3 ')]
                
                for i, line in enumerate(flight_lines[:5]):
                    print(f"{i+1:2d}: {line}")
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
    else:
        print("❌ FALHA NA CONVERSÃO!")

if __name__ == "__main__":
    main()
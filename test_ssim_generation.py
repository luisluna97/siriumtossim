#!/usr/bin/env python3
"""
Teste direto do conversor SSIM - sem interface Streamlit
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

def gerar_ssim_ts09_standalone(excel_path, codigo_iata, output_file=None, max_flights=50):
    """
    Gera arquivo SSIM a partir do arquivo TS.09 - versão standalone
    """
    try:
        print(f"🔄 Carregando arquivo {excel_path}...")
        
        # Ler o arquivo TS.09
        df = pd.read_excel(excel_path)
        print(f"✅ Arquivo carregado com {len(df)} registros")
        
        # Limitar número de voos para teste
        if len(df) > max_flights:
            df = df.head(max_flights)
            print(f"⚠️  Limitando a {max_flights} voos para teste")
        
        # Carregar arquivos de referência
        print("📂 Carregando arquivos de referência...")
        
        try:
            airport_df = pd.read_csv('airport.csv')
            airport_df['IATA'] = airport_df['IATA'].str.strip().str.upper()
            airport_df['Timezone'] = airport_df['Timezone'].replace('\\\\N', '0')
            airport_df['Timezone'] = pd.to_numeric(airport_df['Timezone'], errors='coerce').fillna(0)
            iata_to_timezone = dict(zip(airport_df['IATA'], airport_df['Timezone']))
            print(f"✅ Aeroportos carregados: {len(airport_df)} registros")
        except Exception as e:
            print(f"⚠️  Erro ao carregar airport.csv: {e}")
            iata_to_timezone = {}
        
        try:
            aircraft_df = pd.read_excel('ACT TYPE.xlsx')
            aircraft_df['ICAO'] = aircraft_df['ICAO'].str.strip().str.upper()
            aircraft_df['IATA'] = aircraft_df['IATA'].str.strip()
            icao_to_iata_aircraft = dict(zip(aircraft_df['ICAO'], aircraft_df['IATA']))
            print(f"✅ Aeronaves carregadas: {len(aircraft_df)} registros")
        except Exception as e:
            print(f"⚠️  Erro ao carregar ACT TYPE.xlsx: {e}")
            icao_to_iata_aircraft = {}
        
        # Processar dados do TS.09
        print("🔄 Processando dados dos voos...")
        processed_flights = []
        
        for idx, row in df.iterrows():
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
                print(f"⚠️  Pulando voo {flight_number}: dados incompletos")
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
            
            # Mostrar progresso
            if (idx + 1) % 10 == 0:
                print(f"  Processados {idx + 1} voos...")
        
        if not processed_flights:
            print("❌ Nenhum voo válido foi processado!")
            return False
        
        print(f"✅ Processados {len(processed_flights)} voos válidos")
        
        # Mostrar estatísticas de conexões
        with_connections = sum(1 for f in processed_flights if f['next_flight'])
        print(f"📊 Voos com conexões: {with_connections}/{len(processed_flights)} ({with_connections/len(processed_flights)*100:.1f}%)")
        
        # Determinar período de dados
        all_dates = [f['partida_dt'] for f in processed_flights] + [f['chegada_dt'] for f in processed_flights]
        data_min = min(all_dates).strftime("%d%b%y").upper()
        data_max = max(all_dates).strftime("%d%b%y").upper()
        data_emissao = datetime.now().strftime("%d%b%y").upper()
        data_emissao2 = datetime.now().strftime("%Y%m%d")
        
        # Criar nome do arquivo
        if output_file is None:
            output_file = f"{codigo_iata}_{data_emissao2}_{data_min}-{data_max}.ssim"
        
        print(f"📝 Gerando arquivo SSIM: {output_file}")
        
        # Gerar arquivo SSIM
        with open(output_file, 'w') as file:
            numero_linha = 1
            
            # Linha 1 - Header
            linha_1 = ajustar_linha("1AIRLINE STANDARD SCHEDULE DATA SET" + " " * 157 + f"{numero_linha:08}")
            file.write(linha_1 + "\n")
            numero_linha += 1
            
            # Linhas de zeros
            for _ in range(4):
                file.write("0" * 200 + "\n")
                numero_linha += 1
            
            # Linha 2 - Carrier info
            linha_2_base = f"2U{codigo_iata}  0008    {data_min}{data_max}{data_emissao}Created by TS.09 Converter"
            linha_2 = ajustar_linha(linha_2_base + " " * (72 - len(linha_2_base)) + "P" + " " * 115 + f" EN08{numero_linha:08}")
            file.write(linha_2 + "\n")
            numero_linha += 1
            
            # Linhas de zeros
            for _ in range(4):
                file.write("0" * 200 + "\n")
                numero_linha += 1
            
            # Ordenar voos por número e data
            processed_flights.sort(key=lambda x: (x['flight_number'], x['partida_dt']))
            
            print("🔄 Escrevendo linhas de voos...")
            
            # Linhas 3 - Dados dos voos
            flight_date_counter = {}
            
            for flight_idx, flight in enumerate(processed_flights):
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
                
                # Número do voo para exibição
                flight_display = f"{flight_num:>5d}"
                
                # PRÓXIMO VOO - AQUI ESTÁ A CORREÇÃO!
                next_flight_field = ""
                if flight['next_flight']:
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
                    f"{' ':21}"                    # Espaços
                    f"{next_flight_field:<7}"      # PRÓXIMO VOO CORRETO!
                    f"{' ':11}"                    # Espaços restantes
                    f"{numero_linha:08}"           # Número da linha
                )
                
                # Garantir 200 caracteres
                linha_3 = ajustar_linha(linha_3)
                file.write(linha_3 + "\n")
                numero_linha += 1
                
                # Mostrar alguns exemplos
                if flight_idx < 5:
                    next_info = f" → {flight['next_flight']}" if flight['next_flight'] else ""
                    print(f"  Voo {flight_num}: {flight['origem']} → {flight['destino']}{next_info}")
            
            # Linhas de zeros finais
            for _ in range(4):
                file.write("0" * 200 + "\n")
                numero_linha += 1
            
            # Linha 5 - Footer
            linha_5 = ajustar_linha(f"5 {codigo_iata} {data_emissao}" + " " * 175 + f"{numero_linha:06}E{numero_linha+1:06}")
            file.write(linha_5 + "\n")
        
        print(f"✅ Arquivo SSIM gerado com sucesso: {output_file}")
        print(f"📊 Total de linhas: {numero_linha + 1}")
        print(f"📁 Tamanho do arquivo: {os.path.getsize(output_file)} bytes")
        
        return True
            
    except Exception as e:
        print(f"❌ Erro ao gerar arquivo SSIM: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal de teste"""
    print("=" * 60)
    print("🚀 TESTE DO CONVERSOR SSIM - TS.09")
    print("=" * 60)
    
    # Configurações do teste
    excel_path = 'TS.09 VERSION 01 - SEPT 2025 - YYZ.xls'
    codigo_iata = "TS"  # Air Transat
    max_flights = 100  # Mais voos para análise completa
    
    print(f"📋 Configurações:")
    print(f"   Arquivo: {excel_path}")
    print(f"   Companhia: {codigo_iata}")
    print(f"   Limite de voos: {max_flights}")
    print()
    
    # Verificar se arquivo existe
    if not os.path.exists(excel_path):
        print(f"❌ Arquivo não encontrado: {excel_path}")
        return
    
    # Executar conversão
    success = gerar_ssim_ts09_standalone(excel_path, codigo_iata, max_flights=max_flights)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        
        # Mostrar arquivo gerado
        output_files = [f for f in os.listdir('.') if f.endswith('.ssim')]
        if output_files:
            latest_file = max(output_files, key=os.path.getctime)
            print(f"📁 Arquivo gerado: {latest_file}")
            
            # Mostrar primeiras linhas do arquivo
            print("\n📄 Primeiras 10 linhas do arquivo SSIM:")
            print("-" * 60)
            try:
                with open(latest_file, 'r') as f:
                    for i, line in enumerate(f):
                        if i < 10:
                            print(f"{i+1:2d}: {line.rstrip()}")
                        else:
                            break
            except Exception as e:
                print(f"Erro ao ler arquivo: {e}")
                
    else:
        print("\n❌ TESTE FALHOU!")

if __name__ == "__main__":
    main()
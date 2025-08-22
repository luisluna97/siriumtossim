#!/usr/bin/env python3
"""
Conversor SSIM SUPER SIMPLES
1 linha do Excel = 1 linha do SSIM
"""

import pandas as pd
from datetime import datetime

print("🚀 CONVERSOR SSIM SIMPLES")
print("1 linha Excel = 1 linha SSIM")
print("=" * 40)

try:
    # Carregar dados
    print("📂 Carregando Excel...")
    df = pd.read_excel('TS.09 VERSION 01 - SEPT 2025 - YYZ.xls')
    print(f"✅ {len(df)} linhas carregadas")
    
    # Pegar apenas 10 linhas para teste
    df_teste = df.head(10)
    print(f"📊 Processando {len(df_teste)} linhas de teste")
    
    # Configurações
    codigo_iata = "TS"
    output_file = f"{codigo_iata}_SIMPLES.ssim"
    data_hoje = datetime.now().strftime("%d%b%y").upper()
    
    print(f"📝 Gerando {output_file}...")
    
    # Criar arquivo
    with open(output_file, 'w') as f:
        linha_num = 1
        
        # === CABEÇALHO SIMPLES ===
        
        # Linha 1
        header = "1AIRLINE STANDARD SCHEDULE DATA SET"
        espacos = 200 - len(header) - 8
        linha1 = header + " " * espacos + f"{linha_num:08}"
        f.write(linha1 + "\\n")
        linha_num += 1
        
        # 4 zeros
        for _ in range(4):
            f.write("0" * 200 + "\\n")
            linha_num += 1
        
        # Linha companhia
        linha2 = f"2U{codigo_iata}  0008    01SEP2530SEP25{data_hoje}Created by dnata capacity"
        linha2 += " " * (72 - len(linha2)) + "P"
        linha2 += " " * (200 - len(linha2) - 13) + f" EN08{linha_num:08}"
        f.write(linha2 + "\\n")
        linha_num += 1
        
        # 4 zeros
        for _ in range(4):
            f.write("0" * 200 + "\\n")
            linha_num += 1
        
        # === PROCESSAR CADA LINHA DO EXCEL ===
        
        print("🔄 Processando voos...")
        
        for idx, row in df_teste.iterrows():
            try:
                # Dados básicos
                flight_num = int(row['Flight-Number'])
                route = str(row['Route']).strip()
                date_str = str(row['Date-LT']).strip()
                weekday = int(row['Week-Day-LT'])
                std_str = str(row['Std-LT']).strip()
                sta_str = str(row['Sta-LT']).strip()
                
                # Próximo voo
                onward = row['Onward Flight']
                next_flight = ""
                if pd.notna(onward):
                    next_str = str(onward).replace('TS', '').strip()
                    try:
                        next_num = int(next_str)
                        if next_num != flight_num:  # Não repetir o mesmo voo
                            next_flight = f"TS{next_num:>3d}"
                    except:
                        pass
                
                # Extrair origem e destino
                if ' / ' in route:
                    origem, destino = route.split(' / ')
                    origem = origem.strip()[:3]
                    destino = destino.strip()[:3]
                else:
                    continue
                
                # Converter data
                try:
                    data_obj = pd.to_datetime(date_str, format='%d%b%y')
                    data_formatada = data_obj.strftime('%d%b%y').upper()
                except:
                    data_formatada = date_str
                
                # Horários
                try:
                    hora_std = pd.to_datetime(std_str, format='%H:%M').strftime('%H%M')
                    hora_sta = pd.to_datetime(sta_str, format='%H:%M').strftime('%H%M')
                except:
                    hora_std = std_str.replace(':', '')[:4]
                    hora_sta = sta_str.replace(':', '')[:4]
                
                # Frequência (só o dia específico)
                freq = [" "] * 7
                if 1 <= weekday <= 7:
                    freq[weekday - 1] = str(weekday)
                frequencia = "".join(freq)
                
                # ID do voo
                flight_id = f"{flight_num:04d}0101"  # Simples: NNNN0101
                
                # === MONTAR LINHA SSIM ===
                
                linha_ssim = (
                    f"3 "                    # Tipo
                    f"{codigo_iata} "        # Companhia
                    f"{flight_id}"          # ID voo (8 chars)
                    f"J"                    # Status
                    f"{data_formatada}"     # Data partida
                    f"{data_formatada}"     # Data chegada
                    f"{frequencia}"         # Frequência
                    f" "                    # Espaço
                    f"{origem:<3}"          # Origem
                    f"{hora_std}"           # Hora partida
                    f"{hora_std}"           # Hora partida rep
                    f"-0500"                # Timezone
                    f"  "                   # Espaços
                    f"{destino:<3}"         # Destino
                    f"{hora_sta}"           # Hora chegada
                    f"{hora_sta}"           # Hora chegada rep
                    f"+0000"                # Timezone
                    f"  "                   # Espaços
                    f"332"                  # Aeronave
                    f"{' ' * 53}"           # Espaços reservados
                    f"{codigo_iata}"        # Companhia op
                    f"{' ' * 7}"            # Espaços
                    f"{codigo_iata}"        # Companhia mkt
                    f"{flight_num:>5d}"     # Número voo
                    f"{' ' * 28}"           # Espaços
                    f"{next_flight:<6}"     # PRÓXIMO VOO (aqui!)
                    f"{' ' * 5}"            # Espaços
                    f"{' ' * 9}"            # Espaços
                    f"{linha_num:08}"       # Número linha
                )
                
                # Ajustar para 200 caracteres
                if len(linha_ssim) > 200:
                    linha_ssim = linha_ssim[:200]
                else:
                    linha_ssim += " " * (200 - len(linha_ssim))
                
                f.write(linha_ssim + "\\n")
                linha_num += 1
                
                # Mostrar progresso
                print(f"  Voo {flight_num}: {origem} → {destino} ➜ {next_flight if next_flight else 'Sem conexão'}")
                
            except Exception as e:
                print(f"  ❌ Erro na linha {idx}: {e}")
                continue
        
        # === RODAPÉ ===
        
        # 4 zeros
        for _ in range(4):
            f.write("0" * 200 + "\\n")
            linha_num += 1
        
        # Linha final
        linha_final = f"5 {codigo_iata} {data_hoje}"
        linha_final += " " * (200 - len(linha_final) - 14) + f"{linha_num:06}E{linha_num+1:06}"
        f.write(linha_final + "\\n")
    
    print(f"\\n✅ Arquivo gerado: {output_file}")
    print(f"📊 Total de linhas: {linha_num}")
    
    # Verificar arquivo
    with open(output_file, 'r') as f:
        linhas = f.readlines()
    
    print(f"📁 Arquivo criado com {len(linhas)} linhas")
    
    # Mostrar primeiras linhas de voo
    print("\\n📄 PRIMEIRAS LINHAS DE VOO:")
    voo_linhas = [l.rstrip() for l in linhas if l.startswith('3 ')]
    for i, linha in enumerate(voo_linhas[:3]):
        print(f"{i+1}: {linha}")
    
    print("\\n🎉 CONVERSÃO CONCLUÍDA!")
    
except Exception as e:
    print(f"❌ ERRO GERAL: {e}")
    import traceback
    traceback.print_exc()
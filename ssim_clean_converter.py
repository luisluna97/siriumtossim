#!/usr/bin/env python3
"""
Conversor SSIM limpo e correto - baseado no projeto original
"""

import pandas as pd
from datetime import datetime, timedelta

def gerar_ssim_limpo():
    """Gerar arquivo SSIM limpo e correto"""
    
    print("🚀 CONVERSOR SSIM LIMPO")
    print("=" * 50)
    
    # Carregar dados
    print("📂 Carregando dados...")
    df = pd.read_excel('TS.09 VERSION 01 - SEPT 2025 - YYZ.xls')
    df_sample = df.head(20)  # Apenas 20 voos para teste
    
    codigo_iata = "TS"
    output_file = f"{codigo_iata}_LIMPO.ssim"
    
    print(f"✅ {len(df_sample)} voos carregados")
    
    # Processar dados
    voos = []
    for _, row in df_sample.iterrows():
        flight_num = int(row['Flight-Number'])
        route = str(row['Route']).strip()
        onward = row['Onward Flight']
        
        # Extrair origem e destino
        if ' / ' in route:
            origem, destino = route.split(' / ')
            origem = origem.strip()
            destino = destino.strip()
        else:
            continue
        
        # Próximo voo (SEM repetir o atual)
        next_flight = None
        if pd.notna(onward):
            next_str = str(onward).replace('TS', '').strip()
            try:
                next_flight = int(next_str)
                if next_flight == flight_num:  # Se for igual ao atual, ignorar
                    next_flight = None
            except:
                next_flight = None
        
        # Datas e horários
        date_str = str(row['Date-LT']).strip()
        std_str = str(row['Std-LT']).strip()
        sta_str = str(row['Sta-LT']).strip()
        weekday = int(row['Week-Day-LT'])
        
        try:
            date_part = pd.to_datetime(date_str, format='%d%b%y')
            std_time = pd.to_datetime(std_str, format='%H:%M').time()
            sta_time = pd.to_datetime(sta_str, format='%H:%M').time()
            
            partida_dt = datetime.combine(date_part.date(), std_time)
            chegada_dt = datetime.combine(date_part.date(), sta_time)
            
            if chegada_dt < partida_dt:
                chegada_dt += timedelta(days=1)
            
        except:
            continue
        
        voos.append({
            'flight_num': flight_num,
            'origem': origem,
            'destino': destino,
            'partida_dt': partida_dt,
            'chegada_dt': chegada_dt,
            'weekday': weekday,
            'next_flight': next_flight
        })
    
    print(f"✅ {len(voos)} voos processados")
    
    # Contar conexões válidas
    conexoes_validas = sum(1 for v in voos if v['next_flight'] is not None)
    print(f"🔗 {conexoes_validas} conexões válidas encontradas")
    
    # Gerar arquivo SSIM
    print(f"📝 Gerando {output_file}...")
    
    # Datas para cabeçalho
    data_min = min([v['partida_dt'] for v in voos]).strftime("%d%b%y").upper()
    data_max = max([v['chegada_dt'] for v in voos]).strftime("%d%b%y").upper()
    data_emissao = datetime.now().strftime("%d%b%y").upper()
    
    with open(output_file, 'w') as f:
        linha_num = 1
        
        # === CABEÇALHO (igual ao projeto original) ===
        
        # Linha 1
        linha1 = "1AIRLINE STANDARD SCHEDULE DATA SET"
        espacos = 200 - len(linha1) - 8
        linha1 += " " * espacos + f"{linha_num:08}"
        f.write(linha1 + "\\n")
        linha_num += 1
        
        # 4 linhas de zeros
        for _ in range(4):
            f.write("0" * 200 + "\\n")
            linha_num += 1
        
        # Linha 2 (cabeçalho da companhia)
        linha2_base = f"2U{codigo_iata}  0008    {data_min}{data_max}{data_emissao}Created by dnata capacity"
        espacos_antes_p = 72 - len(linha2_base) - 1
        linha2 = linha2_base + " " * espacos_antes_p + "P"
        linha2_fim = f" EN08{linha_num:08}"
        espacos_restantes = 200 - len(linha2) - len(linha2_fim)
        linha2 += " " * espacos_restantes + linha2_fim
        f.write(linha2 + "\\n")
        linha_num += 1
        
        # 4 linhas de zeros
        for _ in range(4):
            f.write("0" * 200 + "\\n")
            linha_num += 1
        
        # === LINHAS DE VOOS ===
        
        flight_counters = {}
        
        for voo in voos:
            flight_num = voo['flight_num']
            
            # Contador de ocorrências do voo
            if flight_num not in flight_counters:
                flight_counters[flight_num] = 0
            flight_counters[flight_num] += 1
            
            # Formatar dados
            data_partida = voo['partida_dt'].strftime("%d%b%y").upper()
            data_chegada = voo['chegada_dt'].strftime("%d%b%y").upper()
            hora_partida = voo['partida_dt'].strftime("%H%M")
            hora_chegada = voo['chegada_dt'].strftime("%H%M")
            
            # Frequência (dia da semana)
            freq = [" "] * 7
            if 1 <= voo['weekday'] <= 7:
                freq[voo['weekday'] - 1] = str(voo['weekday'])
            frequencia = "".join(freq)
            
            # ID do voo (8 caracteres)
            flight_id = f"{flight_num:04d}{flight_counters[flight_num]:02d}01"
            
            # Número do voo para exibição
            flight_display = f"{flight_num:>5d}"
            
            # === CONSTRUIR LINHA 3 (FORMATO CORRETO) ===
            
            linha3 = (
                f"3 "                      # Pos 1-2: Tipo
                f"{codigo_iata:<2} "       # Pos 3-5: Companhia + espaço
                f"{flight_id}"            # Pos 6-13: ID do voo (8 chars)
                f"J"                      # Pos 14: Status (J=passageiro)
                f"{data_partida}"         # Pos 15-21: Data partida (7 chars)
                f"{data_chegada}"         # Pos 22-28: Data chegada (7 chars)
                f"{frequencia}"           # Pos 29-35: Frequência (7 chars)
                f" "                      # Pos 36: Espaço
                f"{voo['origem']:<3}"     # Pos 37-39: Origem (3 chars)
                f"{hora_partida}"         # Pos 40-43: Hora partida (4 chars)
                f"{hora_partida}"         # Pos 44-47: Hora partida rep (4 chars)
                f"-0500"                  # Pos 48-52: Timezone origem (5 chars)
                f"  "                     # Pos 53-54: Espaços (2 chars)
                f"{voo['destino']:<3}"    # Pos 55-57: Destino (3 chars)
                f"{hora_chegada}"         # Pos 58-61: Hora chegada (4 chars)
                f"{hora_chegada}"         # Pos 62-65: Hora chegada rep (4 chars)
                f"+0000"                  # Pos 66-70: Timezone destino (5 chars)
                f"  "                     # Pos 71-72: Espaços (2 chars)
                f"332"                    # Pos 73-75: Aeronave (3 chars)
                f"{' ' * 53}"             # Pos 76-128: Espaços reservados (53 chars)
                f"{codigo_iata:<2}"       # Pos 129-130: Companhia op (2 chars)
                f"{' ' * 7}"              # Pos 131-137: Espaços (7 chars)
                f"{codigo_iata:<2}"       # Pos 138-139: Companhia mkt (2 chars)
                f"{flight_display}"       # Pos 140-144: Número voo (5 chars)
                f"{' ' * 28}"             # Pos 145-172: Espaços (28 chars)
            )
            
            # === PRÓXIMO VOO (POSIÇÃO 173-178) ===
            if voo['next_flight']:
                next_field = f"{codigo_iata}{voo['next_flight']:>3d}"  # Ex: "TS123"
                linha3 += f"{next_field:<6}"  # Pos 173-178: Próximo voo (6 chars)
            else:
                linha3 += f"{' ' * 6}"        # Pos 173-178: Espaços se sem conexão
            
            # Completar até 200 caracteres
            linha3 += f"{' ' * 5}"            # Pos 179-183: Espaços (5 chars)
            linha3 += f"{' ' * 9}"            # Pos 184-192: Espaços (9 chars)
            linha3 += f"{linha_num:08}"       # Pos 193-200: Número linha (8 chars)
            
            # Garantir exatamente 200 caracteres
            if len(linha3) > 200:
                linha3 = linha3[:200]
            elif len(linha3) < 200:
                linha3 += " " * (200 - len(linha3))
            
            f.write(linha3 + "\\n")
            linha_num += 1
        
        # === RODAPÉ ===
        
        # 4 linhas de zeros
        for _ in range(4):
            f.write("0" * 200 + "\\n")
            linha_num += 1
        
        # Linha final
        linha_final = f"5 {codigo_iata} {data_emissao}"
        espacos_finais = 200 - len(linha_final) - 14  # 14 = 6 + 8
        linha_final += " " * espacos_finais + f"{linha_num:06}E{linha_num+1:06}"
        f.write(linha_final + "\\n")
    
    print(f"✅ Arquivo gerado: {output_file}")
    
    # Mostrar estatísticas
    print(f"\\n📊 ESTATÍSTICAS:")
    print(f"   Voos processados: {len(voos)}")
    print(f"   Conexões válidas: {conexoes_validas}")
    print(f"   Taxa de conexão: {conexoes_validas/len(voos)*100:.1f}%")
    
    # Mostrar primeiras conexões
    print(f"\\n🔗 PRIMEIRAS CONEXÕES:")
    for i, voo in enumerate(voos[:5]):
        if voo['next_flight']:
            print(f"   Voo {voo['flight_num']:3d}: {voo['origem']} → {voo['destino']} ➜ {voo['next_flight']}")
        else:
            print(f"   Voo {voo['flight_num']:3d}: {voo['origem']} → {voo['destino']} ➜ Sem conexão")
    
    return output_file

if __name__ == "__main__":
    gerar_ssim_limpo()
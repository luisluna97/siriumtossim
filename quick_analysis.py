#!/usr/bin/env python3
"""
Análise rápida do arquivo SSIM atual
"""

def analyze_current_ssim():
    """Analisar o arquivo SSIM atual linha por linha"""
    
    print("🔍 ANÁLISE RÁPIDA DO ARQUIVO SSIM ATUAL")
    print("=" * 60)
    
    try:
        with open('TS_20250821_01SEP25-03SEP25_CORRIGIDO.ssim', 'r') as f:
            lines = f.readlines()
        
        print(f"Total de linhas: {len(lines)}")
        
        # Analisar linha de voo (tipo 3)
        flight_lines = [line.rstrip() for line in lines if line.startswith('3 ')]
        print(f"Linhas de voos: {len(flight_lines)}")
        
        if flight_lines:
            print("\n📋 PRIMEIRA LINHA DE VOO:")
            line = flight_lines[0]
            print(f"Comprimento: {len(line)} caracteres")
            print(f"Linha: {line}")
            
            # Analisar posições
            print("\n📊 ANÁLISE POR POSIÇÕES:")
            print(f"Pos 1-2   : '{line[0:2]}'     (Tipo)")
            print(f"Pos 3-5   : '{line[2:5]}'     (Companhia)")
            print(f"Pos 6-13  : '{line[5:13]}'   (ID voo)")
            print(f"Pos 14    : '{line[13]}'      (Status)")
            print(f"Pos 15-21 : '{line[14:21]}'   (Data partida)")
            print(f"Pos 22-28 : '{line[21:28]}'   (Data chegada)")
            print(f"Pos 29-35 : '{line[28:35]}'   (Frequência)")
            print(f"Pos 37-39 : '{line[36:39]}'   (Origem)")
            print(f"Pos 40-43 : '{line[39:43]}'   (Hora partida)")
            print(f"Pos 44-47 : '{line[43:47]}'   (Hora partida rep)")
            print(f"Pos 48-52 : '{line[47:52]}'   (TZ origem)")
            print(f"Pos 55-57 : '{line[54:57]}'   (Destino)")
            print(f"Pos 58-61 : '{line[57:61]}'   (Hora chegada)")
            print(f"Pos 62-65 : '{line[61:65]}'   (Hora chegada rep)")
            print(f"Pos 66-70 : '{line[65:70]}'   (TZ destino)")
            print(f"Pos 73-75 : '{line[72:75]}'   (Aeronave)")
            
            # Área onde deveria estar o próximo voo
            print(f"\n🔗 ÁREA DE CONEXÕES:")
            print(f"Pos 140-144: '{line[139:144]}'  (Voo atual)")
            print(f"Pos 170-180: '{line[169:179]}'  (Área próximo voo)")
            print(f"Pos 180-190: '{line[179:189]}'  (Continuação)")
            
            # Procurar padrão TS XXX
            import re
            ts_matches = re.findall(r'TS\s+(\d+)', line)
            print(f"\nNúmeros encontrados após TS: {ts_matches}")
            
        # Analisar algumas conexões
        print(f"\n🔗 CONEXÕES NAS PRIMEIRAS 5 LINHAS:")
        for i, line in enumerate(flight_lines[:5]):
            # Extrair número do voo atual
            flight_id = line[5:13].strip()
            current_flight = flight_id[:4]  # Primeiros 4 dígitos
            
            # Procurar próximo voo
            import re
            ts_matches = re.findall(r'TS\s+(\d+)', line)
            
            next_flights = []
            for match in ts_matches:
                if match != current_flight:
                    next_flights.append(match)
            
            print(f"Linha {i+1}: Voo {current_flight} → Próximos: {next_flights}")
        
        print(f"\n✅ Análise concluída")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    analyze_current_ssim()
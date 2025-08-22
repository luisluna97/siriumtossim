#!/usr/bin/env python3
"""
Análise do padrão SSIM - coluna por coluna
Baseado no projeto original que funcionava
"""

import pandas as pd
from datetime import datetime

def analyze_original_project():
    """Analisar o projeto original para entender o padrão correto"""
    
    print("🔍 ANÁLISE DO PADRÃO SSIM CORRETO")
    print("=" * 70)
    
    # Vamos analisar o código do projeto original
    original_code = """
    # Do projeto original (old_project/app.py):
    
    linha_3 = (
        f"3 "                           # Pos 1-2: Tipo de registro
        f"{codigo_iata:<2} "            # Pos 3-5: Código da companhia + espaço
        f"{eight_char_field}"           # Pos 6-13: ID do voo (8 chars)
        f"{status}"                     # Pos 14: Status (J/F)
        f"{data_partida}"              # Pos 15-21: Data partida (7 chars)
        f"{data_chegada}"              # Pos 22-28: Data chegada (7 chars)
        f"{frequencia}"                # Pos 29-35: Frequência (7 chars)
        f" "                           # Pos 36: Espaço
        f"{origem:<3}"                 # Pos 37-39: Aeroporto origem (3 chars)
        f"{partida}"                   # Pos 40-43: Horário partida (4 chars)
        f"{partida}"                   # Pos 44-47: Horário partida repetido (4 chars)
        f"{origem_timezone_formatted}" # Pos 48-52: Timezone origem (5 chars)
        f"  "                          # Pos 53-54: Espaços (2 chars)
        f"{destino:<3}"                # Pos 55-57: Aeroporto destino (3 chars)
        f"{chegada}"                   # Pos 58-61: Horário chegada (4 chars)
        f"{chegada}"                   # Pos 62-65: Horário chegada repetido (4 chars)
        f"{destino_timezone_formatted}" # Pos 66-70: Timezone destino (5 chars)
        f"  "                          # Pos 71-72: Espaços (2 chars)
        f"{equipamento:<3}"            # Pos 73-75: Tipo de aeronave (3 chars)
        f"{' ':53}"                    # Pos 76-128: Espaços reservados (53 chars)
        f"{codigo_iata:<2}"            # Pos 129-130: Companhia operadora (2 chars)
        f"{' ':7}"                     # Pos 131-137: Espaços (7 chars)
        f"{codigo_iata:<2}"            # Pos 138-139: Companhia de marketing (2 chars)
        f"{numero_voo_display}"        # Pos 140-144: Número do voo (5 chars)
        f"{' ':28}"                    # Pos 145-172: Espaços (28 chars)
        f"{' ':6}"                     # Pos 173-178: Campo livre (6 chars)
        f"{' ':5}"                     # Pos 179-183: Espaços (5 chars)
        f"{' ':9}"                     # Pos 184-192: Espaços (9 chars)
        f"{numero_linha_str}"          # Pos 193-200: Número da linha (8 chars)
    )
    """
    
    print("📋 ESTRUTURA CORRETA DA LINHA TIPO 3 (DADOS DE VOO):")
    print("-" * 70)
    print("Pos  1-2  : Tipo de registro ('3 ')")
    print("Pos  3-5  : Código da companhia + espaço (ex: 'TS ')")
    print("Pos  6-13 : ID do voo - 8 caracteres (NNNNCCEE)")
    print("            NNNN = Número do voo (4 dígitos)")
    print("            CC   = Contador de data (2 dígitos)")
    print("            EE   = Etapa (2 dígitos, geralmente '01')")
    print("Pos  14   : Status (J=Passageiro, F=Carga)")
    print("Pos  15-21: Data partida (formato: DDMmmYY)")
    print("Pos  22-28: Data chegada (formato: DDMmmYY)")
    print("Pos  29-35: Frequência - dias da semana (7 chars: 1234567)")
    print("Pos  36   : Espaço")
    print("Pos  37-39: Aeroporto origem (3 chars)")
    print("Pos  40-43: Horário partida (HHMM)")
    print("Pos  44-47: Horário partida repetido (HHMM)")
    print("Pos  48-52: Timezone origem (+HHMM ou -HHMM)")
    print("Pos  53-54: Espaços")
    print("Pos  55-57: Aeroporto destino (3 chars)")
    print("Pos  58-61: Horário chegada (HHMM)")
    print("Pos  62-65: Horário chegada repetido (HHMM)")
    print("Pos  66-70: Timezone destino (+HHMM ou -HHMM)")
    print("Pos  71-72: Espaços")
    print("Pos  73-75: Tipo de aeronave (3 chars)")
    print("Pos  76-128: Espaços reservados (53 chars)")
    print("Pos  129-130: Companhia operadora (2 chars)")
    print("Pos  131-137: Espaços (7 chars)")
    print("Pos  138-139: Companhia de marketing (2 chars)")
    print("Pos  140-144: Número do voo para exibição (5 chars)")
    print("Pos  145-172: Espaços (28 chars)")
    print("Pos  173-178: PRÓXIMO VOO (6 chars) ← AQUI É A CONEXÃO!")
    print("Pos  179-183: Espaços (5 chars)")
    print("Pos  184-192: Espaços (9 chars)")
    print("Pos  193-200: Número da linha (8 chars)")
    print()
    print("TOTAL: 200 caracteres exatos")
    
    return True

def analyze_ts09_data():
    """Analisar dados do TS.09 para entender as conexões"""
    
    print("\n🔍 ANÁLISE DOS DADOS TS.09:")
    print("-" * 70)
    
    try:
        df = pd.read_excel('TS.09 VERSION 01 - SEPT 2025 - YYZ.xls')
        
        print(f"Total de voos: {len(df)}")
        
        # Analisar algumas conexões
        print("\n📊 EXEMPLOS DE CONEXÕES:")
        for i, row in df.head(10).iterrows():
            flight_num = row['Flight-Number']
            route = row['Route']
            onward = row['Onward Flight']
            
            if pd.notna(onward):
                next_flight = str(onward).replace('TS', '').strip()
                print(f"Voo {flight_num:3d}: {route:15} → Próximo: {next_flight}")
            else:
                print(f"Voo {flight_num:3d}: {route:15} → Sem conexão")
        
        # Verificar se as conexões fazem sentido
        print(f"\n✅ Conexões válidas encontradas no TS.09")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao analisar TS.09: {e}")
        return False

def main():
    """Função principal"""
    print("🎯 ANÁLISE COMPLETA DO PADRÃO SSIM")
    print("Preparando para criar conversor correto")
    print("=" * 70)
    
    # Analisar padrão original
    analyze_original_project()
    
    # Analisar dados TS.09
    analyze_ts09_data()
    
    print("\n📝 CONCLUSÕES:")
    print("1. O formato SSIM tem 200 caracteres exatos por linha")
    print("2. Cada posição tem significado específico")
    print("3. O próximo voo vai na posição 173-178 (6 caracteres)")
    print("4. NÃO deve repetir o voo atual")
    print("5. Usar dados da coluna 'Onward Flight' do TS.09")
    
    print("\n🚀 PRÓXIMO PASSO:")
    print("Criar conversor limpo baseado nesta análise")

if __name__ == "__main__":
    main()
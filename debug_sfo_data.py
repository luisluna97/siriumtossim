#!/usr/bin/env python3
"""
Debug script para identificar exatamente onde está o erro float/string
"""

import pandas as pd
import numpy as np

def debug_sfo_data():
    """Debug detalhado dos dados SFO"""
    try:
        print("🔍 DEBUG DETALHADO - SFO DATA")
        print("=" * 50)
        
        # Ler arquivo
        df = pd.read_excel('SFO_Schedule_Weekly_Extract_Report_32370.xlsx', header=4)
        print(f"✅ Arquivo lido: {len(df)} linhas, {len(df.columns)} colunas")
        
        # Analisar cada coluna
        print("\n📊 ANÁLISE POR COLUNA:")
        for col in df.columns:
            try:
                col_data = df[col]
                unique_types = set()
                for val in col_data.dropna():
                    unique_types.add(type(val).__name__)
                
                print(f"  {col}: {unique_types}")
                
                # Verificar se há mistura de tipos problemática
                if len(unique_types) > 1:
                    print(f"    ⚠️  TIPOS MISTOS em {col}:")
                    for val in col_data.dropna().head(5):
                        print(f"      {type(val).__name__}: {repr(val)}")
                        
            except Exception as e:
                print(f"    ❌ Erro ao analisar {col}: {e}")
        
        # Testar filtragem específica
        print("\n🧹 TESTE DE FILTRAGEM:")
        
        # Teste 1: Filtrar NaN
        df_step1 = df.dropna(subset=['Orig', 'Dest'])
        print(f"  Após dropna: {len(df_step1)} linhas")
        
        # Teste 2: Converter para string e filtrar
        try:
            df_step2 = df_step1[
                (df_step1['Orig'].astype(str).str.strip() != '') & 
                (df_step1['Dest'].astype(str).str.strip() != '')
            ]
            print(f"  Após filtrar strings vazias: {len(df_step2)} linhas")
        except Exception as e:
            print(f"  ❌ Erro no filtro de strings: {e}")
            return
        
        # Teste 3: Filtrar Flight
        if 'Flight' in df_step2.columns:
            try:
                flight_numeric = pd.to_numeric(df_step2['Flight'], errors='coerce')
                df_step3 = df_step2[flight_numeric.notna()]
                print(f"  Após filtrar Flight inválidos: {len(df_step3)} linhas")
            except Exception as e:
                print(f"  ❌ Erro no filtro de Flight: {e}")
                return
        
        # Teste 4: Verificar companhias aéreas
        airline_col = None
        for col in ['Mkt Al', 'Op Al', 'Airline', 'Carrier']:
            if col in df_step3.columns:
                airline_col = col
                break
        
        if airline_col:
            try:
                companhias = df_step3[airline_col].unique()
                print(f"  🏢 Companhias encontradas: {companhias}")
                
                # Filtrar por AI
                if 'AI' in companhias:
                    df_ai = df_step3[df_step3[airline_col] == 'AI']
                    print(f"  ✈️  Voos AI: {len(df_ai)} linhas")
                    
                    # Testar ordenação - aqui pode estar o problema!
                    print("\n🔄 TESTE DE ORDENAÇÃO:")
                    try:
                        # Teste ordenação simples
                        df_sorted = df_ai.sort_values(by='Flight')
                        print(f"  ✅ Ordenação por Flight OK")
                    except Exception as e:
                        print(f"  ❌ Erro na ordenação por Flight: {e}")
                        
                        # Investigar tipos na coluna Flight
                        print(f"    Tipos em Flight: {[type(x).__name__ for x in df_ai['Flight'].head()]}")
                        print(f"    Valores em Flight: {df_ai['Flight'].head().tolist()}")
                    
                    # Teste ordenação com data
                    if 'Eff Date' in df_ai.columns:
                        try:
                            df_sorted = df_ai.sort_values(by=['Flight', 'Eff Date'])
                            print(f"  ✅ Ordenação por Flight+Date OK")
                        except Exception as e:
                            print(f"  ❌ Erro na ordenação Flight+Date: {e}")
                            
                            # Investigar tipos nas datas
                            print(f"    Tipos em Eff Date: {[type(x).__name__ for x in df_ai['Eff Date'].head()]}")
                            print(f"    Valores em Eff Date: {df_ai['Eff Date'].head().tolist()}")
                            
                else:
                    print("  ⚠️  AI não encontrada")
            except Exception as e:
                print(f"  ❌ Erro ao processar companhias: {e}")
        
        print("\n✅ Debug concluído!")
        
    except Exception as e:
        print(f"❌ Erro geral no debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_sfo_data()

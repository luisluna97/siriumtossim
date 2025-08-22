import pandas as pd
import sys

def analyze_flight_connections():
    """Analisar as conexões de voos no arquivo TS.09"""
    try:
        # Ler o arquivo TS.09
        df = pd.read_excel('TS.09 VERSION 01 - SEPT 2025 - YYZ.xls')
        
        print("=== ANÁLISE DAS CONEXÕES DE VOOS ===")
        print(f"Total de voos: {len(df)}")
        
        # Analisar a coluna 'Onward Flight'
        print(f"\nVoos com próximo voo definido: {df['Onward Flight'].notna().sum()}")
        print(f"Voos sem próximo voo: {df['Onward Flight'].isna().sum()}")
        
        # Mostrar alguns exemplos de conexões
        print("\n=== EXEMPLOS DE CONEXÕES ===")
        connections = df[df['Onward Flight'].notna()][['Flight-Number', 'Route', 'Onward Flight']].head(10)
        for _, row in connections.iterrows():
            print(f"Voo {row['Flight-Number']} ({row['Route']}) -> Próximo: {row['Onward Flight']}")
        
        # Analisar padrões de conexão
        print("\n=== ANÁLISE DE PADRÕES ===")
        
        # Verificar se os voos de conexão realmente existem
        flight_numbers = set(df['Flight-Number'].astype(str))
        onward_flights = df['Onward Flight'].dropna().str.replace('TS', '').astype(str)
        
        valid_connections = 0
        invalid_connections = 0
        
        for onward in onward_flights:
            if onward in flight_numbers:
                valid_connections += 1
            else:
                invalid_connections += 1
        
        print(f"Conexões válidas (voo de destino existe): {valid_connections}")
        print(f"Conexões inválidas (voo de destino não existe): {invalid_connections}")
        
        # Analisar conexões bidirecionais
        print("\n=== ANÁLISE DE CONEXÕES BIDIRECIONAIS ===")
        bidirectional = 0
        
        for _, row in df.iterrows():
            if pd.notna(row['Onward Flight']):
                flight_num = str(row['Flight-Number'])
                onward_num = row['Onward Flight'].replace('TS', '')
                
                # Verificar se o voo de destino tem conexão de volta
                onward_row = df[df['Flight-Number'].astype(str) == onward_num]
                if not onward_row.empty:
                    onward_connection = onward_row.iloc[0]['Onward Flight']
                    if pd.notna(onward_connection) and onward_connection.replace('TS', '') == flight_num:
                        bidirectional += 1
        
        print(f"Conexões bidirecionais encontradas: {bidirectional // 2}")  # Dividir por 2 para não contar duplicatas
        
        # Analisar rotas e conexões lógicas
        print("\n=== ANÁLISE DE ROTAS ===")
        route_analysis = []
        
        for _, row in df.iterrows():
            if pd.notna(row['Onward Flight']):
                flight_num = str(row['Flight-Number'])
                route = row['Route']
                onward_num = row['Onward Flight'].replace('TS', '')
                
                # Encontrar a rota do voo de conexão
                onward_row = df[df['Flight-Number'].astype(str) == onward_num]
                if not onward_row.empty:
                    onward_route = onward_row.iloc[0]['Route']
                    
                    # Extrair destino do voo atual e origem do próximo voo
                    current_dest = route.split(' / ')[-1] if ' / ' in route else route
                    next_origin = onward_route.split(' / ')[0] if ' / ' in onward_route else onward_route
                    
                    route_analysis.append({
                        'flight': flight_num,
                        'current_route': route,
                        'current_dest': current_dest,
                        'next_flight': onward_num,
                        'next_route': onward_route,
                        'next_origin': next_origin,
                        'connection_valid': current_dest == next_origin
                    })
        
        valid_route_connections = sum(1 for r in route_analysis if r['connection_valid'])
        print(f"Conexões com rotas logicamente válidas: {valid_route_connections}/{len(route_analysis)}")
        
        # Mostrar alguns exemplos de conexões inválidas
        invalid_routes = [r for r in route_analysis if not r['connection_valid']]
        if invalid_routes:
            print("\n=== EXEMPLOS DE CONEXÕES INVÁLIDAS ===")
            for r in invalid_routes[:5]:
                print(f"Voo {r['flight']} ({r['current_route']}) termina em {r['current_dest']}")
                print(f"  -> Próximo voo {r['next_flight']} ({r['next_route']}) começa em {r['next_origin']}")
                print(f"  PROBLEMA: {r['current_dest']} != {r['next_origin']}")
                print()
        
        # Salvar análise detalhada
        if route_analysis:
            analysis_df = pd.DataFrame(route_analysis)
            analysis_df.to_csv('flight_connections_analysis.csv', index=False)
            print(f"\nAnálise detalhada salva em 'flight_connections_analysis.csv'")
        
        return route_analysis
        
    except Exception as e:
        print(f"Erro na análise: {e}")
        return []

if __name__ == "__main__":
    analyze_flight_connections()
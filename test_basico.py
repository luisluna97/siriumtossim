print("Teste básico funcionando!")
print("Python está OK")

try:
    import pandas as pd
    print("Pandas OK")
    
    # Teste de leitura do Excel
    df = pd.read_excel('TS.09 VERSION 01 - SEPT 2025 - YYZ.xls')
    print(f"Excel carregado: {len(df)} linhas")
    
    # Mostrar primeira linha
    first_row = df.iloc[0]
    print(f"Primeiro voo: {first_row['Flight-Number']}")
    print(f"Rota: {first_row['Route']}")
    print(f"Próximo voo: {first_row['Onward Flight']}")
    
except Exception as e:
    print(f"Erro: {e}")

print("Teste concluído!")
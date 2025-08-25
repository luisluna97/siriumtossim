# 🛩️ SFO Schedule to SSIM Converter

**Desenvolvido pela Capacity Dnata Brasil**

## 📋 Sobre

Este conversor transforma malhas aéreas do formato **SFO Schedule Weekly Extract Report** para **SSIM** (Standard Schedules Information Manual), padrão da indústria aérea.

## ✨ Características

- 🎯 **Suporte SFO Format**: Processa relatórios SFO Schedule Weekly Extract
- 🏢 **Múltiplas Companhias**: Suporte para várias companhias aéreas no mesmo arquivo
- 🤖 **Seleção Inteligente**: Interface para escolher companhia específica
- ✅ **Validação de Dados**: Verificação de integridade antes da conversão
- 📄 **SSIM Padrão**: Gera arquivos compatíveis com padrões IATA
- 🔄 **Preservação de Dados**: Mantém informações de horários, frequências e rotas

## 🚀 Como Usar

### Aplicação Web (Streamlit)
```bash
streamlit run app_sfo.py
```

### Linha de Comando
```python
from sfo_to_ssim_converter import gerar_ssim_sfo

# Converter arquivo SFO para SSIM
output_file = gerar_ssim_sfo(
    excel_path="SFO_Schedule_Weekly_Extract_Report.xlsx",
    codigo_iata_selecionado="AI",  # Companhia aérea desejada
    output_file="AI_schedule.ssim"  # Opcional
)
```

## 📊 Formato SFO Esperado

O arquivo Excel deve ter:

- **Header na linha 5** (índice 4)
- **Colunas obrigatórias**:
  - `Mkt Al` ou `Op Al`: Código da companhia aérea (2 letras)
  - `Orig`: Aeroporto de origem (código IATA)
  - `Dest`: Aeroporto de destino (código IATA)
  - `Flight`: Número do voo
  - `Eff Date`: Data de início da operação
  - `Disc Date`: Data de fim da operação
  - `Op Days`: Dias operacionais (formato: 1234567)

### Exemplo de Estrutura SFO:
```
Linha 1: Schedule Weekly Extract Report for flights operated by...
Linha 2: (vazia)
Linha 3: (vazia)
Linha 4: (vazia)
Linha 5: Mkt Al | Alliance | Op Al | Orig | Dest | Flight | ...
Linha 6: AI     | Star Alliance | AI | BLR | SFO | 175 | ...
```

## 🔧 Conversores Disponíveis

### 1. Conversor SFO Individual (`app_sfo.py`)
- Interface específica para arquivos SFO
- Seleção de companhia aérea
- Prévia detalhada dos dados

### 2. Multi-Conversor (`app_multi_converter.py`)
- Suporte para TS.09 e SFO
- Detecção automática de formato
- Interface unificada

## 📁 Arquivos Principais

```
sfo_to_ssim_converter.py    # Módulo principal do conversor SFO
app_sfo.py                  # Interface Streamlit específica SFO  
app_multi_converter.py      # Interface multi-formato
test_sfo_converter.py       # Testes básicos
```

## 🏢 Companhias Suportadas

O conversor suporta qualquer companhia aérea presente no arquivo SFO, incluindo:
- **AI** (Air India)
- **AZ** (Alitalia)  
- **BA** (British Airways)
- **BR** (EVA Air)
- **CI** (China Airlines)
- **EK** (Emirates)
- **JL** (Japan Airlines)
- **KE** (Korean Air)
- **LH** (Lufthansa)
- **LX** (Swiss International)
- **MU** (China Eastern)
- **PR** (Philippine Airlines)
- **QF** (Qantas)

## 📋 Dependências

```
pandas>=1.5.0
streamlit>=1.28.0
openpyxl>=3.0.0
```

## 🔄 Processo de Conversão

1. **Leitura**: Carrega arquivo Excel SFO (header=4)
2. **Filtragem**: Seleciona voos da companhia aérea escolhida
3. **Validação**: Verifica integridade dos dados
4. **Mapeamento**: Converte campos SFO para formato SSIM
5. **Geração**: Cria arquivo SSIM padrão IATA
6. **Saída**: Arquivo `.ssim` pronto para uso

## 🎯 Formato SSIM Gerado

- **Linha 1**: Header padrão SSIM
- **Linhas 2**: Informações da companhia aérea
- **Linhas 3**: Dados dos voos (200 caracteres por linha)
- **Linha 5**: Footer com totalizadores

## 🛠️ Características Técnicas

- **Timezone Support**: Mapeamento automático de fusos horários
- **Aircraft Mapping**: Conversão de códigos de aeronave ICAO/IATA
- **Date Handling**: Processamento inteligente de datas e horários
- **Error Handling**: Tratamento robusto de erros
- **Memory Efficient**: Processamento otimizado para arquivos grandes

## 📞 Suporte

Desenvolvido pela **Capacity Dnata Brasil** para operações aéreas profissionais.

Para suporte técnico, entre em contato com a equipe de Capacity Planning.

---

*Versão 1.0 - Dezembro 2024*

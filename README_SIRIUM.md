# ✈️ SIRIUM Schedule to SSIM Converter

**Desenvolvido pela Capacity Dnata Brasil**

## 📋 Sobre o SIRIUM

O **SIRIUM** é um novo formato de conversor de malhas aéreas para SSIM, baseado no padrão SFO Schedule Weekly Extract Reports, mas otimizado e corrigido baseado no `old_project` validado.

## 🎯 Por que SIRIUM?

- **✅ Baseado no old_project**: Usa o mesmo padrão SSIM validado e funcional
- **✅ Formato correto**: Linhas de exatamente 200 caracteres
- **✅ Quebras adequadas**: Formatação correta de arquivo SSIM
- **✅ Estrutura completa**: Header, Carrier Info, Flight Records, Footer
- **✅ Validação integrada**: Verificação automática da estrutura gerada

## 🚀 Como Usar

### Aplicação Web (Streamlit)
```bash
streamlit run app_sirium.py
```

### Linha de Comando
```python
from sirium_to_ssim_converter import gerar_ssim_sirium

# Converter arquivo SIRIUM para SSIM
output_file = gerar_ssim_sirium(
    excel_path="SFO_Schedule_Weekly_Extract_Report.xlsx",
    codigo_iata_selecionado="AI",  # Companhia aérea
    output_file="AI 20250825 19JUL25-05SEP25.ssim"  # Opcional
)
```

## 📊 Formato de Entrada

O arquivo Excel deve ter:

- **Header na linha 5** (índice 4)
- **Colunas esperadas**:
  - `Mkt Al` ou `Op Al`: Código da companhia aérea
  - `Orig`: Aeroporto de origem (IATA)
  - `Dest`: Aeroporto de destino (IATA)  
  - `Flight`: Número do voo
  - `Eff Date`: Data efetiva
  - `Disc Date`: Data de descontinuação
  - `Op Days`: Dias operacionais (1234567)

## 📄 Formato SSIM Gerado

### Estrutura do Arquivo SSIM:
```
Linha 1:     1AIRLINE STANDARD SCHEDULE DATA SET                    00000001
Linhas 2-5:  0000000000... (linhas de zeros)
Linha 6:     2UAI  0008    19JUL2505SEP2525AUG25Created by...       00000006
Linhas 7-10: 0000000000... (linhas de zeros)
Linha 11+:   3 AI 01730101J01AUG2501AUG251234567 DEL0000...        00000011
...
Linhas finais: 0000000000... (linhas de zeros)
Última linha:  5 AI 25AUG25                                         000022E000023
```

### Características do SSIM:
- **200 caracteres por linha**: Formato padrão IATA
- **Numeração sequencial**: Cada linha numerada
- **Timezone support**: Offsets automáticos por aeroporto
- **Aircraft mapping**: Conversão ICAO/IATA automática

## 🔍 Validação Automática

O conversor SIRIUM inclui validação automática:

- ✅ **Comprimento das linhas**: Verifica 200 caracteres
- ✅ **Estrutura SSIM**: Header, Carrier, Flights, Footer
- ✅ **Quebras de linha**: Formatação correta
- ✅ **Dados obrigatórios**: Origem, destino, voos

## 🏢 Companhias Suportadas

Qualquer companhia aérea presente no arquivo, incluindo:
- **AI** (Air India)
- **BA** (British Airways)
- **EK** (Emirates)
- **LH** (Lufthansa)
- **QF** (Qantas)
- E muitas outras...

## 📁 Arquivos do Projeto

```
sirium_to_ssim_converter.py    # Módulo principal
app_sirium.py                  # Interface Streamlit
compare_ssim_formats.py        # Ferramenta de comparação
test_sfo_converter.py          # Testes básicos
README_SIRIUM.md               # Esta documentação
```

## 🔄 Processo de Conversão

1. **Leitura**: Carrega Excel (header=4)
2. **Filtragem**: Seleciona companhia específica
3. **Mapeamento**: Converte campos para SSIM
4. **Validação**: Verifica estrutura dos dados
5. **Geração**: Cria arquivo SSIM padrão
6. **Verificação**: Valida formato final

## 🛠️ Arquivos de Apoio

O conversor utiliza:
- `airport.csv`: Mapeamento de aeroportos e timezones
- `ACT TYPE.xlsx`: Conversão de códigos de aeronave

## ⚡ Diferenças dos Outros Conversores

| Característica | TS.09 | SFO Original | SIRIUM |
|----------------|-------|--------------|---------|
| Quebras de linha | ✅ | ❌ | ✅ |
| 200 caracteres | ✅ | ❌ | ✅ |
| Múltiplas cias | ❌ | ✅ | ✅ |
| Validação | Básica | Básica | Completa |
| Base validada | ✅ | ❌ | ✅ |

## 🧪 Teste e Validação

```bash
# Testar conversor
python sirium_to_ssim_converter.py

# Comparar formatos
python compare_ssim_formats.py

# Interface web com validação
streamlit run app_sirium.py
```

## 📞 Suporte Técnico

Desenvolvido pela **Capacity Dnata Brasil** para operações aéreas profissionais.

O SIRIUM representa a evolução dos conversores SSIM, combinando:
- ✅ **Confiabilidade** do old_project
- ✅ **Flexibilidade** do formato SFO  
- ✅ **Validação** automática integrada

---

*Versão SIRIUM 1.0 - Dezembro 2024*

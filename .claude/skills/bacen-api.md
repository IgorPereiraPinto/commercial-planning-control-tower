---
name: bacen-api
description: >
  Especialista na API oficial do Banco Central do Brasil (BACEN/SGS/PTAX). Cobre cotação
  PTAX de moedas (USD, EUR, GBP, JPY, CHF, CNY e mais), série histórica de câmbio, taxa
  Selic, CDI, IPCA, IGP-M, INPC e outros índices econômicos via API SGS. Inclui autenticação,
  endpoints principais, padrões de consumo em Python e integração com Excel e Power BI.
  Use sempre que o usuário mencionar API do Banco Central, cotação de câmbio, PTAX, Selic,
  CDI, IPCA, IGP-M, índice econômico brasileiro, série histórica de indicador, ou qualquer
  dado macroeconômico oficial brasileiro.
  Trigger para: "busca cotação BACEN", "pega dólar da API do Banco Central", "taxa Selic",
  "IPCA do mês", "histórico de câmbio", "CDI acumulado", "IGP-M", "API SGS", "PTAX hoje".
---

# BACEN API — Banco Central do Brasil

## Identidade

Especialista em consumo da API pública do Banco Central do Brasil (BCB). Cobre PTAX
(câmbio), SGS (séries temporais de indicadores econômicos) e integração com Python,
Excel e Power BI para enriquecimento de análises financeiras.

---

## 1. PTAX — Cotação de Moedas

```python
import requests
import pandas as pd
from datetime import datetime, timedelta

BCB_BASE = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata"

# Códigos de moedas disponíveis na PTAX
MOEDAS = {
    'USD': 'Dólar americano',
    'EUR': 'Euro',
    'GBP': 'Libra esterlina',
    'JPY': 'Iene japonês',
    'CHF': 'Franco suíço',
    'CNY': 'Yuan chinês (Renminbi)',
    'ARS': 'Peso argentino',
    'CAD': 'Dólar canadense',
    'AUD': 'Dólar australiano',
    'MXN': 'Peso mexicano',
}

def cotacao_moeda(moeda: str = 'USD',
                  data_ini: str = None,
                  data_fim: str = None) -> pd.DataFrame:
    """
    Cotação PTAX por período.
    Datas no formato 'MM-DD-YYYY' (padrão BACEN).
    """
    if not data_ini:
        data_ini = (datetime.today() - timedelta(days=30)).strftime('%m-%d-%Y')
    if not data_fim:
        data_fim = datetime.today().strftime('%m-%d-%Y')

    url = (
        f"{BCB_BASE}/CotacaoMoedaPeriodo(moeda=@m,dataInicial=@i,dataFinalCotacao=@f)"
        f"?@m='{moeda}'&@i='{data_ini}'&@f='{data_fim}'"
        f"&$top=1000&$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    dados = r.json().get('value', [])

    df = pd.DataFrame(dados)
    if df.empty:
        return df
    df['dataHoraCotacao'] = pd.to_datetime(df['dataHoraCotacao'])
    df['data'] = df['dataHoraCotacao'].dt.date
    df['moeda'] = moeda
    df['medio'] = (df['cotacaoCompra'] + df['cotacaoVenda']) / 2
    return df[['data','moeda','cotacaoCompra','cotacaoVenda','medio']].rename(
        columns={'cotacaoCompra':'compra','cotacaoVenda':'venda'}
    ).sort_values('data')


def cotacao_atual(moeda: str = 'USD') -> dict:
    """Última cotação disponível (PTAX do dia ou dia útil anterior)."""
    data = datetime.today().strftime('%m-%d-%Y')
    url = (
        f"{BCB_BASE}/CotacaoMoedaDia(moeda=@m,dataCotacao=@d)"
        f"?@m='{moeda}'&@d='{data}'&$format=json&$select=cotacaoCompra,cotacaoVenda"
    )
    r = requests.get(url, timeout=30)
    dados = r.json().get('value', [{}])
    if not dados or not dados[0]:
        return {}
    c, v = dados[0].get('cotacaoCompra', 0), dados[0].get('cotacaoVenda', 0)
    return {'moeda': moeda, 'compra': c, 'venda': v, 'medio': (c+v)/2}
```

---

## 2. SGS — Séries Temporais de Indicadores

```python
SGS_BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"

# Códigos das principais séries do SGS
SGS_SERIES = {
    11:    'Taxa Selic (% a.a.)',
    12:    'CDI (% a.a.)',
    433:   'IPCA (% mês)',
    13522: 'IPCA Acumulado 12M (%)',
    189:   'IGP-M (% mês)',
    7810:  'IGP-M Acumulado 12M (%)',
    682:   'INPC (% mês)',
    4390:  'Taxa Selic (% a.m.)',
    1:     'Taxa de Câmbio USD/BRL',
    21619: 'IPCA (% acumulado ano)',
    4392:  'CDI Over (% a.m.)',
}

def serie_sgs(codigo: int,
              data_ini: str = '01/01/2020',
              data_fim: str = None) -> pd.DataFrame:
    """
    Busca série temporal do SGS BACEN.
    data_ini/fim no formato 'DD/MM/YYYY'.
    """
    if not data_fim:
        data_fim = datetime.today().strftime('%d/%m/%Y')

    url = SGS_BASE.format(codigo=codigo)
    params = {
        'formato': 'json',
        'dataInicial': data_ini,
        'dataFinal': data_fim,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()

    df = pd.DataFrame(r.json())
    df['data']  = pd.to_datetime(df['data'], format='%d/%m/%Y')
    df['valor'] = pd.to_numeric(df['valor'].str.replace(',', '.'), errors='coerce')
    df['serie'] = SGS_SERIES.get(codigo, f'Serie_{codigo}')
    df['codigo_sgs'] = codigo

    return df[['data','serie','valor','codigo_sgs']].sort_values('data')


def multiplas_series(codigos: list, data_ini: str = '01/01/2023') -> pd.DataFrame:
    """Busca e consolida múltiplas séries do SGS."""
    frames = []
    for cod in codigos:
        try:
            df = serie_sgs(cod, data_ini)
            frames.append(df)
            print(f"✅ Série {cod} ({SGS_SERIES.get(cod,'?')}): {len(df)} registros")
        except Exception as e:
            print(f"❌ Série {cod}: {e}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def ipca_acumulado_periodo(data_ini: str, data_fim: str) -> float:
    """Calcula IPCA acumulado entre duas datas (produto dos índices mensais)."""
    df = serie_sgs(433, data_ini, data_fim)  # IPCA mensal
    fator = ((df['valor'] / 100 + 1).prod() - 1) * 100
    print(f"IPCA acumulado {data_ini} a {data_fim}: {fator:.4f}%")
    return round(fator, 4)


def correcao_monetaria(valor: float,
                        data_ini: str,
                        data_fim: str,
                        indice: int = 433) -> dict:
    """Corrige valor monetário por índice (IPCA, IGP-M, etc.)."""
    df = serie_sgs(indice, data_ini, data_fim)
    variacao = (df['valor'] / 100 + 1).prod() - 1
    valor_corrigido = valor * (1 + variacao)
    return {
        'valor_original': valor,
        'data_base': data_ini,
        'data_fim': data_fim,
        'indice': SGS_SERIES.get(indice, str(indice)),
        'variacao_%': round(variacao * 100, 4),
        'valor_corrigido': round(valor_corrigido, 2),
    }
```

---

## 3. Integração com Excel e Power BI

```python
# Atualização automática de planilha de câmbio
def atualizar_excel_cambio(caminho_excel: str,
                            moedas: list = ['USD', 'EUR'],
                            aba: str = 'Câmbio') -> None:
    """Atualiza aba de câmbio no Excel com cotações recentes."""
    import openpyxl
    frames = [cotacao_moeda(m) for m in moedas]
    df = pd.concat(frames)

    wb = openpyxl.load_workbook(caminho_excel)
    if aba not in wb.sheetnames:
        wb.create_sheet(aba)
    ws = wb[aba]
    ws.delete_rows(1, ws.max_row)

    from openpyxl.utils.dataframe import dataframe_to_rows
    for row in dataframe_to_rows(df, index=False, header=True):
        ws.append(row)
    wb.save(caminho_excel)
    print(f"✅ {aba} atualizada em {caminho_excel}")
```

---

## Referência de Endpoints

| Dado | URL | Parâmetros |
|---|---|---|
| PTAX período | `/CotacaoMoedaPeriodo(...)` | moeda, dataInicial, dataFinalCotacao |
| PTAX dia | `/CotacaoMoedaDia(...)` | moeda, dataCotacao |
| Lista moedas | `/Moedas` | — |
| SGS série | `api.bcb.gov.br/dados/serie/bcdata.sgs.{cod}/dados` | formato, dataInicial, dataFinal |

## Regras de Qualidade

- PTAX usa formato de data `MM-DD-YYYY` (não DD/MM/YYYY)
- SGS usa formato `DD/MM/YYYY` — não confundir os dois padrões
- PTAX é atualizada aos dias úteis — fins de semana retornam array vazio
- Sempre salvar a cotação com data de referência declarada no dataset
- Para análises históricas longas, usar Selic com código 11 (a.a.) ou 4390 (a.m.)
- CDI em `%a.a.` — converter para mensal: `(1 + cdi_aa/100)^(1/12) - 1`

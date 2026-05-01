---
name: financial-analytics
description: >
  Especialista em análise financeira, elaboração de DRE, controle de fluxo de caixa,
  conciliação bancária, monitoramento de investimentos, orçamento e variações financeiras.
  Cobre cotação de moedas via API do Banco Central, indicadores EBITDA, margem, ROI, payback
  e integração com SQL Server, Excel e Power BI. Use sempre que o usuário mencionar DRE,
  fluxo de caixa, orçamento, conciliação, câmbio, EBITDA, resultado financeiro, provisão,
  receita vs despesa, contas a pagar, contas a receber, ou qualquer análise financeira
  gerencial ou operacional.
  Trigger para: "elabora DRE", "monta o fluxo de caixa", "varia do orçamento", "busca câmbio",
  "calcula EBITDA", "concilia lançamentos", "análise do resultado financeiro", "contas a receber".
---

# Financial Analytics — Análise Financeira Gerencial

## Identidade

Analista Financeiro Sênior com foco em análise gerencial, DRE, fluxo de caixa, orçamento
e indicadores de resultado. Traduz lançamentos brutos em visão financeira clara para a
tomada de decisão, sem perder de vista o negócio por trás dos números.

---

## Quando Usar

Use esta skill para qualquer demanda financeira gerencial: elaborar DRE, analisar variações
de orçamento, estruturar fluxo de caixa, calcular indicadores (EBITDA, margem, ROI),
extrair cotações de moedas e conciliar lançamentos. Para análise de crédito e carteira,
use `credit-analytics`. Para procurement e spend, use `procurement-compras`.

---

## Como Atuar

1. Entender o objetivo financeiro: decisão de gestão, reporte, auditoria ou controle
2. Identificar as fontes de dados disponíveis (lançamentos, razão, extrato, ERP)
3. Estruturar a visão financeira em camadas: resultado → margem → variação → causa
4. Calcular indicadores com fórmulas explícitas e premissas declaradas
5. Traduzir número em implicação gerencial ou operacional
6. Alertar sobre riscos: sazonalidade, provisões, câmbio, inadimplência

---

## Entradas Esperadas

Lançamentos contábeis ou gerenciais, plano de contas, período de análise, orçamento,
categoria de receita/despesa, moeda, taxa de câmbio, metas de resultado.

---

## Formato de Saída Padrão

```
1. CONTEXTO FINANCEIRO (período, escopo, objetivo)
2. DRE OU FLUXO DE CAIXA (estruturado por linha)
3. INDICADORES PRINCIPAIS (EBITDA, margens, cobertura)
4. VARIAÇÕES (real vs orçado, real vs anterior, em R$ e %)
5. ANÁLISE DE CAUSA (o que explica os desvios)
6. RISCOS E PONTOS DE ATENÇÃO
7. RECOMENDAÇÕES E PRÓXIMOS PASSOS
```

---

## 1. Estrutura de DRE Gerencial

```python
import pandas as pd
import numpy as np
from datetime import datetime

# Estrutura padrão de DRE gerencial
ESTRUTURA_DRE = {
    'Receita Bruta':           {'tipo': 'receita', 'sinal': 1,  'nivel': 1},
    '(-) Deduções':            {'tipo': 'deducao',  'sinal': -1, 'nivel': 2},
    '= Receita Líquida':       {'tipo': 'subtotal', 'sinal': 1,  'nivel': 1},
    '(-) CPV/CMV':             {'tipo': 'custo',    'sinal': -1, 'nivel': 2},
    '= Lucro Bruto':           {'tipo': 'subtotal', 'sinal': 1,  'nivel': 1},
    '(-) Despesas Operacionais':{'tipo': 'despesa', 'sinal': -1, 'nivel': 2},
    '  Despesas Comerciais':   {'tipo': 'despesa',  'sinal': -1, 'nivel': 3},
    '  Despesas Administrativas':{'tipo': 'despesa','sinal': -1, 'nivel': 3},
    '  Despesas com Pessoal':  {'tipo': 'despesa',  'sinal': -1, 'nivel': 3},
    '= EBITDA':                {'tipo': 'subtotal', 'sinal': 1,  'nivel': 1},
    '(-) Depreciação/Amortização':{'tipo': 'nao_caixa','sinal':-1,'nivel': 2},
    '= EBIT (Lucro Operacional)':{'tipo': 'subtotal','sinal': 1, 'nivel': 1},
    '(+/-) Resultado Financeiro':{'tipo': 'financeiro','sinal': 1,'nivel': 2},
    '= EBT (Lucro antes IR)':  {'tipo': 'subtotal', 'sinal': 1,  'nivel': 1},
    '(-) IR e CSLL':           {'tipo': 'imposto',  'sinal': -1, 'nivel': 2},
    '= Lucro Líquido':         {'tipo': 'resultado','sinal': 1,  'nivel': 1},
}


def montar_dre(df_lancamentos: pd.DataFrame,
               valor_col: str = 'valor',
               categoria_col: str = 'categoria',
               periodo_col: str = 'competencia',
               periodo: str = None) -> pd.DataFrame:
    """
    Monta DRE gerencial a partir de lançamentos categorizados.

    Args:
        df_lancamentos: DataFrame com lançamentos financeiros
        valor_col: coluna com valor monetário (positivo = receita, negativo = despesa)
        categoria_col: coluna com categoria DRE
        periodo_col: coluna com competência (YYYY-MM)
        periodo: filtro de período específico (None = todos)

    Returns:
        DataFrame com DRE formatado por linha
    """
    df = df_lancamentos.copy()
    if periodo:
        df = df[df[periodo_col] == periodo]

    # Agrega por categoria
    resumo = df.groupby(categoria_col)[valor_col].sum().reset_index()
    resumo.columns = ['linha_dre', 'valor_real']

    # Calcula indicadores derivados
    rec_liq = resumo.loc[resumo['linha_dre'] == '= Receita Líquida', 'valor_real'].values
    rec_liq_val = rec_liq[0] if len(rec_liq) > 0 else 1

    resumo['margem_pct'] = (resumo['valor_real'] / abs(rec_liq_val) * 100).round(2)
    resumo['nivel'] = resumo['linha_dre'].map(
        lambda x: ESTRUTURA_DRE.get(x, {}).get('nivel', 2))

    print(f"\n{'='*60}")
    print(f"DRE GERENCIAL — {periodo or 'Todos os períodos'}")
    print(f"{'='*60}")
    for _, row in resumo.iterrows():
        indent = '  ' * (row['nivel'] - 1)
        print(f"{indent}{row['linha_dre']:<35} R$ {row['valor_real']:>14,.2f}   {row['margem_pct']:>6.1f}%")

    return resumo


def calcular_indicadores_financeiros(dre: pd.DataFrame) -> dict:
    """Calcula KPIs financeiros a partir do DRE montado."""

    def get_val(linha):
        row = dre[dre['linha_dre'] == linha]
        return float(row['valor_real'].values[0]) if len(row) > 0 else 0.0

    rec_liq   = get_val('= Receita Líquida')
    lb        = get_val('= Lucro Bruto')
    ebitda    = get_val('= EBITDA')
    ebit      = get_val('= EBIT (Lucro Operacional)')
    ll        = get_val('= Lucro Líquido')

    return {
        'receita_liquida':   rec_liq,
        'lucro_bruto':       lb,
        'ebitda':            ebitda,
        'lucro_liquido':     ll,
        'margem_bruta_%':    round(lb / rec_liq * 100, 2) if rec_liq else 0,
        'margem_ebitda_%':   round(ebitda / rec_liq * 100, 2) if rec_liq else 0,
        'margem_ebit_%':     round(ebit / rec_liq * 100, 2) if rec_liq else 0,
        'margem_liquida_%':  round(ll / rec_liq * 100, 2) if rec_liq else 0,
    }
```

---

## 2. API Banco Central — Cotação de Moedas

```python
import requests
import pandas as pd
from datetime import datetime, timedelta
import os

BASE_URL = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata"

def buscar_cotacao_bcb(moeda: str = 'USD',
                        data_inicio: str = None,
                        data_fim: str = None) -> pd.DataFrame:
    """
    Busca cotação PTAX do Banco Central do Brasil.

    Args:
        moeda: código da moeda (USD, EUR, GBP, JPY, etc.)
        data_inicio: 'MM-DD-YYYY' (formato BCEN) ou None = 30 dias atrás
        data_fim:    'MM-DD-YYYY' ou None = hoje

    Returns:
        DataFrame com cotações de compra e venda + data
    """
    if not data_inicio:
        dt_ini = (datetime.today() - timedelta(days=30))
        data_inicio = dt_ini.strftime('%m-%d-%Y')
    if not data_fim:
        data_fim = datetime.today().strftime('%m-%d-%Y')

    url = (
        f"{BASE_URL}/CotacaoMoedaPeriodo(moeda=@moeda,"
        f"dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
        f"?@moeda='{moeda}'&@dataInicial='{data_inicio}'"
        f"&@dataFinalCotacao='{data_fim}'"
        f"&$top=100&$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao"
    )

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    dados = resp.json().get('value', [])

    if not dados:
        print(f"[BCEN] Sem cotações para {moeda} no período.")
        return pd.DataFrame()

    df = pd.DataFrame(dados)
    df['dataHoraCotacao'] = pd.to_datetime(df['dataHoraCotacao'])
    df['data'] = df['dataHoraCotacao'].dt.date
    df['moeda'] = moeda
    df = df.rename(columns={'cotacaoCompra': 'compra', 'cotacaoVenda': 'venda'})
    df['medio'] = (df['compra'] + df['venda']) / 2

    print(f"[BCEN] {moeda}: {len(df)} cotações de {data_inicio} a {data_fim}")
    print(f"  Último: R$ {df['medio'].iloc[-1]:.4f} (compra {df['compra'].iloc[-1]:.4f} / venda {df['venda'].iloc[-1]:.4f})")

    return df[['data', 'moeda', 'compra', 'venda', 'medio']].sort_values('data')


def buscar_cotacao_atual(moeda: str = 'USD') -> dict:
    """Retorna apenas a cotação mais recente disponível (PTAX fechamento)."""
    url = (
        f"{BASE_URL}/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)"
        f"?@moeda='{moeda}'&@dataCotacao='{datetime.today().strftime('%m-%d-%Y')}'"
        f"&$format=json&$select=cotacaoCompra,cotacaoVenda"
    )
    resp = requests.get(url, timeout=30)
    dados = resp.json().get('value', [{}])
    if not dados or not dados[0]:
        return {'moeda': moeda, 'compra': None, 'venda': None, 'medio': None}

    c, v = dados[0].get('cotacaoCompra', 0), dados[0].get('cotacaoVenda', 0)
    return {'moeda': moeda, 'compra': c, 'venda': v, 'medio': (c+v)/2, 'data': datetime.today().date()}


def converter_moeda(valor: float, moeda_origem: str = 'USD',
                     tipo: str = 'venda') -> float:
    """Converte valor de moeda estrangeira para BRL usando PTAX atual."""
    cotacao = buscar_cotacao_atual(moeda_origem)
    taxa = cotacao.get(tipo, cotacao.get('medio', 1))
    resultado = valor * taxa if taxa else valor
    print(f"R$ {resultado:,.2f} (1 {moeda_origem} = R$ {taxa:.4f} {tipo})")
    return resultado


def buscar_multiplas_moedas(moedas: list = ['USD', 'EUR', 'GBP']) -> pd.DataFrame:
    """Retorna cotação atual de várias moedas em um DataFrame."""
    registros = []
    for moeda in moedas:
        try:
            cotacao = buscar_cotacao_atual(moeda)
            registros.append(cotacao)
        except Exception as e:
            print(f"[ERRO] {moeda}: {e}")
    return pd.DataFrame(registros)
```

---

## 3. Fluxo de Caixa — Análise e Projeção

```python
def montar_fluxo_caixa(df: pd.DataFrame,
                         data_col: str,
                         valor_col: str,
                         tipo_col: str,
                         freq: str = 'M') -> pd.DataFrame:
    """
    Monta fluxo de caixa por período com saldo acumulado.

    tipo_col deve conter: 'RECEBIMENTO', 'PAGAMENTO', 'INVESTIMENTO', 'FINANCIAMENTO'
    """
    df = df.copy()
    df[data_col] = pd.to_datetime(df[data_col])

    # Classifica fluxo por grupo
    mapa_sinal = {'RECEBIMENTO': 1, 'PAGAMENTO': -1,
                  'INVESTIMENTO': -1, 'FINANCIAMENTO': 1}
    df['sinal'] = df[tipo_col].map(mapa_sinal).fillna(1)
    df['valor_liq'] = df[valor_col] * df['sinal']

    # Agrega por período e tipo
    pivot = (df.groupby([pd.Grouper(key=data_col, freq=freq), tipo_col])
               ['valor_liq'].sum()
               .unstack(fill_value=0)
               .reset_index())

    # Calcula totais
    colunas_receb = [c for c in pivot.columns if c in ['RECEBIMENTO', 'FINANCIAMENTO']]
    colunas_pag   = [c for c in pivot.columns if c in ['PAGAMENTO', 'INVESTIMENTO']]

    pivot['total_entradas']  = pivot[colunas_receb].sum(axis=1)
    pivot['total_saidas']    = pivot[colunas_pag].sum(axis=1)
    pivot['fluxo_liquido']   = pivot['total_entradas'] + pivot['total_saidas']
    pivot['saldo_acumulado'] = pivot['fluxo_liquido'].cumsum()

    return pivot


def analise_contas_receber(df: pd.DataFrame,
                            vencimento_col: str,
                            valor_col: str,
                            cliente_col: str,
                            status_col: str = None) -> dict:
    """Análise de carteira de contas a receber com aging."""
    hoje = pd.Timestamp.today()
    df = df.copy()
    df[vencimento_col] = pd.to_datetime(df[vencimento_col])
    df['dias_vencimento'] = (df[vencimento_col] - hoje).dt.days

    # Aging em faixas
    def faixa_aging(dias):
        if dias > 0:      return 'A Vencer'
        elif dias >= -30:  return '0-30 dias'
        elif dias >= -60:  return '31-60 dias'
        elif dias >= -90:  return '61-90 dias'
        else:              return '> 90 dias'

    df['faixa'] = df['dias_vencimento'].apply(faixa_aging)
    aging = df.groupby('faixa')[valor_col].agg(['sum', 'count']).reset_index()
    aging['pct'] = (aging['sum'] / aging['sum'].sum() * 100).round(1)

    total_vencido = df[df['dias_vencimento'] < 0][valor_col].sum()
    total_carteira = df[valor_col].sum()

    print(f"\nCarteira Total: R$ {total_carteira:,.2f}")
    print(f"Vencido:        R$ {total_vencido:,.2f} ({total_vencido/total_carteira*100:.1f}%)")
    print("\nAging:")
    print(aging.to_string(index=False))

    return {
        'total_carteira': total_carteira,
        'total_vencido': total_vencido,
        'inadimplencia_%': round(total_vencido/total_carteira*100, 2),
        'aging': aging
    }
```

---

## 4. KPIs Financeiros em SQL Server

```sql
-- DRE gerencial por mês (SQL Server)
WITH lancamentos AS (
    SELECT
        YEAR(data_competencia)  AS ano,
        MONTH(data_competencia) AS mes,
        FORMAT(data_competencia, 'yyyy-MM') AS ano_mes,
        linha_dre,
        grupo_dre,
        SUM(valor) AS valor
    FROM dbo.lancamentos_financeiros
    WHERE data_competencia BETWEEN '2024-01-01' AND '2024-12-31'
      AND status <> 'CANCELADO'
    GROUP BY YEAR(data_competencia), MONTH(data_competencia),
             FORMAT(data_competencia, 'yyyy-MM'), linha_dre, grupo_dre
),
subtotais AS (
    SELECT
        ano, mes, ano_mes,
        -- Receita Líquida
        SUM(CASE WHEN grupo_dre = 'RECEITA_BRUTA'   THEN valor ELSE 0 END)
      - SUM(CASE WHEN grupo_dre = 'DEDUCAO'          THEN valor ELSE 0 END) AS receita_liquida,
        -- Lucro Bruto
        SUM(CASE WHEN grupo_dre = 'RECEITA_BRUTA'   THEN valor ELSE 0 END)
      - SUM(CASE WHEN grupo_dre = 'DEDUCAO'          THEN valor ELSE 0 END)
      - SUM(CASE WHEN grupo_dre = 'CPV'              THEN valor ELSE 0 END) AS lucro_bruto,
        -- EBITDA
        SUM(CASE WHEN grupo_dre IN ('RECEITA_BRUTA')  THEN valor ELSE 0 END)
      - SUM(CASE WHEN grupo_dre IN ('DEDUCAO','CPV','DESPESA_OP') THEN valor ELSE 0 END) AS ebitda,
        -- Lucro Líquido
        SUM(CASE WHEN grupo_dre IN ('RECEITA_BRUTA','RESULT_FIN') THEN valor ELSE 0 END)
      - SUM(CASE WHEN grupo_dre IN ('DEDUCAO','CPV','DESPESA_OP','DEPREC','IMPOSTO') THEN valor ELSE 0 END) AS lucro_liquido
    FROM lancamentos
    GROUP BY ano, mes, ano_mes
)
SELECT
    ano_mes,
    receita_liquida,
    lucro_bruto,
    ebitda,
    lucro_liquido,
    ROUND(lucro_bruto  / NULLIF(receita_liquida,0) * 100, 2) AS margem_bruta_pct,
    ROUND(ebitda       / NULLIF(receita_liquida,0) * 100, 2) AS margem_ebitda_pct,
    ROUND(lucro_liquido/ NULLIF(receita_liquida,0) * 100, 2) AS margem_liquida_pct,
    -- Variação MoM
    ROUND((ebitda - LAG(ebitda) OVER (ORDER BY ano_mes))
          / NULLIF(ABS(LAG(ebitda) OVER (ORDER BY ano_mes)),0) * 100, 2) AS var_ebitda_mom_pct
FROM subtotais
ORDER BY ano_mes;
```

---

## 5. DAX — Medidas Financeiras no Power BI

```dax
// Receita Líquida (com filtro de grupo DRE)
Receita Liquida =
CALCULATE(
    SUM(fLancamentos[valor]),
    fLancamentos[grupo_dre] = "RECEITA_BRUTA"
) - CALCULATE(
    SUM(fLancamentos[valor]),
    fLancamentos[grupo_dre] = "DEDUCAO"
)

// EBITDA
EBITDA =
CALCULATE(SUM(fLancamentos[valor]),
    fLancamentos[grupo_dre] IN {"RECEITA_BRUTA"})
- CALCULATE(SUM(fLancamentos[valor]),
    fLancamentos[grupo_dre] IN {"DEDUCAO","CPV","DESPESA_OP"})

// Margem EBITDA %
Margem EBITDA % =
DIVIDE([EBITDA], [Receita Liquida], 0)

// Variação vs Orçado
Variacao Orcamento R$ =
[Resultado Real] - [Resultado Orcado]

Variacao Orcamento % =
DIVIDE([Resultado Real] - [Resultado Orcado],
       ABS([Resultado Orcado]), 0)

// Cotação USD (tabela de câmbio)
USD Medio Periodo =
CALCULATE(
    AVERAGE(dCambio[medio]),
    DATESBETWEEN(dCambio[data],
                 MIN(dCalendario[Data]),
                 MAX(dCalendario[Data]))
)

// Valor convertido para BRL
Receita BRL =
[Receita USD] * [USD Medio Periodo]
```

---

## Benchmarks de Indicadores Financeiros

| Indicador | Crítico | Atenção | OK | Excelente |
|---|---|---|---|---|
| Margem Bruta | < 20% | 20-35% | 35-50% | > 50% |
| Margem EBITDA | < 5% | 5-12% | 12-20% | > 20% |
| Margem Líquida | < 2% | 2-5% | 5-10% | > 10% |
| Índice de Liquidez | < 1.0 | 1.0-1.2 | 1.2-1.8 | > 1.8 |
| Desvio Orçamento | > 15% | 5-15% | < 5% | < 2% |

---

## Regras de Qualidade

- Sempre declarar a base de cálculo: competência ou caixa, GAAP ou gerencial
- Separar receita bruta de receita líquida explicitamente
- EBITDA = resultado operacional antes de depreciação, amortização, juros e impostos
- Câmbio: usar sempre PTAX BCB, declarar data de referência e tipo (compra, venda, médio)
- Não confundir Lucro Líquido com Fluxo de Caixa Livre
- Provisões e accruals devem estar separados dos pagamentos realizados
- Todo valor em moeda estrangeira precisa da taxa de conversão declarada

## Observações

Para análise de crédito, use `credit-analytics`. Para spend e procurement, use `procurement-compras`.
Para cotações BACEN em detalhe, use `bacen-api`. Para DRE em slides, use `corporate-presentations`.

## Rules complementares

Aplicar junto com esta skill:
- `03_sales-planning.md` — quando a análise financeira tiver componente comercial (receita, margem, mix)
- `27_statistics-business-kpis.md` — para cálculo e interpretação de KPIs financeiros (EBITDA, margens, ROI)

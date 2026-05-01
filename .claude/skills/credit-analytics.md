---
name: credit-analytics
description: >
  Especialista em análise de crédito e risco de carteira. Cobre scoring de crédito,
  PDD (provisão para devedores duvidosos), rating interno, análise de concentração,
  inadimplência, curva de safra (vintage), cobertura de provisão, análise de portfólio
  e decisão de crédito. Integra com SQL Server, Python e Power BI.
  Use sempre que o usuário mencionar crédito, carteira de crédito, inadimplência, PDD,
  provisão, rating, scoring, safra, vintage, cobertura, risco de crédito, aprovação de
  crédito, exposição, concentração de carteira, ou limite de crédito.
  Trigger para: "analisa carteira de crédito", "calcula PDD", "curva de safra", "rating do
  cliente", "análise de inadimplência", "concentração da carteira", "aprovação de crédito",
  "modelo de scoring".
---

# Credit Analytics — Análise de Crédito e Risco de Carteira

## Identidade

Analista de Crédito e Risco Sênior com foco em análise de portfólio, scoring, provisão
e decisão de crédito. Equilibra rigor técnico com visão de negócio, traduzindo risco em
impacto financeiro e recomendações acionáveis para o comitê de crédito ou gestão.

---

## Quando Usar

Use esta skill para análise de carteira de crédito, cálculo de PDD, curva de safra,
scoring e decisão de aprovação. Para análise financeira geral (DRE, fluxo de caixa),
use `financial-analytics`. Para análise de inadimplência em CX, use `customer-experience-analytics`.

---

## Formato de Saída Padrão

```
1. VISÃO DA CARTEIRA (saldo, composição, evolução)
2. INDICADORES DE RISCO (inadimplência, cobertura, concentração)
3. CURVA DE SAFRA (comportamento por coorte)
4. ANÁLISE DE PROVISÃO (PDD calculado vs constituído)
5. SEGMENTAÇÃO DE RISCO (rating, faixas de score)
6. HIPÓTESES E CAUSAS (o que explica os movimentos)
7. RECOMENDAÇÃO (ação de crédito priorizada)
```

---

## 1. KPIs de Crédito

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def kpis_carteira_credito(df: pd.DataFrame,
                           saldo_col: str = 'saldo_devedor',
                           status_col: str = 'status',
                           vencimento_col: str = 'data_vencimento',
                           cliente_col: str = 'id_cliente',
                           provisao_col: str = 'provisao_constituida') -> dict:
    """
    KPIs completos de carteira de crédito.

    status esperado: 'ADIMPLENTE', 'ATRASO_1_30', 'ATRASO_31_60',
                     'ATRASO_61_90', 'ATRASO_91_180', 'ATRASO_180+'
    """
    df = df.copy()
    df[vencimento_col] = pd.to_datetime(df[vencimento_col])
    hoje = pd.Timestamp.today()

    # Faixas de atraso
    df['dias_atraso'] = (hoje - df[vencimento_col]).dt.days.clip(lower=0)
    df.loc[df[status_col] == 'ADIMPLENTE', 'dias_atraso'] = 0

    saldo_total     = df[saldo_col].sum()
    em_atraso       = df[df['dias_atraso'] > 0][saldo_col].sum()
    atraso_90plus   = df[df['dias_atraso'] > 90][saldo_col].sum()
    n_clientes      = df[cliente_col].nunique()
    provisao_total  = df[provisao_col].sum() if provisao_col in df.columns else 0

    # Concentração: % do Top 10 clientes
    top10 = (df.groupby(cliente_col)[saldo_col]
               .sum()
               .sort_values(ascending=False)
               .head(10).sum())

    return {
        'saldo_total':           round(saldo_total, 2),
        'n_clientes':            n_clientes,
        'ticket_medio':          round(saldo_total / n_clientes, 2) if n_clientes else 0,
        'saldo_em_atraso':       round(em_atraso, 2),
        'inadimplencia_%':       round(em_atraso / saldo_total * 100, 2) if saldo_total else 0,
        'saldo_90plus':          round(atraso_90plus, 2),
        'inadimplencia_90plus_%':round(atraso_90plus / saldo_total * 100, 2) if saldo_total else 0,
        'provisao_constituida':  round(provisao_total, 2),
        'cobertura_pct':         round(provisao_total / em_atraso * 100, 2) if em_atraso else None,
        'concentracao_top10_%':  round(top10 / saldo_total * 100, 2) if saldo_total else 0,
    }


def aging_carteira(df: pd.DataFrame,
                    saldo_col: str,
                    dias_atraso_col: str) -> pd.DataFrame:
    """Aging da carteira em faixas de atraso com % e saldo."""

    def faixa(dias):
        if dias == 0:    return 'Adimplente'
        elif dias <= 30:  return '1-30 dias'
        elif dias <= 60:  return '31-60 dias'
        elif dias <= 90:  return '61-90 dias'
        elif dias <= 180: return '91-180 dias'
        else:             return '180+ dias'

    df = df.copy()
    df['faixa_atraso'] = df[dias_atraso_col].apply(faixa)

    aging = (df.groupby('faixa_atraso')
               .agg(saldo=( saldo_col, 'sum'),
                    qtd_contratos=(saldo_col, 'count'))
               .reset_index())
    aging['pct_saldo'] = (aging['saldo'] / aging['saldo'].sum() * 100).round(2)
    aging['pct_contratos'] = (aging['qtd_contratos'] / aging['qtd_contratos'].sum() * 100).round(2)

    # Ordem lógica
    ordem = ['Adimplente','1-30 dias','31-60 dias','61-90 dias','91-180 dias','180+ dias']
    aging['ordem'] = aging['faixa_atraso'].map({f:i for i,f in enumerate(ordem)})
    return aging.sort_values('ordem').drop('ordem', axis=1)
```

---

## 2. Curva de Safra (Vintage Analysis)

```python
def curva_safra(df: pd.DataFrame,
                safra_col: str = 'mes_originacao',
                periodo_col: str = 'mes_referencia',
                saldo_col: str = 'saldo_devedor',
                inadimplente_col: str = 'flag_inadimplente',
                saldo_original_col: str = 'saldo_original') -> pd.DataFrame:
    """
    Análise de safra (vintage): taxa de inadimplência acumulada por coorte.

    Cada safra é um conjunto de contratos originados no mesmo mês.
    A curva mostra como a inadimplência evolui ao longo dos meses de vida.
    """
    df = df.copy()
    df[safra_col]   = pd.to_datetime(df[safra_col]).dt.to_period('M')
    df[periodo_col] = pd.to_datetime(df[periodo_col]).dt.to_period('M')
    df['mes_vida']  = (df[periodo_col] - df[safra_col]).apply(lambda x: x.n)

    # Saldo em risco por safra + mês de vida
    vintage = (df.groupby([safra_col, 'mes_vida'])
                 .agg(
                     saldo_inadimplente = (saldo_col, lambda x: x[df.loc[x.index, inadimplente_col] == 1].sum()),
                     saldo_total        = (saldo_col, 'sum'),
                     saldo_originado    = (saldo_original_col, 'sum')
                 )
                 .reset_index())

    vintage['taxa_inadimplencia_%'] = (
        vintage['saldo_inadimplente'] / vintage['saldo_originado'] * 100
    ).round(3)

    # Pivot para visualização
    pivot = vintage.pivot(index=safra_col, columns='mes_vida',
                          values='taxa_inadimplencia_%')
    pivot.columns = [f'M+{c}' for c in pivot.columns]

    print("Curva de Safra — Taxa de Inadimplência Acumulada (%)")
    print(pivot.round(2).to_string())

    return pivot
```

---

## 3. Cálculo de PDD (Provisão para Devedores Duvidosos)

```python
# Tabela de faixas de PDD — BACEN Resolução 2682/99 (referência)
# Adaptar conforme política interna da empresa
FAIXAS_PDD = [
    {'faixa': 'AA',  'dias_min': 0,   'dias_max': 0,   'pct_provisao': 0.0},
    {'faixa': 'A',   'dias_min': 1,   'dias_max': 14,  'pct_provisao': 0.5},
    {'faixa': 'B',   'dias_min': 15,  'dias_max': 30,  'pct_provisao': 1.0},
    {'faixa': 'C',   'dias_min': 31,  'dias_max': 60,  'pct_provisao': 3.0},
    {'faixa': 'D',   'dias_min': 61,  'dias_max': 90,  'pct_provisao': 10.0},
    {'faixa': 'E',   'dias_min': 91,  'dias_max': 120, 'pct_provisao': 30.0},
    {'faixa': 'F',   'dias_min': 121, 'dias_max': 150, 'pct_provisao': 50.0},
    {'faixa': 'G',   'dias_min': 151, 'dias_max': 180, 'pct_provisao': 70.0},
    {'faixa': 'H',   'dias_min': 181, 'dias_max': 9999,'pct_provisao': 100.0},
]

def classificar_rating_pdd(dias_atraso: int) -> tuple:
    """Retorna (rating, pct_provisao) conforme dias de atraso."""
    for faixa in FAIXAS_PDD:
        if faixa['dias_min'] <= dias_atraso <= faixa['dias_max']:
            return faixa['faixa'], faixa['pct_provisao']
    return 'H', 100.0


def calcular_pdd(df: pd.DataFrame,
                  saldo_col: str = 'saldo_devedor',
                  dias_col: str = 'dias_atraso',
                  politica: str = 'bacen') -> pd.DataFrame:
    """
    Calcula PDD por contrato com rating e provisão requerida.

    politica: 'bacen' = Resolução 2682, 'interna' = usar tabela customizada
    """
    df = df.copy()
    df[['rating', 'pct_pdd']] = df[dias_col].apply(
        lambda d: pd.Series(classificar_rating_pdd(d))
    )
    df['provisao_requerida'] = df[saldo_col] * df['pct_pdd'] / 100

    # Resumo por rating
    resumo = (df.groupby('rating')
                .agg(
                    qtd_contratos    = (saldo_col, 'count'),
                    saldo_total      = (saldo_col, 'sum'),
                    provisao_total   = ('provisao_requerida', 'sum'),
                    pct_pdd_medio    = ('pct_pdd', 'mean')
                )
                .reset_index())
    resumo['pct_carteira'] = (resumo['saldo_total'] / resumo['saldo_total'].sum() * 100).round(2)
    resumo['cobertura_pct'] = (resumo['provisao_total'] / resumo['saldo_total'] * 100).round(2)

    total_provisao   = df['provisao_requerida'].sum()
    total_saldo      = df[saldo_col].sum()
    print(f"\nPDD Total Requerido: R$ {total_provisao:,.2f} ({total_provisao/total_saldo*100:.2f}% da carteira)")
    print(resumo.to_string(index=False))

    return df, resumo
```

---

## 4. SQL — Análise de Carteira

```sql
-- Inadimplência por safra e segmento (SQL Server)
WITH carteira AS (
    SELECT
        c.id_contrato,
        c.id_cliente,
        c.segmento,
        c.produto,
        FORMAT(c.data_originacao, 'yyyy-MM') AS safra,
        FORMAT(r.data_referencia, 'yyyy-MM')  AS mes_referencia,
        DATEDIFF(month, c.data_originacao, r.data_referencia) AS mes_vida,
        r.saldo_devedor,
        r.saldo_original,
        r.dias_atraso,
        CASE
            WHEN r.dias_atraso = 0      THEN 'AA'
            WHEN r.dias_atraso <= 14    THEN 'A'
            WHEN r.dias_atraso <= 30    THEN 'B'
            WHEN r.dias_atraso <= 60    THEN 'C'
            WHEN r.dias_atraso <= 90    THEN 'D'
            WHEN r.dias_atraso <= 120   THEN 'E'
            WHEN r.dias_atraso <= 150   THEN 'F'
            WHEN r.dias_atraso <= 180   THEN 'G'
            ELSE 'H'
        END AS rating,
        CASE
            WHEN r.dias_atraso = 0      THEN 0.0
            WHEN r.dias_atraso <= 14    THEN 0.5
            WHEN r.dias_atraso <= 30    THEN 1.0
            WHEN r.dias_atraso <= 60    THEN 3.0
            WHEN r.dias_atraso <= 90    THEN 10.0
            WHEN r.dias_atraso <= 120   THEN 30.0
            WHEN r.dias_atraso <= 150   THEN 50.0
            WHEN r.dias_atraso <= 180   THEN 70.0
            ELSE 100.0
        END AS pct_pdd
    FROM dbo.contratos c
    INNER JOIN dbo.posicao_carteira r ON c.id_contrato = r.id_contrato
    WHERE r.data_referencia = EOMONTH(GETDATE(), -1)  -- último fechamento
      AND c.status NOT IN ('LIQUIDADO', 'CANCELADO')
)
SELECT
    segmento,
    produto,
    rating,
    COUNT(*)                                                AS qtd_contratos,
    SUM(saldo_devedor)                                      AS saldo_total,
    SUM(saldo_devedor * pct_pdd / 100)                      AS pdd_requerido,
    ROUND(SUM(saldo_devedor * pct_pdd / 100)
          / NULLIF(SUM(saldo_devedor), 0) * 100, 2)         AS cobertura_pct,
    AVG(dias_atraso)                                        AS dias_atraso_medio
FROM carteira
GROUP BY segmento, produto, rating
ORDER BY segmento, produto,
    CASE rating WHEN 'AA' THEN 1 WHEN 'A' THEN 2 WHEN 'B' THEN 3
                WHEN 'C'  THEN 4 WHEN 'D' THEN 5 WHEN 'E' THEN 6
                WHEN 'F'  THEN 7 WHEN 'G' THEN 8 WHEN 'H' THEN 9 END;
```

---

## Benchmarks de Risco de Crédito

| Indicador | Crítico | Atenção | OK | Saudável |
|---|---|---|---|---|
| Inadimplência 90+ | > 8% | 4-8% | 1-4% | < 1% |
| Cobertura de Provisão | < 80% | 80-100% | 100-120% | > 120% |
| Concentração Top 10 | > 40% | 25-40% | 10-25% | < 10% |
| PDD / Carteira | > 10% | 5-10% | 2-5% | < 2% |

## Regras de Qualidade

- Sempre declarar a política de classificação (BACEN 2682, IFRS 9 ou interna)
- PDD ≠ perdas realizadas — PDD é estimativa de perda esperada
- Inadimplência 15+ dias e 90+ dias têm significados distintos — usar sempre o corte correto
- Curva de safra exige dados longitudinais — não usar cross-section como proxy
- Concentração acima de 40% em um único cliente ou grupo é risco sistêmico
- Sempre reportar cobertura = provisão constituída / saldo inadimplente

## Observações

Skill irmã: `financial-analytics` para DRE e resultado financeiro.
Skill irmã: `statistics-business-kpis` para modelos de propensão e scoring com ML.

## Rules complementares

Aplicar junto com esta skill:
- `27_statistics-business-kpis.md` — para scoring, curva de safra e interpretação estatística de risco
- `17_machine-learning.md` — quando a análise envolver modelo de propensão ao default ou churn de crédito

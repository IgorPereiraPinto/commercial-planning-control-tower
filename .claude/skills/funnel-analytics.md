---
name: funnel-analytics
description: >
  Especialista em análise de funil de vendas, funil de conversão, funil de marketing e
  funil de atendimento. Cobre cálculo de taxa de conversão por etapa, drop-off, gargalos,
  velocidade no funil, análise de leads, pipeline comercial e funil multicanal. Integra
  com SQL Server, Python, Power BI e QuickSight.
  Use sempre que o usuário mencionar funil de vendas, pipeline, taxa de conversão, lead,
  oportunidade, drop-off, gargalo de funil, etapa comercial, MQL, SQL, SDR, ciclo de vendas,
  ou qualquer análise de jornada com etapas sequenciais.
  Trigger para: "analisa o funil", "drop off por etapa", "velocidade no funil", "onde está
  perdendo conversão", "taxa de conversão de lead", "pipeline comercial", "funil de marketing".
---

# Funnel Analytics — Análise de Funil de Conversão

## Identidade

Analista de Funil Sênior com foco em identificar gargalos, calcular conversão por etapa e
traduzir a performance do funil em ação comercial. Sempre analisa funil em valor e volume,
separando o que é problema de quantidade do que é problema de qualidade.

---

## Quando Usar

Use esta skill quando a análise central for o fluxo de evolução de oportunidades entre
etapas. Complementa `sales-planning` (que foca em resultado), `customer-experience-analytics`
(que foca em atendimento) e `statistics-business-kpis` (para testes de significância de
conversão).

---

## Formato de Saída Padrão

```
1. VISÃO DO FUNIL (volume e valor por etapa)
2. TAXAS DE CONVERSÃO (por etapa e global)
3. DROP-OFF CRÍTICO (onde perde mais)
4. VELOCIDADE (dias médios entre etapas)
5. ANÁLISE POR DIMENSÃO (canal, vendedor, produto)
6. HIPÓTESES DE GARGALO
7. RECOMENDAÇÃO PRÁTICA
```

---

## 1. Análise de Funil — Core

```python
import pandas as pd
import numpy as np

# Etapas padrão de funil comercial B2B
ETAPAS_FUNIL_PADRAO = [
    'Lead', 'MQL', 'SQL', 'Proposta', 'Negociação', 'Fechado Ganho'
]

ETAPAS_FUNIL_B2C = [
    'Visitante', 'Lead', 'Contato', 'Proposta', 'Fechado'
]

ETAPAS_FUNIL_MARKETING = [
    'Impressão', 'Clique', 'Sessão', 'Lead', 'MQL', 'Conversão'
]


def analisar_funil(df: pd.DataFrame,
                   etapa_col: str,
                   valor_col: str = None,
                   id_col: str = None,
                   etapas: list = None) -> pd.DataFrame:
    """
    Análise de funil com volume, valor, conversão e drop-off.

    Args:
        df: DataFrame com registro de cada oportunidade por etapa atual
        etapa_col: coluna com a etapa atual do lead/oportunidade
        valor_col: coluna com valor potencial (opcional)
        id_col: coluna com identificador único
        etapas: ordem das etapas (se None, usa a mais comum)
    """
    if etapas is None:
        etapas = df[etapa_col].value_counts().index.tolist()

    # Agrega por etapa
    agg = {'volume': (id_col or etapa_col, 'count')}
    if valor_col:
        agg['valor_total'] = (valor_col, 'sum')
        agg['ticket_medio'] = (valor_col, 'mean')

    funil = (df.groupby(etapa_col)
               .agg(**agg)
               .reindex(etapas)
               .reset_index())
    funil.columns = ['etapa'] + list(agg.keys())

    # Taxas de conversão
    funil['conv_anterior_%'] = (
        funil['volume'] / funil['volume'].shift(1) * 100
    ).round(1)
    funil['conv_total_%'] = (
        funil['volume'] / funil['volume'].iloc[0] * 100
    ).round(1)
    funil['drop_off_%'] = (100 - funil['conv_anterior_%']).round(1)
    funil['drop_off_volume'] = (funil['volume'].shift(1) - funil['volume']).fillna(0).astype(int)

    # Etapa com maior drop-off absoluto
    idx_gargalo = funil['drop_off_volume'].idxmax()
    print(f"\n{'='*55}")
    print(f"FUNIL DE CONVERSÃO")
    print(f"{'='*55}")
    for _, row in funil.iterrows():
        barra = '█' * int(row['conv_total_%'] / 5)
        print(f"{row['etapa']:<20} {row['volume']:>6,}  {row['conv_total_%']:>5.1f}%  {barra}")
    print(f"\n⚠️  Maior gargalo: {funil.loc[idx_gargalo, 'etapa']} "
          f"(-{funil.loc[idx_gargalo, 'drop_off_volume']:,} leads, "
          f"{funil.loc[idx_gargalo, 'drop_off_%']:.1f}% de drop-off)")

    return funil


def velocidade_funil(df: pd.DataFrame,
                      id_col: str,
                      etapa_col: str,
                      data_col: str,
                      etapas: list = None) -> pd.DataFrame:
    """
    Calcula dias médios entre cada transição de etapa (velocity analysis).

    df deve ter uma linha por mudança de etapa por oportunidade.
    """
    df = df.copy()
    df[data_col] = pd.to_datetime(df[data_col])
    df = df.sort_values([id_col, data_col])

    if etapas:
        df['etapa_ordem'] = df[etapa_col].map({e:i for i,e in enumerate(etapas)})
        df = df.sort_values([id_col, 'etapa_ordem'])

    df['data_proxima_etapa'] = df.groupby(id_col)[data_col].shift(-1)
    df['dias_na_etapa'] = (df['data_proxima_etapa'] - df[data_col]).dt.days

    velocidade = (df.groupby(etapa_col)['dias_na_etapa']
                    .agg(['mean', 'median', 'count'])
                    .round(1)
                    .reset_index())
    velocidade.columns = ['etapa', 'dias_medio', 'dias_mediana', 'n_transicoes']

    if etapas:
        velocidade['ordem'] = velocidade['etapa'].map({e:i for i,e in enumerate(etapas)})
        velocidade = velocidade.sort_values('ordem').drop('ordem', axis=1)

    # Ciclo de vendas total
    ciclo_total = velocidade['dias_medio'].sum()
    print(f"Ciclo médio total de vendas: {ciclo_total:.0f} dias")
    print(velocidade.to_string(index=False))

    return velocidade


def funil_por_dimensao(df: pd.DataFrame,
                        etapa_col: str,
                        dimensao_col: str,
                        etapa_final: str,
                        id_col: str = None) -> pd.DataFrame:
    """
    Compara taxa de conversão global por dimensão (canal, vendedor, produto).
    """
    agg_col = id_col or etapa_col

    funil_dim = (df.groupby([dimensao_col, etapa_col])
                   .agg(volume=(agg_col, 'count'))
                   .reset_index())

    # Volume total por dimensão
    total_por_dim = (df.groupby(dimensao_col)
                       .agg(total_entrada=(agg_col, 'count'))
                       .reset_index())

    # Fechados por dimensão
    fechados = (df[df[etapa_col] == etapa_final]
                  .groupby(dimensao_col)
                  .agg(total_fechado=(agg_col, 'count'))
                  .reset_index())

    resumo = total_por_dim.merge(fechados, on=dimensao_col, how='left').fillna(0)
    resumo['total_fechado'] = resumo['total_fechado'].astype(int)
    resumo['conv_total_%'] = (resumo['total_fechado'] / resumo['total_entrada'] * 100).round(1)
    return resumo.sort_values('conv_total_%', ascending=False)
```

---

## 2. SQL — Funil de Vendas

```sql
-- Funil de conversão com volume, valor e dias médios por etapa (SQL Server)
WITH historico AS (
    SELECT
        id_oportunidade,
        etapa_atual AS etapa,
        data_mudanca,
        valor_estimado,
        LEAD(data_mudanca) OVER (
            PARTITION BY id_oportunidade ORDER BY data_mudanca
        ) AS data_proxima_etapa
    FROM dbo.historico_funil
    WHERE YEAR(data_mudanca) = YEAR(GETDATE())
),
por_etapa AS (
    SELECT
        etapa,
        COUNT(DISTINCT id_oportunidade)       AS volume,
        SUM(valor_estimado)                    AS valor_potencial,
        AVG(valor_estimado)                    AS ticket_medio,
        AVG(DATEDIFF(day, data_mudanca,
            data_proxima_etapa))               AS dias_medio_etapa
    FROM historico
    GROUP BY etapa
),
etapas_ordenadas AS (
    SELECT *,
        ROW_NUMBER() OVER (ORDER BY volume DESC) AS ordem
    FROM por_etapa
)
SELECT
    etapa,
    volume,
    FORMAT(valor_potencial, 'C', 'pt-BR') AS valor_potencial,
    ticket_medio,
    dias_medio_etapa,
    ROUND(volume * 100.0 / FIRST_VALUE(volume) OVER (ORDER BY ordem), 1) AS conv_total_pct,
    ROUND(volume * 100.0 / LAG(volume, 1, volume) OVER (ORDER BY ordem), 1) AS conv_anterior_pct,
    LAG(volume) OVER (ORDER BY ordem) - volume AS drop_off_volume
FROM etapas_ordenadas
ORDER BY ordem;
```

---

## 3. DAX — Funil no Power BI

```dax
// Volume por etapa (filtrado pelo slicer de etapa)
Volume Etapa =
COUNTROWS(fFunil)

// Taxa de conversão total (etapa / topo do funil)
Taxa Conversao Total % =
DIVIDE(
    [Volume Etapa],
    CALCULATE([Volume Etapa], fFunil[etapa] = "Lead"),
    0
)

// Drop-off: perdas da etapa anterior para a atual
Drop Off Volume =
VAR etapa_atual = SELECTEDVALUE(dEtapas[etapa])
VAR ordem_atual = LOOKUPVALUE(dEtapas[ordem], dEtapas[etapa], etapa_atual)
VAR etapa_anterior = LOOKUPVALUE(dEtapas[etapa], dEtapas[ordem], ordem_atual - 1)
VAR vol_anterior = CALCULATE([Volume Etapa], fFunil[etapa] = etapa_anterior)
RETURN vol_anterior - [Volume Etapa]

// Ciclo médio de vendas (dias entre entrada e fechamento)
Ciclo Medio Dias =
AVERAGEX(
    FILTER(fFunil, fFunil[etapa] = "Fechado Ganho"),
    DATEDIFF(fFunil[data_entrada_funil], fFunil[data_fechamento], DAY)
)
```

---

## Regras de Qualidade

- Sempre analisar funil em volume E valor — perda de leads pequenos pode ser menos crítica que perda de grandes contas
- Drop-off percentual e absoluto são diferentes — 10% de drop-off em 1000 leads é mais crítico que 50% em 10
- Velocidade (dias por etapa) é tão importante quanto conversão — um funil rápido tem mais capacidade
- Funil por dimensão (canal, vendedor) revela diferenças de qualidade de lead e habilidade de fechamento
- Nunca analisar funil sem definir claramente o critério de entrada em cada etapa
- Amostra mínima de 30 oportunidades por célula para taxas de conversão confiáveis

## Observações

Skill irmã: `sales-planning` para meta vs realizado e forecast comercial.
Skill irmã: `statistics-business-kpis` para teste de significância entre funis (A/B).

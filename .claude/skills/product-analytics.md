---
name: product-analytics
description: >
  Especialista em análise de portfólio de produtos e performance de SKU. Cobre curva ABC,
  margem por produto, giro de estoque, sazonalidade, mix de receita, canibalização,
  elasticidade de preço, análise de lançamento vs descontinuação e ranking de SKUs críticos.
  Integra com SQL Server, Python, Power BI e Excel.
  Use sempre que o usuário mencionar análise de produto, SKU, portfólio, curva ABC, margem
  de produto, giro, mix de receita, canibalização, elasticidade, pricing de produto,
  sazonalidade de produto, lançamento, ou descontinuação.
  Trigger para: "analisa performance do produto", "curva ABC de SKUs", "margem por produto",
  "mix de receita por categoria", "giro de estoque", "elasticidade de preço", "SKUs críticos".
---

# Product Analytics — Análise de Portfólio e Performance de SKU

## Identidade

Analista de Produto Sênior com foco em portfólio, margem, giro e mix. Equilibra visão
financeira (margem e receita) com visão operacional (giro, ruptura, canibalização) para
apoiar decisões de pricing, sortimento e gestão de portfólio.

---

## Formato de Saída Padrão

```
1. VISÃO DO PORTFÓLIO (receita, margem, volume por categoria)
2. CURVA ABC (classificação de SKUs por impacto)
3. ANÁLISE DE MARGEM (por SKU, categoria, canal)
4. GIRO E RUPTURA (rotatividade e disponibilidade)
5. SAZONALIDADE (variação ao longo do ano)
6. OPORTUNIDADES (repricing, descontinuação, foco)
7. RECOMENDAÇÃO PRIORIZADA
```

---

## 1. Curva ABC de Produtos

```python
import pandas as pd
import numpy as np

def curva_abc_produtos(df: pd.DataFrame,
                        sku_col: str,
                        receita_col: str,
                        margem_col: str = None,
                        limites: tuple = (0.70, 0.95)) -> pd.DataFrame:
    """
    Classifica SKUs em A, B, C por participação acumulada na receita.

    limites: (% para A, % para A+B) — padrão 70/95/100
    """
    df_abc = (df.groupby(sku_col)
                .agg(
                    receita=(receita_col, 'sum'),
                    qtd_vendas=(receita_col, 'count'),
                    margem_total=(margem_col, 'sum') if margem_col else (receita_col, 'count'),
                )
                .reset_index()
                .sort_values('receita', ascending=False))

    df_abc['pct_receita']  = df_abc['receita'] / df_abc['receita'].sum()
    df_abc['pct_acum']     = df_abc['pct_receita'].cumsum()
    df_abc['curva_abc']    = pd.cut(
        df_abc['pct_acum'],
        bins=[0, limites[0], limites[1], 1.0],
        labels=['A', 'B', 'C']
    )
    df_abc['rank']         = range(1, len(df_abc)+1)

    # Resumo
    resumo = df_abc.groupby('curva_abc').agg(
        qtd_skus=('curva_abc', 'count'),
        receita_total=('receita', 'sum'),
        pct_receita_total=('pct_receita', 'sum')
    ).reset_index()

    print(f"\nCurva ABC — {df_abc[sku_col].nunique():,} SKUs")
    print(resumo.to_string(index=False))
    print(f"\nA: {(df_abc['curva_abc']=='A').sum()} SKUs = {limites[0]*100:.0f}% da receita")
    print(f"B: {(df_abc['curva_abc']=='B').sum()} SKUs = {(limites[1]-limites[0])*100:.0f}% da receita")
    print(f"C: {(df_abc['curva_abc']=='C').sum()} SKUs = {(1-limites[1])*100:.0f}% da receita")

    return df_abc


def matrix_abc_xyz(df: pd.DataFrame,
                    sku_col: str,
                    receita_col: str,
                    periodo_col: str) -> pd.DataFrame:
    """
    Matrix ABC (impacto) × XYZ (previsibilidade/regularidade).
    X = alta regularidade, Y = moderada, Z = irregular/sazonal
    """
    # ABC: por receita acumulada
    abc = curva_abc_produtos(df, sku_col, receita_col)

    # XYZ: por coeficiente de variação da receita mensal
    mensal = (df.groupby([sku_col, periodo_col])[receita_col]
                .sum().reset_index())
    variabilidade = (mensal.groupby(sku_col)[receita_col]
                           .agg(['mean', 'std'])
                           .reset_index())
    variabilidade['cv'] = (variabilidade['std'] / variabilidade['mean']).fillna(0)
    variabilidade['xyz'] = pd.cut(variabilidade['cv'],
                                   bins=[-0.01, 0.2, 0.5, 999],
                                   labels=['X', 'Y', 'Z'])

    matrix = abc.merge(variabilidade[[sku_col, 'cv', 'xyz']], on=sku_col, how='left')
    matrix['segmento'] = matrix['curva_abc'].astype(str) + matrix['xyz'].astype(str)

    print(f"\nMatrix ABC-XYZ:")
    print(matrix.groupby('segmento')['receita'].sum().sort_values(ascending=False).head(9))
    return matrix
```

---

## 2. Análise de Margem e Rentabilidade

```python
def analise_margem_produto(df: pd.DataFrame,
                            sku_col: str,
                            receita_col: str,
                            custo_col: str,
                            categoria_col: str = None) -> pd.DataFrame:
    """
    Margem bruta e contribuição por produto e categoria.
    Identifica SKUs que drenam margem apesar do volume.
    """
    grupo = [sku_col] + ([categoria_col] if categoria_col else [])

    margem = (df.groupby(grupo)
                .agg(
                    receita=(receita_col, 'sum'),
                    custo=(custo_col, 'sum'),
                    volume=(receita_col, 'count'),
                )
                .reset_index())

    margem['lucro_bruto']   = margem['receita'] - margem['custo']
    margem['margem_%']      = (margem['lucro_bruto'] / margem['receita'] * 100).round(2)
    margem['contrib_receita_%'] = (margem['receita'] / margem['receita'].sum() * 100).round(2)
    margem['contrib_margem_%']  = (margem['lucro_bruto'] / margem['lucro_bruto'].sum() * 100).round(2)

    # SKUs que têm margem negativa
    negativos = margem[margem['margem_%'] < 0]
    if len(negativos) > 0:
        print(f"\n⚠️  {len(negativos)} SKUs com margem negativa:")
        print(negativos[[sku_col, 'receita', 'margem_%']].to_string(index=False))

    return margem.sort_values('lucro_bruto', ascending=False)


def elasticidade_preco(df: pd.DataFrame,
                        sku_col: str,
                        preco_col: str,
                        volume_col: str,
                        periodo_col: str) -> pd.DataFrame:
    """
    Estima elasticidade-preço da demanda por SKU.
    Elasticidade = %Δvolume / %Δpreço
    Valor < -1: elástico (sensível ao preço)
    Valor > -1: inelástico (insensível ao preço)
    """
    df_sorted = df.sort_values([sku_col, periodo_col])
    df_sorted['delta_preco_%']  = df_sorted.groupby(sku_col)[preco_col].pct_change()
    df_sorted['delta_volume_%'] = df_sorted.groupby(sku_col)[volume_col].pct_change()

    elasticidade = (df_sorted.groupby(sku_col)
                     .apply(lambda x: np.polyfit(
                         x['delta_preco_%'].dropna(),
                         x['delta_volume_%'].dropna(), 1
                     )[0] if len(x.dropna()) >= 3 else np.nan)
                     .reset_index()
                     .rename(columns={0: 'elasticidade'}))

    elasticidade['tipo'] = elasticidade['elasticidade'].apply(
        lambda e: 'Elástico' if e < -1 else
                  'Inelástico' if -1 <= e <= 0 else
                  'Giffen' if e > 0 else 'N/D'
    )
    return elasticidade
```

---

## 3. SQL — Performance de SKU

```sql
-- Ranking de SKUs com ABC e sazonalidade (SQL Server)
WITH base AS (
    SELECT
        p.id_sku, p.nome_produto, p.categoria, p.subcategoria,
        MONTH(v.data_venda) AS mes,
        SUM(v.valor_liquido)   AS receita,
        SUM(v.custo_produto)   AS custo,
        SUM(v.qtd)             AS volume
    FROM dbo.fVendas v
    INNER JOIN dbo.dProduto p ON v.id_sku = p.id_sku
    WHERE YEAR(v.data_venda) = YEAR(GETDATE())
    GROUP BY p.id_sku, p.nome_produto, p.categoria, p.subcategoria, MONTH(v.data_venda)
),
anual AS (
    SELECT
        id_sku, nome_produto, categoria,
        SUM(receita)                              AS receita_anual,
        SUM(custo)                                AS custo_anual,
        SUM(receita) - SUM(custo)                 AS lucro_bruto,
        (SUM(receita) - SUM(custo))
            / NULLIF(SUM(receita),0) * 100        AS margem_pct,
        STDEV(receita) / NULLIF(AVG(receita),0)   AS cv_receita,
        SUM(receita) * 100.0
            / SUM(SUM(receita)) OVER ()           AS pct_receita,
        SUM(SUM(receita)) OVER (
            ORDER BY SUM(receita) DESC
            ROWS UNBOUNDED PRECEDING)
            / SUM(SUM(receita)) OVER ()           AS pct_acum
    FROM base
    GROUP BY id_sku, nome_produto, categoria
)
SELECT
    id_sku, nome_produto, categoria,
    FORMAT(receita_anual, 'C', 'pt-BR') AS receita_anual,
    ROUND(margem_pct, 1)                AS margem_pct,
    ROUND(pct_receita, 2)               AS pct_receita,
    ROUND(pct_acum * 100, 1)            AS pct_acum,
    CASE WHEN pct_acum <= 0.70 THEN 'A'
         WHEN pct_acum <= 0.95 THEN 'B'
         ELSE 'C' END                   AS curva_abc,
    CASE WHEN cv_receita <= 0.2 THEN 'X'
         WHEN cv_receita <= 0.5 THEN 'Y'
         ELSE 'Z' END                   AS regularidade_xyz,
    RANK() OVER (ORDER BY receita_anual DESC) AS rank_receita
FROM anual
ORDER BY receita_anual DESC;
```

---

## Regras de Qualidade

- Curva ABC deve ser revisada trimestralmente — portfólio muda
- Não descontínuar SKU C sem análise de cross-sell e necessidade de cliente âncora
- Margem negativa em A exige ação imediata — não compensar com volume
- Sazonalidade de produto ≠ queda de performance — separar os efeitos
- Elasticidade requer série histórica com variações de preço reais — não usar com preço estável
- SKU novo: avaliar com 90 dias de dados no mínimo antes de classificar

## Observações

Skill irmã: `procurement-compras` para análise de custo e fornecedor por SKU.
Skill irmã: `sales-planning` para performance comercial por produto e canal.

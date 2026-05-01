---
name: budget-cascade
description: >
  Especialista em cascateamento de metas, budget e forecast por hierarquia organizacional.
  Cobre distribuição top-down e bottom-up, critérios de alocação (histórico, capacidade,
  mercado), rolling forecast, revisões orçamentárias, cenários e reconciliação entre níveis.
  Integra com Excel, Power BI, SQL Server e Python.
  Use sempre que o usuário mencionar cascateamento de meta, distribuição de orçamento,
  budget por equipe, revisão de forecast, rolling forecast, meta por vendedor, alocação de
  budget, cenário orçamentário, ou qualquer processo de desdobramento de números.
  Trigger para: "cascateia a meta", "distribui budget por equipe", "rolling forecast",
  "revisão orçamentária", "desdobra a meta", "cenário otimista pessimista", "aloca budget".
---

# Budget Cascade — Cascateamento de Metas, Budget e Forecast

## Identidade

Especialista em Planejamento e Controle com foco em cascateamento de metas e gestão
orçamentária. Estrutura o raciocínio top-down e bottom-up, identifica inconsistências na
cascata e propõe critérios de distribuição aderentes à realidade do negócio.

---

## Quando Usar

Use esta skill para qualquer processo de distribuição de meta, budget ou forecast por
hierarquia: empresa → diretoria → gerência → equipe → vendedor. Complementa `sales-planning`
(análise do resultado) e `financial-analytics` (DRE e resultado financeiro).

---

## Formato de Saída Padrão

```
1. OBJETIVO DA CASCATA (meta top-down, período, hierarquia)
2. CRITÉRIO DE DISTRIBUIÇÃO (histórico, capacidade, mercado, negociado)
3. CASCATA CALCULADA (por nível hierárquico)
4. VALIDAÇÃO DE CONSISTÊNCIA (soma dos filhos = pai)
5. ANÁLISE DE TENSÃO (metas desafiadoras vs factíveis)
6. CENÁRIOS (base, otimista, pessimista)
7. PRÓXIMOS PASSOS (aprovação, comunicação, monitoramento)
```

---

## 1. Motor de Cascateamento

```python
import pandas as pd
import numpy as np
from typing import Dict, List

# Critérios disponíveis de distribuição
CRITERIOS = {
    'historico':    'Proporcional ao resultado histórico (média 12M)',
    'capacidade':   'Proporcional à capacidade (headcount × produtividade)',
    'mercado':      'Proporcional ao potencial de mercado (TAM por região)',
    'igualitario':  'Distribuição igual entre todos os filhos',
    'negociado':    'Percentuais definidos manualmente pela gestão',
}


def cascatear_meta(meta_total: float,
                   df_hierarquia: pd.DataFrame,
                   nivel_pai_col: str,
                   nivel_filho_col: str,
                   criterio_col: str,
                   criterio: str = 'historico',
                   fator_stretch: float = 1.0) -> pd.DataFrame:
    """
    Cascateia meta de um nível pai para seus filhos.

    Args:
        meta_total: valor total a distribuir
        df_hierarquia: DataFrame com pai, filho e o critério (ex: receita histórica)
        nivel_pai_col: coluna com o nome do nó pai
        nivel_filho_col: coluna com o nome do nó filho
        criterio_col: coluna com o valor usado para distribuição (ex: receita_12m)
        criterio: método de distribuição ('historico', 'igualitario', 'negociado')
        fator_stretch: multiplicador de desafio (ex: 1.15 = 15% acima do histórico)

    Returns:
        DataFrame com meta distribuída por filho
    """
    df = df_hierarquia.copy()

    if criterio == 'igualitario':
        df['peso'] = 1 / len(df)
    elif criterio == 'historico':
        total_criterio = df[criterio_col].sum()
        df['peso'] = df[criterio_col] / total_criterio
    elif criterio == 'negociado':
        # Espera que criterio_col contenha % já definidos (soma = 1)
        df['peso'] = df[criterio_col]
    else:
        raise ValueError(f"Critério '{criterio}' não suportado. Use: {list(CRITERIOS.keys())}")

    df['meta_distribuida'] = (df['peso'] * meta_total * fator_stretch).round(2)
    df['pct_da_meta_total'] = (df['meta_distribuida'] / meta_total * 100).round(2)

    # Validação: soma bate com o total?
    soma = df['meta_distribuida'].sum()
    delta = abs(soma - meta_total * fator_stretch)
    if delta > 0.01:
        print(f"⚠️  Ajuste de arredondamento: delta R$ {delta:.2f}")
        df.loc[df.index[-1], 'meta_distribuida'] += (meta_total * fator_stretch - soma)

    print(f"\n✅ Meta Distribuída: R$ {meta_total*fator_stretch:,.2f} "
          f"(stretch: {fator_stretch:.0%})")
    print(df[[nivel_filho_col, 'meta_distribuida', 'pct_da_meta_total', 'peso']].to_string(index=False))
    return df


def cascata_hierarquica(meta_empresa: float,
                         hierarquia: Dict[str, Dict],
                         historico: Dict[str, float],
                         fator_stretch: float = 1.10) -> pd.DataFrame:
    """
    Cascata multinível: Empresa → Diretoria → Gerência → Vendedor.

    Args:
        meta_empresa: meta total da empresa
        hierarquia: {diretoria: {gerencia: [vendedor1, vendedor2]}}
        historico: {entidade: receita_historica}
        fator_stretch: fator global de desafio

    Exemplo de hierarquia:
        {
            'Dir. Comercial SP': {
                'Ger. SP Norte': ['Ana', 'Bruno', 'Carlos'],
                'Ger. SP Sul':   ['Diana', 'Eduardo'],
            },
            'Dir. Comercial RJ': {
                'Ger. RJ':       ['Fernanda', 'Gustavo'],
            }
        }
    """
    registros = []
    meta_ajustada = meta_empresa * fator_stretch

    # Pesos das diretorias
    total_hist_dir = sum(
        sum(historico.get(g, 0) for g in gecias)
        for gecias in hierarquia.values()
    )

    for diretoria, gecias_dict in hierarquia.items():
        hist_dir = sum(historico.get(g, 0) for gerentes in gecias_dict.values()
                       for g in gerentes)
        peso_dir = hist_dir / total_hist_dir if total_hist_dir else 1/len(hierarquia)
        meta_dir = meta_ajustada * peso_dir

        total_hist_ger = sum(
            sum(historico.get(v, 0) for v in vendedores)
            for vendedores in gecias_dict.values()
        )

        for gerencia, vendedores in gecias_dict.items():
            hist_ger = sum(historico.get(v, 0) for v in vendedores)
            peso_ger = hist_ger / total_hist_ger if total_hist_ger else 1/len(gecias_dict)
            meta_ger = meta_dir * peso_ger

            hist_vendedores = sum(historico.get(v, 0) for v in vendedores)

            for vendedor in vendedores:
                hist_v = historico.get(vendedor, 0)
                peso_v = hist_v / hist_vendedores if hist_vendedores else 1/len(vendedores)
                meta_v = meta_ger * peso_v

                registros.append({
                    'diretoria': diretoria,
                    'gerencia':  gerencia,
                    'vendedor':  vendedor,
                    'historico': hist_v,
                    'peso':      round(peso_v, 4),
                    'meta':      round(meta_v, 2),
                    'stretch_%': round((meta_v / hist_v - 1) * 100, 1) if hist_v else None,
                })

    df = pd.DataFrame(registros)
    print(f"\nCascata concluída: {len(df)} vendedores | Meta total: R$ {df['meta'].sum():,.2f}")
    return df
```

---

## 2. Rolling Forecast

```python
def rolling_forecast(df_realizado: pd.DataFrame,
                      df_budget: pd.DataFrame,
                      mes_atual: str,
                      metrica_col: str = 'receita',
                      mes_col: str = 'mes',
                      metodo: str = 'tendencia') -> pd.DataFrame:
    """
    Gera rolling forecast: meses passados = realizado, meses futuros = projeção.

    metodo:
        'budget'    → usa o budget original para meses futuros
        'tendencia' → usa média móvel ponderada com ajuste de tendência
        'run_rate'  → extrapola o ritmo atual para os meses restantes
    """
    df_r = df_realizado[df_realizado[mes_col] <= mes_atual].copy()
    df_r['tipo'] = 'Realizado'

    meses_futuros = df_budget[df_budget[mes_col] > mes_atual][mes_col].tolist()

    if metodo == 'budget':
        df_f = df_budget[df_budget[mes_col] > mes_atual].copy()
        df_f['tipo'] = 'Forecast (Budget)'

    elif metodo == 'tendencia':
        ultimos = df_r.tail(3)[metrica_col].values
        media = np.mean(ultimos)
        tendencia = (ultimos[-1] - ultimos[0]) / max(len(ultimos)-1, 1)
        projecoes = []
        for i, mes in enumerate(meses_futuros, 1):
            projecoes.append({mes_col: mes, metrica_col: media + tendencia * i, 'tipo': 'Forecast'})
        df_f = pd.DataFrame(projecoes)

    elif metodo == 'run_rate':
        ytd = df_r[metrica_col].sum()
        meses_passados = len(df_r)
        run_rate_mensal = ytd / meses_passados if meses_passados else 0
        projecoes = [{mes_col: m, metrica_col: run_rate_mensal, 'tipo': 'Run Rate'}
                     for m in meses_futuros]
        df_f = pd.DataFrame(projecoes)

    resultado = pd.concat([df_r, df_f], ignore_index=True).sort_values(mes_col)
    resultado['acumulado'] = resultado[metrica_col].cumsum()

    ytd_real = df_r[metrica_col].sum()
    forecast_ano = resultado[metrica_col].sum()
    budget_ano = df_budget[metrica_col].sum()
    print(f"\nRolling Forecast ({metodo})")
    print(f"  YTD Realizado:  R$ {ytd_real:,.0f}")
    print(f"  Forecast Ano:   R$ {forecast_ano:,.0f}")
    print(f"  Budget Ano:     R$ {budget_ano:,.0f}")
    print(f"  Gap Budget:     R$ {forecast_ano - budget_ano:+,.0f} ({(forecast_ano/budget_ano-1)*100:+.1f}%)")
    return resultado


def cenarios_budget(meta_base: float, meses: int = 12) -> pd.DataFrame:
    """Gera 3 cenários (pessimista, base, otimista) com premissas."""
    return pd.DataFrame([
        {'cenario': 'Pessimista', 'fator': 0.85, 'meta_anual': meta_base * 0.85,
         'meta_mensal_media': meta_base * 0.85 / meses,
         'premissa': 'Mercado adverso, perda de clientes chave'},
        {'cenario': 'Base',       'fator': 1.00, 'meta_anual': meta_base,
         'meta_mensal_media': meta_base / meses,
         'premissa': 'Tendência histórica mantida, sem grandes impactos'},
        {'cenario': 'Otimista',   'fator': 1.15, 'meta_anual': meta_base * 1.15,
         'meta_mensal_media': meta_base * 1.15 / meses,
         'premissa': 'Expansão de carteira, novos produtos e canais'},
    ])
```

---

## 3. SQL — Cascata e Acompanhamento

```sql
-- Acompanhamento de atingimento por nível de cascata (SQL Server)
WITH cascata AS (
    SELECT
        m.diretoria, m.gerencia, m.vendedor,
        m.meta_mensal,
        ISNULL(SUM(v.valor_liquido), 0)        AS realizado,
        COUNT(DISTINCT v.id_venda)              AS qtd_vendas
    FROM dbo.metas_cascata m
    LEFT JOIN dbo.fVendas v
        ON  m.vendedor = v.vendedor
        AND MONTH(v.data_venda)  = MONTH(GETDATE())
        AND YEAR(v.data_venda)   = YEAR(GETDATE())
    WHERE m.mes = FORMAT(GETDATE(), 'yyyy-MM')
    GROUP BY m.diretoria, m.gerencia, m.vendedor, m.meta_mensal
)
SELECT
    diretoria, gerencia, vendedor,
    meta_mensal,
    realizado,
    realizado / NULLIF(meta_mensal, 0) * 100              AS atingimento_pct,
    meta_mensal - realizado                               AS gap,
    -- Run rate: se mantiver ritmo atual, fecha quanto?
    realizado / DAY(GETDATE())
        * DAY(EOMONTH(GETDATE()))                         AS projecao_fechamento,
    CASE
        WHEN realizado / NULLIF(meta_mensal,0) >= 1.0 THEN '✅ Acima'
        WHEN realizado / NULLIF(meta_mensal,0) >= 0.8 THEN '🟡 Atenção'
        ELSE '🔴 Abaixo'
    END AS status
FROM cascata
ORDER BY diretoria, gerencia, atingimento_pct DESC;
```

---

## Regras de Qualidade

- Sempre validar: soma das metas dos filhos = meta do pai (consistência vertical)
- Documentar explicitamente o critério de distribuição usado e sua justificativa
- Rolling forecast atualizado mensalmente — nunca travar no budget original após Q1
- Fator de stretch deve ter justificativa de negócio, não ser arbitrário
- Metas individuais: stretch máximo razoável de 20-25% acima do histórico sem mudança de estrutura
- Cenário pessimista serve para planejamento de caixa, não para motivação de time

## Observações

Skill irmã: `sales-planning` para análise de atingimento corrente.
Skill irmã: `financial-analytics` para reconciliação com orçamento financeiro.

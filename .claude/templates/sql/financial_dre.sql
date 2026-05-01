-- =============================================================
-- Template: DRE Gerencial com Variação vs Budget
-- Adaptar: schema, tabelas, colunas e plano de contas
-- Compatível: SQL Server | Athena | BigQuery
-- =============================================================

-- ------------------------------------------------------------
-- [1] BASE: lançamentos do período (competência)
-- ------------------------------------------------------------
WITH lancamentos AS (
    SELECT
        l.dt_competencia,
        l.cd_conta,
        l.ds_conta,
        l.cd_grupo_dre,         -- Receita / Custo / Despesa / Resultado
        l.cd_centro_custo,
        l.nm_centro_custo,
        l.vl_realizado,
        l.vl_budget,
        l.tp_lancamento         -- D (débito) ou C (crédito)
    FROM schema.fato_lancamentos l
    WHERE
        l.dt_competencia BETWEEN :dt_inicio AND :dt_fim
        AND l.fl_estorno = 0
),

-- ------------------------------------------------------------
-- [2] ENRIQUECIMENTO: plano de contas e hierarquia DRE
-- ------------------------------------------------------------
com_plano AS (
    SELECT
        l.*,
        p.nm_linha_dre,         -- Ex: Receita Bruta, CMV, Margem Bruta, EBITDA
        p.nr_ordem_dre,         -- Ordem de exibição na DRE
        p.fl_subtrai,           -- 1 = subtrai do resultado anterior
        p.fl_acumula_ebitda     -- 1 = compõe EBITDA
    FROM lancamentos l
    LEFT JOIN schema.dim_plano_contas p ON l.cd_conta = p.cd_conta
),

-- ------------------------------------------------------------
-- [3] AGREGAÇÃO: por linha da DRE
-- ------------------------------------------------------------
dre_agregado AS (
    SELECT
        nm_linha_dre,
        nr_ordem_dre,
        fl_subtrai,
        fl_acumula_ebitda,
        SUM(vl_realizado)       AS realizado,
        SUM(vl_budget)          AS budget
    FROM com_plano
    GROUP BY
        nm_linha_dre, nr_ordem_dre, fl_subtrai, fl_acumula_ebitda
),

-- ------------------------------------------------------------
-- [4] INDICADORES: variação e % budget
-- ------------------------------------------------------------
dre_indicadores AS (
    SELECT
        nm_linha_dre,
        nr_ordem_dre,
        realizado,
        budget,

        -- Variação absoluta
        realizado - budget                                  AS variacao_absoluta,

        -- Variação % (protegida contra divisão por zero)
        CASE WHEN ABS(budget) > 0
             THEN ((realizado - budget) / NULLIF(ABS(budget), 0)) * 100
             ELSE NULL END                                  AS variacao_pct,

        -- % realizado vs budget
        CASE WHEN ABS(budget) > 0
             THEN (realizado / NULLIF(ABS(budget), 0)) * 100
             ELSE NULL END                                  AS atingimento_pct

    FROM dre_agregado
),

-- ------------------------------------------------------------
-- [5] MARGENS: calculadas sobre Receita Líquida
-- ------------------------------------------------------------
receita_liquida AS (
    SELECT realizado AS vl_receita_liquida
    FROM dre_indicadores
    WHERE nm_linha_dre = 'Receita Líquida'  -- ajustar conforme plano de contas
),

dre_com_margem AS (
    SELECT
        d.*,
        CASE WHEN r.vl_receita_liquida <> 0
             THEN (d.realizado / NULLIF(r.vl_receita_liquida, 0)) * 100
             ELSE NULL END                                  AS margem_pct_realizado,
        CASE WHEN r.vl_receita_liquida <> 0
             THEN (d.budget / NULLIF(r.vl_receita_liquida, 0)) * 100
             ELSE NULL END                                  AS margem_pct_budget
    FROM dre_indicadores d
    CROSS JOIN receita_liquida r
)

-- ------------------------------------------------------------
-- [6] SAÍDA FINAL: DRE ordenada
-- ------------------------------------------------------------
SELECT
    nr_ordem_dre,
    nm_linha_dre,
    realizado,
    budget,
    variacao_absoluta,
    variacao_pct,
    atingimento_pct,
    margem_pct_realizado,
    margem_pct_budget
FROM dre_com_margem
ORDER BY nr_ordem_dre;

-- =============================================================
-- Validação sugerida:
-- Receita Bruta - Deduções = Receita Líquida → conferir manualmente
-- Receita Líquida - CMV = Margem Bruta → checar lógica do plano de contas
-- SELECT SUM(realizado) FROM lancamentos → total deve bater com DRE consolidado
-- =============================================================

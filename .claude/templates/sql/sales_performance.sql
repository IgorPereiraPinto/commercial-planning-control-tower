-- =============================================================
-- Template: Performance Comercial
-- Adaptar: schema, tabelas, colunas e filtros de negócio
-- Compatível: SQL Server | Athena | BigQuery | MySQL
-- =============================================================

-- ------------------------------------------------------------
-- [1] BASE: filtro de período e granularidade
-- ------------------------------------------------------------
WITH base AS (
    SELECT
        f.dt_venda,
        f.id_vendedor,
        f.id_produto,
        f.id_canal,
        f.id_regional,
        f.vl_receita_bruta,
        f.vl_desconto,
        f.vl_receita_liquida,
        f.vl_custo,
        f.qt_pedidos,
        f.qt_itens
    FROM schema.fato_vendas f
    WHERE
        f.dt_venda BETWEEN :dt_inicio AND :dt_fim
        -- Athena/BigQuery: filtrar partição primeiro
        -- AND f.ano_particao = :ano AND f.mes_particao = :mes
        AND f.fl_cancelado = 0
),

-- ------------------------------------------------------------
-- [2] ENRIQUECIMENTO: dimensões e hierarquia
-- ------------------------------------------------------------
enriquecido AS (
    SELECT
        b.*,
        v.nm_vendedor,
        v.nm_equipe,
        v.nm_regional,
        p.nm_produto,
        p.nm_categoria,
        p.nm_marca,
        c.nm_canal,
        -- Meta do período para o vendedor
        m.vl_meta_receita,
        m.vl_meta_pedidos
    FROM base b
    LEFT JOIN schema.dim_vendedor v ON b.id_vendedor = v.id_vendedor
        -- Risco de duplicidade se dim_vendedor tem múltiplas linhas por vendedor
        -- Garantir unicidade: WHERE v.fl_ativo = 1
    LEFT JOIN schema.dim_produto p ON b.id_produto = p.id_produto
    LEFT JOIN schema.dim_canal c ON b.id_canal = c.id_canal
    LEFT JOIN schema.dim_meta m
        ON b.id_vendedor = m.id_vendedor
        AND b.dt_venda BETWEEN m.dt_inicio_vigencia AND m.dt_fim_vigencia
),

-- ------------------------------------------------------------
-- [3] AGREGAÇÃO: KPIs por corte desejado
-- ------------------------------------------------------------
agregado AS (
    SELECT
        nm_regional,
        nm_equipe,
        nm_vendedor,
        nm_canal,
        nm_categoria,

        -- Volume e receita
        SUM(vl_receita_bruta)                               AS receita_bruta,
        SUM(vl_desconto)                                    AS total_desconto,
        SUM(vl_receita_liquida)                             AS receita_liquida,
        SUM(vl_custo)                                       AS custo_total,
        SUM(qt_pedidos)                                     AS qtd_pedidos,
        SUM(qt_itens)                                       AS qtd_itens,

        -- Margem
        SUM(vl_receita_liquida) - SUM(vl_custo)            AS margem_bruta,

        -- Meta
        MAX(vl_meta_receita)                                AS meta_receita,
        MAX(vl_meta_pedidos)                                AS meta_pedidos

    FROM enriquecido
    GROUP BY
        nm_regional, nm_equipe, nm_vendedor, nm_canal, nm_categoria
),

-- ------------------------------------------------------------
-- [4] INDICADORES: cálculos derivados e % atingimento
-- ------------------------------------------------------------
indicadores AS (
    SELECT
        *,

        -- Ticket médio (protegido contra divisão por zero)
        CASE WHEN qtd_pedidos > 0
             THEN receita_liquida / NULLIF(qtd_pedidos, 0)
             ELSE 0 END                                     AS ticket_medio,

        -- Margem % (protegida)
        CASE WHEN receita_liquida > 0
             THEN (margem_bruta / NULLIF(receita_liquida, 0)) * 100
             ELSE 0 END                                     AS margem_pct,

        -- Desconto % sobre bruto
        CASE WHEN receita_bruta > 0
             THEN (total_desconto / NULLIF(receita_bruta, 0)) * 100
             ELSE 0 END                                     AS desconto_pct,

        -- Atingimento de meta (%)
        CASE WHEN meta_receita > 0
             THEN (receita_liquida / NULLIF(meta_receita, 0)) * 100
             ELSE NULL END                                  AS atingimento_pct,

        -- Gap vs meta
        receita_liquida - COALESCE(meta_receita, 0)        AS gap_meta

    FROM agregado
)

-- ------------------------------------------------------------
-- [5] SAÍDA FINAL
-- ------------------------------------------------------------
SELECT
    nm_regional,
    nm_equipe,
    nm_vendedor,
    nm_canal,
    nm_categoria,
    receita_bruta,
    total_desconto,
    desconto_pct,
    receita_liquida,
    custo_total,
    margem_bruta,
    margem_pct,
    qtd_pedidos,
    ticket_medio,
    meta_receita,
    atingimento_pct,
    gap_meta
FROM indicadores
ORDER BY
    receita_liquida DESC;

-- =============================================================
-- Validação sugerida:
-- SELECT SUM(receita_liquida) FROM indicadores → comparar com total esperado
-- SELECT COUNT(*) FROM base → checar volume de registros
-- SELECT COUNT(DISTINCT id_vendedor) FROM base → checar cobertura de vendedores
-- =============================================================

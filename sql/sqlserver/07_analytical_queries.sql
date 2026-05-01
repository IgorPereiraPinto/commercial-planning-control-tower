-- =============================================================================
-- 07_analytical_queries.sql — Queries analíticas de validação e diagnóstico
-- Planejamento Comercial
-- =============================================================================
--
-- RESPONSABILIDADE:
--   Fornecer queries prontas para:
--   1. Validar a integridade do DW após a carga
--   2. Calcular os KPIs principais diretamente em SQL
--   3. Diagnosticar qualidade dos dados
--   4. Servir como base para views analíticas que o Power BI pode consumir
--
-- USO:
--   Execute as queries individualmente no SSMS ou Azure Data Studio
--   para validar os dados antes de abrir o Power BI.
--
-- [REUTILIZAÇÃO]:
--   Adapte os filtros de período e as métricas conforme o novo projeto.
-- =============================================================================

USE planejamento_comercial; -- [EDITÁVEL] nome do banco — deve ser igual ao criado no 00_setup.sql
GO

-- =============================================================================
-- SEÇÃO 1: VALIDAÇÃO DO DW
-- =============================================================================

-- Query 1.1 — Contagem de linhas por tabela do DW
-- Primeiro sanity check após a carga: volumes fazem sentido?
PRINT '=== 1.1 Contagem de linhas por tabela ===';
SELECT 'dw.fVendas'     AS Tabela, COUNT(*) AS Linhas FROM [dw].[fVendas] UNION ALL
SELECT 'dw.fMetas'      AS Tabela, COUNT(*) AS Linhas FROM [dw].[fMetas]  UNION ALL
SELECT 'dw.dCalendario' AS Tabela, COUNT(*) AS Linhas FROM [dw].[dCalendario] UNION ALL
SELECT 'dw.dProdutos'   AS Tabela, COUNT(*) AS Linhas FROM [dw].[dProdutos]   UNION ALL
SELECT 'dw.dVendedor'   AS Tabela, COUNT(*) AS Linhas FROM [dw].[dVendedor]   UNION ALL
SELECT 'dw.dClientes'   AS Tabela, COUNT(*) AS Linhas FROM [dw].[dClientes]   UNION ALL
SELECT 'dw.dCidade'     AS Tabela, COUNT(*) AS Linhas FROM [dw].[dCidade]     UNION ALL
SELECT 'dw.dUnidades'   AS Tabela, COUNT(*) AS Linhas FROM [dw].[dUnidades]   UNION ALL
SELECT 'dw.dStatus'     AS Tabela, COUNT(*) AS Linhas FROM [dw].[dStatus]     UNION ALL
SELECT 'dw.dPagamento'  AS Tabela, COUNT(*) AS Linhas FROM [dw].[dPagamento]
ORDER BY Tabela;
GO

-- Query 1.2 — Range de datas do fato de vendas
-- Confirma que o período carregado está correto
PRINT '=== 1.2 Range de datas em fVendas ===';
SELECT
    MIN([Data])             AS DataMinima,
    MAX([Data])             AS DataMaxima,
    DATEDIFF(MONTH, MIN([Data]), MAX([Data])) AS MesesCobertos,
    COUNT(DISTINCT [Id Vendedor]) AS Vendedores,
    COUNT(DISTINCT [Id Produto])  AS Produtos,
    COUNT(*)                AS TotalLinhas
FROM [dw].[fVendas];
GO

-- Query 1.3 — Verifica IDs órfãos (FKs sem correspondência na dimensão)
-- Deve retornar 0 para todas as dimensões se a integridade estiver ok
PRINT '=== 1.3 Verificação de IDs órfãos ===';
SELECT
    'Id Vendedor'   AS Chave,
    COUNT(*)        AS OrfaosEncontrados
FROM [dw].[fVendas] f
WHERE NOT EXISTS (SELECT 1 FROM [dw].[dVendedor] d WHERE d.[Id Vendedor] = f.[Id Vendedor])

UNION ALL

SELECT
    'Id Produto',
    COUNT(*)
FROM [dw].[fVendas] f
WHERE NOT EXISTS (SELECT 1 FROM [dw].[dProdutos] d WHERE d.[Id Produto] = f.[Id Produto])

UNION ALL

SELECT
    'Id Cliente',
    COUNT(*)
FROM [dw].[fVendas] f
WHERE NOT EXISTS (SELECT 1 FROM [dw].[dClientes] d WHERE d.[Id Cliente] = f.[Id Cliente])

UNION ALL

SELECT
    'Data → dCalendario',
    COUNT(*)
FROM [dw].[fVendas] f
WHERE NOT EXISTS (SELECT 1 FROM [dw].[dCalendario] d WHERE d.[Data] = f.[Data]);
GO

-- =============================================================================
-- SEÇÃO 2: KPIs PRINCIPAIS — META VS REALIZADO
-- =============================================================================

-- Query 2.1 — Faturamento Realizado vs Meta por Vendedor e Ano
-- Este é o KPI central do projeto
PRINT '=== 2.1 Meta vs Realizado por Vendedor/Ano ===';
WITH
-- Faturamento agrupado por vendedor e ano
Realizado AS (
    SELECT
        v.[Id Vendedor],
        v.[Vendedor],
        c.[Ano],
        SUM(f.[Faturamento Total])  AS FaturamentoRealizado,
        SUM(f.[Custo Total])        AS CustoTotal,
        SUM(f.[Margem Bruta])       AS MargemBruta,
        COUNT(DISTINCT f.[Num Venda]) AS QtdVendas
    FROM [dw].[fVendas] f
    INNER JOIN [dw].[dCalendario] c ON f.[Data] = c.[Data]
    INNER JOIN [dw].[dVendedor]   v ON f.[Id Vendedor] = v.[Id Vendedor]
    GROUP BY v.[Id Vendedor], v.[Vendedor], c.[Ano]
),
-- Metas por vendedor e ano
Metas AS (
    SELECT
        m.[Id Vendedor],
        m.[Ano],
        SUM(m.[Valor Meta]) AS MetaAnual
    FROM [dw].[fMetas] m
    GROUP BY m.[Id Vendedor], m.[Ano]
)
SELECT
    r.[Vendedor],
    r.[Ano],
    r.FaturamentoRealizado,
    m.MetaAnual,
    -- % Atingimento: quanto do realizado em relação à meta
    ROUND(
        CAST(r.FaturamentoRealizado AS FLOAT) / NULLIF(m.MetaAnual, 0) * 100,
        1
    )                               AS PctAtingimento,
    -- Desvio absoluto: positivo = superou, negativo = ficou abaixo
    r.FaturamentoRealizado - m.MetaAnual AS DesvioAbsoluto,
    -- Margem Bruta %
    ROUND(
        CAST(r.MargemBruta AS FLOAT) / NULLIF(r.FaturamentoRealizado, 0) * 100,
        1
    )                               AS MargemBrutaPct,
    r.QtdVendas
FROM Realizado r
LEFT JOIN Metas m ON r.[Id Vendedor] = m.[Id Vendedor] AND r.[Ano] = m.[Ano]
ORDER BY r.[Ano], r.FaturamentoRealizado DESC;
GO

-- Query 2.2 — Evolução Mensal: Meta vs Realizado (todos os vendedores)
PRINT '=== 2.2 Evolução Mensal: Meta vs Realizado ===';
WITH
RealizadoMensal AS (
    SELECT
        c.[AnoMes],
        c.[Ano],
        c.[Mes],
        c.[NomeMes],
        SUM(f.[Faturamento Total]) AS FaturamentoRealizado
    FROM [dw].[fVendas] f
    INNER JOIN [dw].[dCalendario] c ON f.[Data] = c.[Data]
    GROUP BY c.[AnoMes], c.[Ano], c.[Mes], c.[NomeMes]
),
MetaMensal AS (
    SELECT
        m.[Ano],
        m.[Mes],
        SUM(m.[Valor Meta]) AS MetaMensal
    FROM [dw].[fMetas] m
    GROUP BY m.[Ano], m.[Mes]
)
SELECT
    r.[AnoMes],
    r.[Ano],
    r.[Mes],
    r.[NomeMes],
    r.FaturamentoRealizado,
    m.MetaMensal,
    ROUND(
        CAST(r.FaturamentoRealizado AS FLOAT) / NULLIF(m.MetaMensal, 0) * 100,
        1
    ) AS PctAtingimento
FROM RealizadoMensal r
LEFT JOIN MetaMensal m ON r.[Ano] = m.[Ano] AND r.[Mes] = m.[Mes]
ORDER BY r.[AnoMes];
GO

-- =============================================================================
-- SEÇÃO 3: ANÁLISE DE MARGENS
-- =============================================================================

-- Query 3.1 — Decomposição da Receita: Faturamento → Margem → Resultado Líquido
-- Alimenta o gráfico Waterfall da Página 5 do Power BI
PRINT '=== 3.1 Decomposição de margens por ano ===';
SELECT
    c.[Ano],
    SUM(f.[Faturamento Total])                      AS Faturamento,
    SUM(f.[Custo Total])                            AS CustoTotal,
    SUM(f.[Margem Bruta])                           AS MargemBruta,
    SUM(f.[Qtde] * f.[Despesa Unit])                AS TotalDespesas,
    SUM(f.[Qtde] * f.[Impostos Unit])               AS TotalImpostos,
    SUM(f.[Qtde] * f.[Comissão Unit])               AS TotalComissoes,
    SUM(f.[Resultado Liquido])                      AS ResultadoLiquido,
    -- % sobre Faturamento
    ROUND(SUM(f.[Margem Bruta])     / NULLIF(SUM(f.[Faturamento Total]), 0) * 100, 1) AS MargemBrutaPct,
    ROUND(SUM(f.[Resultado Liquido])/ NULLIF(SUM(f.[Faturamento Total]), 0) * 100, 1) AS ResultadoLiquidoPct
FROM [dw].[fVendas] f
INNER JOIN [dw].[dCalendario] c ON f.[Data] = c.[Data]
GROUP BY c.[Ano]
ORDER BY c.[Ano];
GO

-- =============================================================================
-- SEÇÃO 4: ANÁLISE DE PARETO (CONCENTRAÇÃO DE VENDEDORES)
-- =============================================================================

-- Query 4.1 — Pareto de vendedores: quem representa 80% da receita?
PRINT '=== 4.1 Pareto de Vendedores ===';
WITH
FaturamentoPorVendedor AS (
    SELECT
        v.[Vendedor],
        SUM(f.[Faturamento Total])  AS Faturamento
    FROM [dw].[fVendas] f
    INNER JOIN [dw].[dVendedor] v ON f.[Id Vendedor] = v.[Id Vendedor]
    GROUP BY v.[Vendedor]
),
Ranqueado AS (
    SELECT
        [Vendedor],
        [Faturamento],
        SUM([Faturamento]) OVER ()                           AS TotalGeral,
        SUM([Faturamento]) OVER (ORDER BY [Faturamento] DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS FaturamentoAcumulado,
        RANK() OVER (ORDER BY [Faturamento] DESC)           AS Rank
    FROM FaturamentoPorVendedor
)
SELECT
    [Rank],
    [Vendedor],
    [Faturamento],
    ROUND([Faturamento] / [TotalGeral] * 100, 1)            AS PctDoTotal,
    ROUND([FaturamentoAcumulado] / [TotalGeral] * 100, 1)   AS PctAcumulado,
    -- Classificação Pareto
    CASE
        WHEN [FaturamentoAcumulado] / [TotalGeral] <= 0.80 THEN 'Top 80%'  -- [EDITÁVEL] limiar Pareto: 0.80 = top 80% da receita
        ELSE 'Restante 20%'
    END AS ClassificacaoPareto
FROM Ranqueado
ORDER BY [Rank];
GO

-- =============================================================================
-- SEÇÃO 5: ANÁLISE DE PRODUTOS
-- =============================================================================

-- Query 5.1 — Top N produtos por faturamento com margem
-- [EDITÁVEL] ajuste o número no SELECT TOP conforme o ranking desejado
PRINT '=== 5.1 Top 10 Produtos por Faturamento ===';
SELECT TOP 10  -- [EDITÁVEL] número de produtos no ranking (ex: 5, 10, 20)
    p.[Categoria],
    p.[Subcategoria],
    p.[Produto],
    p.[Marca],
    SUM(f.[Qtde])                   AS QtdVendida,
    SUM(f.[Faturamento Total])      AS Faturamento,
    SUM(f.[Margem Bruta])           AS MargemBruta,
    ROUND(
        SUM(f.[Margem Bruta]) / NULLIF(SUM(f.[Faturamento Total]), 0) * 100,
        1
    )                               AS MargemBrutaPct
FROM [dw].[fVendas] f
INNER JOIN [dw].[dProdutos] p ON f.[Id Produto] = p.[Id Produto]
GROUP BY p.[Categoria], p.[Subcategoria], p.[Produto], p.[Marca]
ORDER BY Faturamento DESC;
GO

-- =============================================================================
-- SEÇÃO 6: ANÁLISE GEOGRÁFICA
-- =============================================================================

-- Query 6.1 — Faturamento por Estado
PRINT '=== 6.1 Faturamento por Estado ===';
SELECT
    ci.[UF],
    ci.[Estado],
    COUNT(DISTINCT f.[Id Cliente])  AS QtdClientes,
    SUM(f.[Faturamento Total])      AS Faturamento,
    ROUND(
        SUM(f.[Faturamento Total]) / SUM(SUM(f.[Faturamento Total])) OVER () * 100,
        1
    )                               AS PctDoTotal
FROM [dw].[fVendas] f
INNER JOIN [dw].[dClientes]    cl ON f.[Id Cliente] = cl.[Id Cliente]
INNER JOIN [dw].[dCidade]      ci ON cl.[Id Cidade] = ci.[Id Cidade]
GROUP BY ci.[UF], ci.[Estado]
ORDER BY Faturamento DESC;
GO

PRINT '';
PRINT '=== Todas as queries analíticas executadas com sucesso. ===';
PRINT 'Use estas queries como base para views no Power BI ou diagnóstico manual.';

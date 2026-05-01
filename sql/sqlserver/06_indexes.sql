-- =============================================================================
-- 06_create_indexes.sql — Índices de performance para o star schema
-- Planejamento Comercial
-- =============================================================================
--
-- RESPONSABILIDADE:
--   Criar os índices necessários para garantir boa performance nas consultas
--   do Power BI, especialmente nas operações de JOIN entre fatos e dimensões.
--
-- POR QUE ÍNDICES SÃO CRÍTICOS NO POWER BI?
--   O Power BI envia queries SQL ao banco a cada interação do usuário
--   (filtro, drill-down, cross-filter). Sem índices adequados, cada
--   clique gera um full table scan — o relatório fica lento.
--
-- ESTRATÉGIA DE INDEXAÇÃO DO STAR SCHEMA:
--   1. PKs das dimensões: já indexadas pelo CONSTRAINT PRIMARY KEY
--   2. FKs na fato fVendas: criam índices para acelerar JOINs
--   3. Colunas de filtro frequente: Data, Id Vendedor, Id Produto
--   4. Índice composto para o KPI principal (Meta vs Realizado)
--
-- QUANDO REINDEXAR:
--   Após cargas grandes, execute: ALTER INDEX ALL ON tabela REBUILD;
--   Para cargas incrementais pequenas: ALTER INDEX ALL ON tabela REORGANIZE;
--
-- [REUTILIZAÇÃO]:
--   Mantenha índices nas colunas de FK da fato e nas colunas de filtro
--   mais usadas nos relatórios Power BI do novo projeto.
-- =============================================================================

USE planejamento_comercial; -- [EDITÁVEL] nome do banco — deve ser igual ao criado no 00_setup.sql
GO

PRINT '>>> Criando índices de performance...';

-- =============================================================================
-- ÍNDICES NA dw.fVendas
-- =============================================================================

-- IX_fVendas_Data: filtro mais frequente — quase toda query filtra por data
-- Coberto com INCLUDE para evitar lookup à tabela em queries de KPIs básicos
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_fVendas_Data' AND object_id = OBJECT_ID('dw.fVendas'))
CREATE NONCLUSTERED INDEX [IX_fVendas_Data]
ON [dw].[fVendas] ([Data])
INCLUDE ([Id Vendedor], [Faturamento Total], [Custo Total]);
PRINT '    IX_fVendas_Data criado.';

-- IX_fVendas_IdVendedor: suporte ao RLS e KPIs por vendedor
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_fVendas_IdVendedor' AND object_id = OBJECT_ID('dw.fVendas'))
CREATE NONCLUSTERED INDEX [IX_fVendas_IdVendedor]
ON [dw].[fVendas] ([Id Vendedor])
INCLUDE ([Data], [Faturamento Total], [Custo Total], [Qtde]);
PRINT '    IX_fVendas_IdVendedor criado.';

-- IX_fVendas_IdProduto: suporte a análises por produto e categoria
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_fVendas_IdProduto' AND object_id = OBJECT_ID('dw.fVendas'))
CREATE NONCLUSTERED INDEX [IX_fVendas_IdProduto]
ON [dw].[fVendas] ([Id Produto])
INCLUDE ([Data], [Faturamento Total], [Custo Total], [Qtde]);
PRINT '    IX_fVendas_IdProduto criado.';

-- IX_fVendas_IdCliente: suporte a análises por cliente e geografia
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_fVendas_IdCliente' AND object_id = OBJECT_ID('dw.fVendas'))
CREATE NONCLUSTERED INDEX [IX_fVendas_IdCliente]
ON [dw].[fVendas] ([Id Cliente])
INCLUDE ([Data], [Faturamento Total]);
PRINT '    IX_fVendas_IdCliente criado.';

-- IX_fVendas_IdUnidade: suporte a análises por unidade/filial
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_fVendas_IdUnidade' AND object_id = OBJECT_ID('dw.fVendas'))
CREATE NONCLUSTERED INDEX [IX_fVendas_IdUnidade]
ON [dw].[fVendas] ([Id Unidade])
INCLUDE ([Data], [Faturamento Total]);
PRINT '    IX_fVendas_IdUnidade criado.';

-- IX_fVendas_IdStatus: suporte ao filtro de pedidos válidos/inválidos
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_fVendas_IdStatus' AND object_id = OBJECT_ID('dw.fVendas'))
CREATE NONCLUSTERED INDEX [IX_fVendas_IdStatus]
ON [dw].[fVendas] ([Id Status]);
PRINT '    IX_fVendas_IdStatus criado.';

-- IX_fVendas_VendedorData: índice composto para o KPI "Meta vs Realizado por vendedor/mês"
-- Este é o JOIN mais executado no Power BI: fVendas ↔ fMetas por vendedor + data
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_fVendas_VendedorData' AND object_id = OBJECT_ID('dw.fVendas'))
CREATE NONCLUSTERED INDEX [IX_fVendas_VendedorData]
ON [dw].[fVendas] ([Id Vendedor], [Data])
INCLUDE ([Faturamento Total], [Custo Total], [Margem Bruta], [Resultado Liquido]);
PRINT '    IX_fVendas_VendedorData criado (índice composto para KPI principal).';
GO

-- =============================================================================
-- ÍNDICES NA dw.fMetas
-- =============================================================================

-- IX_fMetas_IdVendedor: suporte a filtros de meta por vendedor
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_fMetas_IdVendedor' AND object_id = OBJECT_ID('dw.fMetas'))
CREATE NONCLUSTERED INDEX [IX_fMetas_IdVendedor]
ON [dw].[fMetas] ([Id Vendedor])
INCLUDE ([Data Meta], [Ano], [Mes], [Valor Meta]);
PRINT '    IX_fMetas_IdVendedor criado.';

-- IX_fMetas_DataMeta: suporte ao JOIN com dCalendario
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_fMetas_DataMeta' AND object_id = OBJECT_ID('dw.fMetas'))
CREATE NONCLUSTERED INDEX [IX_fMetas_DataMeta]
ON [dw].[fMetas] ([Data Meta])
INCLUDE ([Id Vendedor], [Valor Meta]);
PRINT '    IX_fMetas_DataMeta criado.';

-- IX_fMetas_AnoMes: suporte a filtros de ano e mês sem JOIN com dCalendario
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_fMetas_AnoMes' AND object_id = OBJECT_ID('dw.fMetas'))
CREATE NONCLUSTERED INDEX [IX_fMetas_AnoMes]
ON [dw].[fMetas] ([Ano], [Mes])
INCLUDE ([Id Vendedor], [Valor Meta]);
PRINT '    IX_fMetas_AnoMes criado.';
GO

-- =============================================================================
-- ÍNDICES NAS DIMENSÕES (além das PKs já criadas)
-- =============================================================================

-- dw.dVendedor: índice no Gerente para suporte ao RLS do Power BI
-- O RLS filtra por email/nome de gerente → este índice acelera o filtro
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_dVendedor_Gerente' AND object_id = OBJECT_ID('dw.dVendedor'))
CREATE NONCLUSTERED INDEX [IX_dVendedor_Gerente]
ON [dw].[dVendedor] ([Gerente])
INCLUDE ([Id Vendedor], [Vendedor]);
PRINT '    IX_dVendedor_Gerente criado (suporte ao RLS).';

-- dw.dProdutos: índice na Categoria para drill-down de produto
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_dProdutos_Categoria' AND object_id = OBJECT_ID('dw.dProdutos'))
CREATE NONCLUSTERED INDEX [IX_dProdutos_Categoria]
ON [dw].[dProdutos] ([Categoria], [Subcategoria])
INCLUDE ([Id Produto], [Produto], [Marca]);
PRINT '    IX_dProdutos_Categoria criado.';

-- dw.dCidade: índice no UF para análise geográfica por estado
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_dCidade_UF' AND object_id = OBJECT_ID('dw.dCidade'))
CREATE NONCLUSTERED INDEX [IX_dCidade_UF]
ON [dw].[dCidade] ([UF])
INCLUDE ([Id Cidade], [Cidade], [Estado]);
PRINT '    IX_dCidade_UF criado.';

-- dw.dClientes: índice na cidade para JOIN com dCidade
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_dClientes_IdCidade' AND object_id = OBJECT_ID('dw.dClientes'))
CREATE NONCLUSTERED INDEX [IX_dClientes_IdCidade]
ON [dw].[dClientes] ([Id Cidade])
INCLUDE ([Id Cliente], [Cliente]);
PRINT '    IX_dClientes_IdCidade criado.';
GO

-- =============================================================================
-- ÍNDICES NA CAMADA STAGING (para suporte às queries analíticas diretas)
-- =============================================================================

-- staging.fVendas: índice de data e vendedor para queries de validação
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_stg_fVendas_Data' AND object_id = OBJECT_ID('staging.fVendas'))
CREATE NONCLUSTERED INDEX [IX_stg_fVendas_Data]
ON [staging].[fVendas] ([Data], [Id Vendedor]);
PRINT '    IX_stg_fVendas_Data criado (staging).';
GO

-- =============================================================================
-- RESUMO
-- =============================================================================
PRINT '';
PRINT '=== Resumo dos índices criados ===';
SELECT
    SCHEMA_NAME(t.schema_id) + '.' + t.name  AS Tabela,
    i.name                                    AS Indice,
    i.type_desc                               AS Tipo
FROM sys.indexes i
INNER JOIN sys.tables t ON i.object_id = t.object_id
WHERE SCHEMA_NAME(t.schema_id) IN ('dw', 'staging')
  AND i.type > 0  -- Exclui heap (tabela sem índice clusterizado)
ORDER BY Tabela, i.name;

PRINT '>>> Índices de performance criados com sucesso.';

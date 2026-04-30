-- =============================================================================
-- 02_create_staging_tables.sql — Camada STAGING: dados limpos e tipados
-- Commercial Planning Control Tower
-- =============================================================================
--
-- RESPONSABILIDADE:
--   Criar as tabelas da camada staging com tipos de dados corretos,
--   espelhando o que o Python entrega após transform.py.
--
-- DIFERENÇAS EM RELAÇÃO À RAW:
--   - Colunas de data são DATE (não NVARCHAR)
--   - IDs são INT (não NVARCHAR)
--   - Métricas são DECIMAL (não NVARCHAR)
--   - fMetas está em formato LONG (uma linha por vendedor-mês, não wide)
--   - Strings têm tamanhos máximos ajustados ao dado real
--
-- PRINCÍPIO DA CAMADA STAGING (Silver):
--   "Dado limpo, tipado e pronto para o modelo dimensional."
--   O staging é o contrato entre o ETL Python e o DW SQL.
--
-- [REUTILIZAÇÃO]:
--   Ajuste os tipos e tamanhos de colunas conforme os dados reais do
--   novo projeto. Mantenha o padrão: IDs como INT, datas como DATE,
--   métricas financeiras como DECIMAL(18,2).
-- =============================================================================

USE planejamento_comercial;
GO

PRINT '>>> Criando tabelas da camada STAGING...';

-- =============================================================================
-- staging.fVendas — Fato de vendas limpo e tipado
-- =============================================================================
DROP TABLE IF EXISTS [staging].[fVendas];
CREATE TABLE [staging].[fVendas] (
    -- Identificadores e datas (tipados corretamente)
    [Data]              DATE            NOT NULL,
    [Data Envio]        DATE            NULL,
    [Num Venda]         NVARCHAR(50)    NOT NULL,

    -- Chaves estrangeiras (INT após conversão do staging)
    [Id Produto]        INT             NOT NULL,
    [Id Vendedor]       INT             NOT NULL,
    [Nome Vendedor]     NVARCHAR(100)   NULL,
    [Id Cliente]        INT             NOT NULL,
    [Nome Cliente]      NVARCHAR(200)   NULL,
    [Id Unidade]        INT             NULL,
    [Nome Unidade]      NVARCHAR(100)   NULL,
    [Id Status]         INT             NULL,
    [Id Pgto]           INT             NULL,

    -- Métricas: DECIMAL(18,2) para valores monetários (18 dígitos, 2 casas decimais)
    -- Por que 18,2? Suporta valores até 9.999.999.999.999.999,99 — mais que suficiente
    -- para faturamento em R$ sem perder precisão de centavos.
    [Qtde]              DECIMAL(18, 4)  NULL,   -- 4 casas para quantidades fracionadas
    [Valor Unit]        DECIMAL(18, 4)  NULL,
    [Custo Unit]        DECIMAL(18, 6)  NULL,   -- 6 casas pois custo pode ter muitas decimais
    [Despesa Unit]      DECIMAL(18, 4)  NULL,
    [Impostos Unit]     DECIMAL(18, 4)  NULL,
    [Comissão Unit]     DECIMAL(18, 4)  NULL,
    [Faturamento Total] DECIMAL(18, 2)  NULL,
    [Custo Total]       DECIMAL(18, 2)  NULL,

    -- Metadados ETL
    [_etl_loaded_at]    DATETIME2       NULL,
    [_etl_source]       NVARCHAR(200)   NULL
);
PRINT '    staging.fVendas criada.';
GO

-- =============================================================================
-- staging.dProdutos
-- =============================================================================
DROP TABLE IF EXISTS [staging].[dProdutos];
CREATE TABLE [staging].[dProdutos] (
    [Id Produto]    INT             NOT NULL,
    [Produto]       NVARCHAR(200)   NOT NULL,
    [Categoria]     NVARCHAR(100)   NULL,
    [Subcategoria]  NVARCHAR(100)   NULL,
    [Marca]         NVARCHAR(100)   NULL,
    [_etl_loaded_at] DATETIME2      NULL,
    [_etl_source]   NVARCHAR(200)   NULL
);
PRINT '    staging.dProdutos criada.';
GO

-- =============================================================================
-- staging.dVendedor
-- =============================================================================
DROP TABLE IF EXISTS [staging].[dVendedor];
CREATE TABLE [staging].[dVendedor] (
    [Id Vendedor]   INT             NOT NULL,
    [Vendedor]      NVARCHAR(100)   NOT NULL,
    [URL Foto]      NVARCHAR(500)   NULL,
    [Gerente]       NVARCHAR(100)   NULL,
    [_etl_loaded_at] DATETIME2      NULL,
    [_etl_source]   NVARCHAR(200)   NULL
);
PRINT '    staging.dVendedor criada.';
GO

-- =============================================================================
-- staging.dClientes
-- =============================================================================
DROP TABLE IF EXISTS [staging].[dClientes];
CREATE TABLE [staging].[dClientes] (
    [Id Cliente]    INT             NOT NULL,
    [Cliente]       NVARCHAR(200)   NULL,
    [Id Cidade]     INT             NULL,
    [_etl_loaded_at] DATETIME2      NULL,
    [_etl_source]   NVARCHAR(200)   NULL
);
PRINT '    staging.dClientes criada.';
GO

-- =============================================================================
-- staging.dCidade
-- =============================================================================
DROP TABLE IF EXISTS [staging].[dCidade];
CREATE TABLE [staging].[dCidade] (
    [Id Cidade]     INT             NOT NULL,
    [Cidade]        NVARCHAR(100)   NULL,
    [UF]            CHAR(2)         NULL,   -- UF tem sempre 2 caracteres (SP, RJ, etc.)
    [Estado]        NVARCHAR(100)   NULL,
    [_etl_loaded_at] DATETIME2      NULL,
    [_etl_source]   NVARCHAR(200)   NULL
);
PRINT '    staging.dCidade criada.';
GO

-- =============================================================================
-- staging.dUnidades
-- =============================================================================
DROP TABLE IF EXISTS [staging].[dUnidades];
CREATE TABLE [staging].[dUnidades] (
    [Id Unidade]    INT             NOT NULL,
    [Unidade]       NVARCHAR(100)   NOT NULL,
    [_etl_loaded_at] DATETIME2      NULL,
    [_etl_source]   NVARCHAR(200)   NULL
);
PRINT '    staging.dUnidades criada.';
GO

-- =============================================================================
-- staging.dStatus
-- =============================================================================
DROP TABLE IF EXISTS [staging].[dStatus];
CREATE TABLE [staging].[dStatus] (
    [Id Status]     INT             NOT NULL,
    [Status]        NVARCHAR(50)    NOT NULL,
    [_etl_loaded_at] DATETIME2      NULL,
    [_etl_source]   NVARCHAR(200)   NULL
);
PRINT '    staging.dStatus criada.';
GO

-- =============================================================================
-- staging.dPagamento
-- =============================================================================
DROP TABLE IF EXISTS [staging].[dPagamento];
CREATE TABLE [staging].[dPagamento] (
    [Id Pagamento]          INT             NOT NULL,
    [Forma de Pagamento]    NVARCHAR(50)    NOT NULL,
    [_etl_loaded_at]        DATETIME2       NULL,
    [_etl_source]           NVARCHAR(200)   NULL
);
PRINT '    staging.dPagamento criada.';
GO

-- =============================================================================
-- staging.fMetas — Metas em formato LONG (pós UNPIVOT do Python)
--
-- Esta é a principal diferença em relação à raw:
-- Na raw, as metas estão em formato WIDE (coluna por mês).
-- No staging, estão em formato LONG (uma linha por vendedor-mês).
--
-- Exemplo:
--   Id Vendedor | Vendedor | Ano  | Mes | Data Meta  | Valor Meta
--   1           | Ronaldo  | 2018 | 1   | 2018-01-01 | 5.000.000,00
--   1           | Ronaldo  | 2018 | 2   | 2018-02-01 | 4.800.000,00
-- =============================================================================
DROP TABLE IF EXISTS [staging].[fMetas];
CREATE TABLE [staging].[fMetas] (
    [Id Vendedor]   INT             NOT NULL,
    [Vendedor]      NVARCHAR(100)   NULL,
    [Ano]           INT             NOT NULL,
    [Mes]           INT             NOT NULL,
    [Data Meta]     DATE            NOT NULL,   -- Primeiro dia do mês: 2018-01-01
    [Valor Meta]    DECIMAL(18, 2)  NOT NULL,
    [_etl_loaded_at] DATETIME2      NULL,
    [_etl_source]   NVARCHAR(200)   NULL
);
PRINT '    staging.fMetas criada (formato long — todos os anos consolidados).';
PRINT '>>> Camada STAGING concluída: 9 tabelas criadas.';
GO

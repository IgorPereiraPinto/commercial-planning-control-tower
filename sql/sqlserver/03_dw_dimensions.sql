-- =============================================================================
-- 03_create_dimensions.sql — Camada DW: tabelas de dimensão (star schema)
-- Planejamento Comercial
-- =============================================================================
--
-- RESPONSABILIDADE:
--   Criar as tabelas de dimensão do Data Warehouse no schema dw.
--   As dimensões são populadas a partir do staging via INSERT...SELECT.
--
-- MODELO ESTRELA (Star Schema):
--
--                      dw.dCalendario
--                           |
--   dStatus   dPagamento    |    dUnidades
--       \          \        |       /
--        -----  dw.fVendas  -------
--                   |
--         dVendedor |  dProdutos
--                   |
--               dClientes -- dCidade
--
--       dw.fMetas ---- dVendedor
--               \----- dCalendario
--
-- POR QUE STAR SCHEMA?
--   - Performance superior no Power BI (filtros percorrem menos joins)
--   - Leitura mais simples para analistas e para DAX
--   - Padrão Kimball — amplamente adotado em mercado
--   - Facilita a aplicação de RLS (filtros em dimensões propagam para fatos)
--
-- SOBRE SURROGATE KEYS:
--   Neste projeto, usamos as chaves naturais dos dados (Id Produto, Id Vendedor
--   etc.) como PKs do DW. Isso é suficiente para o volume e contexto deste case.
--   Em projetos maiores com integrações de múltiplas fontes (ex: CRM + ERP),
--   surrogate keys (INT IDENTITY) são recomendadas para desacoplar o DW
--   das chaves dos sistemas de origem.
--
-- [REUTILIZAÇÃO]:
--   Adicione dimensões seguindo o mesmo padrão.
--   Se precisar de surrogate keys, adicione coluna IDENTITY e ajuste os INSERTs.
-- =============================================================================

USE planejamento_comercial; -- [EDITÁVEL] nome do banco — deve ser igual ao criado no 00_setup.sql
GO

PRINT '>>> Criando dimensões do DW (star schema)...';

-- =============================================================================
-- dw.dCalendario — Dimensão tempo
-- Tabela central para toda análise temporal no Power BI.
-- É populada pelo script 05_populate_dCalendario.sql, não pelo ETL Python.
--
-- POR QUE TER dCalendario?
--   - Permite filtros por ano, mês, trimestre, semana com uma única dimensão
--   - Habilita funções DAX de inteligência temporal (DATESYTD, SAMEPERIODLASTYEAR)
--   - Controla quais datas são dias úteis para cálculos de produtividade
--   - O Power BI funciona MUITO melhor com tabela calendário dedicada do que
--     com colunas de data direto nas fatos
-- =============================================================================
DROP TABLE IF EXISTS [dw].[dCalendario];
CREATE TABLE [dw].[dCalendario] (
    -- Chave primária: a própria data (granularidade diária)
    [Data]              DATE            NOT NULL,

    -- Decomposição temporal para filtros e agrupamentos
    [Ano]               INT             NOT NULL,   -- Ex: 2018, 2019, 2020, 2021
    [Semestre]          INT             NOT NULL,   -- 1 ou 2
    [Trimestre]         INT             NOT NULL,   -- 1, 2, 3 ou 4
    [Mes]               INT             NOT NULL,   -- 1 a 12
    [NomeMes]           NVARCHAR(20)    NOT NULL,   -- "Janeiro", "Fevereiro", ...
    [NomeMesAbrev]      NVARCHAR(5)     NOT NULL,   -- "Jan", "Fev", ...
    [Semana]            INT             NOT NULL,   -- Número da semana no ano (1–53)
    [DiaSemana]         INT             NOT NULL,   -- 1=Segunda, 7=Domingo
    [NomeDiaSemana]     NVARCHAR(20)    NOT NULL,   -- "Segunda-feira", ...
    [NomeDiaSemanaAbrev] NVARCHAR(5)   NOT NULL,   -- "Seg", "Ter", ...
    [DiaDoMes]          INT             NOT NULL,   -- 1 a 31
    [DiaDoAno]          INT             NOT NULL,   -- 1 a 366

    -- Chaves de agrupamento para filtros e joins
    [AnoMes]            INT             NOT NULL,   -- Ex: 202101 (útil para ordenação)
    [AnoTrimestre]      NVARCHAR(10)    NOT NULL,   -- Ex: "2021-Q1"
    [AnoSemestre]       NVARCHAR(10)    NOT NULL,   -- Ex: "2021-S1"

    -- Datas de referência do período
    [InicioMes]         DATE            NOT NULL,   -- Primeiro dia do mês
    [FimMes]            DATE            NOT NULL,   -- Último dia do mês

    -- Indicadores booleanos (1=Sim, 0=Não)
    -- Usados em medidas DAX e filtros de dias úteis
    [IsDiaUtil]         BIT             NOT NULL    DEFAULT 1,
    [IsFimDeSemana]     BIT             NOT NULL    DEFAULT 0,
    [IsUltimoDiaMes]    BIT             NOT NULL    DEFAULT 0,
    [IsPrimeiroDiaMes]  BIT             NOT NULL    DEFAULT 0,

    -- Campos de comparação relativa (úteis para filtros "período atual")
    -- Calculados em relação à data de carga — podem ser recalculados com UPDATE
    [IsAnoAtual]        BIT             NOT NULL    DEFAULT 0,
    [IsMesAtual]        BIT             NOT NULL    DEFAULT 0,
    [IsTrimestreAtual]  BIT             NOT NULL    DEFAULT 0,

    CONSTRAINT PK_dCalendario PRIMARY KEY ([Data])
);
PRINT '    dw.dCalendario criada (será populada pelo script 05).';
GO

-- =============================================================================
-- dw.dProdutos — Hierarquia Marca > Categoria > Subcategoria > Produto
-- =============================================================================
DROP TABLE IF EXISTS [dw].[dProdutos];
CREATE TABLE [dw].[dProdutos] (
    [Id Produto]    INT             NOT NULL,
    [Produto]       NVARCHAR(200)   NOT NULL,
    [Categoria]     NVARCHAR(100)   NULL,
    [Subcategoria]  NVARCHAR(100)   NULL,
    [Marca]         NVARCHAR(100)   NULL,

    -- Metadados de controle do DW
    [_dw_loaded_at] DATETIME2       NOT NULL    DEFAULT GETDATE(),
    [_dw_source]    NVARCHAR(50)    NOT NULL    DEFAULT 'staging.dProdutos',

    CONSTRAINT PK_dProdutos PRIMARY KEY ([Id Produto])
);
PRINT '    dw.dProdutos criada.';
GO

-- =============================================================================
-- dw.dVendedor — Hierarquia Gerente > Vendedor
-- Esta dimensão é usada pelo RLS do Power BI para controle de acesso.
-- =============================================================================
DROP TABLE IF EXISTS [dw].[dVendedor];
CREATE TABLE [dw].[dVendedor] (
    [Id Vendedor]   INT             NOT NULL,
    [Vendedor]      NVARCHAR(100)   NOT NULL,
    [URL Foto]      NVARCHAR(500)   NULL,   -- Usada em cards visuais no Power BI
    [Gerente]       NVARCHAR(100)   NULL,   -- Base do RLS: Guardiola, Marta, Zagallo

    [_dw_loaded_at] DATETIME2       NOT NULL    DEFAULT GETDATE(),
    [_dw_source]    NVARCHAR(50)    NOT NULL    DEFAULT 'staging.dVendedor',

    CONSTRAINT PK_dVendedor PRIMARY KEY ([Id Vendedor])
);
PRINT '    dw.dVendedor criada.';
GO

-- =============================================================================
-- dw.dClientes — Clientes com vínculo à dimensão geográfica
-- =============================================================================
DROP TABLE IF EXISTS [dw].[dClientes];
CREATE TABLE [dw].[dClientes] (
    [Id Cliente]    INT             NOT NULL,
    [Cliente]       NVARCHAR(200)   NULL,
    [Id Cidade]     INT             NULL,   -- FK para dw.dCidade

    [_dw_loaded_at] DATETIME2       NOT NULL    DEFAULT GETDATE(),
    [_dw_source]    NVARCHAR(50)    NOT NULL    DEFAULT 'staging.dClientes',

    CONSTRAINT PK_dClientes PRIMARY KEY ([Id Cliente])
);
PRINT '    dw.dClientes criada.';
GO

-- =============================================================================
-- dw.dCidade — Hierarquia geográfica: Cidade > UF > Estado
-- Permite análise de receita por região no Power BI (mapa, drill-down)
-- =============================================================================
DROP TABLE IF EXISTS [dw].[dCidade];
CREATE TABLE [dw].[dCidade] (
    [Id Cidade]     INT             NOT NULL,
    [Cidade]        NVARCHAR(100)   NULL,
    [UF]            CHAR(2)         NULL,
    [Estado]        NVARCHAR(100)   NULL,

    [_dw_loaded_at] DATETIME2       NOT NULL    DEFAULT GETDATE(),
    [_dw_source]    NVARCHAR(50)    NOT NULL    DEFAULT 'staging.dCidade',

    CONSTRAINT PK_dCidade PRIMARY KEY ([Id Cidade])
);
PRINT '    dw.dCidade criada.';
GO

-- =============================================================================
-- dw.dUnidades — Unidades de negócio (Filial 1-9 + Matriz)
-- =============================================================================
DROP TABLE IF EXISTS [dw].[dUnidades];
CREATE TABLE [dw].[dUnidades] (
    [Id Unidade]    INT             NOT NULL,
    [Unidade]       NVARCHAR(100)   NOT NULL,
    [Tipo]          NVARCHAR(20)    NULL,   -- "Filial" ou "Matriz" (derivado do nome)

    [_dw_loaded_at] DATETIME2       NOT NULL    DEFAULT GETDATE(),
    [_dw_source]    NVARCHAR(50)    NOT NULL    DEFAULT 'staging.dUnidades',

    CONSTRAINT PK_dUnidades PRIMARY KEY ([Id Unidade])
);
PRINT '    dw.dUnidades criada.';
GO

-- =============================================================================
-- dw.dStatus — Status de pedidos com classificação de negócio
-- =============================================================================
DROP TABLE IF EXISTS [dw].[dStatus];
CREATE TABLE [dw].[dStatus] (
    [Id Status]             INT             NOT NULL,
    [Status]                NVARCHAR(50)    NOT NULL,
    [Conta Para Faturamento] BIT            NOT NULL DEFAULT 1,
    -- Indica se este status deve entrar no faturamento real.
    -- Pedidos "Inválidos" geralmente não entram nos KPIs de receita.
    -- [REUTILIZAÇÃO]: Ajuste esta regra conforme o negócio do novo projeto.

    [_dw_loaded_at] DATETIME2       NOT NULL    DEFAULT GETDATE(),
    [_dw_source]    NVARCHAR(50)    NOT NULL    DEFAULT 'staging.dStatus',

    CONSTRAINT PK_dStatus PRIMARY KEY ([Id Status])
);
PRINT '    dw.dStatus criada.';
GO

-- =============================================================================
-- dw.dPagamento — Formas de pagamento
-- =============================================================================
DROP TABLE IF EXISTS [dw].[dPagamento];
CREATE TABLE [dw].[dPagamento] (
    [Id Pagamento]          INT             NOT NULL,
    [Forma de Pagamento]    NVARCHAR(50)    NOT NULL,
    [Tipo]                  NVARCHAR(30)    NULL,
    -- Ex: "À Vista" (Débito, Boleto), "Parcelado" (Crédito), "Digital" (Paypal)
    -- [REUTILIZAÇÃO]: Classifique conforme as formas de pagamento do novo projeto.

    [_dw_loaded_at] DATETIME2       NOT NULL    DEFAULT GETDATE(),
    [_dw_source]    NVARCHAR(50)    NOT NULL    DEFAULT 'staging.dPagamento',

    CONSTRAINT PK_dPagamento PRIMARY KEY ([Id Pagamento])
);
PRINT '    dw.dPagamento criada.';
PRINT '>>> Dimensões DW criadas: dCalendario + 7 dimensões de negócio.';
GO

-- =============================================================================
-- SCRIPTS DE CARGA: staging → dw (dimensões)
-- Populam as dimensões a partir do staging após cada execução do ETL Python.
-- Estratégia: truncate + insert (mesma lógica do ETL Python).
-- =============================================================================

-- Script de carga das dimensões (execute após o pipeline Python)
-- [REUTILIZAÇÃO]: Este bloco pode ser encapsulado em uma stored procedure
-- chamada pelo pipeline ou agendada via SQL Server Agent.

PRINT '';
PRINT '=== Scripts de carga staging → dw (dimensões) ===';
PRINT 'Execute após o pipeline Python para popular as dimensões no DW.';

/*
-- Descomente e execute manualmente ou via procedure quando necessário:

TRUNCATE TABLE [dw].[dProdutos];
INSERT INTO [dw].[dProdutos] ([Id Produto], [Produto], [Categoria], [Subcategoria], [Marca])
SELECT [Id Produto], [Produto], [Categoria], [Subcategoria], [Marca]
FROM [staging].[dProdutos];

TRUNCATE TABLE [dw].[dVendedor];
INSERT INTO [dw].[dVendedor] ([Id Vendedor], [Vendedor], [URL Foto], [Gerente])
SELECT [Id Vendedor], [Vendedor], [URL Foto], [Gerente]
FROM [staging].[dVendedor];

TRUNCATE TABLE [dw].[dClientes];
INSERT INTO [dw].[dClientes] ([Id Cliente], [Cliente], [Id Cidade])
SELECT [Id Cliente], [Cliente], [Id Cidade]
FROM [staging].[dClientes];

TRUNCATE TABLE [dw].[dCidade];
INSERT INTO [dw].[dCidade] ([Id Cidade], [Cidade], [UF], [Estado])
SELECT [Id Cidade], [Cidade], [UF], [Estado]
FROM [staging].[dCidade];

TRUNCATE TABLE [dw].[dUnidades];
INSERT INTO [dw].[dUnidades] ([Id Unidade], [Unidade], [Tipo])
SELECT
    [Id Unidade],
    [Unidade],
    CASE
        WHEN [Unidade] LIKE '%Matriz%' THEN 'Matriz'
        WHEN [Unidade] LIKE '%Filial%' THEN 'Filial'
        ELSE 'Outros'
    END AS [Tipo]
FROM [staging].[dUnidades];

TRUNCATE TABLE [dw].[dStatus];
INSERT INTO [dw].[dStatus] ([Id Status], [Status], [Conta Para Faturamento])
SELECT
    [Id Status],
    [Status],
    CASE WHEN [Status] = 'Válidas' THEN 1 ELSE 0 END
FROM [staging].[dStatus];

TRUNCATE TABLE [dw].[dPagamento];
INSERT INTO [dw].[dPagamento] ([Id Pagamento], [Forma de Pagamento], [Tipo])
SELECT
    [Id Pagamento],
    [Forma de Pagamento],
    CASE
        WHEN [Forma de Pagamento] IN ('Débito', 'Boleto') THEN 'À Vista'
        WHEN [Forma de Pagamento] = 'Crédito' THEN 'Parcelado'
        WHEN [Forma de Pagamento] = 'Paypal' THEN 'Digital'
        ELSE 'Outros'
    END AS [Tipo]
FROM [staging].[dPagamento];
*/
GO

-- =============================================================================
-- 01_create_raw_tables.sql — Camada RAW: espelho direto dos arquivos Excel
-- Commercial Planning Control Tower
-- =============================================================================
--
-- RESPONSABILIDADE:
--   Criar as tabelas da camada raw como espelho fiel das planilhas Excel.
--   Todas as colunas são VARCHAR para preservar o dado exatamente como
--   foi lido, sem nenhuma conversão que possa descartar informação.
--
-- PRINCÍPIO DA CAMADA RAW (Bronze):
--   "Guardar o dado como veio — sem transformar, sem interpretar."
--   Isso permite:
--   - Auditar a fonte em caso de divergência
--   - Reprocessar a transformação sem reler os arquivos Excel
--   - Rastrear a origem de qualquer dado no sistema
--
-- QUANDO REEXECUTAR:
--   As tabelas usam DROP IF EXISTS + CREATE, portanto reexecutar este script
--   APAGA todos os dados raw existentes. Isso é intencional — raw é sempre
--   recriado a partir dos arquivos Excel pelo pipeline Python.
--
-- [REUTILIZAÇÃO]:
--   Adicione ou remova colunas conforme as colunas dos novos arquivos Excel.
--   Mantenha todos os tipos como NVARCHAR na camada raw.
-- =============================================================================

USE planejamento_comercial;
GO

PRINT '>>> Criando tabelas da camada RAW...';

-- =============================================================================
-- raw.fVendas — Transações de vendas (20.004 linhas, Jan/2018 a Abr/2021)
-- Granularidade: uma linha por item de venda (produto × pedido)
-- =============================================================================
DROP TABLE IF EXISTS [raw].[fVendas];
CREATE TABLE [raw].[fVendas] (
    -- Identificadores e datas
    [Data]              NVARCHAR(50),   -- Ex: "01/01/2018" ou "2018-01-01"
    [Data Envio]        NVARCHAR(50),
    [Num Venda]         NVARCHAR(50),   -- Ex: "2018VA1804"

    -- Chaves estrangeiras (vindas como string da planilha)
    [Id Produto]        NVARCHAR(20),
    [Id Vendedor]       NVARCHAR(20),
    [Nome Vendedor]     NVARCHAR(100),
    [Id Cliente]        NVARCHAR(20),
    [Nome Cliente]      NVARCHAR(200),
    [Id Unidade]        NVARCHAR(20),
    [Nome Unidade]      NVARCHAR(100),
    [Id Status]         NVARCHAR(10),
    [Id Pgto]           NVARCHAR(10),

    -- Métricas (todas como string na raw — conversão acontece no staging)
    [Qtde]              NVARCHAR(30),
    [Valor Unit]        NVARCHAR(30),
    [Custo Unit]        NVARCHAR(30),
    [Despesa Unit]      NVARCHAR(30),
    [Impostos Unit]     NVARCHAR(30),
    [Comissão Unit]     NVARCHAR(30),
    [Faturamento Total] NVARCHAR(30),
    [Custo Total]       NVARCHAR(30),

    -- Metadados ETL (adicionados pelo Python antes da carga)
    [_etl_loaded_at]    NVARCHAR(30),
    [_etl_source]       NVARCHAR(200)
);
PRINT '    raw.fVendas criada.';
GO

-- =============================================================================
-- raw.dProdutos — 499 produtos com hierarquia Categoria > Subcategoria > Marca
-- =============================================================================
DROP TABLE IF EXISTS [raw].[dProdutos];
CREATE TABLE [raw].[dProdutos] (
    [Id Produto]    NVARCHAR(20),
    [Produto]       NVARCHAR(200),
    [Categoria]     NVARCHAR(100),
    [Subcategoria]  NVARCHAR(100),
    [Marca]         NVARCHAR(100),
    [_etl_loaded_at] NVARCHAR(30),
    [_etl_source]   NVARCHAR(200)
);
PRINT '    raw.dProdutos criada.';
GO

-- =============================================================================
-- raw.dVendedor — 20 vendedores com hierarquia Gerente > Vendedor
-- =============================================================================
DROP TABLE IF EXISTS [raw].[dVendedor];
CREATE TABLE [raw].[dVendedor] (
    [Id Vendedor]   NVARCHAR(20),
    [Vendedor]      NVARCHAR(100),
    [URL Foto]      NVARCHAR(500),
    [Gerente]       NVARCHAR(100),
    [_etl_loaded_at] NVARCHAR(30),
    [_etl_source]   NVARCHAR(200)
);
PRINT '    raw.dVendedor criada.';
GO

-- =============================================================================
-- raw.dClientes — 9.760 clientes vinculados a cidades
-- =============================================================================
DROP TABLE IF EXISTS [raw].[dClientes];
CREATE TABLE [raw].[dClientes] (
    [Id Cliente]    NVARCHAR(20),
    [Cliente]       NVARCHAR(200),
    [id Cidade]     NVARCHAR(20),
    [_etl_loaded_at] NVARCHAR(30),
    [_etl_source]   NVARCHAR(200)
);
PRINT '    raw.dClientes criada.';
GO

-- =============================================================================
-- raw.dCidade — 9.888 cidades com UF e nome do estado
-- =============================================================================
DROP TABLE IF EXISTS [raw].[dCidade];
CREATE TABLE [raw].[dCidade] (
    [Id Cidade]     NVARCHAR(20),
    [Cidade]        NVARCHAR(100),
    [UF]            NVARCHAR(10),
    [Estado]        NVARCHAR(100),
    [_etl_loaded_at] NVARCHAR(30),
    [_etl_source]   NVARCHAR(200)
);
PRINT '    raw.dCidade criada.';
GO

-- =============================================================================
-- raw.dUnidades — 11 unidades de negócio (Filial 1-9 + Matriz + 1 extra)
-- =============================================================================
DROP TABLE IF EXISTS [raw].[dUnidades];
CREATE TABLE [raw].[dUnidades] (
    [Id Unidade]    NVARCHAR(20),
    [Unidade]       NVARCHAR(100),
    [_etl_loaded_at] NVARCHAR(30),
    [_etl_source]   NVARCHAR(200)
);
PRINT '    raw.dUnidades criada.';
GO

-- =============================================================================
-- raw.dStatus — 3 status de pedido (Válidas, Inválidas, ...)
-- =============================================================================
DROP TABLE IF EXISTS [raw].[dStatus];
CREATE TABLE [raw].[dStatus] (
    [Id Status]     NVARCHAR(10),
    [Status]        NVARCHAR(50),
    [_etl_loaded_at] NVARCHAR(30),
    [_etl_source]   NVARCHAR(200)
);
PRINT '    raw.dStatus criada.';
GO

-- =============================================================================
-- raw.dPagamento — 5 formas de pagamento (Débito, Crédito, Boleto, Paypal, ...)
-- =============================================================================
DROP TABLE IF EXISTS [raw].[dPagamento];
CREATE TABLE [raw].[dPagamento] (
    [Id Pagamento]      NVARCHAR(10),
    [Forma de Pagamento] NVARCHAR(50),
    [_etl_loaded_at]    NVARCHAR(30),
    [_etl_source]       NVARCHAR(200)
);
PRINT '    raw.dPagamento criada.';
GO

-- =============================================================================
-- raw.fMetas_YYYY — Uma tabela por ano, no formato wide original do Excel
-- Colunas: Id Vendedor | Vendedor | janeiro | fevereiro | ... | dezembro
--
-- [REUTILIZAÇÃO]: Adicione ou remova tabelas conforme os anos disponíveis.
-- =============================================================================

DROP TABLE IF EXISTS [raw].[fMetas_2018];
CREATE TABLE [raw].[fMetas_2018] (
    [Id Vendedor]   NVARCHAR(20),
    [Vendedor]      NVARCHAR(100),
    [janeiro]       NVARCHAR(30),
    [fevereiro]     NVARCHAR(30),
    [março]         NVARCHAR(30),
    [abril]         NVARCHAR(30),
    [maio]          NVARCHAR(30),
    [junho]         NVARCHAR(30),
    [julho]         NVARCHAR(30),
    [agosto]        NVARCHAR(30),
    [setembro]      NVARCHAR(30),
    [outubro]       NVARCHAR(30),
    [novembro]      NVARCHAR(30),
    [dezembro]      NVARCHAR(30),
    [_etl_loaded_at] NVARCHAR(30),
    [_etl_source]   NVARCHAR(200)
);

DROP TABLE IF EXISTS [raw].[fMetas_2019];
CREATE TABLE [raw].[fMetas_2019] (
    [Id Vendedor]   NVARCHAR(20),
    [Vendedor]      NVARCHAR(100),
    [janeiro]       NVARCHAR(30),
    [fevereiro]     NVARCHAR(30),
    [março]         NVARCHAR(30),
    [abril]         NVARCHAR(30),
    [maio]          NVARCHAR(30),
    [junho]         NVARCHAR(30),
    [julho]         NVARCHAR(30),
    [agosto]        NVARCHAR(30),
    [setembro]      NVARCHAR(30),
    [outubro]       NVARCHAR(30),
    [novembro]      NVARCHAR(30),
    [dezembro]      NVARCHAR(30),
    [_etl_loaded_at] NVARCHAR(30),
    [_etl_source]   NVARCHAR(200)
);

DROP TABLE IF EXISTS [raw].[fMetas_2020];
CREATE TABLE [raw].[fMetas_2020] (
    [Id Vendedor]   NVARCHAR(20),
    [Vendedor]      NVARCHAR(100),
    [janeiro]       NVARCHAR(30),
    [fevereiro]     NVARCHAR(30),
    [março]         NVARCHAR(30),
    [abril]         NVARCHAR(30),
    [maio]          NVARCHAR(30),
    [junho]         NVARCHAR(30),
    [julho]         NVARCHAR(30),
    [agosto]        NVARCHAR(30),
    [setembro]      NVARCHAR(30),
    [outubro]       NVARCHAR(30),
    [novembro]      NVARCHAR(30),
    [dezembro]      NVARCHAR(30),
    [_etl_loaded_at] NVARCHAR(30),
    [_etl_source]   NVARCHAR(200)
);

DROP TABLE IF EXISTS [raw].[fMetas_2021];
CREATE TABLE [raw].[fMetas_2021] (
    [Id Vendedor]   NVARCHAR(20),
    [Vendedor]      NVARCHAR(100),
    [janeiro]       NVARCHAR(30),
    [fevereiro]     NVARCHAR(30),
    [março]         NVARCHAR(30),
    [abril]         NVARCHAR(30),
    [maio]          NVARCHAR(30),
    [junho]         NVARCHAR(30),
    [julho]         NVARCHAR(30),
    [agosto]        NVARCHAR(30),
    [setembro]      NVARCHAR(30),
    [outubro]       NVARCHAR(30),
    [novembro]      NVARCHAR(30),
    [dezembro]      NVARCHAR(30),
    [_etl_loaded_at] NVARCHAR(30),
    [_etl_source]   NVARCHAR(200)
);

PRINT '    raw.fMetas_2018/2019/2020/2021 criadas.';
PRINT '>>> Camada RAW concluída: 12 tabelas criadas.';
GO

-- =============================================================================
-- 04_create_facts.sql — Camada DW: tabelas fato (star schema)
-- Planejamento Comercial
-- =============================================================================
--
-- RESPONSABILIDADE:
--   Criar as duas tabelas fato do modelo dimensional:
--   1. dw.fVendas   — transações de vendas realizadas
--   2. dw.fMetas    — metas de budget por vendedor/mês
--
-- POR QUE DUAS TABELAS FATO?
--   fVendas e fMetas têm granularidades diferentes:
--   - fVendas: granularidade = uma transação de venda (produto × pedido × data)
--   - fMetas: granularidade = um mês × vendedor (totalizador mensal)
--
--   Separar em duas fatos é a prática correta do star schema (Kimball).
--   No Power BI, as duas fatos se conectam ao mesmo dCalendario e dVendedor,
--   permitindo comparar meta vs. realizado na mesma visualização.
--
-- RELACIONAMENTOS NO POWER BI:
--
--   dw.fVendas.Data        → dw.dCalendario.Data       (muitos:1)
--   dw.fVendas.Id Produto  → dw.dProdutos.Id Produto   (muitos:1)
--   dw.fVendas.Id Vendedor → dw.dVendedor.Id Vendedor  (muitos:1)
--   dw.fVendas.Id Cliente  → dw.dClientes.Id Cliente   (muitos:1)
--   dw.fVendas.Id Unidade  → dw.dUnidades.Id Unidade   (muitos:1)
--   dw.fVendas.Id Status   → dw.dStatus.Id Status      (muitos:1)
--   dw.fVendas.Id Pgto     → dw.dPagamento.Id Pagamento (muitos:1)
--   dw.dClientes.Id Cidade → dw.dCidade.Id Cidade      (muitos:1)
--
--   dw.fMetas.Data Meta    → dw.dCalendario.Data       (muitos:1)
--   dw.fMetas.Id Vendedor  → dw.dVendedor.Id Vendedor  (muitos:1)
--
-- [REUTILIZAÇÃO]:
--   Se o novo projeto tiver métricas diferentes (ex: NPS, SLA), adicione
--   colunas nas fatos. Se tiver granularidade diferente (ex: diária por canal),
--   ajuste as colunas de ID e métricas conforme necessário.
-- =============================================================================

USE planejamento_comercial; -- [EDITÁVEL] nome do banco — deve ser igual ao criado no 00_setup.sql
GO

PRINT '>>> Criando tabelas fato do DW...';

-- =============================================================================
-- dw.fVendas — Fato central de transações de vendas
--
-- Granularidade: uma linha por produto × pedido × data
-- Volume: ~20.004 linhas (Jan/2018 a Abr/2021)
-- Atualizações: truncate + reload completo a cada execução do pipeline
-- =============================================================================
DROP TABLE IF EXISTS [dw].[fVendas];
CREATE TABLE [dw].[fVendas] (

    -- -------------------------------------------------------------------------
    -- CHAVES ESTRANGEIRAS (Foreign Keys)
    -- Conectam a fato às dimensões no star schema.
    -- Todas são NOT NULL com exceção das dimensões opcionais.
    -- -------------------------------------------------------------------------

    -- Data da venda → JOIN com dCalendario para análises temporais
    [Data]              DATE            NOT NULL,

    -- Data de envio do produto ao cliente
    -- NULL permitido: nem todo pedido tem data de envio registrada
    [Data Envio]        DATE            NULL,

    -- Número do pedido de venda (chave de negócio — não é PK do DW)
    [Num Venda]         NVARCHAR(50)    NOT NULL,

    -- FK → dw.dProdutos
    [Id Produto]        INT             NOT NULL,

    -- FK → dw.dVendedor
    [Id Vendedor]       INT             NOT NULL,

    -- FK → dw.dClientes
    [Id Cliente]        INT             NOT NULL,

    -- FK → dw.dUnidades
    [Id Unidade]        INT             NULL,

    -- FK → dw.dStatus
    [Id Status]         INT             NULL,

    -- FK → dw.dPagamento
    [Id Pgto]           INT             NULL,

    -- -------------------------------------------------------------------------
    -- MÉTRICAS (Measures)
    -- São os valores que serão agregados nas medidas DAX do Power BI.
    -- DECIMAL(18,4) para valores unitários (mais casas decimais).
    -- DECIMAL(18,2) para totais (precisão de centavos é suficiente).
    -- -------------------------------------------------------------------------

    -- Volume
    [Qtde]              DECIMAL(18, 4)  NULL,   -- Quantidade de itens vendidos

    -- Valores unitários (base para análise de pricing)
    [Valor Unit]        DECIMAL(18, 4)  NULL,   -- Preço de venda por unidade
    [Custo Unit]        DECIMAL(18, 6)  NULL,   -- Custo de aquisição por unidade
    [Despesa Unit]      DECIMAL(18, 4)  NULL,   -- Despesas operacionais por unidade
    [Impostos Unit]     DECIMAL(18, 4)  NULL,   -- Impostos por unidade
    [Comissão Unit]     DECIMAL(18, 4)  NULL,   -- Comissão do vendedor por unidade

    -- Totalizadores (= Qtde × Valor/Custo unitário)
    -- Estes valores vêm calculados do Excel — validamos a consistência no ETL.
    [Faturamento Total] DECIMAL(18, 2)  NULL,   -- Receita bruta da linha
    [Custo Total]       DECIMAL(18, 2)  NULL,   -- Custo total da linha

    -- -------------------------------------------------------------------------
    -- MÉTRICAS DERIVADAS (calculadas no SQL, evitando DAX complexo)
    -- [REUTILIZAÇÃO]: Adicione colunas derivadas que são pesadas para calcular
    -- em DAX — melhor calcular uma vez no SQL e persistir.
    -- -------------------------------------------------------------------------

    -- Margem bruta em R$ por linha (Faturamento - Custo)
    -- AS PERSISTED = calculada automaticamente ao inserir/atualizar
    [Margem Bruta]  AS ([Faturamento Total] - [Custo Total])   PERSISTED,

    -- Resultado líquido por linha (Faturamento - Custo - Despesa - Imposto - Comissão)
    [Resultado Liquido] AS (
        [Faturamento Total]
        - [Custo Total]
        - ([Qtde] * [Despesa Unit])
        - ([Qtde] * [Impostos Unit])
        - ([Qtde] * [Comissão Unit])
    ) PERSISTED,

    -- -------------------------------------------------------------------------
    -- METADADOS
    -- -------------------------------------------------------------------------
    [_dw_loaded_at] DATETIME2   NOT NULL    DEFAULT GETDATE(),
    [_dw_source]    NVARCHAR(50) NOT NULL   DEFAULT 'staging.fVendas'
);
PRINT '    dw.fVendas criada (com colunas computadas: Margem Bruta, Resultado Liquido).';
GO

-- =============================================================================
-- dw.fMetas — Fato de metas de budget por vendedor e mês
--
-- Granularidade: uma linha por vendedor × mês × ano
-- Volume: 11 vendedores × 12 meses × 4 anos = 528 linhas
-- Atualizações: truncate + reload completo a cada execução do pipeline
-- =============================================================================
DROP TABLE IF EXISTS [dw].[fMetas];
CREATE TABLE [dw].[fMetas] (

    -- -------------------------------------------------------------------------
    -- CHAVES ESTRANGEIRAS
    -- -------------------------------------------------------------------------

    -- FK → dw.dCalendario (primeiro dia do mês: 2018-01-01, 2018-02-01, etc.)
    -- Usar o primeiro dia do mês garante o JOIN com dCalendario.Data
    [Data Meta]     DATE            NOT NULL,

    -- FK → dw.dVendedor
    [Id Vendedor]   INT             NOT NULL,

    -- -------------------------------------------------------------------------
    -- ATRIBUTOS DE CONTEXTO
    -- Armazenamos Ano e Mes explicitamente para facilitar filtros no Power BI
    -- sem precisar sempre fazer o JOIN com dCalendario.
    -- -------------------------------------------------------------------------
    [Ano]           INT             NOT NULL,
    [Mes]           INT             NOT NULL,

    -- -------------------------------------------------------------------------
    -- MÉTRICA PRINCIPAL
    -- -------------------------------------------------------------------------
    [Valor Meta]    DECIMAL(18, 2)  NOT NULL,

    -- -------------------------------------------------------------------------
    -- METADADOS
    -- -------------------------------------------------------------------------
    [_dw_loaded_at] DATETIME2   NOT NULL    DEFAULT GETDATE(),
    [_dw_source]    NVARCHAR(50) NOT NULL   DEFAULT 'staging.fMetas'
);
PRINT '    dw.fMetas criada.';
GO

-- =============================================================================
-- SCRIPTS DE CARGA: staging → dw (fatos)
-- Populam as fatos a partir do staging após cada execução do ETL Python.
-- =============================================================================

PRINT '';
PRINT '=== Scripts de carga staging → dw (fatos) ===';

/*
-- Descomente e execute após o pipeline Python:

-- Carga de fVendas (apenas status válidos entram no DW)
-- Por que filtrar aqui? Para que os KPIs do Power BI não incluam
-- pedidos cancelados no faturamento. Pedidos inválidos ficam no staging
-- para análise operacional mas não chegam ao DW analítico.
TRUNCATE TABLE [dw].[fVendas];
INSERT INTO [dw].[fVendas] (
    [Data], [Data Envio], [Num Venda],
    [Id Produto], [Id Vendedor], [Id Cliente], [Id Unidade], [Id Status], [Id Pgto],
    [Qtde], [Valor Unit], [Custo Unit], [Despesa Unit], [Impostos Unit], [Comissão Unit],
    [Faturamento Total], [Custo Total]
)
SELECT
    f.[Data],
    f.[Data Envio],
    f.[Num Venda],
    f.[Id Produto],
    f.[Id Vendedor],
    f.[Id Cliente],
    f.[Id Unidade],
    f.[Id Status],
    f.[Id Pgto],
    f.[Qtde],
    f.[Valor Unit],
    f.[Custo Unit],
    f.[Despesa Unit],
    f.[Impostos Unit],
    f.[Comissão Unit],
    f.[Faturamento Total],
    f.[Custo Total]
FROM [staging].[fVendas] f
-- JOIN com dStatus para garantir que só carregamos registros de status existentes
INNER JOIN [dw].[dStatus] s ON f.[Id Status] = s.[Id Status]
-- [REUTILIZAÇÃO]: Se quiser carregar todos os status independentemente,
-- troque por LEFT JOIN ou remova o filtro WHERE abaixo.
WHERE s.[Conta Para Faturamento] = 1;


-- Carga de fMetas (todos os anos consolidados)
TRUNCATE TABLE [dw].[fMetas];
INSERT INTO [dw].[fMetas] ([Data Meta], [Id Vendedor], [Ano], [Mes], [Valor Meta])
SELECT
    [Data Meta],
    [Id Vendedor],
    [Ano],
    [Mes],
    [Valor Meta]
FROM [staging].[fMetas]
-- Garante que só entram vendedores que existem na dimensão
WHERE [Id Vendedor] IN (SELECT [Id Vendedor] FROM [dw].[dVendedor]);
*/
GO

PRINT '>>> Fatos DW criados: fVendas + fMetas.';

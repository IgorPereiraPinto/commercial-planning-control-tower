-- =============================================================================
-- 08_comissao.sql — Camada de Comissão: tabelas paramétricas + fato mensal
-- Planejamento Comercial
-- =============================================================================
--
-- RESPONSABILIDADE:
--   Implementar a camada analítica de comissão do projeto, criando:
--
--   1. [config].[param_regra_comissao]   — faixas de payout por atingimento
--   2. [config].[param_prioridade_produto] — multiplicadores por prioridade
--   3. [dw].[fComissaoMensal]             — fato mensal de comissão calculada
--
-- POR QUE UM SCHEMA [config]?
--   Parâmetros de negócio não devem viver no código nem no DW analítico.
--   O schema [config] centraliza regras ajustáveis sem exigir reescrita de SQL
--   ou DAX. Um gestor pode alterar a política via UPDATE sem afetar o pipeline.
--
-- FLUXO DE CÁLCULO:
--
--   fVendas (realizado)
--       └─→ JOIN dProdutos (prioridade)
--       └─→ JOIN param_prioridade_produto (multiplicador)
--       └─→ fMetas (meta mensal por vendedor)
--       └─→ cálculo de atingimento %
--       └─→ JOIN param_regra_comissao (fator de payout por faixa)
--       └─→ INSERT fComissaoMensal
--
-- CONEXÃO COM O MODELO DE DADOS:
--   fComissaoMensal liga-se a:
--     - dw.dVendedor   (Id Vendedor)
--     - dw.dCalendario (Data Ref = primeiro dia do mês)
--   Permite que o Power BI compare comissão calculada, provisão e pagamento
--   na mesma visualização temporal, com filtros de gerente, região e unidade.
--
-- CALENDÁRIO CORPORATIVO DE COMISSÃO (quando executar cada etapa):
--
--   Dia 20 do mês corrente  → Rodar query de projeção de vendas (EXEC sp_ProjecaoVendas)
--   Dia 22 do mês corrente  → Calcular provisão: INSERT em fComissaoMensal (status = 'Provisao')
--   Dia 24 do mês corrente  → Validação pela área comercial e planejamento
--   Dia 27 do mês corrente  → Enviar provisão ao financeiro (UPDATE status = 'Enviado')
--   Dia 03 do mês seguinte  → Fechamento definitivo de vendas (ETL completo)
--   Dia 05 do mês seguinte  → Recalcular comissão com dados fechados (status = 'Definitivo')
--   Dia 10 do mês seguinte  → Aprovação e liberação para pagamento (UPDATE status = 'Pago')
--
-- [EDITÁVEL] Para adaptar este arquivo ao seu projeto:
--   1. Ajuste as faixas de atingimento em param_regra_comissao (INSERT abaixo)
--   2. Ajuste os multiplicadores em param_prioridade_produto
--   3. Revise a taxa base em fComissaoMensal (atualmente 2,4% = 0.024)
--   4. Substitua os nomes de tabela se o seu DW usar nomenclatura diferente
-- =============================================================================

USE planejamento_comercial; -- [EDITÁVEL] nome do banco
GO

-- =============================================================================
-- SCHEMA config — parâmetros de negócio (regras ajustáveis sem reescrever SQL)
-- =============================================================================
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'config')
    EXEC ('CREATE SCHEMA [config]');
GO
PRINT '>>> Schema [config] verificado.';

-- =============================================================================
-- 1. config.param_regra_comissao
--    Faixas de atingimento de meta com fator de payout correspondente.
--    Uma linha por faixa. Colunas:
--      - id_regra          : identificador sequencial
--      - nome_faixa        : rótulo legível para relatórios
--      - ating_min         : limite inferior da faixa (inclusive)
--      - ating_max         : limite superior da faixa (exclusive)
--      - fator_payout      : multiplicador a aplicar sobre a comissão elegível
--      - vigencia_inicio   : data de início da vigência desta política
--      - vigencia_fim      : NULL = política atual ainda em vigor
--      - ativo             : 1 = faixa em uso, 0 = histórica
-- =============================================================================
DROP TABLE IF EXISTS [config].[param_regra_comissao];
CREATE TABLE [config].[param_regra_comissao] (
    [id_regra]          INT             NOT NULL IDENTITY(1,1) PRIMARY KEY,
    [nome_faixa]        NVARCHAR(50)    NOT NULL,
    -- [EDITÁVEL] limites de cada faixa de atingimento
    [ating_min]         DECIMAL(7, 2)   NOT NULL,   -- inclusive (ex: 80.00)
    [ating_max]         DECIMAL(7, 2)   NOT NULL,   -- exclusive (ex: 90.00); use 9999 para ilimitado
    -- [EDITÁVEL] multiplicador de payout (0 = sem payout, 1.0 = payout cheio)
    [fator_payout]      DECIMAL(5, 4)   NOT NULL,
    [vigencia_inicio]   DATE            NOT NULL    DEFAULT '2018-01-01',
    [vigencia_fim]      DATE            NULL,                               -- NULL = vigente
    [ativo]             BIT             NOT NULL    DEFAULT 1,
    [_criado_em]        DATETIME2       NOT NULL    DEFAULT GETDATE()
);
PRINT '    config.param_regra_comissao criada.';
GO

-- Inserir as faixas da política atual
-- [EDITÁVEL] Ajuste conforme a política de RV do projeto
INSERT INTO [config].[param_regra_comissao]
    ([nome_faixa], [ating_min], [ating_max], [fator_payout], [vigencia_inicio])
VALUES
    ('Abaixo do piso',    0.00,   80.00,  0.0000, '2018-01-01'),  -- [EDITÁVEL] sem payout abaixo de 80%
    ('Faixa básica',     80.00,   90.00,  0.5000, '2018-01-01'),  -- [EDITÁVEL] 50% de payout para 80-89%
    ('Faixa intermediária',90.00,100.00,  0.8000, '2018-01-01'),  -- [EDITÁVEL] 80% para 90-99%
    ('Payout cheio',    100.00,  110.00,  1.0000, '2018-01-01'),  -- [EDITÁVEL] 100% para 100-109%
    ('Acelerador 1',    110.00,  120.00,  1.3000, '2018-01-01'),  -- [EDITÁVEL] 130% para 110-119%
    ('Acelerador 2',    120.00, 9999.00,  1.6000, '2018-01-01'); -- [EDITÁVEL] 160% acima de 120%
GO
PRINT '    param_regra_comissao: 6 faixas de payout inseridas.';

-- =============================================================================
-- 2. config.param_prioridade_produto
--    Multiplicadores de comissão por prioridade estratégica de produto.
--    Conecta-se a dw.dProdutos via [Prioridade].
--    Uma linha por nível de prioridade.
-- =============================================================================
DROP TABLE IF EXISTS [config].[param_prioridade_produto];
CREATE TABLE [config].[param_prioridade_produto] (
    [prioridade]        NVARCHAR(5)     NOT NULL PRIMARY KEY,   -- P1, P2, P3, P4
    [descricao]         NVARCHAR(100)   NOT NULL,
    -- [EDITÁVEL] multiplicador aplicado sobre a comissão base do produto
    [multiplicador]     DECIMAL(5, 4)   NOT NULL,
    [vigencia_inicio]   DATE            NOT NULL    DEFAULT '2018-01-01',
    [vigencia_fim]      DATE            NULL,
    [ativo]             BIT             NOT NULL    DEFAULT 1,
    [_criado_em]        DATETIME2       NOT NULL    DEFAULT GETDATE()
);
PRINT '    config.param_prioridade_produto criada.';
GO

-- [EDITÁVEL] Ajuste os multiplicadores conforme a estratégia comercial do projeto
INSERT INTO [config].[param_prioridade_produto]
    ([prioridade], [descricao], [multiplicador])
VALUES
    ('P1', 'Produto estratégico — maior incentivo de comissão', 1.3500),  -- [EDITÁVEL]
    ('P2', 'Produto prioritário — incentivo elevado',           1.1500),  -- [EDITÁVEL]
    ('P3', 'Produto padrão — sem ajuste',                       1.0000),  -- [EDITÁVEL]
    ('P4', 'Produto de baixa prioridade — incentivo reduzido',  0.8500);  -- [EDITÁVEL]
GO
PRINT '    param_prioridade_produto: 4 níveis P1-P4 inseridos.';

-- =============================================================================
-- 3. dw.fComissaoMensal
--    Fato mensal de comissão — granularidade: vendedor × mês × status.
--    Armazena provisão (estimada em D-3) e definitivo (pós-fechamento de mês).
--
--    STATUS POSSÍVEIS (coluna [status_apuracao]):
--      'Provisao'   — calculado com dados parciais (dia 22 do mês)
--      'Enviado'    — provisão enviada ao financeiro (dia 27)
--      'Definitivo' — recalculado após fechamento do mês (dia 05 mês+1)
--      'Pago'       — aprovado e liberado para pagamento (dia 10 mês+1)
-- =============================================================================
DROP TABLE IF EXISTS [dw].[fComissaoMensal];
CREATE TABLE [dw].[fComissaoMensal] (

    -- -------------------------------------------------------------------------
    -- IDENTIFICAÇÃO
    -- -------------------------------------------------------------------------
    [id_comissao]           INT             NOT NULL IDENTITY(1,1) PRIMARY KEY,

    -- FK → dw.dCalendario (primeiro dia do mês de referência)
    [data_ref]              DATE            NOT NULL,

    -- FK → dw.dVendedor
    [Id Vendedor]           INT             NOT NULL,

    -- -------------------------------------------------------------------------
    -- ATRIBUTOS DE APURAÇÃO
    -- -------------------------------------------------------------------------
    [Ano]                   INT             NOT NULL,
    [Mes]                   INT             NOT NULL,

    -- Status do ciclo (ver comentário acima)
    [status_apuracao]       NVARCHAR(20)    NOT NULL    DEFAULT 'Provisao',

    -- Faixa de atingimento aplicada nesta apuração
    [nome_faixa_payout]     NVARCHAR(50)    NOT NULL,

    -- -------------------------------------------------------------------------
    -- MÉTRICAS DA APURAÇÃO
    -- -------------------------------------------------------------------------
    -- Vendas do período (base de cálculo)
    [faturamento_periodo]   DECIMAL(18, 2)  NOT NULL,   -- Realizado no mês

    -- Meta do período
    [meta_periodo]          DECIMAL(18, 2)  NOT NULL,

    -- % de atingimento calculado
    [atingimento_pct]       DECIMAL(7, 2)   NOT NULL,

    -- [EDITÁVEL] taxa base de comissão sobre receita líquida (ex: 0.024 = 2,4%)
    [taxa_base]             DECIMAL(7, 6)   NOT NULL    DEFAULT 0.024000,

    -- Multiplicador médio ponderado de prioridade de produto do vendedor no mês
    [mult_prioridade_medio] DECIMAL(5, 4)   NOT NULL    DEFAULT 1.0000,

    -- Comissão elegível (antes de aplicar fator de atingimento)
    -- = faturamento_periodo × taxa_base × mult_prioridade_medio
    [comissao_elegivel]     DECIMAL(18, 2)  NOT NULL,

    -- Fator de payout da faixa (0, 0.5, 0.8, 1.0, 1.3 ou 1.6)
    [fator_payout]          DECIMAL(5, 4)   NOT NULL,

    -- Comissão calculada = comissão elegível × fator de payout
    [comissao_calculada]    DECIMAL(18, 2)  NOT NULL,

    -- Comissão efetivamente paga (pode ser ajustada por exceção gerencial)
    -- NULL enquanto status < 'Pago'
    [comissao_paga]         DECIMAL(18, 2)  NULL,

    -- Observação de ajuste manual (quando comissao_paga difere de comissao_calculada)
    [observacao_ajuste]     NVARCHAR(500)   NULL,

    -- -------------------------------------------------------------------------
    -- METADADOS
    -- -------------------------------------------------------------------------
    [_calculado_em]         DATETIME2       NOT NULL    DEFAULT GETDATE(),
    [_calculado_por]        NVARCHAR(100)   NOT NULL    DEFAULT SYSTEM_USER,
    [_dw_source]            NVARCHAR(100)   NOT NULL    DEFAULT '08_comissao.sql'
);
GO
PRINT '    dw.fComissaoMensal criada.';

-- =============================================================================
-- ÍNDICES DE PERFORMANCE
-- =============================================================================
CREATE NONCLUSTERED INDEX [ix_fComissaoMensal_vendedor_mes]
    ON [dw].[fComissaoMensal] ([Id Vendedor], [Ano], [Mes]);

CREATE NONCLUSTERED INDEX [ix_fComissaoMensal_data_status]
    ON [dw].[fComissaoMensal] ([data_ref], [status_apuracao]);
GO
PRINT '    Índices de fComissaoMensal criados.';

-- =============================================================================
-- SCRIPT DE CARGA: calcular e inserir fComissaoMensal a partir do DW
--
-- QUANDO EXECUTAR:
--   - Provisão: todo dia 22 do mês (substitua dados do mês corrente)
--   - Definitivo: todo dia 05 do mês seguinte (substitua status = 'Definitivo')
--
-- PARÂMETROS AJUSTÁVEIS (declare antes de executar):
--   @ano INT   = ano de referência
--   @mes INT   = mês de referência
--   @status NVARCHAR(20) = 'Provisao' ou 'Definitivo'
-- =============================================================================

/*
-- Descomente e execute conforme o calendário corporativo:

DECLARE @ano  INT          = YEAR(GETDATE());
DECLARE @mes  INT          = MONTH(GETDATE());
DECLARE @status NVARCHAR(20) = 'Provisao'; -- [EDITÁVEL] 'Provisao' | 'Definitivo' | 'Pago'
DECLARE @data_ref DATE     = DATEFROMPARTS(@ano, @mes, 1);
DECLARE @taxa_base DECIMAL(7,6) = 0.024000; -- [EDITÁVEL] taxa base de comissão

-- Remover apuração anterior do mesmo mês/status antes de recalcular
DELETE FROM [dw].[fComissaoMensal]
WHERE [Ano] = @ano AND [Mes] = @mes AND [status_apuracao] = @status;

-- Calcular e inserir comissão mensal por vendedor
WITH base_vendas AS (
    -- Faturamento realizado no mês por vendedor
    SELECT
        f.[Id Vendedor],
        SUM(f.[Faturamento Total])                         AS faturamento_periodo,
        -- Multiplicador médio de prioridade (ponderado pelo faturamento)
        SUM(f.[Faturamento Total] * COALESCE(pp.[multiplicador], 1.0))
            / NULLIF(SUM(f.[Faturamento Total]), 0)        AS mult_prioridade_medio
    FROM [dw].[fVendas] f
    LEFT JOIN [dw].[dProdutos] dp ON f.[Id Produto] = dp.[Id Produto]
    LEFT JOIN [config].[param_prioridade_produto] pp
        ON pp.[prioridade] = dp.[Prioridade]
        AND pp.[ativo] = 1
    WHERE MONTH(f.[Data]) = @mes
      AND YEAR(f.[Data])  = @ano
    GROUP BY f.[Id Vendedor]
),
base_metas AS (
    -- Meta do mês por vendedor
    SELECT
        m.[Id Vendedor],
        SUM(m.[Valor Meta]) AS meta_periodo
    FROM [dw].[fMetas] m
    WHERE m.[Mes] = @mes AND m.[Ano] = @ano
    GROUP BY m.[Id Vendedor]
),
base_calculo AS (
    -- Unir vendas, metas e calcular atingimento
    SELECT
        v.[Id Vendedor],
        COALESCE(v.faturamento_periodo, 0)      AS faturamento_periodo,
        COALESCE(m.meta_periodo, 0)             AS meta_periodo,
        -- [EDITÁVEL] atingimento: protegido com NULLIF para evitar divisão por zero
        COALESCE(
            ROUND(
                CAST(v.faturamento_periodo AS FLOAT)
                / NULLIF(m.meta_periodo, 0) * 100, 2
            ), 0
        )                                       AS atingimento_pct,
        COALESCE(v.mult_prioridade_medio, 1.0)  AS mult_prioridade_medio
    FROM base_vendas v
    FULL OUTER JOIN base_metas m ON v.[Id Vendedor] = m.[Id Vendedor]
    -- Inclui vendedores com meta mas sem vendas (atingimento = 0%)
    WHERE v.[Id Vendedor] IS NOT NULL
       OR m.[Id Vendedor] IS NOT NULL
),
base_payout AS (
    -- Aplicar faixa de payout ao atingimento calculado
    SELECT
        c.*,
        r.[nome_faixa]                          AS nome_faixa_payout,
        r.[fator_payout],
        -- Comissão elegível (antes do fator de atingimento)
        ROUND(
            c.faturamento_periodo * @taxa_base * c.mult_prioridade_medio, 2
        )                                       AS comissao_elegivel,
        -- Comissão calculada (após fator de atingimento)
        ROUND(
            c.faturamento_periodo * @taxa_base * c.mult_prioridade_medio
            * r.[fator_payout], 2
        )                                       AS comissao_calculada
    FROM base_calculo c
    -- JOIN com a faixa de payout correta para o atingimento apurado
    INNER JOIN [config].[param_regra_comissao] r
        ON c.atingimento_pct >= r.[ating_min]
       AND c.atingimento_pct <  r.[ating_max]
       AND r.[ativo] = 1
       AND (r.[vigencia_fim] IS NULL OR r.[vigencia_fim] >= @data_ref)
       AND r.[vigencia_inicio] <= @data_ref
)
INSERT INTO [dw].[fComissaoMensal] (
    [data_ref], [Id Vendedor], [Ano], [Mes],
    [status_apuracao], [nome_faixa_payout],
    [faturamento_periodo], [meta_periodo], [atingimento_pct],
    [taxa_base], [mult_prioridade_medio],
    [comissao_elegivel], [fator_payout], [comissao_calculada]
)
SELECT
    @data_ref,
    [Id Vendedor],
    @ano,
    @mes,
    @status,
    [nome_faixa_payout],
    [faturamento_periodo],
    [meta_periodo],
    [atingimento_pct],
    @taxa_base,
    [mult_prioridade_medio],
    [comissao_elegivel],
    [fator_payout],
    [comissao_calculada]
FROM base_payout;

PRINT 'fComissaoMensal: ' + CAST(@@ROWCOUNT AS NVARCHAR) + ' linhas inseridas para ' + CAST(@mes AS NVARCHAR) + '/' + CAST(@ano AS NVARCHAR);
*/
GO

-- =============================================================================
-- QUERY DE VALIDAÇÃO — Resumo mensal de comissão (executar após a carga)
-- =============================================================================

/*
-- Execute para conferir o resultado da apuração:

SELECT
    v.[Vendedor],
    v.[Gerente],
    c.[Mes],
    c.[Ano],
    c.[status_apuracao],
    c.[faturamento_periodo]   AS [Faturamento (R$)],
    c.[meta_periodo]          AS [Meta (R$)],
    c.[atingimento_pct]       AS [Atingimento (%)],
    c.[nome_faixa_payout]     AS [Faixa],
    c.[mult_prioridade_medio] AS [Mult. Prioridade],
    c.[comissao_elegivel]     AS [Elegível (R$)],
    c.[fator_payout]          AS [Fator Payout],
    c.[comissao_calculada]    AS [Comissão Calculada (R$)],
    c.[comissao_paga]         AS [Comissão Paga (R$)]
FROM [dw].[fComissaoMensal] c
INNER JOIN [dw].[dVendedor] v ON c.[Id Vendedor] = v.[Id Vendedor]
ORDER BY c.[Ano], c.[Mes], c.[atingimento_pct] DESC;
*/
GO

-- =============================================================================
-- QUERY DE PROVISÃO MENSAL — uso pelo financeiro
-- Totaliza a provisão de despesa comercial por gerente e mês.
-- =============================================================================

/*
SELECT
    v.[Gerente],
    c.[Mes],
    c.[Ano],
    c.[status_apuracao],
    COUNT(*)                        AS [Qtde Vendedores],
    SUM(c.[meta_periodo])           AS [Meta Total (R$)],
    SUM(c.[faturamento_periodo])    AS [Faturamento Total (R$)],
    ROUND(
        SUM(c.[faturamento_periodo]) / NULLIF(SUM(c.[meta_periodo]), 0) * 100, 1
    )                               AS [Atingimento Equipe (%)],
    SUM(c.[comissao_elegivel])      AS [Pool Elegível (R$)],
    SUM(c.[comissao_calculada])     AS [Provisão de Comissão (R$)],
    ROUND(
        SUM(c.[comissao_calculada]) / NULLIF(SUM(c.[faturamento_periodo]), 0) * 100, 2
    )                               AS [Comissão / Receita (%)]
FROM [dw].[fComissaoMensal] c
INNER JOIN [dw].[dVendedor] v ON c.[Id Vendedor] = v.[Id Vendedor]
WHERE c.[status_apuracao] IN ('Provisao', 'Definitivo')  -- [EDITÁVEL]
GROUP BY v.[Gerente], c.[Mes], c.[Ano], c.[status_apuracao]
ORDER BY c.[Ano], c.[Mes], v.[Gerente];
*/
GO

PRINT '';
PRINT '>>> 08_comissao.sql concluído.';
PRINT '    Objetos criados:';
PRINT '      config.param_regra_comissao     (6 faixas de payout)';
PRINT '      config.param_prioridade_produto (4 níveis P1-P4)';
PRINT '      dw.fComissaoMensal              (fato mensal de comissão)';
PRINT '    Próximos passos:';
PRINT '      1. Ajuste as faixas em param_regra_comissao conforme a política da empresa';
PRINT '      2. Execute o script de carga (seção comentada acima) no dia 22 ou 05 do mês';
PRINT '      3. Valide com a query de validação ao final deste arquivo';

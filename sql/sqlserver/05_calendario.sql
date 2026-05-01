-- =============================================================================
-- 05_populate_dCalendario.sql — População da dimensão calendário
-- Planejamento Comercial
-- =============================================================================
--
-- RESPONSABILIDADE:
--   Gerar e inserir todas as datas do período do projeto na dw.dCalendario,
--   com todos os atributos temporais necessários para o Power BI.
--
-- PERÍODO GERADO: 2017-01-01 até 2022-12-31
--   - Começa 1 ano antes dos dados (2017) para comportar análises YoY
--   - Termina 1 ano depois dos dados (2022) para comportar planejamento futuro
--   - [REUTILIZAÇÃO]: Ajuste @DataInicio e @DataFim conforme o projeto
--
-- TÉCNICA UTILIZADA: Recursive CTE (Common Table Expression)
--   Gera uma sequência de datas usando recursão: começa na data inicial e
--   adiciona 1 dia por iteração até atingir a data final.
--   É mais legível e portável que usar tabelas de números.
--
-- QUANDO EXECUTAR:
--   - Uma única vez ao configurar o ambiente
--   - Reexecutar se o período precisar ser estendido (novos anos de dados)
--   - Este script é idempotente: apaga e recria todo o conteúdo
--
-- [REUTILIZAÇÃO]:
--   Ajuste apenas @DataInicio e @DataFim. Todo o resto é calculado
--   automaticamente para qualquer período.
-- =============================================================================

USE planejamento_comercial; -- [EDITÁVEL] nome do banco — deve ser igual ao criado no 00_setup.sql
GO

PRINT '>>> Populando dw.dCalendario...';

-- Limpa antes de repopular (idempotente)
TRUNCATE TABLE [dw].[dCalendario];
GO

-- =============================================================================
-- GERAÇÃO DAS DATAS VIA RECURSIVE CTE
-- =============================================================================
DECLARE @DataInicio DATE = '2017-01-01';  -- [EDITÁVEL] início do período: normalmente 1 ano antes dos dados
DECLARE @DataFim    DATE = '2022-12-31';  -- [EDITÁVEL] fim do período: normalmente 1-2 anos depois dos dados

-- Tabela temporária para trabalhar com os dados antes de inserir
-- (melhor performance que INSERT direto na CTE recursiva)
;WITH
-- CTE recursiva que gera uma linha por dia entre @DataInicio e @DataFim
Datas AS (
    -- Âncora: começa na data inicial
    SELECT @DataInicio AS [Data]

    UNION ALL

    -- Recursão: adiciona 1 dia enquanto não ultrapassar @DataFim
    SELECT DATEADD(DAY, 1, [Data])
    FROM Datas
    WHERE DATEADD(DAY, 1, [Data]) <= @DataFim
)

-- Insert com todos os atributos calculados a partir da data
INSERT INTO [dw].[dCalendario] (
    [Data],
    [Ano],
    [Semestre],
    [Trimestre],
    [Mes],
    [NomeMes],
    [NomeMesAbrev],
    [Semana],
    [DiaSemana],
    [NomeDiaSemana],
    [NomeDiaSemanaAbrev],
    [DiaDoMes],
    [DiaDoAno],
    [AnoMes],
    [AnoTrimestre],
    [AnoSemestre],
    [InicioMes],
    [FimMes],
    [IsDiaUtil],
    [IsFimDeSemana],
    [IsUltimoDiaMes],
    [IsPrimeiroDiaMes],
    [IsAnoAtual],
    [IsMesAtual],
    [IsTrimestreAtual]
)
SELECT
    -- Data original
    d.[Data],

    -- Ano: ex. 2018, 2019, 2020, 2021
    YEAR(d.[Data])                  AS [Ano],

    -- Semestre: 1 para jan-jun, 2 para jul-dez
    CASE WHEN MONTH(d.[Data]) <= 6 THEN 1 ELSE 2 END AS [Semestre],

    -- Trimestre: 1, 2, 3 ou 4
    DATEPART(QUARTER, d.[Data])     AS [Trimestre],

    -- Mês: 1 a 12
    MONTH(d.[Data])                 AS [Mes],

    -- Nome do mês em português
    CASE MONTH(d.[Data])
        WHEN 1  THEN 'Janeiro'
        WHEN 2  THEN 'Fevereiro'
        WHEN 3  THEN 'Março'
        WHEN 4  THEN 'Abril'
        WHEN 5  THEN 'Maio'
        WHEN 6  THEN 'Junho'
        WHEN 7  THEN 'Julho'
        WHEN 8  THEN 'Agosto'
        WHEN 9  THEN 'Setembro'
        WHEN 10 THEN 'Outubro'
        WHEN 11 THEN 'Novembro'
        WHEN 12 THEN 'Dezembro'
    END AS [NomeMes],

    -- Abreviação do mês (3 letras)
    CASE MONTH(d.[Data])
        WHEN 1  THEN 'Jan' WHEN 2  THEN 'Fev' WHEN 3  THEN 'Mar'
        WHEN 4  THEN 'Abr' WHEN 5  THEN 'Mai' WHEN 6  THEN 'Jun'
        WHEN 7  THEN 'Jul' WHEN 8  THEN 'Ago' WHEN 9  THEN 'Set'
        WHEN 10 THEN 'Out' WHEN 11 THEN 'Nov' WHEN 12 THEN 'Dez'
    END AS [NomeMesAbrev],

    -- Semana do ano (ISO: 1 a 53)
    DATEPART(WEEK, d.[Data])        AS [Semana],

    -- Dia da semana: DATEPART com WEEKDAY retorna 1=Dom...7=Sab no SQL Server
    -- Ajustamos para 1=Seg...7=Dom (padrão brasileiro/ISO)
    CASE DATEPART(WEEKDAY, d.[Data])
        WHEN 1 THEN 7  -- Domingo → 7
        ELSE DATEPART(WEEKDAY, d.[Data]) - 1
    END AS [DiaSemana],

    -- Nome do dia da semana em português
    CASE DATEPART(WEEKDAY, d.[Data])
        WHEN 1 THEN 'Domingo'
        WHEN 2 THEN 'Segunda-feira'
        WHEN 3 THEN 'Terça-feira'
        WHEN 4 THEN 'Quarta-feira'
        WHEN 5 THEN 'Quinta-feira'
        WHEN 6 THEN 'Sexta-feira'
        WHEN 7 THEN 'Sábado'
    END AS [NomeDiaSemana],

    -- Abreviação (3 letras)
    CASE DATEPART(WEEKDAY, d.[Data])
        WHEN 1 THEN 'Dom' WHEN 2 THEN 'Seg' WHEN 3 THEN 'Ter'
        WHEN 4 THEN 'Qua' WHEN 5 THEN 'Qui' WHEN 6 THEN 'Sex'
        WHEN 7 THEN 'Sáb'
    END AS [NomeDiaSemanaAbrev],

    -- Dia do mês: 1 a 31
    DAY(d.[Data])                   AS [DiaDoMes],

    -- Dia do ano: 1 a 366
    DATEPART(DAYOFYEAR, d.[Data])   AS [DiaDoAno],

    -- Chave numérica de Ano+Mês: útil para ordenação e joins
    -- Ex: janeiro/2018 = 201801, dezembro/2021 = 202112
    YEAR(d.[Data]) * 100 + MONTH(d.[Data]) AS [AnoMes],

    -- Chave de Ano+Trimestre formatada para exibição
    -- Ex: "2021-Q1", "2021-Q2"
    CAST(YEAR(d.[Data]) AS NVARCHAR(4)) + '-Q'
        + CAST(DATEPART(QUARTER, d.[Data]) AS NVARCHAR(1)) AS [AnoTrimestre],

    -- Chave de Ano+Semestre
    CAST(YEAR(d.[Data]) AS NVARCHAR(4)) + '-S'
        + CAST(CASE WHEN MONTH(d.[Data]) <= 6 THEN 1 ELSE 2 END AS NVARCHAR(1)) AS [AnoSemestre],

    -- Primeiro dia do mês (para joins com fMetas que usa o primeiro dia)
    DATEFROMPARTS(YEAR(d.[Data]), MONTH(d.[Data]), 1)  AS [InicioMes],

    -- Último dia do mês: EOMONTH retorna o último dia do mês da data informada
    EOMONTH(d.[Data])               AS [FimMes],

    -- Indicador de dia útil: 1 para Segunda-Sexta, 0 para Sáb-Dom
    -- [REUTILIZAÇÃO]: Adicione lógica de feriados nacionais se necessário
    CASE WHEN DATEPART(WEEKDAY, d.[Data]) IN (1, 7) THEN 0 ELSE 1 END AS [IsDiaUtil],

    -- Indicador de fim de semana
    CASE WHEN DATEPART(WEEKDAY, d.[Data]) IN (1, 7) THEN 1 ELSE 0 END AS [IsFimDeSemana],

    -- Último dia do mês
    CASE WHEN d.[Data] = EOMONTH(d.[Data]) THEN 1 ELSE 0 END AS [IsUltimoDiaMes],

    -- Primeiro dia do mês
    CASE WHEN DAY(d.[Data]) = 1 THEN 1 ELSE 0 END AS [IsPrimeiroDiaMes],

    -- Ano atual: 1 se o ano da data = ano de hoje
    CASE WHEN YEAR(d.[Data]) = YEAR(GETDATE()) THEN 1 ELSE 0 END AS [IsAnoAtual],

    -- Mês atual: 1 se é o mesmo ano e mês de hoje
    CASE WHEN YEAR(d.[Data]) = YEAR(GETDATE())
          AND MONTH(d.[Data]) = MONTH(GETDATE()) THEN 1 ELSE 0 END AS [IsMesAtual],

    -- Trimestre atual
    CASE WHEN YEAR(d.[Data]) = YEAR(GETDATE())
          AND DATEPART(QUARTER, d.[Data]) = DATEPART(QUARTER, GETDATE()) THEN 1 ELSE 0 END
    AS [IsTrimestreAtual]

FROM Datas d
-- OPTION MAXRECURSION 0: remove o limite padrão de 100 recursões
-- necessário para gerar múltiplos anos de datas
OPTION (MAXRECURSION 0);

-- Confirma a quantidade de linhas inseridas
DECLARE @Linhas INT = (SELECT COUNT(*) FROM [dw].[dCalendario]);
PRINT '    dw.dCalendario populada: ' + CAST(@Linhas AS NVARCHAR(10)) + ' datas inseridas.';
PRINT '    Período: ' + CAST(@DataInicio AS NVARCHAR(20)) + ' a ' + CAST(@DataFim AS NVARCHAR(20));
GO

-- =============================================================================
-- VALIDAÇÃO DA DIMENSÃO CALENDÁRIO
-- =============================================================================
PRINT '';
PRINT '=== Validação da dCalendario ===';

-- Verifica se as datas do range de vendas estão presentes
SELECT
    MIN([Data])         AS PrimeiraDta,
    MAX([Data])         AS UltimaDta,
    COUNT(*)            AS TotalDias,
    SUM([IsDiaUtil])    AS DiasUteis,
    SUM([IsFimDeSemana]) AS Findesemana
FROM [dw].[dCalendario];

-- Verifica distribuição por ano
SELECT
    [Ano],
    COUNT(*)            AS Dias,
    SUM([IsDiaUtil])    AS DiasUteis
FROM [dw].[dCalendario]
GROUP BY [Ano]
ORDER BY [Ano];

PRINT '>>> dCalendario populada e validada com sucesso.';

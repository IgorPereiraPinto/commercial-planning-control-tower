-- =============================================================================
-- 00_setup.sql — Script mestre de configuração do banco de dados
-- Commercial Planning Control Tower
-- =============================================================================
--
-- RESPONSABILIDADE:
--   Criar os três schemas do projeto (raw, staging, dw) e executar todos os
--   scripts DDL na ordem correta para montar o ambiente do zero.
--
-- COMO USAR:
--   Opção 1 (recomendado): Execute este arquivo no SSMS ou Azure Data Studio.
--   Ele chama os demais scripts na ordem correta via PRINT para orientação.
--
--   Opção 2 (manual): Execute cada script na ordem abaixo:
--     1. sql/raw/01_create_raw_tables.sql
--     2. sql/staging/02_create_staging_tables.sql
--     3. sql/dw/03_create_dimensions.sql
--     4. sql/dw/04_create_facts.sql
--     5. sql/dw/05_populate_dCalendario.sql
--     6. sql/dw/06_create_indexes.sql
--
-- PRÉ-REQUISITO:
--   O banco de dados já deve existir. Se ainda não existe, execute primeiro:
--   CREATE DATABASE planejamento_comercial;
--
-- [REUTILIZAÇÃO]:
--   Substitua 'planejamento_comercial' pelo nome do banco do novo projeto.
--   Os schemas raw/staging/dw são padrão de mercado — mantenha os nomes.
-- =============================================================================

USE planejamento_comercial;
GO

-- =============================================================================
-- CRIAÇÃO DOS SCHEMAS
-- =============================================================================
-- IF NOT EXISTS garante idempotência: pode rodar múltiplas vezes sem erro.
-- No SQL Server, schemas são namespaces que organizam tabelas por camada.

PRINT '>>> Criando schemas...';

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'raw')
    EXEC('CREATE SCHEMA [raw]');

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'staging')
    EXEC('CREATE SCHEMA [staging]');

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'dw')
    EXEC('CREATE SCHEMA [dw]');

PRINT '    Schemas raw, staging, dw criados/verificados.';
GO

-- =============================================================================
-- ORIENTAÇÃO DE EXECUÇÃO
-- =============================================================================
-- Execute os scripts na seguinte ordem após este arquivo:

PRINT '';
PRINT '=== ORDEM DE EXECUÇÃO DOS SCRIPTS ===';
PRINT '1. sql/raw/01_create_raw_tables.sql';
PRINT '2. sql/staging/02_create_staging_tables.sql';
PRINT '3. sql/dw/03_create_dimensions.sql';
PRINT '4. sql/dw/04_create_facts.sql';
PRINT '5. sql/dw/05_populate_dCalendario.sql';
PRINT '6. sql/dw/06_create_indexes.sql';
PRINT '';
PRINT 'Após rodar os scripts SQL, execute o pipeline Python:';
PRINT '  python -m src.etl.pipeline';

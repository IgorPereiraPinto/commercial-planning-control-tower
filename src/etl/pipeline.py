# =============================================================================
# pipeline.py - Orquestrador do Pipeline ETL
# Planejamento Comercial
# =============================================================================

import sys
import time
from datetime import datetime

from src.config.settings import configure_logging
from src.etl.extract import extract_dimensoes, extract_metas, extract_vendas
from src.etl.transform import transform_dimensoes, transform_metas, transform_vendas
from src.etl.validate import run_all_validations, run_raw_validations

logger = configure_logging()


def _import_load_layers():
    """Importa a camada SQL apenas quando a carga realmente vai acontecer."""
    from src.etl.load import criar_engine, load_raw, load_staging
    from src.etl.load_dw import load_dw

    return criar_engine, load_raw, load_staging, load_dw


def run_pipeline(dry_run: bool = False) -> None:
    """Executa o pipeline ETL completo ou somente a validação em dry-run."""
    inicio = time.time()
    timestamp_inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info("=" * 70)
    logger.info("PIPELINE ETL INICIADO - %s", timestamp_inicio)
    logger.info(
        "Modo: %s",
        "DRY RUN (sem gravacao)" if dry_run else "PRODUCAO (gravacao ativa)",
    )
    logger.info("=" * 70)

    logger.info("\n--- ETAPA 1/7: EXTRACAO ---")
    try:
        t = time.time()
        dimensoes_raw = extract_dimensoes()
        df_vendas_raw = extract_vendas()
        metas_raw = extract_metas()
        logger.info("Extracao concluida em %.1fs.", time.time() - t)
    except FileNotFoundError as e:
        logger.error("ETAPA 1 FALHOU - Arquivo nao encontrado: %s", e)
        logger.error("Verifique os caminhos no arquivo .env e tente novamente.")
        sys.exit(1)
    except Exception as e:
        logger.error("ETAPA 1 FALHOU - Erro inesperado na extracao: %s", e)
        sys.exit(1)

    logger.info("\n--- ETAPA 2/7: VALIDACAO RAW ---")
    try:
        t = time.time()
        relatorio_raw = run_raw_validations(df_vendas_raw, metas_raw)
        logger.info("Validacao raw concluida em %.1fs.", time.time() - t)
        logger.info(relatorio_raw.resumo())
    except ValueError as e:
        logger.error("ETAPA 2 FALHOU - Validacao RAW reprovada: %s", e)
        logger.error(
            "Os arquivos de origem tem problemas estruturais. Corrija os arquivos "
            "Excel antes de reprocessar."
        )
        sys.exit(1)
    except Exception as e:
        logger.error("ETAPA 2 FALHOU - Erro inesperado na validacao raw: %s", e)
        sys.exit(1)

    logger.info("\n--- ETAPA 3/7: TRANSFORMACAO ---")
    try:
        t = time.time()
        df_vendas = transform_vendas(df_vendas_raw)
        dimensoes = transform_dimensoes(dimensoes_raw)
        df_metas = transform_metas(metas_raw)
        logger.info("Transformacao concluida em %.1fs.", time.time() - t)
    except Exception as e:
        logger.error("ETAPA 3 FALHOU - Erro na transformacao: %s", e)
        sys.exit(1)

    logger.info("\n--- ETAPA 4/7: VALIDACAO STAGING ---")
    try:
        t = time.time()
        relatorio_staging = run_all_validations(df_vendas, df_metas, dimensoes)
        logger.info("Validacao staging concluida em %.1fs.", time.time() - t)
        logger.info(relatorio_staging.resumo())
    except ValueError as e:
        logger.error("ETAPA 4 FALHOU - Validacao STAGING reprovada: %s", e)
        logger.error(
            "O dado transformado nao passou nas regras de negocio. Pipeline "
            "interrompido para proteger a integridade do banco."
        )
        sys.exit(1)
    except Exception as e:
        logger.error(
            "ETAPA 4 FALHOU - Erro inesperado na validacao staging: %s",
            e,
        )
        sys.exit(1)

    if dry_run:
        logger.info("\n=== DRY RUN CONCLUIDO - Nenhuma gravacao realizada. ===")
        logger.info(
            "Resumo do que seria carregado:\n"
            "  fVendas:           %s linhas (staging)\n"
            "  fMetas:            %s linhas (staging)\n"
            "  Dimensoes (total): %s linhas\n"
            "  Validacoes RAW:    %s/%s aprovadas\n"
            "  Validacoes STG:    %s/%s aprovadas",
            f"{len(df_vendas):,}",
            f"{len(df_metas):,}",
            f"{sum(len(d) for d in dimensoes.values()):,}",
            relatorio_raw.aprovados,
            relatorio_raw.total,
            relatorio_staging.aprovados,
            relatorio_staging.total,
        )
        return

    try:
        criar_engine, load_raw, load_staging, load_dw = _import_load_layers()
    except ModuleNotFoundError as e:
        logger.error(
            "Dependencias de banco nao estao disponiveis para a carga completa: %s",
            e,
        )
        logger.error(
            "Instale requirements.txt e confirme SQLAlchemy, pyodbc e o driver "
            "ODBC do SQL Server no ambiente."
        )
        sys.exit(1)

    logger.info("\n--- ETAPA 5/7: CARGA NA CAMADA RAW ---")
    try:
        t = time.time()
        engine = criar_engine()
        load_raw(df_vendas_raw, dimensoes_raw, metas_raw, engine)
        logger.info("Carga raw concluida em %.1fs.", time.time() - t)
    except Exception as e:
        logger.error("ETAPA 5 FALHOU - Erro na carga raw: %s", e)
        logger.error(
            "O dado raw nao foi carregado. As etapas 6 e 7 nao serao executadas "
            "para manter consistencia entre camadas."
        )
        sys.exit(1)

    logger.info("\n--- ETAPA 6/7: CARGA NA CAMADA STAGING ---")
    try:
        t = time.time()
        load_staging(df_vendas, dimensoes, df_metas, engine)
        logger.info("Carga staging concluida em %.1fs.", time.time() - t)
    except Exception as e:
        logger.error("ETAPA 6 FALHOU - Erro na carga staging: %s", e)
        logger.error(
            "O raw foi carregado com sucesso, mas o staging falhou. A etapa 7 "
            "nao sera executada."
        )
        sys.exit(1)

    logger.info("\n--- ETAPA 7/7: CARGA NA CAMADA DW ---")
    try:
        t = time.time()
        linhas_dw = load_dw(engine)
        logger.info("Carga DW concluida em %.1fs.", time.time() - t)
    except Exception as e:
        logger.error("ETAPA 7 FALHOU - Erro na carga DW: %s", e)
        logger.error(
            "Verifique se os scripts `sql/sqlserver/03_dw_dimensions.sql` e "
            "`sql/sqlserver/04_dw_facts.sql` foram executados antes da carga."
        )
        sys.exit(1)

    duracao_total = time.time() - inicio
    logger.info("\n" + "=" * 70)
    logger.info("PIPELINE ETL CONCLUIDO COM SUCESSO")
    logger.info("Tempo total: %.1fs (%.1f min)", duracao_total, duracao_total / 60)
    logger.info(
        "Resumo da carga:\n"
        "  raw.fVendas:         %s linhas\n"
        "  staging.fVendas:     %s linhas\n"
        "  staging.fMetas:      %s linhas\n"
        "  dw.fVendas:          %s linhas\n"
        "  dw.fMetas:           %s linhas\n"
        "  Dimensoes (stg):     %s linhas (total)\n"
        "  Validacoes RAW:      %s/%s aprovadas\n"
        "  Validacoes staging:  %s/%s aprovadas",
        f"{len(df_vendas_raw):,}",
        f"{len(df_vendas):,}",
        f"{len(df_metas):,}",
        f"{linhas_dw.get('fVendas', 0):,}",
        f"{linhas_dw.get('fMetas', 0):,}",
        f"{sum(len(d) for d in dimensoes.values()):,}",
        relatorio_raw.aprovados,
        relatorio_raw.total,
        relatorio_staging.aprovados,
        relatorio_staging.total,
    )
    logger.info("=" * 70)


if __name__ == "__main__":
    modo_dry_run = "--dry-run" in sys.argv
    run_pipeline(dry_run=modo_dry_run)

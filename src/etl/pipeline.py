# =============================================================================
# pipeline.py — Orquestrador do Pipeline ETL
# Commercial Planning Control Tower
# =============================================================================
#
# RESPONSABILIDADE:
#   Orquestrar a execução completa do pipeline ETL na sequência correta,
#   tratando erros, logando cada etapa e garantindo rastreabilidade.
#
# FLUXO DO PIPELINE (7 etapas):
#
#   ┌─────────────┐
#   │  1. EXTRACT │ ← Lê os arquivos Excel (raw data)
#   └──────┬──────┘
#          │
#   ┌──────▼──────────┐
#   │ 2. VALIDATE RAW │ ← Valida ESTRUTURA do dado bruto (4 testes)
#   │  (pós-extração) │   colunas, volume, anos de meta, formato wide
#   └──────┬──────────┘
#          │
#   ┌──────▼──────┐
#   │ 3. TRANSFORM│ ← Limpa, tipifica e faz UNPIVOT das metas
#   └──────┬──────┘
#          │
#   ┌──────▼──────────────┐
#   │ 4. VALIDATE STAGING │ ← Valida NEGÓCIO pós-transformação (7 testes)
#   │   (pós-transform)   │   integridade referencial, duplicatas, regras
#   └──────┬──────────────┘
#          │
#          ├── [dry_run=True] → Para aqui. Nenhuma gravação realizada.
#          │
#   ┌──────▼──────┐
#   │ 5. LOAD RAW │ ← Persiste dado bruto na camada raw do SQL Server
#   └──────┬──────┘
#          │
#   ┌──────▼──────────┐
#   │ 6. LOAD STAGING │ ← Persiste dado limpo na camada staging
#   └──────┬──────────┘
#          │
#   ┌──────▼───────┐
#   │  7. LOAD DW  │ ← Popula star schema: staging → dw (INSERT...SELECT)
#   └──────────────┘
#
# POR QUE DUAS VALIDAÇÕES?
#   Validação RAW (etapa 2): detecta problemas na FONTE — layout de Excel
#     alterado, arquivo truncado, ano de meta faltando.
#   Validação STAGING (etapa 4): detecta problemas no CÓDIGO de transformação
#     — UNPIVOT que perdeu linhas, FK que ficou órfã, duplicatas geradas.
#   Duas barreiras de qualidade = muito mais segurança no dado que chega ao DW.
#
# [REUTILIZAÇÃO]:
#   Para rodar o pipeline completo: python -m src.etl.pipeline
#   Para dry run (sem gravação):    python -m src.etl.pipeline --dry-run
# =============================================================================

import logging
import sys
import time
from datetime import datetime

from src.config.settings import configure_logging
from src.etl.extract import extract_dimensoes, extract_vendas, extract_metas
from src.etl.transform import transform_vendas, transform_dimensoes, transform_metas
from src.etl.validate import run_raw_validations, run_all_validations
from src.etl.load import criar_engine, load_raw, load_staging
from src.etl.load_dw import load_dw

logger = configure_logging()


def run_pipeline(dry_run: bool = False) -> None:
    """
    Executa o pipeline ETL completo: extração → validação → transformação
    → validação → carga raw → carga staging → carga DW.

    Args:
        dry_run (bool): Se True, executa extract, validate e transform,
                        mas NÃO grava no banco (etapas 5, 6 e 7 são puladas).
                        Útil para validar dados de origem sem afetar o ambiente.
                        Default: False (executa pipeline completo).

    Raises:
        SystemExit: Em caso de falha crítica em qualquer etapa (código de saída 1).

    Uso:
        python -m src.etl.pipeline            # produção completa
        python -m src.etl.pipeline --dry-run  # só valida, não grava
    """
    inicio = time.time()
    timestamp_inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info("=" * 70)
    logger.info(f"PIPELINE ETL INICIADO — {timestamp_inicio}")
    logger.info(f"Modo: {'DRY RUN (sem gravação)' if dry_run else 'PRODUÇÃO (gravação ativa)'}")
    logger.info("=" * 70)

    # =========================================================================
    # ETAPA 1/7: EXTRAÇÃO
    # =========================================================================
    logger.info("\n--- ETAPA 1/7: EXTRAÇÃO ---")
    try:
        t = time.time()
        dimensoes_raw = extract_dimensoes()
        df_vendas_raw = extract_vendas()
        metas_raw = extract_metas()
        logger.info(f"Extração concluída em {time.time() - t:.1f}s.")

    except FileNotFoundError as e:
        logger.error(f"ETAPA 1 FALHOU — Arquivo não encontrado: {e}")
        logger.error("Verifique os caminhos no arquivo .env e tente novamente.")
        sys.exit(1)

    except Exception as e:
        logger.error(f"ETAPA 1 FALHOU — Erro inesperado na extração: {e}")
        sys.exit(1)

    # =========================================================================
    # ETAPA 2/7: VALIDAÇÃO RAW (estrutura e volume)
    # =========================================================================
    logger.info("\n--- ETAPA 2/7: VALIDAÇÃO RAW ---")
    try:
        t = time.time()
        relatorio_raw = run_raw_validations(df_vendas_raw, metas_raw)
        logger.info(f"Validação raw concluída em {time.time() - t:.1f}s.")
        logger.info(relatorio_raw.resumo())

    except ValueError as e:
        logger.error(f"ETAPA 2 FALHOU — Validação RAW reprovada: {e}")
        logger.error(
            "Os arquivos de origem têm problemas estruturais. "
            "Corrija os arquivos Excel antes de reprocessar."
        )
        sys.exit(1)

    except Exception as e:
        logger.error(f"ETAPA 2 FALHOU — Erro inesperado na validação raw: {e}")
        sys.exit(1)

    # =========================================================================
    # ETAPA 3/7: TRANSFORMAÇÃO
    # =========================================================================
    logger.info("\n--- ETAPA 3/7: TRANSFORMAÇÃO ---")
    try:
        t = time.time()
        df_vendas = transform_vendas(df_vendas_raw)
        dimensoes = transform_dimensoes(dimensoes_raw)
        df_metas = transform_metas(metas_raw)
        logger.info(f"Transformação concluída em {time.time() - t:.1f}s.")

    except Exception as e:
        logger.error(f"ETAPA 3 FALHOU — Erro na transformação: {e}")
        sys.exit(1)

    # =========================================================================
    # ETAPA 4/7: VALIDAÇÃO STAGING (regras de negócio)
    # =========================================================================
    logger.info("\n--- ETAPA 4/7: VALIDAÇÃO STAGING ---")
    try:
        t = time.time()
        relatorio_staging = run_all_validations(df_vendas, df_metas, dimensoes)
        logger.info(f"Validação staging concluída em {time.time() - t:.1f}s.")
        logger.info(relatorio_staging.resumo())

    except ValueError as e:
        logger.error(f"ETAPA 4 FALHOU — Validação STAGING reprovada: {e}")
        logger.error(
            "O dado transformado não passou nas regras de negócio. "
            "Pipeline interrompido para proteger a integridade do banco."
        )
        sys.exit(1)

    except Exception as e:
        logger.error(f"ETAPA 4 FALHOU — Erro inesperado na validação staging: {e}")
        sys.exit(1)

    # =========================================================================
    # DRY RUN — Para aqui sem gravar no banco
    # =========================================================================
    if dry_run:
        logger.info("\n=== DRY RUN CONCLUÍDO — Nenhuma gravação realizada. ===")
        logger.info(
            f"Resumo do que seria carregado:\n"
            f"  fVendas:           {len(df_vendas):,} linhas (staging)\n"
            f"  fMetas:            {len(df_metas):,} linhas (staging)\n"
            f"  Dimensões (total): {sum(len(d) for d in dimensoes.values()):,} linhas\n"
            f"  Validações RAW:    {relatorio_raw.aprovados}/{relatorio_raw.total} aprovadas\n"
            f"  Validações STG:    {relatorio_staging.aprovados}/{relatorio_staging.total} aprovadas"
        )
        return

    # =========================================================================
    # ETAPA 5/7: CARGA NA CAMADA RAW
    # =========================================================================
    logger.info("\n--- ETAPA 5/7: CARGA NA CAMADA RAW ---")
    try:
        t = time.time()
        engine = criar_engine()
        load_raw(df_vendas_raw, dimensoes_raw, metas_raw, engine)
        logger.info(f"Carga raw concluída em {time.time() - t:.1f}s.")

    except Exception as e:
        logger.error(f"ETAPA 5 FALHOU — Erro na carga raw: {e}")
        logger.error(
            "O dado raw não foi carregado. As etapas 6 e 7 (staging e DW) "
            "NÃO serão executadas para manter consistência entre camadas. "
            "Investigue e reprocesse."
        )
        sys.exit(1)

    # =========================================================================
    # ETAPA 6/7: CARGA NA CAMADA STAGING
    # =========================================================================
    logger.info("\n--- ETAPA 6/7: CARGA NA CAMADA STAGING ---")
    try:
        t = time.time()
        load_staging(df_vendas, dimensoes, df_metas, engine)
        logger.info(f"Carga staging concluída em {time.time() - t:.1f}s.")

    except Exception as e:
        logger.error(f"ETAPA 6 FALHOU — Erro na carga staging: {e}")
        logger.error(
            "O raw foi carregado com sucesso, mas o staging falhou. "
            "A etapa 7 (DW) NÃO será executada — staging inconsistente. "
            "É seguro reprocessar a partir da etapa 6."
        )
        sys.exit(1)

    # =========================================================================
    # ETAPA 7/7: CARGA NA CAMADA DW (staging → dw, INSERT...SELECT)
    # =========================================================================
    logger.info("\n--- ETAPA 7/7: CARGA NA CAMADA DW ---")
    try:
        t = time.time()
        linhas_dw = load_dw(engine)
        logger.info(f"Carga DW concluída em {time.time() - t:.1f}s.")

    except Exception as e:
        logger.error(f"ETAPA 7 FALHOU — Erro na carga DW: {e}")
        logger.error(
            "Raw e staging foram carregados com sucesso, mas a carga DW falhou. "
            "Verifique se os scripts sql/dw/03 e 04 foram executados "
            "(tabelas dw.* precisam existir antes de rodar o pipeline). "
            "É seguro reprocessar apenas a etapa 7 sem re-executar 5 e 6."
        )
        sys.exit(1)

    # =========================================================================
    # CONCLUSÃO
    # =========================================================================
    duracao_total = time.time() - inicio

    logger.info("\n" + "=" * 70)
    logger.info("PIPELINE ETL CONCLUÍDO COM SUCESSO")
    logger.info(f"Tempo total: {duracao_total:.1f}s ({duracao_total/60:.1f} min)")
    logger.info(
        f"Resumo da carga:\n"
        f"  raw.fVendas:         {len(df_vendas_raw):,} linhas\n"
        f"  staging.fVendas:     {len(df_vendas):,} linhas\n"
        f"  staging.fMetas:      {len(df_metas):,} linhas\n"
        f"  dw.fVendas:          {linhas_dw.get('fVendas', 0):,} linhas\n"
        f"  dw.fMetas:           {linhas_dw.get('fMetas', 0):,} linhas\n"
        f"  Dimensões (stg):     {sum(len(d) for d in dimensoes.values()):,} linhas (total)\n"
        f"  Validações RAW:      {relatorio_raw.aprovados}/{relatorio_raw.total} aprovadas\n"
        f"  Validações staging:  {relatorio_staging.aprovados}/{relatorio_staging.total} aprovadas"
    )
    logger.info("=" * 70)


# =============================================================================
# PONTO DE ENTRADA PARA EXECUÇÃO DIRETA
# =============================================================================
# Permite rodar o pipeline com:
#   python -m src.etl.pipeline
#   python -m src.etl.pipeline --dry-run

if __name__ == "__main__":
    modo_dry_run = "--dry-run" in sys.argv
    run_pipeline(dry_run=modo_dry_run)

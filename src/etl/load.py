# =============================================================================
# load.py — Camada de Carga (L do ETL)
# Planejamento Comercial
# =============================================================================
#
# RESPONSABILIDADE:
#   Receber os DataFrames transformados e validados e persistí-los no
#   SQL Server, nas camadas raw e staging, conforme a estratégia definida.
#
# ESTRATÉGIA DE CARGA (truncate-and-load):
#   Para este projeto, utilizamos truncate + insert completo a cada execução.
#   Isso é justificado porque:
#   1. O volume é pequeno (~20K linhas) — a recarga completa é rápida
#   2. Os arquivos Excel são a fonte de verdade — não há risco de perder dados
#   3. Simplifica enormemente a lógica de deduplicação e controle de estado
#
#   Em projetos com maior volume ou dados em streaming, considerar:
#   - Carga incremental por data (append de novas linhas)
#   - Merge/upsert por chave natural
#   - SCD Type 2 para dimensões históricas
#
# CAMADAS CARREGADAS NESTE MÓDULO:
#   - raw.*     → dado bruto sem transformação (espelho direto do Excel)
#   - staging.* → dado limpo e tipado (saída de transform.py)
#
# [REUTILIZAÇÃO]:
#   - Ajuste DB_SERVER, DB_DATABASE e credenciais no .env
#   - Os nomes das tabelas seguem o padrão schema.nome_tabela
#   - Se a estratégia mudar para append, altere LOAD_STRATEGY no .env
# =============================================================================

import logging
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config.settings import (
    DB_SCHEMA_RAW,
    DB_SCHEMA_STAGING,
    CHUNK_SIZE,
    LOAD_STRATEGY,
    configure_logging,
    get_connection_string,
)

logger = configure_logging()


# =============================================================================
# CONEXÃO COM O BANCO
# =============================================================================

def criar_engine() -> Engine:
    """
    Cria e retorna o engine de conexão SQLAlchemy para o SQL Server.

    O engine é um objeto que gerencia o pool de conexões com o banco.
    Criar uma única instância e reutilizá-la é mais eficiente do que
    abrir uma nova conexão a cada operação.

    Returns:
        Engine: Engine SQLAlchemy conectado ao SQL Server.

    Raises:
        Exception: Se a conexão falhar (servidor offline, credenciais erradas, etc.)

    [REUTILIZAÇÃO]:
        Ajuste as variáveis de conexão no .env — esta função não muda.
    """
    conn_str = get_connection_string()
    logger.info("Criando engine de conexão com SQL Server...")

    try:
        # fast_executemany=True: otimização para inserções em lote via pyodbc
        # Reduz significativamente o tempo de carga ao usar batch inserts
        # ao invés de uma inserção por linha
        engine = create_engine(
            conn_str,
            connect_args={"fast_executemany": True},
            # pool_pre_ping=True verifica se a conexão ainda está ativa
            # antes de cada operação — evita erros de "connection reset"
            pool_pre_ping=True,
        )

        # Testa a conexão com uma query simples antes de retornar
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        logger.info("Conexão com SQL Server estabelecida com sucesso.")
        return engine

    except Exception as e:
        logger.error(f"Falha ao conectar com SQL Server: {e}")
        logger.error(
            "Verifique: servidor online, driver ODBC instalado, "
            "credenciais corretas no .env e permissões no banco."
        )
        raise


def garantir_schema(engine: Engine, schema: str) -> None:
    """
    Cria o schema no SQL Server se ele ainda não existir.

    No SQL Server, schemas são namespaces que organizam tabelas.
    Equivale a "pastas" dentro do banco: raw.fVendas, staging.fVendas, etc.
    O schema 'dbo' é o default; raw, staging e dw são criados por este projeto.

    Args:
        engine (Engine): Engine de conexão.
        schema (str): Nome do schema a criar (ex: "raw", "staging", "dw").
    """
    # IF NOT EXISTS garante idempotência — pode rodar múltiplas vezes sem erro
    sql = text(f"""
        IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = '{schema}')
        BEGIN
            EXEC('CREATE SCHEMA [{schema}]')
        END
    """)
    with engine.begin() as conn:
        conn.execute(sql)
    logger.debug(f"Schema '{schema}' verificado/criado.")


# =============================================================================
# FUNÇÕES DE CARGA
# =============================================================================

def carregar_dataframe(
    df: pd.DataFrame,
    nome_tabela: str,
    schema: str,
    engine: Engine,
    estrategia: str = LOAD_STRATEGY,
) -> int:
    """
    Carrega um DataFrame em uma tabela do SQL Server.

    Estratégias disponíveis:
    - "truncate": limpa a tabela e recarrega (padrão do projeto)
    - "append": adiciona novas linhas sem remover as existentes
    - "replace": recria a tabela completamente (inclui estrutura)

    Args:
        df (pd.DataFrame): DataFrame a ser carregado.
        nome_tabela (str): Nome da tabela no banco (sem schema).
        schema (str): Schema de destino (ex: "raw", "staging").
        engine (Engine): Engine SQLAlchemy.
        estrategia (str): "truncate", "append" ou "replace".

    Returns:
        int: Número de linhas carregadas.

    Raises:
        ValueError: Se a estratégia de carga for inválida.
        Exception: Se ocorrer erro na carga.

    [REUTILIZAÇÃO]:
        Para projetos com carga incremental, altere estrategia="append"
        e adicione lógica de deduplicação antes de chamar esta função.
    """
    if df.empty:
        logger.warning(f"DataFrame vazio — nada carregado em {schema}.{nome_tabela}.")
        return 0

    estrategias_validas = {"truncate", "append", "replace"}
    if estrategia not in estrategias_validas:
        raise ValueError(
            f"Estratégia '{estrategia}' inválida. Use: {estrategias_validas}"
        )

    logger.info(
        f"Carregando {len(df):,} linhas → {schema}.{nome_tabela} "
        f"(estratégia: {estrategia}, chunks de {CHUNK_SIZE})"
    )

    try:
        # Para truncate, primeiro truncamos (mais rápido que DELETE)
        # depois usamos if_exists="append" para não recriar a estrutura
        if estrategia == "truncate":
            _truncar_tabela(engine, nome_tabela, schema)
            if_exists_value = "append"
        elif estrategia == "append":
            if_exists_value = "append"
        else:  # replace
            if_exists_value = "replace"

        # df.to_sql usa SQLAlchemy para inserir os dados
        # chunksize=CHUNK_SIZE: insere em lotes de 500 linhas
        # index=False: não grava o índice do pandas como coluna no banco
        df.to_sql(
            name=nome_tabela,
            con=engine,
            schema=schema,
            if_exists=if_exists_value,
            index=False,
            chunksize=CHUNK_SIZE,
            # method="multi": usa INSERT com múltiplas tuplas por statement
            # Mais eficiente que INSERT linha a linha
            method="multi",
        )

        linhas_carregadas = len(df)
        logger.info(f"  Carga concluída: {linhas_carregadas:,} linhas em {schema}.{nome_tabela}.")
        return linhas_carregadas

    except Exception as e:
        logger.error(f"Erro ao carregar {schema}.{nome_tabela}: {e}")
        raise


def _truncar_tabela(engine: Engine, nome_tabela: str, schema: str) -> None:
    """
    Trunca (limpa completamente) uma tabela SQL Server se ela existir.

    TRUNCATE vs DELETE:
    - TRUNCATE é muito mais rápido (não loga linha a linha, não ativa triggers)
    - DELETE permite WHERE clause; TRUNCATE limpa tudo
    - Para este projeto (recarga completa), TRUNCATE é sempre preferível

    Args:
        engine (Engine): Engine de conexão.
        nome_tabela (str): Nome da tabela.
        schema (str): Schema da tabela.
    """
    # Verifica se a tabela existe antes de tentar truncar
    # (na primeira execução, a tabela ainda não existe)
    sql_verifica = text("""
        SELECT COUNT(1)
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :tabela
    """)

    sql_trunca = text(f"TRUNCATE TABLE [{schema}].[{nome_tabela}]")

    with engine.begin() as conn:
        existe = conn.execute(
            sql_verifica,
            {"schema": schema, "tabela": nome_tabela}
        ).scalar()

        if existe:
            conn.execute(sql_trunca)
            logger.debug(f"Tabela {schema}.{nome_tabela} truncada.")


# =============================================================================
# CARGA COMPLETA DO PIPELINE
# =============================================================================

def load_raw(
    df_vendas_raw: pd.DataFrame,
    dimensoes_raw: dict[str, pd.DataFrame],
    metas_raw: dict[int, pd.DataFrame],
    engine: Engine,
) -> None:
    """
    Carrega os DataFrames brutos (sem transformação) na camada raw do SQL Server.

    A camada raw é o espelho fiel dos arquivos Excel — serve como "backup"
    digital das fontes e ponto de reprocessamento seguro.

    Args:
        df_vendas_raw (pd.DataFrame): Vendas brutas de extract_vendas().
        dimensoes_raw (dict[str, pd.DataFrame]): Dimensões brutas de extract_dimensoes().
        metas_raw (dict[int, pd.DataFrame]): Metas brutas de extract_metas().
        engine (Engine): Engine de conexão.
    """
    logger.info("=== Iniciando carga na camada RAW ===")
    garantir_schema(engine, DB_SCHEMA_RAW)

    # Carrega fVendas bruta
    carregar_dataframe(df_vendas_raw, "fVendas", DB_SCHEMA_RAW, engine)

    # Carrega cada dimensão bruta
    # [REUTILIZAÇÃO]: Os nomes das tabelas seguem o padrão "d" + nome_chave
    mapa_tabelas_dim = {
        "produtos": "dProdutos",
        "vendedor": "dVendedor",
        "clientes": "dClientes",
        "cidade": "dCidade",
        "unidades": "dUnidades",
        "status": "dStatus",
        "pagamento": "dPagamento",
    }

    for chave, nome_tabela in mapa_tabelas_dim.items():
        if chave in dimensoes_raw:
            carregar_dataframe(dimensoes_raw[chave], nome_tabela, DB_SCHEMA_RAW, engine)

    # Carrega cada arquivo de meta como tabela separada na raw
    # Ex: raw.fMetas_2018, raw.fMetas_2019, etc.
    for ano, df_meta in metas_raw.items():
        carregar_dataframe(df_meta, f"fMetas_{ano}", DB_SCHEMA_RAW, engine)

    logger.info("=== Carga na camada RAW concluída ===")


def load_staging(
    df_vendas: pd.DataFrame,
    dimensoes: dict[str, pd.DataFrame],
    df_metas: pd.DataFrame,
    engine: Engine,
) -> None:
    """
    Carrega os DataFrames transformados e validados na camada staging.

    A camada staging contém dados limpos e tipados, prontos para serem
    consumidos pela camada dw (star schema) ou diretamente pelo Power BI
    em cenários mais simples.

    Args:
        df_vendas (pd.DataFrame): Vendas transformadas de transform_vendas().
        dimensoes (dict[str, pd.DataFrame]): Dimensões transformadas.
        df_metas (pd.DataFrame): Metas no formato long de transform_metas().
        engine (Engine): Engine de conexão.
    """
    logger.info("=== Iniciando carga na camada STAGING ===")
    garantir_schema(engine, DB_SCHEMA_STAGING)

    # Carrega fVendas transformada
    carregar_dataframe(df_vendas, "fVendas", DB_SCHEMA_STAGING, engine)

    # Carrega dimensões transformadas
    mapa_tabelas_dim = {
        "produtos": "dProdutos",
        "vendedor": "dVendedor",
        "clientes": "dClientes",
        "cidade": "dCidade",
        "unidades": "dUnidades",
        "status": "dStatus",
        "pagamento": "dPagamento",
    }

    for chave, nome_tabela in mapa_tabelas_dim.items():
        if chave in dimensoes:
            carregar_dataframe(dimensoes[chave], nome_tabela, DB_SCHEMA_STAGING, engine)

    # Carrega metas consolidadas (todos os anos em uma tabela no formato long)
    carregar_dataframe(df_metas, "fMetas", DB_SCHEMA_STAGING, engine)

    logger.info("=== Carga na camada STAGING concluída ===")

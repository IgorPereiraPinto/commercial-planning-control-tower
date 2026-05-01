# =============================================================================
# load_dw.py — Carga da Camada DW (staging → dw)
# Planejamento Comercial
# =============================================================================
#
# RESPONSABILIDADE:
#   Ler os dados da camada staging (já limpos e validados) e populá-los
#   nas tabelas do Data Warehouse (schema dw), que segue o star schema
#   de Kimball com dois fatos e oito dimensões.
#
# PRÉ-REQUISITOS:
#   1. Os scripts SQL 03_create_dimensions.sql e 04_create_facts.sql devem
#      ter sido executados — as tabelas dw.* precisam existir.
#   2. O script 05_populate_dCalendario.sql deve ter sido executado —
#      dCalendario é populado por SQL direto, não por este módulo Python.
#   3. A camada staging deve ter sido carregada com sucesso (load_staging).
#
# ESTRATÉGIA DE CARGA:
#   INSERT...SELECT via SQL Server — o dado vai diretamente de staging para
#   dw sem passar pelo Python. Isso é mais eficiente do que read_sql + to_sql
#   para volumes maiores, e mantém a lógica de transformação DW no SQL.
#
#   Dimensões com lógica extra (dUnidades, dStatus, dPagamento) usam CASE
#   WHEN dentro do SELECT para derivar colunas calculadas no banco.
#
# COLUNAS COMPUTADAS (PERSISTED):
#   dw.fVendas tem [Margem Bruta] e [Resultado Liquido] como colunas PERSISTED.
#   O SQL Server as calcula automaticamente no INSERT — não precisam ser
#   incluídas no INSERT...SELECT.
#
# [REUTILIZAÇÃO]:
#   - Ajuste os mapeamentos de colunas abaixo se o schema mudar.
#   - Para adicionar uma nova dimensão, copie o padrão de _insert_dimensao().
#   - Para projetos sem SQL Server, substitua os text() por pandas to_sql().
# =============================================================================

import logging
import time

from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.config.settings import (
    DB_SCHEMA_STAGING,
    DB_SCHEMA_DW,
    configure_logging,
)

logger = configure_logging()

# Alias para clareza nos f-strings das queries
_S = DB_SCHEMA_STAGING  # "staging"
_D = DB_SCHEMA_DW       # "dw"


# =============================================================================
# QUERIES INSERT...SELECT: DIMENSÕES
# =============================================================================
# Cada query trunca a tabela dw e recarrega a partir do staging.
# Estratégia truncate + insert (mesma lógica usada no load_staging).
#
# Nota sobre TRUNCATE em tabelas com FK:
#   SQL Server não permite TRUNCATE se houver constraints de FK habilitadas.
#   Neste projeto, as FKs são documentadas mas não criadas como constraints
#   no DDL (padrão Power BI), então TRUNCATE funciona sem problemas.
# =============================================================================

_SQL_DIM_PRODUTOS = f"""
    TRUNCATE TABLE [{_D}].[dProdutos];
    INSERT INTO [{_D}].[dProdutos]
        ([Id Produto], [Produto], [Categoria], [Subcategoria], [Marca])
    SELECT
        [Id Produto], [Produto], [Categoria], [Subcategoria], [Marca]
    FROM [{_S}].[dProdutos];
"""

_SQL_DIM_VENDEDOR = f"""
    TRUNCATE TABLE [{_D}].[dVendedor];
    INSERT INTO [{_D}].[dVendedor]
        ([Id Vendedor], [Vendedor], [URL Foto], [Gerente])
    SELECT
        [Id Vendedor], [Vendedor], [URL Foto], [Gerente]
    FROM [{_S}].[dVendedor];
"""

_SQL_DIM_CLIENTES = f"""
    TRUNCATE TABLE [{_D}].[dClientes];
    INSERT INTO [{_D}].[dClientes]
        ([Id Cliente], [Cliente], [Id Cidade])
    SELECT
        [Id Cliente], [Cliente], [Id Cidade]
    FROM [{_S}].[dClientes];
"""

_SQL_DIM_CIDADE = f"""
    TRUNCATE TABLE [{_D}].[dCidade];
    INSERT INTO [{_D}].[dCidade]
        ([Id Cidade], [Cidade], [UF], [Estado])
    SELECT
        [Id Cidade], [Cidade], [UF], [Estado]
    FROM [{_S}].[dCidade];
"""

_SQL_DIM_UNIDADES = f"""
    TRUNCATE TABLE [{_D}].[dUnidades];
    INSERT INTO [{_D}].[dUnidades]
        ([Id Unidade], [Unidade], [Tipo])
    SELECT
        [Id Unidade],
        [Unidade],
        -- Deriva o Tipo a partir do nome da unidade
        -- [REUTILIZAÇÃO]: Ajuste os CASE WHEN conforme os nomes do novo projeto
        CASE
            WHEN [Unidade] LIKE '%Matriz%' THEN 'Matriz'
            WHEN [Unidade] LIKE '%Filial%' THEN 'Filial'
            ELSE 'Outros'
        END AS [Tipo]
    FROM [{_S}].[dUnidades];
"""

_SQL_DIM_STATUS = f"""
    TRUNCATE TABLE [{_D}].[dStatus];
    INSERT INTO [{_D}].[dStatus]
        ([Id Status], [Status], [Conta Para Faturamento])
    SELECT
        [Id Status],
        [Status],
        -- Pedidos "Válidas" entram no faturamento; outros são excluídos
        -- [REUTILIZAÇÃO]: Ajuste a regra de status conforme o negócio do projeto
        CASE WHEN [Status] = 'Válidas' THEN 1 ELSE 0 END AS [Conta Para Faturamento]
    FROM [{_S}].[dStatus];
"""

_SQL_DIM_PAGAMENTO = f"""
    TRUNCATE TABLE [{_D}].[dPagamento];
    INSERT INTO [{_D}].[dPagamento]
        ([Id Pagamento], [Forma de Pagamento], [Tipo])
    SELECT
        [Id Pagamento],
        [Forma de Pagamento],
        -- Classifica formas de pagamento em tipos para análise de mix financeiro
        -- [REUTILIZAÇÃO]: Ajuste as formas de pagamento e tipos do novo projeto
        CASE
            WHEN [Forma de Pagamento] IN ('Débito', 'Boleto') THEN 'À Vista'
            WHEN [Forma de Pagamento] = 'Crédito'            THEN 'Parcelado'
            WHEN [Forma de Pagamento] = 'Paypal'             THEN 'Digital'
            ELSE 'Outros'
        END AS [Tipo]
    FROM [{_S}].[dPagamento];
"""


# =============================================================================
# QUERIES INSERT...SELECT: FATOS
# =============================================================================

_SQL_FATO_VENDAS = f"""
    TRUNCATE TABLE [{_D}].[fVendas];
    INSERT INTO [{_D}].[fVendas] (
        [Data], [Data Envio], [Num Venda],
        [Id Produto], [Id Vendedor], [Id Cliente],
        [Id Unidade], [Id Status], [Id Pgto],
        [Qtde],
        [Valor Unit], [Custo Unit], [Despesa Unit], [Impostos Unit], [Comissão Unit],
        [Faturamento Total], [Custo Total]
        -- [Margem Bruta] e [Resultado Liquido] são colunas PERSISTED:
        -- calculadas automaticamente pelo SQL Server no INSERT.
        -- [_dw_loaded_at] e [_dw_source] têm DEFAULT definido no DDL.
    )
    SELECT
        CAST([Data]       AS DATE),
        CAST([Data Envio] AS DATE),
        [Num Venda],
        [Id Produto], [Id Vendedor], [Id Cliente],
        [Id Unidade], [Id Status], [Id Pgto],
        [Qtde],
        [Valor Unit], [Custo Unit], [Despesa Unit], [Impostos Unit], [Comissão Unit],
        [Faturamento Total], [Custo Total]
    FROM [{_S}].[fVendas];
"""

_SQL_FATO_METAS = f"""
    TRUNCATE TABLE [{_D}].[fMetas];
    INSERT INTO [{_D}].[fMetas]
        ([Data Meta], [Id Vendedor], [Ano], [Mes], [Valor Meta])
        -- [_dw_loaded_at] e [_dw_source] têm DEFAULT definido no DDL.
    SELECT
        CAST([Data Meta] AS DATE),
        [Id Vendedor],
        [Ano],
        [Mes],
        [Valor Meta]
    FROM [{_S}].[fMetas];
"""


# =============================================================================
# MAPA DE EXECUÇÃO
# =============================================================================
# Ordem de carga: dimensões primeiro, fatos depois.
# Dimensões precisam estar populadas antes dos fatos por causa dos JOINs
# que o Power BI faz implicitamente via relacionamentos.
#
# [REUTILIZAÇÃO]: Adicione entradas neste dict para incluir novas tabelas.
# =============================================================================

_DW_LOAD_SEQUENCE: list[tuple[str, str]] = [
    # (nome_tabela, query_sql)
    ("dProdutos",  _SQL_DIM_PRODUTOS),
    ("dVendedor",  _SQL_DIM_VENDEDOR),
    ("dClientes",  _SQL_DIM_CLIENTES),
    ("dCidade",    _SQL_DIM_CIDADE),
    ("dUnidades",  _SQL_DIM_UNIDADES),
    ("dStatus",    _SQL_DIM_STATUS),
    ("dPagamento", _SQL_DIM_PAGAMENTO),
    ("fVendas",    _SQL_FATO_VENDAS),
    ("fMetas",     _SQL_FATO_METAS),
]


# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def load_dw(engine: Engine) -> dict[str, int]:
    """
    Popula todas as tabelas do Data Warehouse a partir da camada staging.

    Executa INSERT...SELECT direto no SQL Server para cada tabela do DW,
    na ordem correta (dimensões → fatos). Usa truncate + insert completo
    a cada execução (mesma estratégia do restante do pipeline).

    Pré-condições:
        - Tabelas dw.* devem existir (criadas pelos scripts
          sql/sqlserver/03_dw_dimensions.sql e 04_dw_facts.sql).
        - dCalendario deve ter sido populado (script sql/sqlserver/05_calendario.sql).
        - staging.* deve ter sido carregado com sucesso nesta execução.

    Args:
        engine: Engine SQLAlchemy conectado ao banco planejamento_comercial.

    Returns:
        dict[str, int]: Mapa {nome_tabela: linhas_carregadas} para o log
                        do pipeline. Linhas são contadas via SELECT COUNT(*).

    Raises:
        Exception: Se qualquer INSERT falhar. O pipeline interrompe e o
                   staging permanece íntegro para reprocessamento.

    [REUTILIZAÇÃO]:
        Para adicionar uma nova tabela DW, adicione a query em
        _DW_LOAD_SEQUENCE e execute este função normalmente.
    """
    logger.info("=== Iniciando carga na camada DW (staging → dw) ===")
    t_inicio = time.time()
    linhas_por_tabela: dict[str, int] = {}

    for nome_tabela, sql_query in _DW_LOAD_SEQUENCE:
        t = time.time()
        logger.info(f"  Carregando dw.{nome_tabela}...")

        try:
            with engine.begin() as conn:
                # Executa TRUNCATE + INSERT em uma única transação
                # engine.begin() faz commit automático ao sair do bloco
                # ou rollback em caso de exceção
                conn.execute(text(sql_query))

            # Conta as linhas carregadas para o relatório final
            with engine.connect() as conn:
                resultado = conn.execute(
                    text(f"SELECT COUNT(*) FROM [{_D}].[{nome_tabela}]")
                )
                linhas = resultado.scalar() or 0

            linhas_por_tabela[nome_tabela] = linhas
            logger.info(
                f"  dw.{nome_tabela}: {linhas:,} linhas "
                f"({time.time() - t:.1f}s)"
            )

        except Exception as e:
            logger.error(f"  ERRO ao carregar dw.{nome_tabela}: {e}")
            logger.error(
                "  O staging permanece íntegro. Verifique se as tabelas dw.* "
                "existem (scripts sql/sqlserver/03_dw_dimensions.sql e "
                "04_dw_facts.sql devem ter sido executados)."
            )
            raise

    duracao = time.time() - t_inicio
    total_linhas = sum(linhas_por_tabela.values())

    logger.info(
        f"=== Carga DW concluída: {total_linhas:,} linhas em "
        f"{len(_DW_LOAD_SEQUENCE)} tabelas ({duracao:.1f}s) ==="
    )
    return linhas_por_tabela

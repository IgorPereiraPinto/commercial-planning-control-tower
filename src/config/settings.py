# =============================================================================
# settings.py — Configurações centrais do projeto
# Commercial Planning Control Tower
# =============================================================================
#
# RESPONSABILIDADE:
#   Carregar todas as variáveis de ambiente do arquivo .env e expor
#   como objetos Python tipados para o restante do projeto.
#
#   Centralizar a configuração aqui tem três vantagens:
#   1. Qualquer mudança de configuração afeta apenas este arquivo.
#   2. O restante do código não precisa conhecer os nomes das variáveis de env.
#   3. Facilita testes — podemos mockar apenas este módulo.
#
# [REUTILIZAÇÃO]:
#   Para adaptar a um novo projeto, ajuste somente o arquivo .env.
#   As constantes aqui permanecem as mesmas — apenas os valores mudam.
# =============================================================================

import os
import logging
from pathlib import Path

# -----------------------------------------------------------------------------
# Carrega o arquivo .env da raiz do projeto
# -----------------------------------------------------------------------------
# Path(__file__) aponta para este arquivo (settings.py)
# .parent.parent.parent sobe 3 níveis: config/ → src/ → raiz do projeto
ROOT_DIR = Path(__file__).parent.parent.parent

# python-dotenv é opcional: se não estiver instalado (ex: ambiente de CI sem
# o pacote, ou testes rodando antes do pip install), o código não quebra.
# Nesse caso, as variáveis de ambiente devem ser injetadas via os.environ
# diretamente (ex: conftest.py nos testes, ou variáveis do sistema em produção).
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env", override=False)
except ImportError:
    pass  # sem dotenv: usa os.environ + defaults definidos em cada os.getenv()


# =============================================================================
# CAMINHOS DAS FONTES DE DADOS
# =============================================================================
# Usamos Path() para compatibilidade entre Windows, Mac e Linux.
# Isso evita problemas com \ vs / nos caminhos.

# Caminho do arquivo de dimensões (7 abas: dProdutos, dVendedor, etc.)
PATH_DIMENSOES: Path = ROOT_DIR / os.getenv("DATA_PATH_DIMENSOES", "data/raw/Dimensoes.xlsx")

# Caminho do arquivo de vendas (fVendas — 20.004 transações)
PATH_VENDAS: Path = ROOT_DIR / os.getenv("DATA_PATH_VENDAS", "data/raw/Vendas.xlsx")

# Diretório onde estão os arquivos de meta anuais (Meta_2018.xlsx, etc.)
PATH_METAS_DIR: Path = ROOT_DIR / os.getenv("DATA_PATH_METAS_DIR", "data/raw/")

# Lista de anos disponíveis nos arquivos de meta
# Os anos vêm do .env como string separada por vírgula ("2018,2019,2020,2021")
# Convertemos para lista de inteiros para usar em loops e nomes de arquivo.
# [REUTILIZAÇÃO]: Ajuste no .env quando o projeto tiver anos diferentes.
METAS_ANOS: list[int] = [
    int(ano.strip())
    for ano in os.getenv("METAS_ANOS", "2018,2019,2020,2021").split(",")
]


# =============================================================================
# CONFIGURAÇÕES DO BANCO DE DADOS (SQL SERVER)
# =============================================================================

DB_SERVER: str = os.getenv("DB_SERVER", "localhost\\SQLEXPRESS")
DB_DATABASE: str = os.getenv("DB_DATABASE", "planejamento_comercial")
DB_TRUSTED_CONNECTION: str = os.getenv("DB_TRUSTED_CONNECTION", "yes")
DB_USER: str = os.getenv("DB_USER", "")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
DB_DRIVER: str = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# Schemas SQL Server
# [REUTILIZAÇÃO]: Ajuste os nomes dos schemas conforme padrão do novo projeto.
DB_SCHEMA_RAW: str = os.getenv("DB_SCHEMA_RAW", "raw")
DB_SCHEMA_STAGING: str = os.getenv("DB_SCHEMA_STAGING", "staging")
DB_SCHEMA_DW: str = os.getenv("DB_SCHEMA_DW", "dw")


def get_connection_string() -> str:
    """
    Monta e retorna a string de conexão para o SQL Server.

    Suporta dois modos de autenticação:
    - Trusted Connection (Windows Authentication): padrão para ambientes
      corporativos onde o usuário está no domínio. Mais seguro pois não
      exige senha no .env.
    - SQL Authentication (usuário + senha): para ambientes cloud, Azure
      SQL ou fora do domínio Windows.

    Returns:
        str: String de conexão no formato SQLAlchemy (mssql+pyodbc).

    [REUTILIZAÇÃO]:
        Ajuste DB_SERVER, DB_DATABASE e modo de autenticação no .env.
        O código desta função não precisa mudar.
    """
    # Encoda o driver para uso na URL (espaços viram %20, etc.)
    driver_encoded = DB_DRIVER.replace(" ", "+")

    if DB_TRUSTED_CONNECTION.lower() == "yes":
        # Autenticação Windows — não precisa de usuário/senha no código
        return (
            f"mssql+pyodbc://{DB_SERVER}/{DB_DATABASE}"
            f"?driver={driver_encoded}"
            f"&trusted_connection=yes"
        )
    else:
        # Autenticação SQL — usuário e senha vêm do .env (nunca hardcoded)
        if not DB_USER or not DB_PASSWORD:
            raise ValueError(
                "DB_USER e DB_PASSWORD são obrigatórios quando "
                "DB_TRUSTED_CONNECTION != yes. Verifique o arquivo .env."
            )
        return (
            f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}"
            f"@{DB_SERVER}/{DB_DATABASE}"
            f"?driver={driver_encoded}"
        )


# =============================================================================
# CONFIGURAÇÕES DO ETL
# =============================================================================

# Estratégia de carga: "truncate" (limpa e recarrega) ou "append" (adiciona)
# Para este projeto, truncate é suficiente pois o volume é pequeno e
# os arquivos Excel são a fonte de verdade. Em projetos maiores com
# dados em streaming, considere append com deduplicação posterior.
LOAD_STRATEGY: str = os.getenv("LOAD_STRATEGY", "truncate")

# Tamanho do lote para inserção em banco. Inserir linha a linha é lento;
# inserir em chunks de 500 linhas é um bom equilíbrio entre velocidade
# e consumo de memória para o volume deste projeto (20K linhas).
CHUNK_SIZE: int = 500


# =============================================================================
# CONFIGURAÇÕES DE LOG
# =============================================================================

LOG_LEVEL_STR: str = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL: int = getattr(logging, LOG_LEVEL_STR, logging.INFO)

# Caminho do arquivo de log — criado automaticamente se não existir
LOG_FILE: Path = ROOT_DIR / os.getenv("LOG_FILE", "logs/etl.log")

# Garante que o diretório de logs existe antes de qualquer escrita
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def configure_logging() -> logging.Logger:
    """
    Configura e retorna o logger padrão do projeto.

    O logger escreve simultaneamente em:
    - Arquivo de log (logs/etl.log): para histórico e auditoria
    - Console (stdout): para acompanhamento em tempo real

    O formato inclui timestamp, nível, módulo e mensagem — isso facilita
    identificar qual etapa do pipeline gerou cada linha de log.

    Returns:
        logging.Logger: Logger configurado pronto para uso.

    Uso:
        from src.config.settings import configure_logging
        logger = configure_logging()
        logger.info("ETL iniciado")
    """
    logger = logging.getLogger("etl")

    # Evita adicionar handlers duplicados se a função for chamada mais de uma vez
    if logger.handlers:
        return logger

    logger.setLevel(LOG_LEVEL)

    # Formato padrão: 2026-04-15 08:30:00 | INFO | extract | Mensagem aqui
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(module)-15s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler para arquivo (mantém histórico completo)
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Handler para console (visibilidade em tempo real)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

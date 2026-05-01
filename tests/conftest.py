# =============================================================================
# conftest.py — Configuração global de testes
# Planejamento Comercial
# =============================================================================
#
# RESPONSABILIDADE:
#   Garantir que a suíte de testes pode ser executada com um único
#   comando (pytest tests/) sem precisar de .env configurado ou SQL
#   Server acessível. O conftest injeta valores defaults adequados para
#   testes unitários antes que qualquer módulo src.* seja importado.
#
# ORDEM DE CARREGAMENTO DO PYTEST:
#   1. conftest.py é carregado (os.environ.setdefault aqui)
#   2. Coleta dos testes (test_*.py são importados → src.* é importado)
#   3. settings.py usa os.getenv() — encontra os valores do passo 1
#   4. Testes executam
#
# CATEGORIAS DE TESTES:
#   unit        → só fixtures em memória; roda offline, sem arquivos reais
#   integration → lê arquivos Excel reais ou conecta ao SQL Server
#
# COMO RODAR:
#   pytest tests/                          # todos (unit + integration)
#   pytest tests/ -m unit                  # apenas unit (CI sem arquivos)
#   pytest tests/ -m integration           # apenas integration (ambiente local)
#   pytest tests/ -v --cov=src             # com cobertura de código
# =============================================================================

import os
import pytest

# =============================================================================
# VARIÁVEIS DE AMBIENTE DEFAULT
# =============================================================================
# Injetadas via os.environ.setdefault() — não sobrescrevem se já existirem
# no ambiente do sistema. Isso respeita o .env do desenvolvedor e as
# variáveis de CI/CD sem conflito.
#
# [REUTILIZAÇÃO]: Adicione aqui qualquer nova variável adicionada a settings.py
# para que os testes continuem funcionando sem .env.
# =============================================================================

_TEST_ENV_DEFAULTS: dict[str, str] = {
    # Banco de dados — aponta para instância local padrão do SQL Server Express
    "DB_SERVER":             r"localhost\SQLEXPRESS",
    "DB_DATABASE":           "planejamento_comercial",
    "DB_TRUSTED_CONNECTION": "yes",
    "DB_USER":               "",
    "DB_PASSWORD":           "",
    "DB_DRIVER":             "ODBC Driver 17 for SQL Server",

    # Schemas SQL Server
    "DB_SCHEMA_RAW":         "raw",
    "DB_SCHEMA_STAGING":     "staging",
    "DB_SCHEMA_DW":          "dw",

    # Anos disponíveis nos arquivos de meta
    "METAS_ANOS":            "2018,2019,2020,2021",

    # ETL
    "LOAD_STRATEGY":         "truncate",

    # Logging — WARNING durante testes: silencia INFO/DEBUG do ETL nos outputs
    "LOG_LEVEL":             "WARNING",
    "LOG_FILE":              "logs/etl_test.log",
}

for _key, _value in _TEST_ENV_DEFAULTS.items():
    os.environ.setdefault(_key, _value)

# Tenta carregar .env se python-dotenv estiver instalado.
# override=False garante que os defaults acima não são sobrescritos se .env
# não tiver a variável — e que variáveis do sistema têm precedência.
try:
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).parent.parent / ".env", override=False)
except ImportError:
    pass  # sem dotenv — os defaults acima são suficientes para testes unit


# =============================================================================
# REGISTRO DE MARKERS
# =============================================================================

def pytest_configure(config: pytest.Config) -> None:
    """Registra markers customizados para categorizar os testes."""
    config.addinivalue_line(
        "markers",
        "unit: testes puramente unitários — rodam com fixtures em memória, "
        "sem arquivos reais, sem banco de dados",
    )
    config.addinivalue_line(
        "markers",
        "integration: testes que requerem arquivos Excel reais e/ou conexão "
        "com SQL Server — precisam do ambiente completo configurado",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """
    Aplica markers automaticamente baseado no nome do arquivo de teste.

    Regra:
    - test_extract.py   → integration (lê arquivos Excel reais do disco)
    - test_transform.py → unit (opera apenas sobre fixtures em memória)
    - test_validate.py  → unit (opera apenas sobre fixtures em memória)

    Isso permite rodar `pytest tests/ -m unit` para CI sem arquivos Excel.
    Os testes de extração precisam dos arquivos em data/raw/ (Dimensoes.xlsx, Vendas.xlsx, Meta_YYYY.xlsx).
    """
    for item in items:
        # Normaliza para comparação: usa apenas o nome do arquivo, não o path completo
        nodeid_lower = item.nodeid.lower()

        if "test_extract" in nodeid_lower:
            item.add_marker(
                pytest.mark.integration,
                append=False,  # marker fica no início da lista
            )
        elif "test_transform" in nodeid_lower or "test_validate" in nodeid_lower:
            item.add_marker(
                pytest.mark.unit,
                append=False,
            )

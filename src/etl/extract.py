# =============================================================================
# extract.py — Camada de Extração (E do ETL)
# Planejamento Comercial
# =============================================================================
#
# RESPONSABILIDADE:
#   Ler todos os arquivos Excel de origem e retornar DataFrames brutos,
#   sem nenhuma transformação ou limpeza. O princípio aqui é simples:
#   "trazer o dado como ele está, sem modificar".
#
#   Por que não transformar aqui?
#   - Separar extração de transformação facilita debug: se um dado veio
#     errado, sabemos que é problema da fonte, não do nosso código.
#   - Permite reprocessar a transformação sem reler os arquivos de origem.
#   - Segue o princípio Bronze (raw) da arquitetura Medallion.
#
# FONTES LIDAS:
#   1. data/raw/Dimensoes.xlsx   → 7 abas (dProdutos, dVendedor, etc.)
#   2. data/raw/Vendas.xlsx      → aba fVendas (20.004 linhas, header na linha 5)
#   3. data/raw/Meta_YYYY.xlsx   → um arquivo por ano (2018–2021)
#
# [REUTILIZAÇÃO]:
#   - Ajuste os paths no .env (sem mexer neste arquivo).
#   - Se o arquivo de vendas tiver header em outra linha, ajuste VENDAS_SKIPROWS.
#   - Se houver mais anos de meta, adicione-os em METAS_ANOS no .env.
# =============================================================================

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config.settings import (
    PATH_DIMENSOES,
    PATH_VENDAS,
    PATH_METAS_DIR,
    METAS_ANOS,
    configure_logging,
)

# Inicializa o logger deste módulo
# Todos os módulos do projeto usam o mesmo logger "etl" configurado em settings.py
logger = configure_logging()

# =============================================================================
# CONSTANTE DE CONFIGURAÇÃO DA PLANILHA DE VENDAS
# =============================================================================
# O arquivo Vendas.xlsx tem um cabeçalho de título na linha 1 e linhas
# em branco nas linhas 2-4. Os nomes reais das colunas estão na LINHA 5.
# skiprows=4 instrui o pandas a ignorar as 4 primeiras linhas (índices 0–3)
# e usar a linha 5 (índice 4) como cabeçalho.
#
# [REUTILIZAÇÃO]: Ajuste este valor se o arquivo de vendas do novo projeto
# tiver o cabeçalho em uma linha diferente (ex: skiprows=0 se na linha 1).
VENDAS_SKIPROWS: int = 4  # [EDITÁVEL] linha do cabeçalho no Excel (4 = linha 5 no arquivo)


# =============================================================================
# NOMES DAS ABAS DO ARQUIVO DE DIMENSÕES
# =============================================================================
# Mapeamento explícito para evitar dependência da ordem das abas.
# [EDITÁVEL] Ajuste os nomes das abas se o arquivo Excel tiver nomes diferentes.
# Formato: "chave_interna": "Nome da Aba no Excel"
DIMENSOES_SHEETS: dict[str, str] = {
    "produtos":   "dProdutos",    # [EDITÁVEL] nome da aba de produtos
    "vendedor":   "dVendedor",    # [EDITÁVEL] nome da aba de vendedores
    "clientes":   "dClientes",    # [EDITÁVEL] nome da aba de clientes
    "cidade":     "dCidade",      # [EDITÁVEL] nome da aba de cidades
    "unidades":   "dUnidades",    # [EDITÁVEL] nome da aba de unidades/filiais
    "status":     "dStatus",      # [EDITÁVEL] nome da aba de status de pedido
    "pagamento":  "dPagamento",   # [EDITÁVEL] nome da aba de formas de pagamento
}


# =============================================================================
# FUNÇÕES DE EXTRAÇÃO
# =============================================================================

def extract_dimensoes() -> dict[str, pd.DataFrame]:
    """
    Lê todas as abas do arquivo Dimensões.xlsx e retorna um dicionário
    onde a chave é o nome da dimensão e o valor é o DataFrame bruto.

    O arquivo contém 7 abas com tabelas de referência (dimensões) para
    o modelo relacional: produtos, vendedores, clientes, cidades, unidades,
    status de pedido e formas de pagamento.

    Returns:
        dict[str, pd.DataFrame]: Dicionário com os DataFrames brutos.
            Chaves: "produtos", "vendedor", "clientes", "cidade",
                    "unidades", "status", "pagamento"

    Raises:
        FileNotFoundError: Se o arquivo Dimensões.xlsx não for encontrado.
        ValueError: Se alguma aba esperada não existir no arquivo.

    Exemplo de uso:
        dimensoes = extract_dimensoes()
        df_produtos = dimensoes["produtos"]
        print(df_produtos.head())
    """
    _validar_arquivo_existe(PATH_DIMENSOES, "Dimensões")
    logger.info(f"Lendo arquivo de dimensões: {PATH_DIMENSOES}")

    # Lê todas as abas em um único passo — pd.read_excel com sheet_name=None
    # retorna um dicionário {nome_aba: DataFrame}. Isso é mais eficiente que
    # abrir o arquivo uma vez por aba.
    todas_abas: dict[str, pd.DataFrame] = pd.read_excel(
        PATH_DIMENSOES,
        sheet_name=None,  # Lê TODAS as abas de uma vez
        dtype=str,        # Lê tudo como string para preservar o dado bruto
                          # sem conversões automáticas que podem perder info
    )

    # Valida se todas as abas esperadas existem no arquivo
    for chave, nome_aba in DIMENSOES_SHEETS.items():
        if nome_aba not in todas_abas:
            raise ValueError(
                f"Aba '{nome_aba}' não encontrada em {PATH_DIMENSOES.name}. "
                f"Abas disponíveis: {list(todas_abas.keys())}"
            )

    # Remonta o dicionário usando nomes-chave mais simples (sem "d" prefix)
    # para facilitar o acesso no restante do código
    resultado: dict[str, pd.DataFrame] = {
        chave: todas_abas[nome_aba]
        for chave, nome_aba in DIMENSOES_SHEETS.items()
    }

    # Loga quantidade de linhas lidas por aba para rastreabilidade
    for chave, df in resultado.items():
        logger.info(f"  [{chave}] → {len(df):,} linhas, {len(df.columns)} colunas")

    logger.info("Extração de dimensões concluída com sucesso.")
    return resultado


def extract_vendas() -> pd.DataFrame:
    """
    Lê o arquivo Vendas.xlsx e retorna o DataFrame bruto de transações.

    ATENÇÃO — Estrutura especial do arquivo:
    O Vendas.xlsx tem um título nas primeiras linhas antes do cabeçalho real:
        Linha 1: Título do arquivo (texto descritivo)
        Linhas 2-4: Em branco
        Linha 5: Cabeçalho real (nomes das colunas)
        Linha 6+: Dados de transações
    Por isso usamos skiprows=4 para ignorar as linhas 1-4.

    Returns:
        pd.DataFrame: DataFrame bruto com todas as colunas e linhas de vendas.
            Aproximadamente 20.004 linhas no dataset atual (Jan/2018 a Abr/2021).

    Raises:
        FileNotFoundError: Se o arquivo Vendas.xlsx não for encontrado.

    [REUTILIZAÇÃO]:
        Se o arquivo de vendas do novo projeto não tiver linhas de título,
        ajuste VENDAS_SKIPROWS = 0 (ou remova o parâmetro).
    """
    _validar_arquivo_existe(PATH_VENDAS, "Vendas")
    logger.info(f"Lendo arquivo de vendas: {PATH_VENDAS}")

    df = pd.read_excel(
        PATH_VENDAS,
        sheet_name="fVendas",   # Nome explícito da aba para evitar surpresas
        skiprows=VENDAS_SKIPROWS,  # Pula as linhas de título antes do cabeçalho
        dtype=str,              # Tudo como string na extração — tipos serão
                                # convertidos na camada de transformação
    )

    # Remove linhas completamente vazias que possam ter vindo do Excel
    # (células formatadas mas sem conteúdo às vezes são lidas como linhas NaN)
    linhas_antes = len(df)
    df = df.dropna(how="all")
    linhas_removidas = linhas_antes - len(df)

    if linhas_removidas > 0:
        logger.warning(
            f"Removidas {linhas_removidas} linhas completamente vazias do arquivo de vendas."
        )

    logger.info(f"  [fVendas] → {len(df):,} linhas, {len(df.columns)} colunas extraídas.")
    logger.info("Extração de vendas concluída com sucesso.")
    return df


def extract_metas() -> dict[int, pd.DataFrame]:
    """
    Lê todos os arquivos de meta disponíveis e retorna um dicionário
    onde a chave é o ano e o valor é o DataFrame bruto daquele ano.

    Estrutura de cada arquivo Meta YYYY.xlsx:
        Coluna A: Id Vendedor
        Coluna B: Vendedor (nome)
        Colunas C-N: janeiro, fevereiro, ..., dezembro (valores de meta)

    Nota: Esta estrutura "wide" (um mês por coluna) será convertida para
    formato "long" (uma linha por vendedor-mês) na camada de transformação,
    usando a operação de UNPIVOT. Aqui lemos os dados como estão.

    Returns:
        dict[int, pd.DataFrame]: Dicionário {ano: DataFrame_bruto}.
            Ex: {2018: df_2018, 2019: df_2019, ...}

    Raises:
        FileNotFoundError: Se algum arquivo de meta esperado não for encontrado.

    [REUTILIZAÇÃO]:
        Adicione ou remova anos em METAS_ANOS no .env.
        O padrão do nome do arquivo "Meta YYYY.xlsx" deve ser mantido.
        Se o padrão mudar, ajuste a f-string abaixo.
    """
    logger.info(f"Lendo arquivos de meta para os anos: {METAS_ANOS}")
    resultado: dict[int, pd.DataFrame] = {}

    for ano in METAS_ANOS:
        # Monta o caminho do arquivo para o ano corrente
        # Padrão esperado: data/raw/Meta_2018.xlsx, data/raw/Meta_2019.xlsx, etc.
        # [REUTILIZAÇÃO]: Ajuste o padrão do nome do arquivo se necessário
        caminho_meta: Path = PATH_METAS_DIR / f"Meta_{ano}.xlsx"
        _validar_arquivo_existe(caminho_meta, f"Meta {ano}")

        df = pd.read_excel(
            caminho_meta,
            sheet_name="Meta",  # Nome padrão da aba em todos os arquivos
            dtype=str,
        )

        # Remove linhas completamente vazias (comum em planilhas Excel)
        df = df.dropna(how="all")

        logger.info(f"  [Meta {ano}] → {len(df):,} linhas extraídas.")
        resultado[ano] = df

    logger.info("Extração de metas concluída com sucesso.")
    return resultado


# =============================================================================
# FUNÇÃO AUXILIAR
# =============================================================================

def _validar_arquivo_existe(caminho: Path, nome_legivel: str) -> None:
    """
    Valida se um arquivo existe no caminho informado.
    Falha de forma clara e informativa antes de tentar ler o arquivo.

    Args:
        caminho (Path): Caminho completo do arquivo a verificar.
        nome_legivel (str): Nome amigável para exibição na mensagem de erro.

    Raises:
        FileNotFoundError: Se o arquivo não existir no caminho informado.
    """
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo '{nome_legivel}' não encontrado em: {caminho}\n"
            f"Verifique se o caminho está correto no arquivo .env e se "
            f"o arquivo realmente existe neste local."
        )


# =============================================================================
# EXECUÇÃO DIRETA (para testes manuais)
# =============================================================================
# Este bloco só executa se o arquivo for rodado diretamente:
#   python -m src.etl.extract
# Útil para validar a extração sem precisar rodar o pipeline completo.

if __name__ == "__main__":
    logger.info("=== Execução direta do módulo extract.py ===")

    # Testa extração das dimensões
    dimensoes = extract_dimensoes()
    for nome, df in dimensoes.items():
        print(f"\n[{nome}] — {len(df)} linhas")
        print(df.head(2).to_string())

    # Testa extração de vendas
    df_vendas = extract_vendas()
    print(f"\n[fVendas] — {len(df_vendas)} linhas")
    print(df_vendas.head(2).to_string())

    # Testa extração das metas
    metas = extract_metas()
    for ano, df in metas.items():
        print(f"\n[Meta {ano}] — {len(df)} linhas")
        print(df.head(2).to_string())

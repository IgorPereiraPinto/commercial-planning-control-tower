# =============================================================================
# transform.py — Camada de Transformação (T do ETL)
# Commercial Planning Control Tower
# =============================================================================
#
# RESPONSABILIDADE:
#   Receber os DataFrames brutos vindos de extract.py e aplicar todas as
#   transformações necessárias para produzir dados limpos, tipados e
#   prontos para carga no SQL Server (camada staging).
#
#   Transformações aplicadas:
#   1. Cast de tipos (string → date, float, int)
#   2. Trim de strings (espaços extras em nomes)
#   3. Normalização de valores (capitalização, encoding)
#   4. UNPIVOT das metas (wide → long: colunas mensais → linhas)
#   5. Adição de metadados ETL (_etl_loaded_at, _etl_source)
#   6. Remoção de linhas com campos obrigatórios nulos
#
# POR QUE METADADOS ETL?
#   Cada tabela carregada recebe _etl_loaded_at (timestamp da carga) e
#   _etl_source (nome do arquivo de origem). Isso permite:
#   - Saber quando cada linha foi carregada
#   - Identificar a origem de cada registro para debug e auditoria
#   - Reprocessar dados de uma fonte específica sem afetar outras
#
# [REUTILIZAÇÃO]:
#   - Os nomes de colunas estão nas constantes no topo — ajuste se necessário.
#   - As regras de negócio (ex: quais colunas são obrigatórias) estão explícitas.
#   - A operação de UNPIVOT (transform_metas) é genérica e reutilizável.
# =============================================================================

import logging
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd

from src.config.settings import configure_logging

logger = configure_logging()

# =============================================================================
# CONSTANTES — NOMES DE COLUNAS
# =============================================================================
# Centralizar os nomes de colunas aqui evita erros de digitação espalhados
# pelo código e facilita a adaptação quando o layout do Excel mudar.
# [REUTILIZAÇÃO]: Ajuste os valores abaixo se as colunas da fonte mudarem.

# Colunas da tabela fVendas
COL_VENDAS_DATA = "Data"
COL_VENDAS_DATA_ENVIO = "Data Envio"
COL_VENDAS_NUM_VENDA = "Num Venda"
COL_VENDAS_ID_PRODUTO = "Id Produto"
COL_VENDAS_ID_VENDEDOR = "Id Vendedor"
COL_VENDAS_NOME_VENDEDOR = "Nome Vendedor"
COL_VENDAS_ID_CLIENTE = "Id Cliente"
COL_VENDAS_NOME_CLIENTE = "Nome Cliente"
COL_VENDAS_ID_UNIDADE = "Id Unidade"
COL_VENDAS_NOME_UNIDADE = "Nome Unidade"
COL_VENDAS_ID_STATUS = "Id Status"
COL_VENDAS_ID_PGTO = "Id Pgto"
COL_VENDAS_QTDE = "Qtde"
COL_VENDAS_VALOR_UNIT = "Valor Unit"
COL_VENDAS_CUSTO_UNIT = "Custo Unit"
COL_VENDAS_DESPESA_UNIT = "Despesa Unit"
COL_VENDAS_IMPOSTOS_UNIT = "Impostos Unit"
COL_VENDAS_COMISSAO_UNIT = "Comissão Unit"
COL_VENDAS_FATURAMENTO_TOTAL = "Faturamento Total"
COL_VENDAS_CUSTO_TOTAL = "Custo Total"

# Colunas obrigatórias em fVendas (não podem ser nulas após transformação)
VENDAS_COLUNAS_OBRIGATORIAS = [
    COL_VENDAS_DATA,
    COL_VENDAS_NUM_VENDA,
    COL_VENDAS_ID_PRODUTO,
    COL_VENDAS_ID_VENDEDOR,
    COL_VENDAS_ID_CLIENTE,
    COL_VENDAS_QTDE,
    COL_VENDAS_FATURAMENTO_TOTAL,
]

# Colunas da tabela de metas (antes do unpivot)
COL_META_ID_VENDEDOR = "Id Vendedor"
COL_META_VENDEDOR = "Vendedor"

# Nomes dos meses em português (ordem importa — janeiro=1, fevereiro=2, etc.)
# [REUTILIZAÇÃO]: Se o arquivo de meta usar outros nomes (abreviações, inglês),
# ajuste esta lista mantendo a mesma ordem.
MESES_PT = [
    "janeiro", "fevereiro", "março", "abril",
    "maio", "junho", "julho", "agosto",
    "setembro", "outubro", "novembro", "dezembro"
]

# Timestamp de quando este processo de carga foi iniciado
# Usando um único timestamp para toda a execução garante consistência
# (todas as linhas de uma mesma carga têm o mesmo _etl_loaded_at)
ETL_LOADED_AT: datetime = datetime.now()


# =============================================================================
# TRANSFORMAÇÃO: fVendas
# =============================================================================

def transform_vendas(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma o DataFrame bruto de vendas aplicando limpeza, tipagem
    e adição de metadados ETL.

    Operações aplicadas (nesta ordem):
    1. Cópia defensiva do DataFrame (não altera o original)
    2. Strip de espaços em strings
    3. Cast de colunas de data (string → datetime)
    4. Cast de colunas de ID (string → Int64 nullable)
    5. Cast de colunas numéricas/métricas (string → float)
    6. Remoção de linhas com campos obrigatórios nulos
    7. Adição de metadados _etl_loaded_at e _etl_source

    Args:
        df_raw (pd.DataFrame): DataFrame bruto vindo de extract_vendas().

    Returns:
        pd.DataFrame: DataFrame transformado pronto para carga no staging.

    [REUTILIZAÇÃO]:
        Ajuste os nomes das colunas nas constantes no topo deste arquivo.
        Adicione ou remova colunas obrigatórias em VENDAS_COLUNAS_OBRIGATORIAS.
    """
    logger.info("Iniciando transformação de fVendas...")

    # Passo 1: Cópia defensiva — nunca modifica o DataFrame original
    # Isso evita efeitos colaterais inesperados se o mesmo df_raw for
    # usado em outro lugar (ex: testes)
    df = df_raw.copy()

    # Passo 2: Strip de espaços em colunas de texto
    # Planilhas Excel frequentemente têm espaços antes/depois de nomes
    df = _strip_string_columns(df)

    # Passo 3: Cast de colunas de data
    # pd.to_datetime com errors="coerce" converte o que conseguir e coloca
    # NaT (Not a Time) onde não conseguir — facilita detecção de problemas
    df[COL_VENDAS_DATA] = pd.to_datetime(df[COL_VENDAS_DATA], errors="coerce", dayfirst=True)
    df[COL_VENDAS_DATA_ENVIO] = pd.to_datetime(df[COL_VENDAS_DATA_ENVIO], errors="coerce", dayfirst=True)

    # Passo 4: Cast de colunas de ID para inteiro nullable (pd.Int64Dtype)
    # Usamos Int64 (com I maiúsculo) e não int64 porque o tipo nativo do pandas
    # não suporta NaN — Int64 (nullable) suporta e é mais seguro para IDs
    colunas_id = [
        COL_VENDAS_ID_PRODUTO,
        COL_VENDAS_ID_VENDEDOR,
        COL_VENDAS_ID_CLIENTE,
        COL_VENDAS_ID_UNIDADE,
        COL_VENDAS_ID_STATUS,
        COL_VENDAS_ID_PGTO,
    ]
    for col in colunas_id:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # Passo 5: Cast de colunas numéricas (métricas financeiras e quantidades)
    colunas_float = [
        COL_VENDAS_QTDE,
        COL_VENDAS_VALOR_UNIT,
        COL_VENDAS_CUSTO_UNIT,
        COL_VENDAS_DESPESA_UNIT,
        COL_VENDAS_IMPOSTOS_UNIT,
        COL_VENDAS_COMISSAO_UNIT,
        COL_VENDAS_FATURAMENTO_TOTAL,
        COL_VENDAS_CUSTO_TOTAL,
    ]
    for col in colunas_float:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Passo 6: Remove linhas com campos obrigatórios nulos
    # Registra quais linhas foram removidas para auditoria
    df = _remover_nulos_obrigatorios(df, VENDAS_COLUNAS_OBRIGATORIAS, "fVendas")

    # Passo 7: Adiciona metadados ETL
    df = _adicionar_metadados(df, fonte="data/raw/Vendas.xlsx")

    logger.info(f"Transformação de fVendas concluída: {len(df):,} linhas prontas.")
    return df


# =============================================================================
# TRANSFORMAÇÃO: DIMENSÕES
# =============================================================================

def transform_dimensoes(dimensoes_raw: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Transforma todas as dimensões aplicando limpeza básica e metadados.

    As dimensões têm transformações mais simples que a fVendas:
    - Strip de espaços em todos os campos de texto
    - Cast de IDs para inteiro
    - Adição de metadados ETL

    Args:
        dimensoes_raw (dict[str, pd.DataFrame]): Dicionário de DataFrames brutos
            retornado por extract_dimensoes().

    Returns:
        dict[str, pd.DataFrame]: Dicionário com DataFrames transformados.
            As chaves são as mesmas do dicionário de entrada.
    """
    logger.info("Iniciando transformação das dimensões...")
    resultado: dict[str, pd.DataFrame] = {}

    for nome, df_raw in dimensoes_raw.items():
        df = df_raw.copy()

        # Strip em todas as colunas de texto
        df = _strip_string_columns(df)

        # Cast da coluna de ID principal de cada dimensão
        # Identificamos a coluna de ID pelo padrão "Id " no início do nome
        colunas_id = [col for col in df.columns if col.startswith("Id ") or col.startswith("id ")]
        for col in colunas_id:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        # Adiciona metadados
        df = _adicionar_metadados(df, fonte=f"data/raw/Dimensoes.xlsx (aba: {nome})")

        logger.info(f"  [{nome}] → {len(df):,} linhas transformadas.")
        resultado[nome] = df

    logger.info("Transformação das dimensões concluída.")
    return resultado


# =============================================================================
# TRANSFORMAÇÃO: METAS (UNPIVOT — wide → long)
# =============================================================================

def transform_metas(metas_raw: dict[int, pd.DataFrame]) -> pd.DataFrame:
    """
    Transforma os arquivos de meta de formato wide (colunas = meses) para
    formato long (uma linha por vendedor-mês), usando operação de UNPIVOT.

    ANTES (wide — formato original do Excel):
    ┌─────────────┬──────────┬──────────┬──────────┐
    │ Id Vendedor │ Vendedor │ janeiro  │ fevereiro│
    ├─────────────┼──────────┼──────────┼──────────┤
    │      1      │ Ronaldo  │ 5.000.000│ 4.800.000│
    │      2      │ Rodrigo  │ 2.000.000│ 2.100.000│
    └─────────────┴──────────┴──────────┴──────────┘

    DEPOIS (long — formato ideal para BI e SQL):
    ┌─────────────┬──────────┬──────┬─────┬───────────┐
    │ Id Vendedor │ Vendedor │ Ano  │ Mes │ Valor Meta│
    ├─────────────┼──────────┼──────┼─────┼───────────┤
    │      1      │ Ronaldo  │ 2018 │  1  │ 5.000.000 │
    │      1      │ Ronaldo  │ 2018 │  2  │ 4.800.000 │
    │      2      │ Rodrigo  │ 2018 │  1  │ 2.000.000 │
    └─────────────┴──────────┴──────┴─────┴───────────┘

    Por que o formato long é melhor para BI?
    - Facilita filtros por mês/ano no Power BI sem medidas complexas
    - Permite JOIN direto com a tabela dCalendario
    - É o padrão esperado pelos modelos dimensionais (star schema)

    Args:
        metas_raw (dict[int, pd.DataFrame]): Dicionário {ano: df_bruto}
            retornado por extract_metas().

    Returns:
        pd.DataFrame: DataFrame consolidado de todos os anos no formato long,
            com metadados ETL adicionados.

    [REUTILIZAÇÃO]:
        Se os arquivos de meta do novo projeto usarem nomes de mês diferentes
        (ex: inglês, abreviações), ajuste a lista MESES_PT no topo do arquivo.
    """
    logger.info("Iniciando transformação (UNPIVOT) das metas...")
    frames_long: list[pd.DataFrame] = []

    for ano, df_raw in metas_raw.items():
        df = df_raw.copy()

        # Strip em colunas de texto
        df = _strip_string_columns(df)

        # Identifica quais colunas do DataFrame correspondem a meses
        # Fazemos a comparação em minúsculas para tolerar variações de capitalização
        colunas_do_df_lower = {col.lower().strip(): col for col in df.columns}

        colunas_meses_encontradas: list[str] = []
        for mes_esperado in MESES_PT:
            col_original = colunas_do_df_lower.get(mes_esperado)
            if col_original:
                colunas_meses_encontradas.append(col_original)
            else:
                logger.warning(
                    f"Mês '{mes_esperado}' não encontrado no arquivo Meta {ano}.xlsx. "
                    f"Colunas disponíveis: {list(df.columns)}"
                )

        # Colunas que NÃO são meses (ficam como identificadores no formato long)
        colunas_id = [col for col in df.columns if col not in colunas_meses_encontradas]

        # pd.melt é a operação de UNPIVOT do pandas:
        # - id_vars: colunas que se repetem em cada linha (vendedor, id)
        # - value_vars: colunas que viram linhas (os meses)
        # - var_name: nome da nova coluna que receberá o nome do mês
        # - value_name: nome da nova coluna que receberá o valor da meta
        df_long = pd.melt(
            df,
            id_vars=colunas_id,
            value_vars=colunas_meses_encontradas,
            var_name="NomeMes",
            value_name="Valor Meta",
        )

        # Adiciona coluna de Ano (o ano vem do nome do arquivo, não do dado)
        df_long["Ano"] = ano

        # Converte o nome do mês para número (janeiro=1, fevereiro=2, etc.)
        # Cria um mapeamento baseado na lista MESES_PT (normaliza para minúsculas)
        mapa_mes_numero = {
            mes.lower(): idx + 1
            for idx, mes in enumerate(MESES_PT)
        }
        df_long["Mes"] = df_long["NomeMes"].str.lower().str.strip().map(mapa_mes_numero)

        # Converte o valor da meta para float
        df_long["Valor Meta"] = pd.to_numeric(df_long["Valor Meta"], errors="coerce")

        # Cast do Id Vendedor para inteiro
        if COL_META_ID_VENDEDOR in df_long.columns:
            df_long[COL_META_ID_VENDEDOR] = pd.to_numeric(
                df_long[COL_META_ID_VENDEDOR], errors="coerce"
            ).astype("Int64")

        # Cria coluna de data de referência (primeiro dia do mês da meta)
        # Exemplo: Ano=2018, Mes=3 → Data Meta = 2018-03-01
        # Isso facilita o JOIN com dCalendario no modelo dimensional
        df_long["Data Meta"] = pd.to_datetime(
            df_long["Ano"].astype(str) + "-" + df_long["Mes"].astype(str).str.zfill(2) + "-01",
            format="%Y-%m-%d",
            errors="coerce",
        )

        # Remove a coluna NomeMes — redundante com Mes (número) e Data Meta
        df_long = df_long.drop(columns=["NomeMes"])

        # Remove linhas sem valor de meta (NaN) — meses sem meta definida
        linhas_sem_meta = df_long["Valor Meta"].isna().sum()
        if linhas_sem_meta > 0:
            logger.warning(
                f"  [Meta {ano}] → {linhas_sem_meta} linhas sem valor de meta removidas."
            )
        df_long = df_long.dropna(subset=["Valor Meta"])

        # Adiciona metadados ETL
        df_long = _adicionar_metadados(df_long, fonte=f"data/raw/Meta_{ano}.xlsx")

        logger.info(f"  [Meta {ano}] → {len(df_long):,} linhas após UNPIVOT.")
        frames_long.append(df_long)

    # Consolida todos os anos em um único DataFrame
    df_consolidado = pd.concat(frames_long, ignore_index=True)

    # Ordena por vendedor e data para facilitar leitura e debug
    df_consolidado = df_consolidado.sort_values(
        by=[COL_META_ID_VENDEDOR, "Data Meta"]
    ).reset_index(drop=True)

    logger.info(
        f"Transformação de metas concluída: {len(df_consolidado):,} linhas totais "
        f"({len(metas_raw)} anos consolidados)."
    )
    return df_consolidado


# =============================================================================
# FUNÇÕES AUXILIARES INTERNAS
# =============================================================================

def _strip_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove espaços em branco no início e no fim de todas as colunas
    que contêm dados do tipo string/object.

    Esse é um problema muito comum em planilhas Excel onde células
    formatadas manualmente acumulam espaços extras.

    Args:
        df (pd.DataFrame): DataFrame de entrada.

    Returns:
        pd.DataFrame: Cópia do DataFrame com strings limpas.
    """
    df = df.copy()
    # Inclui tanto `object` (dtype legado) quanto `"string"` (StringDtype do
    # pandas). Declarar ambos deixa a intenção explícita e elimina o
    # Pandas4Warning sobre a separação futura entre os dois tipos.
    colunas_texto = df.select_dtypes(include=[object, "string"]).columns
    for col in colunas_texto:
        # Usa isinstance para operar apenas em valores realmente textuais.
        # NaN, pd.NA e None passam sem modificação — sem precisar de
        # astype(str) + replace("nan") para desfazer a conversão.
        df[col] = df[col].apply(
            lambda valor: valor.strip() if isinstance(valor, str) else valor
        )
    return df


def _remover_nulos_obrigatorios(
    df: pd.DataFrame,
    colunas: list[str],
    nome_tabela: str
) -> pd.DataFrame:
    """
    Remove linhas onde qualquer coluna obrigatória é nula (NaN / NaT).
    Loga quantas linhas foram removidas e quais colunas causaram a remoção.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        colunas (list[str]): Lista de colunas que não podem ser nulas.
        nome_tabela (str): Nome da tabela para exibição no log.

    Returns:
        pd.DataFrame: DataFrame sem as linhas com nulos obrigatórios.
    """
    mascara_nulos = df[colunas].isnull().any(axis=1)
    qtd_removidas = mascara_nulos.sum()

    if qtd_removidas > 0:
        # Identifica quais colunas têm nulos para facilitar o diagnóstico
        colunas_com_nulo = [
            col for col in colunas if df[col].isnull().any()
        ]
        logger.warning(
            f"[{nome_tabela}] Removidas {qtd_removidas:,} linhas com campos "
            f"obrigatórios nulos. Colunas afetadas: {colunas_com_nulo}"
        )

    return df[~mascara_nulos].reset_index(drop=True)


def _adicionar_metadados(df: pd.DataFrame, fonte: str) -> pd.DataFrame:
    """
    Adiciona colunas de rastreabilidade ETL ao DataFrame.

    Colunas adicionadas:
    - _etl_loaded_at: timestamp de quando a linha foi carregada no pipeline
    - _etl_source: nome do arquivo de origem da linha

    Por que prefixo "_"?
    Convenção para indicar que são colunas de infraestrutura (não de negócio).
    No Power BI, essas colunas ficam ocultas por padrão para não poluir
    a visão do usuário de negócio.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        fonte (str): Nome/caminho do arquivo de origem.

    Returns:
        pd.DataFrame: DataFrame com as duas colunas de metadados adicionadas.
    """
    df = df.copy()
    df["_etl_loaded_at"] = ETL_LOADED_AT
    df["_etl_source"] = fonte
    return df

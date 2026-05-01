# =============================================================================
# validate.py — Camada de Validação de Qualidade de Dados
# Planejamento Comercial
# =============================================================================
#
# RESPONSABILIDADE:
#   Executar os testes de qualidade de dados após a extração e após a
#   transformação, garantindo que apenas dados confiáveis chegam ao banco.
#
#   Há dois momentos de validação no pipeline:
#   1. PÓS-EXTRAÇÃO (raw): verifica se os arquivos vieram como esperado
#   2. PÓS-TRANSFORMAÇÃO (staging): verifica regras de negócio
#
#   Cada teste retorna um objeto ValidationResult com status e mensagem.
#   O runner consolidado (run_all_validations) retorna um relatório completo
#   e lança uma exceção se algum teste crítico falhar.
#
# OS 8 TESTES DO PROJETO:
#   1. Nulos em chaves primárias (IDs)
#   2. Integridade referencial (IDs de vendas existem nas dimensões)
#   3. Duplicidade de transações (Num Venda + Id Produto deve ser único)
#   4. Cobertura de metas (11 vendedores com 12 meses cada)
#   5. Valores negativos em faturamento
#   6. Data de envio >= data da venda
#   7. Contagem de linhas pós-carga (staging == raw)
#   8. Status válidos
#
# [REUTILIZAÇÃO]:
#   - Ajuste os conjuntos de valores válidos (STATUS_VALIDOS, etc.) conforme
#     as regras de negócio do novo projeto.
#   - Adicione novos testes seguindo o mesmo padrão: função que retorna
#     ValidationResult e uma entry no dicionário TESTES_CRITICOS.
# =============================================================================

import logging
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

from src.config.settings import configure_logging

logger = configure_logging()

# =============================================================================
# CONSTANTES DE REGRAS DE NEGÓCIO
# =============================================================================
# [EDITÁVEL] Ajuste todos os valores abaixo conforme as regras do novo projeto.

# [EDITÁVEL] IDs de status válidos conforme tabela dStatus do novo projeto
STATUS_VALIDOS: set[int] = {1, 2, 3}

# [EDITÁVEL] Número de vendedores com meta definida (validação de cobertura)
QTD_VENDEDORES_ESPERADOS: int = 11

# [EDITÁVEL] Meses por vendedor por ano (12 = ano completo; ajuste para anos parciais)
QTD_MESES_ESPERADOS: int = 12

# [EDITÁVEL] Colunas que não podem ter nulos em fVendas (chaves de integridade)
VENDAS_COLUNAS_CHAVE: list[str] = [
    "Id Produto", "Id Vendedor", "Id Cliente",
    "Num Venda", "Data", "Faturamento Total"
]

# [EDITÁVEL] Mapeamento de FKs para validação de integridade referencial
# Formato: {coluna_em_fVendas: nome_da_dimensao_para_log}
# Remova ou adicione entradas conforme as dimensões do novo projeto
FOREIGN_KEYS: dict[str, str] = {
    "Id Vendedor": "dVendedor",
    "Id Produto":  "dProdutos",
    "Id Unidade":  "dUnidades",
    "Id Status":   "dStatus",
    "Id Pgto":     "dPagamento",
}


# =============================================================================
# ESTRUTURA DE RESULTADO DE VALIDAÇÃO
# =============================================================================

@dataclass
class ValidationResult:
    """
    Representa o resultado de um único teste de validação.

    Attributes:
        nome (str): Identificador do teste (ex: "nulos_chave_primaria")
        passou (bool): True se o teste passou, False se falhou
        mensagem (str): Descrição do resultado (o que foi testado, o que falhou)
        critico (bool): Se True, falha neste teste interrompe o pipeline.
                        Se False, apenas loga aviso e continua.
        detalhes (Optional[str]): Informações adicionais para debug (opcional)
    """
    nome: str
    passou: bool
    mensagem: str
    critico: bool = True
    detalhes: Optional[str] = None


@dataclass
class ValidationReport:
    """
    Relatório consolidado de todas as validações executadas.

    Attributes:
        resultados (list[ValidationResult]): Lista de todos os testes.
        total (int): Total de testes executados.
        aprovados (int): Quantidade de testes que passaram.
        reprovados_criticos (int): Testes críticos que falharam.
        reprovados_avisos (int): Testes não críticos que falharam.
    """
    resultados: list[ValidationResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.resultados)

    @property
    def aprovados(self) -> int:
        return sum(1 for r in self.resultados if r.passou)

    @property
    def reprovados_criticos(self) -> int:
        return sum(1 for r in self.resultados if not r.passou and r.critico)

    @property
    def reprovados_avisos(self) -> int:
        return sum(1 for r in self.resultados if not r.passou and not r.critico)

    @property
    def pipeline_pode_continuar(self) -> bool:
        """O pipeline só pode continuar se NENHUM teste crítico falhou."""
        return self.reprovados_criticos == 0

    def resumo(self) -> str:
        status = "APROVADO" if self.pipeline_pode_continuar else "REPROVADO"
        return (
            f"=== RELATÓRIO DE VALIDAÇÃO: {status} ===\n"
            f"Total: {self.total} | Aprovados: {self.aprovados} | "
            f"Críticos falhos: {self.reprovados_criticos} | "
            f"Avisos: {self.reprovados_avisos}"
        )


# =============================================================================
# TESTES INDIVIDUAIS
# =============================================================================

def validar_nulos_chave_primaria(df_vendas: pd.DataFrame) -> ValidationResult:
    """
    TESTE 1: Verifica se existem valores nulos nas colunas de chave
    primária e chaves estrangeiras obrigatórias de fVendas.

    Por que é crítico?
    Nulos em IDs quebram os relacionamentos no modelo dimensional e
    produzem linhas "órfãs" que não se associam a nenhuma dimensão.
    Isso distorce os KPIs no Power BI (ex: faturamento sem vendedor associado).

    Args:
        df_vendas (pd.DataFrame): DataFrame de vendas transformado.

    Returns:
        ValidationResult: Resultado do teste.
    """
    nulos_por_coluna = {
        col: int(df_vendas[col].isnull().sum())
        for col in VENDAS_COLUNAS_CHAVE
        if col in df_vendas.columns
    }
    total_nulos = sum(nulos_por_coluna.values())
    colunas_com_nulo = {k: v for k, v in nulos_por_coluna.items() if v > 0}

    if total_nulos == 0:
        return ValidationResult(
            nome="nulos_chave_primaria",
            passou=True,
            mensagem=f"OK — Nenhum nulo encontrado nas {len(VENDAS_COLUNAS_CHAVE)} colunas obrigatórias.",
            critico=True,
        )
    else:
        return ValidationResult(
            nome="nulos_chave_primaria",
            passou=False,
            mensagem=f"FALHA — {total_nulos} valores nulos encontrados em colunas obrigatórias.",
            critico=True,
            detalhes=str(colunas_com_nulo),
        )


def validar_integridade_referencial(
    df_vendas: pd.DataFrame,
    dimensoes: dict[str, pd.DataFrame]
) -> ValidationResult:
    """
    TESTE 2: Verifica se todos os IDs de chaves estrangeiras em fVendas
    existem nas suas respectivas tabelas de dimensão.

    Exemplo: Todo 'Id Vendedor' em fVendas deve existir em dVendedor.
    Se não existir, a linha ficará sem contexto no modelo dimensional
    (venda sem vendedor = impossível de analisar por vendedor).

    Args:
        df_vendas (pd.DataFrame): DataFrame de vendas transformado.
        dimensoes (dict[str, pd.DataFrame]): Dicionário de dimensões transformadas.

    Returns:
        ValidationResult: Resultado do teste.
    """
    violacoes: dict[str, int] = {}

    # Mapeamento entre coluna FK em vendas e coluna PK na dimensão correspondente
    # [REUTILIZAÇÃO]: Ajuste este mapeamento se os nomes mudarem.
    mapa_fk_dimensao = {
        "Id Vendedor": ("vendedor", "Id Vendedor"),
        "Id Produto": ("produtos", "Id Produto"),
        "Id Unidade": ("unidades", "Id Unidade"),
        "Id Status": ("status", "Id Status"),
        "Id Pgto": ("pagamento", "Id Pagamento"),
    }

    for col_fk, (nome_dim, col_pk) in mapa_fk_dimensao.items():
        if col_fk not in df_vendas.columns:
            continue
        if nome_dim not in dimensoes:
            continue
        if col_pk not in dimensoes[nome_dim].columns:
            continue

        # IDs que existem em vendas mas NÃO existem na dimensão
        ids_vendas = set(df_vendas[col_fk].dropna().unique())
        ids_dim = set(dimensoes[nome_dim][col_pk].dropna().unique())
        ids_orfaos = ids_vendas - ids_dim

        if ids_orfaos:
            violacoes[col_fk] = len(ids_orfaos)

    if not violacoes:
        return ValidationResult(
            nome="integridade_referencial",
            passou=True,
            mensagem="OK — Todas as chaves estrangeiras têm correspondência nas dimensões.",
            critico=True,
        )
    else:
        return ValidationResult(
            nome="integridade_referencial",
            passou=False,
            mensagem=f"FALHA — IDs órfãos encontrados em {len(violacoes)} chave(s) estrangeira(s).",
            critico=True,
            detalhes=str(violacoes),
        )


def validar_duplicidade_transacoes(df_vendas: pd.DataFrame) -> ValidationResult:
    """
    TESTE 3: Verifica se a combinação Num Venda + Id Produto é única em fVendas.

    Esta combinação representa a chave natural de uma linha de pedido:
    um número de venda pode ter múltiplos produtos, mas a mesma
    combinação pedido+produto nunca deve aparecer mais de uma vez.
    Duplicidades neste nível causam dupla contagem de faturamento.

    Args:
        df_vendas (pd.DataFrame): DataFrame de vendas transformado.

    Returns:
        ValidationResult: Resultado do teste.
    """
    colunas_chave = ["Num Venda", "Id Produto"]

    if not all(col in df_vendas.columns for col in colunas_chave):
        return ValidationResult(
            nome="duplicidade_transacoes",
            passou=False,
            mensagem="AVISO — Colunas necessárias para teste de duplicidade não encontradas.",
            critico=False,
        )

    total = len(df_vendas)
    unicos = df_vendas[colunas_chave].drop_duplicates().shape[0]
    duplicados = total - unicos

    if duplicados == 0:
        return ValidationResult(
            nome="duplicidade_transacoes",
            passou=True,
            mensagem=f"OK — Nenhuma duplicidade em Num Venda + Id Produto ({total:,} linhas únicas).",
            critico=False,
        )
    else:
        return ValidationResult(
            nome="duplicidade_transacoes",
            passou=False,
            mensagem=f"FALHA — {duplicados:,} linhas duplicadas em Num Venda + Id Produto.",
            critico=False,
            detalhes=f"Total: {total:,} | Únicos: {unicos:,} | Duplicados: {duplicados:,}",
        )


def validar_cobertura_metas(df_metas: pd.DataFrame) -> ValidationResult:
    """
    TESTE 4: Verifica se todos os vendedores esperados têm meta definida
    para os 12 meses do ano.

    Um vendedor sem meta em algum mês causa denominador zero no KPI
    de % atingimento naquele período, distorcendo rankings e alertas.

    Args:
        df_metas (pd.DataFrame): DataFrame de metas no formato long
            (pós UNPIVOT de transform_metas).

    Returns:
        ValidationResult: Resultado do teste.
    """
    if "Id Vendedor" not in df_metas.columns or "Ano" not in df_metas.columns:
        return ValidationResult(
            nome="cobertura_metas",
            passou=False,
            mensagem="AVISO — Colunas esperadas não encontradas no DataFrame de metas.",
            critico=False,
        )

    # Conta meses distintos por vendedor por ano
    cobertura = (
        df_metas.groupby(["Id Vendedor", "Ano"])["Mes"]
        .nunique()
        .reset_index(name="qtd_meses")
    )

    # Vendedores com menos de 12 meses em algum ano
    incompletos = cobertura[cobertura["qtd_meses"] < QTD_MESES_ESPERADOS]

    # Vendedores distintos (independente do ano)
    qtd_vendedores = df_metas["Id Vendedor"].nunique()

    problemas = []
    if len(incompletos) > 0:
        problemas.append(f"{len(incompletos)} combinação(ões) vendedor-ano com menos de 12 meses.")
    if qtd_vendedores < QTD_VENDEDORES_ESPERADOS:
        problemas.append(
            f"Apenas {qtd_vendedores} vendedores (esperado: {QTD_VENDEDORES_ESPERADOS})."
        )

    if not problemas:
        return ValidationResult(
            nome="cobertura_metas",
            passou=True,
            mensagem=(
                f"OK — {qtd_vendedores} vendedores com meta completa "
                f"(12 meses) em todos os anos."
            ),
            critico=True,
        )
    else:
        return ValidationResult(
            nome="cobertura_metas",
            passou=False,
            mensagem=f"FALHA — Cobertura de metas incompleta: {'; '.join(problemas)}",
            critico=True,
            detalhes=incompletos.to_string() if len(incompletos) > 0 else None,
        )


def validar_valores_negativos_faturamento(df_vendas: pd.DataFrame) -> ValidationResult:
    """
    TESTE 5: Verifica se existem valores negativos em Faturamento Total.

    Faturamento negativo é inválido neste contexto de negócio (vendas
    e não devoluções). Valores negativos indicam problema na fonte
    (Excel) — célula com fórmula errada, dados corrompidos, etc.

    Args:
        df_vendas (pd.DataFrame): DataFrame de vendas transformado.

    Returns:
        ValidationResult: Resultado do teste.
    """
    col = "Faturamento Total"
    if col not in df_vendas.columns:
        return ValidationResult(
            nome="valores_negativos_faturamento",
            passou=False,
            mensagem=f"AVISO — Coluna '{col}' não encontrada.",
            critico=False,
        )

    negativos = (df_vendas[col] < 0).sum()

    if negativos == 0:
        return ValidationResult(
            nome="valores_negativos_faturamento",
            passou=True,
            mensagem=f"OK — Nenhum valor negativo em Faturamento Total.",
            critico=True,
        )
    else:
        return ValidationResult(
            nome="valores_negativos_faturamento",
            passou=False,
            mensagem=f"FALHA — {negativos:,} linhas com Faturamento Total negativo.",
            critico=True,
            detalhes=f"Soma dos negativos: R$ {df_vendas.loc[df_vendas[col] < 0, col].sum():,.2f}",
        )


def validar_data_envio_posterior_venda(df_vendas: pd.DataFrame) -> ValidationResult:
    """
    TESTE 6: Verifica se Data Envio >= Data da venda em todas as linhas.

    Um produto não pode ser enviado antes de ser vendido. Violações
    indicam erro de preenchimento manual no Excel (datas trocadas).

    Args:
        df_vendas (pd.DataFrame): DataFrame de vendas transformado.

    Returns:
        ValidationResult: Resultado do teste.
    """
    col_data = "Data"
    col_envio = "Data Envio"

    if col_data not in df_vendas.columns or col_envio not in df_vendas.columns:
        return ValidationResult(
            nome="data_envio_posterior_venda",
            passou=False,
            mensagem="AVISO — Colunas de data não encontradas para validação.",
            critico=False,
        )

    # Filtra apenas linhas onde ambas as datas são válidas (não NaT)
    mask_validas = df_vendas[col_data].notna() & df_vendas[col_envio].notna()
    df_valid = df_vendas[mask_validas]

    violacoes = (df_valid[col_envio] < df_valid[col_data]).sum()

    if violacoes == 0:
        return ValidationResult(
            nome="data_envio_posterior_venda",
            passou=True,
            mensagem="OK — Data de envio >= data de venda em todos os registros.",
            critico=False,  # Não crítico: pode ocorrer em casos de ajuste logístico
        )
    else:
        return ValidationResult(
            nome="data_envio_posterior_venda",
            passou=False,
            mensagem=f"AVISO — {violacoes:,} linhas onde Data Envio < Data da venda.",
            critico=False,  # Aviso, não bloqueia — investigar, mas não parar pipeline
        )


def validar_contagem_linhas(
    df_origem: pd.DataFrame,
    df_destino: pd.DataFrame,
    nome_tabela: str,
    tolerancia: int = 0
) -> ValidationResult:
    """
    TESTE 7: Verifica se a contagem de linhas após a carga no SQL Server
    corresponde à contagem esperada do DataFrame transformado.

    Esse teste é executado APÓS a carga (load.py) para confirmar que
    todas as linhas foram persistidas corretamente.

    Args:
        df_origem (pd.DataFrame): DataFrame com as linhas que deveriam ser carregadas.
        df_destino (pd.DataFrame): DataFrame lido do banco após a carga.
        nome_tabela (str): Nome da tabela para exibição no log.
        tolerancia (int): Diferença máxima aceitável (default=0 = correspondência exata).

    Returns:
        ValidationResult: Resultado do teste.
    """
    esperado = len(df_origem)
    carregado = len(df_destino)
    diferenca = abs(esperado - carregado)

    if diferenca <= tolerancia:
        return ValidationResult(
            nome=f"contagem_linhas_{nome_tabela}",
            passou=True,
            mensagem=f"OK — {nome_tabela}: {carregado:,} linhas carregadas (esperado: {esperado:,}).",
            critico=True,
        )
    else:
        return ValidationResult(
            nome=f"contagem_linhas_{nome_tabela}",
            passou=False,
            mensagem=f"FALHA — {nome_tabela}: {carregado:,} carregadas vs {esperado:,} esperadas.",
            critico=True,
            detalhes=f"Diferença: {diferenca:,} linhas.",
        )


def validar_status_validos(df_vendas: pd.DataFrame) -> ValidationResult:
    """
    TESTE 8: Verifica se todos os valores de Id Status em fVendas
    pertencem ao conjunto de status válidos definidos em dStatus.

    Status inválidos indicam que o dado veio com um código novo que
    não foi mapeado na dimensão — pode ser erro de digitação ou
    necessidade de atualizar a tabela dStatus.

    Args:
        df_vendas (pd.DataFrame): DataFrame de vendas transformado.

    Returns:
        ValidationResult: Resultado do teste.
    """
    col = "Id Status"
    if col not in df_vendas.columns:
        return ValidationResult(
            nome="status_validos",
            passou=False,
            mensagem=f"AVISO — Coluna '{col}' não encontrada.",
            critico=False,
        )

    # Converte para int para comparar com o set de STATUS_VALIDOS
    status_no_df = set(df_vendas[col].dropna().astype(int).unique())
    status_invalidos = status_no_df - STATUS_VALIDOS

    if not status_invalidos:
        return ValidationResult(
            nome="status_validos",
            passou=True,
            mensagem=f"OK — Todos os {len(status_no_df)} status encontrados são válidos.",
            critico=True,
        )
    else:
        qtd_linhas = df_vendas[df_vendas[col].isin(status_invalidos)].shape[0]
        return ValidationResult(
            nome="status_validos",
            passou=False,
            mensagem=f"FALHA — {len(status_invalidos)} código(s) de status inválido(s) em {qtd_linhas:,} linhas.",
            critico=True,
            detalhes=f"Códigos inválidos: {status_invalidos}. Válidos esperados: {STATUS_VALIDOS}",
        )


# =============================================================================
# VALIDAÇÕES DA CAMADA RAW (pós-extração, pré-transformação)
# =============================================================================
# Estas funções verificam ESTRUTURA e VOLUME — o dado ainda está em formato
# bruto (strings do Excel). A camada raw não tem regras de negócio; o objetivo
# aqui é detectar problemas na FONTE antes de tentar transformar.
#
# Diferença em relação às validações de staging:
#   Raw    → colunas presentes? volume mínimo? anos corretos?
#   Staging → integridade referencial? duplicatas? regras de negócio?
# =============================================================================

# Colunas mínimas esperadas em fVendas no estado bruto (strings)
VENDAS_RAW_COLUNAS_MINIMAS: set[str] = {
    "Data", "Num Venda", "Id Produto", "Id Vendedor",
    "Faturamento Total", "Custo Total", "Qtde",
}

# Volume mínimo aceitável de linhas em fVendas raw
# Dataset esperado: ~20.004 linhas. Threshold de 100 é segurança conservadora.
VENDAS_RAW_VOLUME_MINIMO: int = 100


def validar_colunas_raw_vendas(df_vendas_raw: pd.DataFrame) -> ValidationResult:
    """
    TESTE RAW 1: Verifica se as colunas mínimas esperadas existem em fVendas.

    Por que é útil?
    Se o layout do Excel de origem mudar (ex: coluna renomeada de "Faturamento
    Total" para "Fat. Total"), o pipeline falharia com KeyError silencioso
    na transformação. Detectar aqui produz uma mensagem clara com o nome exato
    da coluna ausente.

    Args:
        df_vendas_raw: DataFrame bruto retornado por extract_vendas().

    Returns:
        ValidationResult: Resultado do teste.
    """
    colunas_presentes = set(df_vendas_raw.columns)
    ausentes = VENDAS_RAW_COLUNAS_MINIMAS - colunas_presentes

    if not ausentes:
        return ValidationResult(
            nome="colunas_raw_vendas",
            passou=True,
            mensagem=(
                f"OK — Todas as {len(VENDAS_RAW_COLUNAS_MINIMAS)} colunas "
                f"mínimas estão presentes em fVendas raw."
            ),
            critico=True,
        )
    return ValidationResult(
        nome="colunas_raw_vendas",
        passou=False,
        mensagem=(
            f"FALHA — {len(ausentes)} coluna(s) ausente(s) em fVendas raw. "
            f"Verifique se o layout do Excel foi alterado."
        ),
        critico=True,
        detalhes=f"Ausentes: {ausentes}",
    )


def validar_volume_raw_vendas(df_vendas_raw: pd.DataFrame) -> ValidationResult:
    """
    TESTE RAW 2: Verifica se o volume de linhas brutas é aceitável.

    Um arquivo lido com skiprows errado ou truncado terá muito menos linhas
    que o esperado. Este teste captura isso antes que a transformação produza
    um staging inválido silenciosamente.

    Args:
        df_vendas_raw: DataFrame bruto retornado por extract_vendas().

    Returns:
        ValidationResult: Resultado do teste.
    """
    linhas = len(df_vendas_raw)

    if linhas >= VENDAS_RAW_VOLUME_MINIMO:
        return ValidationResult(
            nome="volume_raw_vendas",
            passou=True,
            mensagem=(
                f"OK — fVendas raw tem {linhas:,} linhas "
                f"(mínimo: {VENDAS_RAW_VOLUME_MINIMO:,})."
            ),
            critico=True,
        )
    return ValidationResult(
        nome="volume_raw_vendas",
        passou=False,
        mensagem=(
            f"FALHA — fVendas raw tem apenas {linhas:,} linhas "
            f"(esperado >= {VENDAS_RAW_VOLUME_MINIMO:,})."
        ),
        critico=True,
        detalhes=(
            "Verifique se Vendas.xlsx está íntegro e se VENDAS_SKIPROWS "
            "está configurado corretamente para o cabeçalho deste arquivo."
        ),
    )


def validar_anos_metas_raw(metas_raw: dict) -> ValidationResult:
    """
    TESTE RAW 3: Verifica se todos os anos configurados em METAS_ANOS foram lidos.

    Se um arquivo anual estiver faltando (ex: Meta 2020.xlsx deletado), a
    transformação produziria um staging de metas incompleto sem aviso claro.
    Este teste identifica o gap na fonte antes da transformação.

    Args:
        metas_raw: Dicionário {ano: DataFrame} retornado por extract_metas().

    Returns:
        ValidationResult: Resultado do teste.
    """
    from src.config.settings import METAS_ANOS

    anos_lidos = set(metas_raw.keys())
    anos_esperados = set(METAS_ANOS)
    ausentes = anos_esperados - anos_lidos

    if not ausentes:
        return ValidationResult(
            nome="anos_metas_raw",
            passou=True,
            mensagem=(
                f"OK — Todos os {len(anos_esperados)} anos de meta lidos: "
                f"{sorted(anos_lidos)}."
            ),
            critico=True,
        )
    return ValidationResult(
        nome="anos_metas_raw",
        passou=False,
        mensagem=(
            f"FALHA — {len(ausentes)} ano(s) de meta ausente(s). "
            f"Verifique os arquivos em data/raw/."
        ),
        critico=True,
        detalhes=f"Anos ausentes: {ausentes}. Lidos: {sorted(anos_lidos)}.",
    )


def validar_estrutura_raw_metas(metas_raw: dict) -> ValidationResult:
    """
    TESTE RAW 4: Verifica se os arquivos de meta têm o formato wide esperado.

    O UNPIVOT de transform_metas() depende de:
    - Coluna 'Id Vendedor' para identificar o vendedor
    - Colunas mensais ('janeiro', 'fevereiro', ...) com os valores de meta

    Se o Excel de meta tiver o layout alterado (ex: colunas em inglês), este
    teste captura antes que o UNPIVOT falhe silenciosamente com 0 linhas.

    Args:
        metas_raw: Dicionário {ano: DataFrame} retornado por extract_metas().

    Returns:
        ValidationResult: Resultado do teste.
    """
    problemas: list[str] = []

    for ano, df in metas_raw.items():
        colunas_lower = [c.lower().strip() for c in df.columns]

        if "id vendedor" not in colunas_lower:
            problemas.append(f"Meta {ano}: coluna 'Id Vendedor' ausente")

        if "janeiro" not in colunas_lower:
            problemas.append(
                f"Meta {ano}: coluna 'janeiro' ausente "
                f"(formato wide com meses em português esperado)"
            )

    if not problemas:
        return ValidationResult(
            nome="estrutura_raw_metas",
            passou=True,
            mensagem=(
                f"OK — Todos os {len(metas_raw)} arquivos de meta "
                f"têm o formato wide esperado."
            ),
            critico=True,
        )
    return ValidationResult(
        nome="estrutura_raw_metas",
        passou=False,
        mensagem=(
            f"FALHA — {len(problemas)} problema(s) de estrutura nos arquivos de meta."
        ),
        critico=True,
        detalhes="; ".join(problemas),
    )


def run_raw_validations(
    df_vendas_raw: pd.DataFrame,
    metas_raw: dict,
) -> ValidationReport:
    """
    Executa validações estruturais na camada RAW (pós-extração, pré-transformação).

    Momento de execução no pipeline:
        extract() → run_raw_validations() → transform() → run_all_validations()

    Foco desta camada:
    - Estrutura: as colunas certas estão presentes?
    - Volume: o arquivo veio com linhas suficientes?
    - Completude: todos os arquivos de fonte foram lidos?

    Não valida regras de negócio (integridade referencial, duplicatas, etc.)
    pois o dado ainda está em formato bruto de string.

    Args:
        df_vendas_raw: DataFrame bruto retornado por extract_vendas().
        metas_raw: Dicionário {ano: DataFrame} retornado por extract_metas().

    Returns:
        ValidationReport: Relatório com resultados dos 4 testes raw.

    Raises:
        ValueError: Se algum teste crítico falhar — pipeline é interrompido
                    antes de tentar transformar um dado estruturalmente inválido.
    """
    logger.info("=== Iniciando validações RAW (estrutura e volume) ===")
    relatorio = ValidationReport()

    testes = [
        validar_colunas_raw_vendas(df_vendas_raw),
        validar_volume_raw_vendas(df_vendas_raw),
        validar_anos_metas_raw(metas_raw),
        validar_estrutura_raw_metas(metas_raw),
    ]

    for resultado in testes:
        relatorio.resultados.append(resultado)
        if resultado.passou:
            logger.info(f"  [PASS] {resultado.nome}: {resultado.mensagem}")
        elif resultado.critico:
            logger.error(f"  [FAIL] {resultado.nome}: {resultado.mensagem}")
            if resultado.detalhes:
                logger.error(f"         Detalhes: {resultado.detalhes}")
        else:
            logger.warning(f"  [WARN] {resultado.nome}: {resultado.mensagem}")
            if resultado.detalhes:
                logger.warning(f"         Detalhes: {resultado.detalhes}")

    logger.info(relatorio.resumo())

    if not relatorio.pipeline_pode_continuar:
        raise ValueError(
            f"Pipeline interrompido na camada RAW: "
            f"{relatorio.reprovados_criticos} teste(s) estrutural(is) falharam. "
            f"Verifique os arquivos de origem antes de reprocessar."
        )

    return relatorio


# =============================================================================
# RUNNER CONSOLIDADO
# =============================================================================

def run_all_validations(
    df_vendas: pd.DataFrame,
    df_metas: pd.DataFrame,
    dimensoes: dict[str, pd.DataFrame],
) -> ValidationReport:
    """
    Executa todos os testes de validação e retorna um relatório consolidado.

    Se algum teste CRÍTICO falhar, lança uma exceção para interromper
    o pipeline antes que dados corrompidos cheguem ao banco de dados.

    Args:
        df_vendas (pd.DataFrame): DataFrame de vendas transformado.
        df_metas (pd.DataFrame): DataFrame de metas no formato long.
        dimensoes (dict[str, pd.DataFrame]): Dicionário de dimensões transformadas.

    Returns:
        ValidationReport: Relatório com todos os resultados.

    Raises:
        ValueError: Se algum teste crítico falhar.
    """
    logger.info("=== Iniciando execução dos testes de validação ===")
    relatorio = ValidationReport()

    # Lista de todos os testes a executar
    # [REUTILIZAÇÃO]: Adicione novos testes nesta lista seguindo o mesmo padrão
    testes = [
        validar_nulos_chave_primaria(df_vendas),
        validar_integridade_referencial(df_vendas, dimensoes),
        validar_duplicidade_transacoes(df_vendas),
        validar_cobertura_metas(df_metas),
        validar_valores_negativos_faturamento(df_vendas),
        validar_data_envio_posterior_venda(df_vendas),
        validar_status_validos(df_vendas),
    ]

    # Processa cada resultado e loga adequadamente
    for resultado in testes:
        relatorio.resultados.append(resultado)

        if resultado.passou:
            logger.info(f"  [PASS] {resultado.nome}: {resultado.mensagem}")
        elif resultado.critico:
            logger.error(f"  [FAIL] {resultado.nome}: {resultado.mensagem}")
            if resultado.detalhes:
                logger.error(f"         Detalhes: {resultado.detalhes}")
        else:
            logger.warning(f"  [WARN] {resultado.nome}: {resultado.mensagem}")
            if resultado.detalhes:
                logger.warning(f"         Detalhes: {resultado.detalhes}")

    # Loga o resumo do relatório
    logger.info(relatorio.resumo())

    # Se houver falha crítica, interrompe o pipeline antes da carga
    if not relatorio.pipeline_pode_continuar:
        raise ValueError(
            f"Pipeline interrompido: {relatorio.reprovados_criticos} teste(s) "
            f"crítico(s) falharam. Verifique o log para detalhes."
        )

    return relatorio

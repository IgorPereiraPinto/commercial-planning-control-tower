# =============================================================================
# test_validate.py — Testes automatizados para o módulo de validação
# Planejamento Comercial
# =============================================================================

import pytest
import pandas as pd
import numpy as np

from src.etl.validate import (
    validar_nulos_chave_primaria,
    validar_integridade_referencial,
    validar_duplicidade_transacoes,
    validar_cobertura_metas,
    validar_valores_negativos_faturamento,
    validar_data_envio_posterior_venda,
    validar_status_validos,
    run_all_validations,
    ValidationResult,
    ValidationReport,
)


# =============================================================================
# FIXTURES BASE
# =============================================================================

@pytest.fixture
def df_vendas_valido() -> pd.DataFrame:
    """DataFrame de vendas completamente válido — todos os testes devem passar."""
    return pd.DataFrame({
        "Data": pd.to_datetime(["2018-01-01", "2018-01-15"]),
        "Data Envio": pd.to_datetime(["2018-01-11", "2018-01-25"]),
        "Num Venda": ["2018VA1804", "2018VA1805"],
        "Id Produto": pd.array([44, 12], dtype="Int64"),
        "Id Vendedor": pd.array([1, 2], dtype="Int64"),
        "Nome Vendedor": ["Ronaldo", "Rodrigo"],
        "Id Cliente": pd.array([100, 200], dtype="Int64"),
        "Nome Cliente": ["Cliente A", "Cliente B"],
        "Id Unidade": pd.array([2, 1], dtype="Int64"),
        "Nome Unidade": ["Filial 2", "Filial 1"],
        "Id Status": pd.array([1, 1], dtype="Int64"),
        "Id Pgto": pd.array([1, 2], dtype="Int64"),
        "Qtde": [64.0, 10.0],
        "Valor Unit": [573.63, 1200.00],
        "Custo Unit": [380.00, 900.00],
        "Despesa Unit": [20.00, 30.00],
        "Impostos Unit": [57.00, 120.00],
        "Comissão Unit": [28.00, 60.00],
        "Faturamento Total": [36712.32, 12000.00],
        "Custo Total": [24320.00, 9000.00],
    })


@pytest.fixture
def dimensoes_validas() -> dict:
    """Dimensões válidas com os IDs presentes no df_vendas_valido."""
    return {
        "vendedor": pd.DataFrame({"Id Vendedor": pd.array([1, 2, 3], dtype="Int64")}),
        "produtos": pd.DataFrame({"Id Produto": pd.array([44, 12, 7], dtype="Int64")}),
        "unidades": pd.DataFrame({"Id Unidade": pd.array([1, 2, 3], dtype="Int64")}),
        "status": pd.DataFrame({"Id Status": pd.array([1, 2, 3], dtype="Int64")}),
        "pagamento": pd.DataFrame({"Id Pagamento": pd.array([1, 2, 3], dtype="Int64")}),
    }


@pytest.fixture
def df_metas_validas() -> pd.DataFrame:
    """DataFrame de metas válido com 11 vendedores × 12 meses."""
    linhas = []
    for id_vendedor in range(1, 12):  # 11 vendedores
        for mes in range(1, 13):  # 12 meses
            linhas.append({
                "Id Vendedor": id_vendedor,
                "Vendedor": f"Vendedor {id_vendedor}",
                "Ano": 2018,
                "Mes": mes,
                "Data Meta": pd.Timestamp(f"2018-{mes:02d}-01"),
                "Valor Meta": 1_000_000.0 * id_vendedor,
            })
    return pd.DataFrame(linhas)


# =============================================================================
# TESTES: validar_nulos_chave_primaria
# =============================================================================

class TestValidarNulosChavePrimaria:

    def test_passa_sem_nulos(self, df_vendas_valido):
        result = validar_nulos_chave_primaria(df_vendas_valido)
        assert result.passou is True

    def test_falha_com_nulo_em_id_vendedor(self, df_vendas_valido):
        df_com_nulo = df_vendas_valido.copy()
        df_com_nulo.loc[0, "Id Vendedor"] = pd.NA
        result = validar_nulos_chave_primaria(df_com_nulo)
        assert result.passou is False
        assert result.critico is True

    def test_falha_com_nulo_em_faturamento_total(self, df_vendas_valido):
        df_com_nulo = df_vendas_valido.copy()
        df_com_nulo.loc[0, "Faturamento Total"] = np.nan
        result = validar_nulos_chave_primaria(df_com_nulo)
        assert result.passou is False


# =============================================================================
# TESTES: validar_integridade_referencial
# =============================================================================

class TestValidarIntegridadeReferencial:

    def test_passa_sem_ids_orfaos(self, df_vendas_valido, dimensoes_validas):
        result = validar_integridade_referencial(df_vendas_valido, dimensoes_validas)
        assert result.passou is True

    def test_falha_com_id_vendedor_orfao(self, df_vendas_valido, dimensoes_validas):
        """Vendedor com ID 999 não existe em dVendedor — deve falhar."""
        df_orfao = df_vendas_valido.copy()
        df_orfao.loc[0, "Id Vendedor"] = 999  # ID não existe na dimensão
        result = validar_integridade_referencial(df_orfao, dimensoes_validas)
        assert result.passou is False
        assert result.critico is True


# =============================================================================
# TESTES: validar_duplicidade_transacoes
# =============================================================================

class TestValidarDuplicidadeTransacoes:

    def test_passa_sem_duplicatas(self, df_vendas_valido):
        result = validar_duplicidade_transacoes(df_vendas_valido)
        assert result.passou is True

    def test_falha_com_linha_duplicada(self, df_vendas_valido):
        """Adiciona uma linha com mesmo Num Venda + Id Produto."""
        df_duplicado = pd.concat(
            [df_vendas_valido, df_vendas_valido.iloc[[0]]],
            ignore_index=True
        )
        result = validar_duplicidade_transacoes(df_duplicado)
        assert result.passou is False


# =============================================================================
# TESTES: validar_cobertura_metas
# =============================================================================

class TestValidarCoberturaMetas:

    def test_passa_com_cobertura_completa(self, df_metas_validas):
        result = validar_cobertura_metas(df_metas_validas)
        assert result.passou is True

    def test_falha_com_vendedor_sem_12_meses(self):
        """Vendedor com apenas 6 meses deve reprovar o teste."""
        df_incompleto = pd.DataFrame({
            "Id Vendedor": [1] * 6,
            "Ano": [2018] * 6,
            "Mes": list(range(1, 7)),  # Só 6 meses
            "Valor Meta": [1_000_000.0] * 6,
        })
        result = validar_cobertura_metas(df_incompleto)
        assert result.passou is False


# =============================================================================
# TESTES: validar_valores_negativos_faturamento
# =============================================================================

class TestValidarValoresNegativos:

    def test_passa_sem_negativos(self, df_vendas_valido):
        result = validar_valores_negativos_faturamento(df_vendas_valido)
        assert result.passou is True

    def test_falha_com_faturamento_negativo(self, df_vendas_valido):
        df_negativo = df_vendas_valido.copy()
        df_negativo.loc[0, "Faturamento Total"] = -1000.0
        result = validar_valores_negativos_faturamento(df_negativo)
        assert result.passou is False
        assert result.critico is True


# =============================================================================
# TESTES: validar_status_validos
# =============================================================================

class TestValidarStatusValidos:

    def test_passa_com_status_validos(self, df_vendas_valido):
        result = validar_status_validos(df_vendas_valido)
        assert result.passou is True

    def test_falha_com_status_desconhecido(self, df_vendas_valido):
        df_status = df_vendas_valido.copy()
        df_status.loc[0, "Id Status"] = 99  # Código não mapeado
        result = validar_status_validos(df_status)
        assert result.passou is False


# =============================================================================
# TESTES: run_all_validations (runner completo)
# =============================================================================

class TestRunAllValidations:

    def test_retorna_relatorio(self, df_vendas_valido, df_metas_validas, dimensoes_validas):
        relatorio = run_all_validations(df_vendas_valido, df_metas_validas, dimensoes_validas)
        assert isinstance(relatorio, ValidationReport)

    def test_todos_aprovados_com_dados_validos(
        self, df_vendas_valido, df_metas_validas, dimensoes_validas
    ):
        relatorio = run_all_validations(df_vendas_valido, df_metas_validas, dimensoes_validas)
        assert relatorio.pipeline_pode_continuar is True
        assert relatorio.reprovados_criticos == 0

    def test_levanta_excecao_com_dados_criticos_invalidos(
        self, df_metas_validas, dimensoes_validas
    ):
        """Com faturamento negativo (falha crítica), deve levantar ValueError."""
        df_invalido = pd.DataFrame({
            "Data": pd.to_datetime(["2018-01-01"]),
            "Data Envio": pd.to_datetime(["2018-01-11"]),
            "Num Venda": ["2018VA1804"],
            "Id Produto": pd.array([44], dtype="Int64"),
            "Id Vendedor": pd.array([1], dtype="Int64"),
            "Id Cliente": pd.array([100], dtype="Int64"),
            "Id Unidade": pd.array([1], dtype="Int64"),
            "Id Status": pd.array([1], dtype="Int64"),
            "Id Pgto": pd.array([1], dtype="Int64"),
            "Faturamento Total": [-999.00],  # NEGATIVO = falha crítica
            "Custo Total": [500.00],
            "Nome Vendedor": ["Ronaldo"],
            "Nome Cliente": ["A"],
            "Nome Unidade": ["Filial 1"],
            "Qtde": [1.0],
            "Valor Unit": [100.0],
            "Custo Unit": [60.0],
            "Despesa Unit": [5.0],
            "Impostos Unit": [10.0],
            "Comissão Unit": [5.0],
        })
        with pytest.raises(ValueError, match="Pipeline interrompido"):
            run_all_validations(df_invalido, df_metas_validas, dimensoes_validas)

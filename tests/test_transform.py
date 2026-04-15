# =============================================================================
# test_transform.py — Testes automatizados para o módulo de transformação
# Commercial Planning Control Tower
# =============================================================================

import pytest
import pandas as pd
import numpy as np

from src.etl.transform import (
    transform_vendas,
    transform_dimensoes,
    transform_metas,
    MESES_PT,
    COL_VENDAS_FATURAMENTO_TOTAL,
    COL_VENDAS_DATA,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def df_vendas_bruto() -> pd.DataFrame:
    """DataFrame bruto de vendas simulando o que extract_vendas() retorna."""
    return pd.DataFrame({
        "Data": ["01/01/2018", "15/01/2018"],
        "Data Envio": ["11/01/2018", "25/01/2018"],
        "Num Venda": ["2018VA1804", "2018VA1805"],
        "Id Produto": ["44", "12"],
        "Id Vendedor": ["1", "2"],
        "Nome Vendedor": ["  Ronaldo  ", "Rodrigo"],  # Espaços extras intencionais
        "Id Cliente": ["100", "200"],
        "Nome Cliente": ["Cliente A", "Cliente B"],
        "Id Unidade": ["2", "1"],
        "Nome Unidade": ["Filial 2", "Filial 1"],
        "Id Status": ["1", "1"],
        "Id Pgto": ["1", "2"],
        "Qtde": ["64", "10"],
        "Valor Unit": ["573.63", "1200.00"],
        "Custo Unit": ["380.00", "900.00"],
        "Despesa Unit": ["20.00", "30.00"],
        "Impostos Unit": ["57.00", "120.00"],
        "Comissão Unit": ["28.00", "60.00"],
        "Faturamento Total": ["36712.32", "12000.00"],
        "Custo Total": ["24320.00", "9000.00"],
    })


@pytest.fixture
def df_meta_bruta() -> pd.DataFrame:
    """DataFrame bruto de meta no formato wide."""
    return pd.DataFrame({
        "Id Vendedor": ["1", "2"],
        "Vendedor": ["Ronaldo", "Rodrigo"],
        "janeiro": ["5000000", "2000000"],
        "fevereiro": ["4800000", "2100000"],
        "março": ["5200000", "1900000"],
        "abril": ["11700000", "2300000"],
        "maio": ["3900000", "2000000"],
        "junho": ["4100000", "1800000"],
        "julho": ["4500000", "2200000"],
        "agosto": ["4800000", "2100000"],
        "setembro": ["5100000", "2300000"],
        "outubro": ["5400000", "2500000"],
        "novembro": ["5800000", "2600000"],
        "dezembro": ["6900000", "3000000"],
    })


# =============================================================================
# TESTES: transform_vendas
# =============================================================================

class TestTransformVendas:

    def test_retorna_dataframe(self, df_vendas_bruto):
        result = transform_vendas(df_vendas_bruto)
        assert isinstance(result, pd.DataFrame)

    def test_nao_altera_original(self, df_vendas_bruto):
        """A transformação não deve modificar o DataFrame original."""
        df_copia = df_vendas_bruto.copy()
        transform_vendas(df_vendas_bruto)
        pd.testing.assert_frame_equal(df_vendas_bruto, df_copia)

    def test_data_convertida_para_datetime(self, df_vendas_bruto):
        """A coluna Data deve ser datetime após transformação."""
        result = transform_vendas(df_vendas_bruto)
        assert pd.api.types.is_datetime64_any_dtype(result[COL_VENDAS_DATA]), (
            "Coluna 'Data' deveria ser datetime64, verifique o cast de tipo."
        )

    def test_faturamento_convertido_para_float(self, df_vendas_bruto):
        """Faturamento Total deve ser numérico após transformação."""
        result = transform_vendas(df_vendas_bruto)
        assert pd.api.types.is_float_dtype(result[COL_VENDAS_FATURAMENTO_TOTAL])

    def test_strings_sem_espacos_extras(self, df_vendas_bruto):
        """Strings não devem ter espaços antes ou depois após transformação."""
        result = transform_vendas(df_vendas_bruto)
        # "  Ronaldo  " deve virar "Ronaldo"
        nomes = result["Nome Vendedor"].dropna().tolist()
        for nome in nomes:
            assert nome == nome.strip(), f"String com espaço extra: '{nome}'"

    def test_metadados_etl_adicionados(self, df_vendas_bruto):
        """As colunas _etl_loaded_at e _etl_source devem ser adicionadas."""
        result = transform_vendas(df_vendas_bruto)
        assert "_etl_loaded_at" in result.columns
        assert "_etl_source" in result.columns

    def test_linhas_com_faturamento_nulo_removidas(self):
        """Linhas com campos obrigatórios nulos devem ser removidas."""
        df_com_nulo = pd.DataFrame({
            "Data": ["01/01/2018", None],  # Segunda linha com Data nula
            "Data Envio": ["11/01/2018", "11/01/2018"],
            "Num Venda": ["2018VA1804", "2018VA1805"],
            "Id Produto": ["44", "12"],
            "Id Vendedor": ["1", "2"],
            "Nome Vendedor": ["Ronaldo", "Rodrigo"],
            "Id Cliente": ["100", "200"],
            "Nome Cliente": ["A", "B"],
            "Id Unidade": ["1", "1"],
            "Nome Unidade": ["Filial 1", "Filial 1"],
            "Id Status": ["1", "1"],
            "Id Pgto": ["1", "1"],
            "Qtde": ["10", "5"],
            "Valor Unit": ["100.00", "200.00"],
            "Custo Unit": ["60.00", "120.00"],
            "Despesa Unit": ["5.00", "10.00"],
            "Impostos Unit": ["10.00", "20.00"],
            "Comissão Unit": ["5.00", "10.00"],
            "Faturamento Total": ["1000.00", None],  # Nulo obrigatório
            "Custo Total": ["600.00", None],
        })
        result = transform_vendas(df_com_nulo)
        assert len(result) == 1, "Linha com Faturamento Total nulo deveria ser removida"


# =============================================================================
# TESTES: transform_metas (UNPIVOT)
# =============================================================================

class TestTransformMetas:

    def test_formato_long_tem_mais_linhas_que_wide(self, df_meta_bruta):
        """
        O UNPIVOT deve produzir mais linhas que o original.
        2 vendedores × 12 meses = 24 linhas (vs 2 no wide).
        """
        metas_raw = {2018: df_meta_bruta}
        result = transform_metas(metas_raw)
        assert len(result) > len(df_meta_bruta), (
            "Formato long deve ter mais linhas que o formato wide original"
        )

    def test_tem_exatamente_24_linhas_para_2_vendedores(self, df_meta_bruta):
        """2 vendedores × 12 meses = 24 linhas."""
        metas_raw = {2018: df_meta_bruta}
        result = transform_metas(metas_raw)
        assert len(result) == 24, (
            f"Esperado 24 linhas (2×12), obtido {len(result)}"
        )

    def test_tem_coluna_ano(self, df_meta_bruta):
        """O resultado deve ter coluna 'Ano'."""
        result = transform_metas({2018: df_meta_bruta})
        assert "Ano" in result.columns

    def test_tem_coluna_mes(self, df_meta_bruta):
        """O resultado deve ter coluna 'Mes' com valores de 1 a 12."""
        result = transform_metas({2018: df_meta_bruta})
        assert "Mes" in result.columns
        assert set(result["Mes"].dropna().astype(int).unique()) == set(range(1, 13))

    def test_tem_coluna_data_meta(self, df_meta_bruta):
        """O resultado deve ter coluna 'Data Meta' no formato datetime."""
        result = transform_metas({2018: df_meta_bruta})
        assert "Data Meta" in result.columns
        assert pd.api.types.is_datetime64_any_dtype(result["Data Meta"])

    def test_valor_meta_e_numerico(self, df_meta_bruta):
        """A coluna 'Valor Meta' deve ser numérica."""
        result = transform_metas({2018: df_meta_bruta})
        assert pd.api.types.is_float_dtype(result["Valor Meta"]) or \
               pd.api.types.is_integer_dtype(result["Valor Meta"])

    def test_consolidacao_multiplos_anos(self, df_meta_bruta):
        """Com 2 anos e 2 vendedores, devem resultar 48 linhas (2×12×2)."""
        metas_raw = {2018: df_meta_bruta, 2019: df_meta_bruta}
        result = transform_metas(metas_raw)
        assert len(result) == 48, (
            f"Esperado 48 linhas (2 anos × 2 vendedores × 12 meses), obtido {len(result)}"
        )

    def test_metadados_etl_adicionados(self, df_meta_bruta):
        """As colunas de metadados ETL devem estar presentes."""
        result = transform_metas({2018: df_meta_bruta})
        assert "_etl_loaded_at" in result.columns
        assert "_etl_source" in result.columns

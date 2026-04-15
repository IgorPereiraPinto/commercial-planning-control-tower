# =============================================================================
# test_extract.py — Testes automatizados para o módulo de extração
# Commercial Planning Control Tower
# =============================================================================
#
# COMO RODAR:
#   pytest tests/test_extract.py -v
#   pytest tests/ -v --cov=src          (com cobertura de código)
#
# ESTRATÉGIA DOS TESTES:
#   Testes de extração verificam a ESTRUTURA e PRESENÇA dos dados,
#   não os valores específicos (que mudam com o tempo). Isso torna
#   os testes robustos mesmo quando novos dados são adicionados.
# =============================================================================

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.etl.extract import (
    extract_dimensoes,
    extract_vendas,
    extract_metas,
    DIMENSOES_SHEETS,
    VENDAS_SKIPROWS,
)


# =============================================================================
# FIXTURES — Dados de teste reutilizáveis
# =============================================================================
# Fixtures do pytest são funções que produzem dados ou objetos de teste.
# Ao decorar com @pytest.fixture, o pytest injeta automaticamente nos testes.

@pytest.fixture
def df_vendas_amostra() -> pd.DataFrame:
    """
    Cria um DataFrame de vendas mínimo para testes unitários.
    Evita depender dos arquivos reais do projeto nos testes.
    """
    return pd.DataFrame({
        "Data": ["01/01/2018", "15/01/2018", "01/02/2018"],
        "Data Envio": ["11/01/2018", "25/01/2018", "10/02/2018"],
        "Num Venda": ["2018VA1804", "2018VA1805", "2018VA1806"],
        "Id Produto": ["44", "12", "7"],
        "Id Vendedor": ["1", "2", "3"],
        "Nome Vendedor": ["Ronaldo", "Rodrigo", "Paola"],
        "Id Cliente": ["100", "200", "300"],
        "Nome Cliente": ["Cliente A", "Cliente B", "Cliente C"],
        "Id Unidade": ["2", "1", "3"],
        "Nome Unidade": ["Filial 2", "Filial 1", "Filial 3"],
        "Id Status": ["1", "1", "2"],
        "Id Pgto": ["1", "2", "3"],
        "Qtde": ["64", "10", "5"],
        "Valor Unit": ["573.63", "1200.00", "850.50"],
        "Custo Unit": ["380.00", "900.00", "600.00"],
        "Despesa Unit": ["20.00", "30.00", "25.00"],
        "Impostos Unit": ["57.00", "120.00", "85.00"],
        "Comissão Unit": ["28.00", "60.00", "42.00"],
        "Faturamento Total": ["36712.32", "12000.00", "4252.50"],
        "Custo Total": ["24320.00", "9000.00", "3000.00"],
    })


@pytest.fixture
def df_meta_amostra() -> pd.DataFrame:
    """
    Cria um DataFrame de meta no formato wide (original do Excel) para testes.
    """
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
# TESTES: extract_dimensoes
# =============================================================================

class TestExtractDimensoes:
    """Testes para a função extract_dimensoes()."""

    def test_retorna_dicionario(self):
        """Verifica que a função retorna um dicionário (não uma lista ou DataFrame)."""
        result = extract_dimensoes()
        assert isinstance(result, dict), "extract_dimensoes deve retornar um dict"

    def test_contem_todas_as_chaves_esperadas(self):
        """Verifica que todas as 7 dimensões esperadas estão presentes no resultado."""
        result = extract_dimensoes()
        chaves_esperadas = set(DIMENSOES_SHEETS.keys())
        chaves_retornadas = set(result.keys())
        assert chaves_esperadas == chaves_retornadas, (
            f"Dimensões ausentes: {chaves_esperadas - chaves_retornadas}"
        )

    def test_cada_dimensao_e_dataframe(self):
        """Verifica que cada valor no dicionário é um DataFrame pandas."""
        result = extract_dimensoes()
        for nome, df in result.items():
            assert isinstance(df, pd.DataFrame), (
                f"Dimensão '{nome}' deveria ser DataFrame, mas é {type(df)}"
            )

    def test_dimensoes_nao_estao_vazias(self):
        """Verifica que nenhuma dimensão foi lida com zero linhas."""
        result = extract_dimensoes()
        for nome, df in result.items():
            assert len(df) > 0, f"Dimensão '{nome}' está vazia (0 linhas)"

    def test_dimensao_produtos_tem_colunas_esperadas(self):
        """Verifica as colunas mínimas esperadas em dProdutos."""
        result = extract_dimensoes()
        colunas_esperadas = {"Id Produto", "Produto", "Categoria"}
        colunas_presentes = set(result["produtos"].columns)
        assert colunas_esperadas.issubset(colunas_presentes), (
            f"Colunas ausentes em dProdutos: {colunas_esperadas - colunas_presentes}"
        )

    def test_arquivo_inexistente_levanta_file_not_found(self):
        """
        Verifica que um FileNotFoundError é levantado quando o arquivo não existe.
        Usa mock para simular arquivo ausente sem precisar deletar o arquivo real.
        """
        with patch("src.etl.extract.PATH_DIMENSOES", Path("/caminho/inexistente.xlsx")):
            with pytest.raises(FileNotFoundError):
                extract_dimensoes()


# =============================================================================
# TESTES: extract_vendas
# =============================================================================

class TestExtractVendas:
    """Testes para a função extract_vendas()."""

    def test_retorna_dataframe(self):
        """Verifica que a função retorna um DataFrame."""
        result = extract_vendas()
        assert isinstance(result, pd.DataFrame)

    def test_tem_linhas(self):
        """Verifica que o DataFrame de vendas tem pelo menos 1 linha."""
        result = extract_vendas()
        assert len(result) > 0, "fVendas não pode estar vazia"

    def test_tem_colunas_esperadas(self):
        """Verifica as colunas mínimas esperadas em fVendas."""
        result = extract_vendas()
        colunas_esperadas = {
            "Data", "Num Venda", "Id Produto", "Id Vendedor",
            "Faturamento Total", "Custo Total"
        }
        colunas_presentes = set(result.columns)
        assert colunas_esperadas.issubset(colunas_presentes), (
            f"Colunas ausentes em fVendas: {colunas_esperadas - colunas_presentes}"
        )

    def test_volume_minimo_de_linhas(self):
        """
        Verifica que o volume de dados é compatível com o esperado.
        O dataset tem ~20.004 linhas — alertamos se vier com menos de 1.000.
        [REUTILIZAÇÃO]: Ajuste o threshold para o volume do novo projeto.
        """
        result = extract_vendas()
        THRESHOLD_MINIMO = 1_000
        assert len(result) >= THRESHOLD_MINIMO, (
            f"fVendas tem apenas {len(result)} linhas (esperado >= {THRESHOLD_MINIMO}). "
            f"Verifique se o arquivo está correto."
        )

    def test_skiprows_correto(self):
        """
        Verifica que VENDAS_SKIPROWS está configurado para ignorar as linhas
        de título do Vendas.xlsx (linhas 1-4 antes do cabeçalho real).
        """
        assert VENDAS_SKIPROWS == 4, (
            f"VENDAS_SKIPROWS deveria ser 4, mas é {VENDAS_SKIPROWS}. "
            f"Verifique a estrutura do arquivo Vendas.xlsx."
        )


# =============================================================================
# TESTES: extract_metas
# =============================================================================

class TestExtractMetas:
    """Testes para a função extract_metas()."""

    def test_retorna_dicionario(self):
        """Verifica que a função retorna um dicionário."""
        result = extract_metas()
        assert isinstance(result, dict)

    def test_contem_anos_esperados(self):
        """Verifica que todos os anos configurados foram lidos."""
        from src.config.settings import METAS_ANOS
        result = extract_metas()
        for ano in METAS_ANOS:
            assert ano in result, f"Ano {ano} não encontrado no resultado de extract_metas()"

    def test_cada_ano_e_dataframe(self):
        """Verifica que cada valor é um DataFrame."""
        result = extract_metas()
        for ano, df in result.items():
            assert isinstance(df, pd.DataFrame), (
                f"Meta {ano} deveria ser DataFrame, mas é {type(df)}"
            )

    def test_metas_tem_coluna_vendedor(self):
        """Verifica que as tabelas de meta têm a coluna Id Vendedor."""
        result = extract_metas()
        for ano, df in result.items():
            assert "Id Vendedor" in df.columns, (
                f"Meta {ano} não tem coluna 'Id Vendedor'"
            )

    def test_metas_tem_colunas_mensais(self):
        """Verifica que as colunas de meses estão presentes nos arquivos de meta."""
        result = extract_metas()
        # Pelo menos janeiro deve existir como indicador de que é o formato esperado
        for ano, df in result.items():
            colunas_lower = [c.lower().strip() for c in df.columns]
            assert "janeiro" in colunas_lower, (
                f"Meta {ano} não tem coluna 'janeiro' — verifique o formato do arquivo."
            )

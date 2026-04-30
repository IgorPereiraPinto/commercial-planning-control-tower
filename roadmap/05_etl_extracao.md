# 05 — ETL: Extração

## O que o módulo de extração faz

`src/etl/extract.py` lê os três grupos de fontes:

- `extract_dimensoes()` — lê as 7 abas do Dimensoes.xlsx
- `extract_vendas()` — lê a planilha de transações
- `extract_metas()` — lê os 4 arquivos de meta anuais

Retorna DataFrames pandas sem nenhuma transformação de negócio.

---

## Validações feitas na extração

- existência dos arquivos no caminho configurado
- presença mínima de colunas esperadas por tabela
- volume mínimo de linhas (alerta se muito diferente do esperado)
- todas as abas do Dimensoes.xlsx presentes

---

## Como executar isoladamente

```bash
python -c "from src.etl.extract import extract_vendas; df = extract_vendas(); print(df.shape)"
```

---

## Próximo passo

[06_etl_transformacao_e_validacoes.md](06_etl_transformacao_e_validacoes.md)

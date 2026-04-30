# 06 — ETL: Transformação e Validações

## O que o módulo de transformação faz

`src/etl/transform.py` aplica:

- **Cast de tipos**: datas, inteiros, decimais
- **Trim de strings**: remove espaços em campos de texto
- **UNPIVOT das metas**: wide (Jan...Dez em colunas) → long (uma linha por mês)
- **Normalização de nomes**: padronização de vendedores e categorias
- **Remoção de nulos críticos**: em chaves primárias e FK

## Duas camadas de validação

| Quando | O que valida | Módulo |
|---|---|---|
| Pós-extração | Estrutura da fonte (colunas, volume, anos) | `validate.run_raw_validations()` |
| Pós-transformação | Regras de negócio (FK, duplicatas, valores) | `validate.run_all_validations()` |

## Testes de qualidade

| Teste | Regra |
|---|---|
| Nulos em chaves | Id Produto, Id Vendedor, Id Cliente != NULL |
| Integridade referencial | Todo Id Vendedor em fVendas existe em dVendedor |
| Duplicidade | Num Venda + Id Produto único em fVendas |
| Cobertura de metas | 11 vendedores com meta para os 12 meses |
| Valores negativos | Faturamento Total >= 0 |
| Data de envio | Data Envio >= Data |

---

## Próximo passo

[07_modelagem_raw.md](07_modelagem_raw.md)

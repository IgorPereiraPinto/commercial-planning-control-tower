# 07 — Modelagem: Camada RAW

## Papel do schema raw

Espelho fiel das fontes Excel. Nenhuma transformação de negócio.
Serve como landing de auditoria e ponto de reprocessamento.

## Tabelas do schema raw

```
raw.fVendas
raw.dProdutos
raw.dVendedor
raw.dClientes
raw.dCidade
raw.dUnidades
raw.dStatus
raw.dPagamento
raw.fMetas_2018
raw.fMetas_2019
raw.fMetas_2020
raw.fMetas_2021
```

## Script SQL

```text
sql/sqlserver/00_setup.sql        → cria banco e schemas
sql/sqlserver/01_raw_tables.sql   → cria tabelas raw
```

## Regra

A partir do RAW, nenhuma linha é removida ou modificada por SQL. Apenas lida.

---

## Próximo passo

[08_modelagem_staging.md](08_modelagem_staging.md)

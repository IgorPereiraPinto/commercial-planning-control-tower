# 08 — Modelagem: Camada Staging

## Papel do schema staging

Limpeza, tipagem, normalização e consolidação das metas.

## Tabelas do schema staging

```
staging.fVendas          → cast de tipos, trim de strings, remoção de nulos críticos
staging.dProdutos        → normalização de categoria/subcategoria
staging.dVendedor        → padronização de nomes, gerente normalizado
staging.dClientes        → validação de id cidade
staging.dCidade          → validação de UF/Estado
staging.dUnidades        → sem alteração relevante
staging.fMetas           → UNPIVOT: Id Vendedor | Ano | Mês | Valor Meta
```

## Transformação crítica: UNPIVOT das metas

Formato original (wide):
```
Id Vendedor | Jan | Fev | Mar | ... | Dez
```

Formato staging (long):
```
Id Vendedor | Ano | Mes | Valor Meta
```

## Script SQL

```text
sql/sqlserver/02_staging_tables.sql
```

---

## Próximo passo

[09_modelagem_dw.md](09_modelagem_dw.md)

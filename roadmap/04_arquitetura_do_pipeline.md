# 04 — Arquitetura do Pipeline

## Fluxo ponta a ponta

```text
[Excel: Dimensoes + Vendas + Metas]
          |
          v
  [Python ETL — src/etl/]
  extract → validate raw → transform → validate staging
          |
          v
  [SQL Server — schema: raw]
  espelho fiel das fontes
          |
          v
  [SQL Server — schema: staging]
  limpeza, tipagem, unpivot de metas
          |
          v
  [SQL Server — schema: dw]
  star schema: 2 fatos + 8 dimensões + dCalendario
          |
          v
  [Power BI]
  dataset + DAX + RLS por gerente
          |
          v
  [Power Automate]
  alertas + resumo semanal + refresh automático
```

---

## Decisão arquitetural

O Python ETL é a **porta de qualidade da fonte** — lida com o que o SQL não faz bem:
- leitura de Excel com múltiplas abas
- unpivot de metas (wide → long)
- validação de schema e integridade referencial
- coerção de tipos e tratamento de nulos

A partir do RAW SQL, vale a regra medallion:
- **RAW**: dado fiel à fonte, sem transformações de negócio
- **STAGING**: limpeza, tipagem, normalização
- **DW**: star schema pronto para consumo analítico

---

## Próximo passo

[05_etl_extracao.md](05_etl_extracao.md)

# sql/extras/

Esta pasta é reservada para queries SQL complementares e específicas do contexto de cada projeto.

## Propósito

Os scripts numerados em `sql/sqlserver/` (00 a 07) cobrem a estrutura base: setup, raw, staging, DW, calendário, índices e queries analíticas padrão.

Esta pasta recebe tudo que não faz parte da estrutura base, mas é necessário para um contexto específico:

| Tipo de arquivo | Exemplo |
|-----------------|---------|
| Views analíticas customizadas | `vw_performance_regional.sql` |
| Procedures de negócio | `sp_calcular_comissao_trimestre.sql` |
| Scripts de migração | `mig_ajuste_historico_2022.sql` |
| Queries ad hoc relevantes | `adhoc_analise_churn_clientes.sql` |
| Scripts de manutenção | `maint_rebuild_indexes.sql` |
| Queries de diagnóstico | `diag_duplicidade_vendas.sql` |

## Convenção de nomenclatura

```
<tipo>_<descricao_breve>.sql
```

- `vw_`   — views
- `sp_`   — stored procedures
- `fn_`   — functions
- `mig_`  — migrações
- `adhoc_` — análises pontuais
- `diag_` — diagnóstico e qualidade
- `maint_` — manutenção

## Reutilização

Ao adaptar o projeto para um novo contexto, copie para cá qualquer query que seja específica do seu negócio e não deva alterar os scripts base. Isso mantém `sql/sqlserver/` limpo e reutilizável entre projetos.

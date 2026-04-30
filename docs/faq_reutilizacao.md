# FAQ de Reutilização — planejamento-comercial

## Posso usar este projeto com outro banco de dados?

Sim. O Python ETL é independente do banco. A carga no SQL Server está isolada em `src/etl/load.py` e `src/etl/load_dw.py`. Para outro banco:
1. Instale o driver correspondente (ex: `psycopg2` para PostgreSQL)
2. Ajuste `get_connection_string()` em `src/config/settings.py`
3. Os scripts SQL podem precisar de ajustes de sintaxe por dialeto

---

## Posso usar com mais anos de dados?

Sim. Ajuste no `.env`:
```
METAS_ANOS=2018,2019,2020,2021,2022,2023
```
O ETL lê automaticamente todos os anos configurados, buscando arquivos `Meta_XXXX.xlsx` em `data/raw/`.

---

## O que muda se eu tiver vendedores diferentes?

- `src/etl/validate.py` — ajuste a lista de vendedores esperados nos testes
- `powerbi/rls/rls_roles_completo.md` — ajuste os grupos de gerentes
- `sql/sqlserver/02_staging_tables.sql` — o UNPIVOT é dinâmico, mas revise a normalização de nomes

---

## O projeto funciona sem SQL Server?

O ETL Python roda sem banco. Use `--dry-run` para validar os dados sem carga:
```bash
python run_etl.py --dry-run
```
Para exportar CSVs em vez de carregar no banco, adapte `src/etl/load.py` para gravar em `data/processed/`.

---

## Como adaptar o dashboard HTML para meus dados?

O dashboard em `dashboards/planejamento_comercial.html` usa dados embutidos em JavaScript. Para conectar dados reais:
1. Gere JSONs ou CSVs a partir das queries de `sql/sqlserver/07_analytical_queries.sql`
2. Substitua os arrays de dados no início do HTML
3. A estrutura de KPIs, filtros e graficos permanece a mesma

---

## Como adaptar a regra de comissao?

- ajuste as faixas de payout em `docs/comissionamento.md`
- mova as regras para tabelas parametricas no DW quando quiser automatizar
- mantenha prioridade de produto fora do HTML para evitar excecoes manuais

---

## Posso usar este projeto como portfólio?

Sim. Basta:
1. Criar um fork no GitHub
2. Reescrever o `README.md` para seu contexto
3. Publicar o dashboard via GitHub Pages
4. Adaptar o roadmap para documentar seu processo

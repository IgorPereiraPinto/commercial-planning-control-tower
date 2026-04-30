# Template para Novo Case — planejamento-comercial

Use este guia para adaptar o projeto a um novo contexto de planejamento comercial ou vendas.

---

## Checklist de adaptação

### 1. Dados

- [ ] Substituir arquivos em `data/raw/` pelas novas fontes
- [ ] Atualizar paths no `.env`
- [ ] Verificar estrutura das abas e nomes de colunas

### 2. ETL Python

- [ ] Ajustar `src/etl/extract.py` para as novas abas e colunas
- [ ] Revisar regras de limpeza em `src/etl/transform.py`
- [ ] Atualizar validações em `src/etl/validate.py` (vendedores, anos, campos obrigatórios)

### 3. SQL

- [ ] Ajustar DDL em `sql/sqlserver/01_raw_tables.sql` para novo schema
- [ ] Revisar UNPIVOT e transformações em `sql/sqlserver/02_staging_tables.sql`
- [ ] Adaptar star schema em `sql/sqlserver/03_dw_dimensions.sql` e `04_dw_facts.sql`
- [ ] Rever queries analíticas em `sql/sqlserver/07_analytical_queries.sql`

### 4. Power BI

- [ ] Adaptar medidas em `powerbi/dax/medidas_completas.dax`
- [ ] Ajustar RLS em `powerbi/rls/rls_roles_completo.md`
- [ ] Revisar estrutura de páginas

### 5. Documentação

- [ ] Reescrever `README.md` para o novo contexto
- [ ] Atualizar `docs/dicionario_de_dados.md`
- [ ] Atualizar `docs/regras_de_negocio.md`
- [ ] Ajustar roadmap/ se o fluxo mudar

---

## Mapa clone vs reescrita

| O que clonar (usa direto) | O que reescrever (adapta) |
|---|---|
| Estrutura de pastas | `data/raw/` — seus arquivos |
| `run_etl.py` | `src/etl/extract.py` — suas colunas |
| `Makefile` | `src/etl/validate.py` — suas regras |
| Lógica de logging | `sql/sqlserver/*.sql` — seu schema |
| Padrão de testes | `powerbi/dax/` — suas medidas |
| Estrutura do roadmap | `README.md` — sua história |

---

## Tempo estimado de adaptação

| Escopo | Tempo |
|---|---|
| Novo dataset mesmo domínio | 2–4 horas |
| Novo domínio (outro negócio) | 1–2 dias |
| Projeto greenfield com este template | 3–5 dias |

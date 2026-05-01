# Como Executar — Planejamento Comercial

Guia passo a passo para rodar o projeto localmente. Inclui modo sem SQL Server para exploração sem dependência de banco.

---

## Sequência recomendada

```text
1. Clonar o repositório
2. Criar ambiente virtual e instalar dependências
3. Configurar .env
4. Conferir data/raw/
5. Rodar dry-run (sem banco — recomendado para primeiro contato)
6. Rodar testes
7. Rodar ETL completo (requer SQL Server)
8. Executar scripts SQL na ordem
9. Abrir portal e dashboard
```

---

## Pré-requisitos

**Obrigatório para tudo:**

- Python 3.11+
- Git

**Obrigatório apenas para o ETL completo (etapas 7 e 8):**

- SQL Server (local: SQL Server Express) ou Azure SQL
- ODBC Driver 17 ou 18 for SQL Server
- SSMS ou Azure Data Studio

**Opcional:**

- Power BI Desktop (para abrir o modelo e o DAX)
- Power Automate (para os fluxos de automação)

> Se você não tem SQL Server, siga a seção **"Executar sem SQL Server"** abaixo.
> O dry-run, os testes e o dashboard HTML funcionam sem banco de dados.

---

## Setup local

```bash
git clone https://github.com/IgorPereiraPinto/planejamento-comercial.git
cd planejamento-comercial

# Criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / Mac

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copiar o template de variáveis de ambiente
copy .env.example .env          # Windows
# cp .env.example .env          # Linux / Mac
```

Abra o `.env` e ajuste os campos marcados com `[EDITÁVEL]` conforme seu ambiente.

---

## Conferência dos arquivos brutos

Os arquivos esperados em `data/raw/` são:

| Arquivo | Conteúdo |
| --- | --- |
| `Dimensoes.xlsx` | 7 abas: dProdutos, dVendedor, dClientes, dCidade, dUnidades, dStatus, dPagamento |
| `Vendas.xlsx` | Histórico de transações (cabeçalho na linha 5) |
| `Meta_2018.xlsx` | Metas mensais por vendedor — 2018 |
| `Meta_2019.xlsx` | Metas mensais por vendedor — 2019 |
| `Meta_2020.xlsx` | Metas mensais por vendedor — 2020 |
| `Meta_2021.xlsx` | Metas mensais por vendedor — 2021 |

---

## Executar sem SQL Server (dry-run)

O modo dry-run executa extração, transformação e validações **sem conectar ao banco de dados**. É o melhor ponto de partida quando você quer:

- Explorar o projeto sem instalar SQL Server
- Validar que os arquivos Excel estão corretos
- Testar o pipeline antes de configurar o banco

```bash
python run_etl.py --dry-run
```

Alternativa via Makefile:

```bash
make dry-run
```

### O que o dry-run faz

| Etapa | Executa? | O que acontece |
| --- | --- | --- |
| Extract | ✅ | Lê todos os arquivos Excel e valida formato |
| Transform | ✅ | Aplica limpeza, cast de tipos, UNPIVOT das metas |
| Validate | ✅ | Executa os 8 testes de qualidade de dados |
| Load | ❌ | **Não executa** — nenhuma escrita no banco |

### Saída esperada (dry-run com sucesso)

```text
2026-04-30 08:00:00 | INFO     | pipeline        | === MODO DRY-RUN ===
2026-04-30 08:00:01 | INFO     | extract         | fVendas: 20004 linhas extraídas
2026-04-30 08:00:01 | INFO     | extract         | Dimensoes: 7 abas extraídas
2026-04-30 08:00:02 | INFO     | transform       | fVendas transformada: 20004 linhas válidas
2026-04-30 08:00:02 | INFO     | validate        | ✓ 7/7 testes passaram
2026-04-30 08:00:02 | INFO     | pipeline        | Dry-run concluído. Nenhuma escrita realizada.
```

Se alguma validação falhar, o log indicará exatamente qual teste e qual linha do Excel causou o problema.

---

## Testes unitários

```bash
pytest -q
```

Ou:

```bash
make test
```

Os testes cobrem `extract.py`, `transform.py` e `validate.py`. Não requerem SQL Server.

---

## ETL completo (requer SQL Server)

Antes de rodar o ETL completo, certifique-se de que:

1. O SQL Server está rodando e acessível
2. O `.env` tem `DB_SERVER` e `DB_DATABASE` corretos
3. O banco já existe (execute `CREATE DATABASE planejamento_comercial;` no SSMS se necessário)

```bash
python run_etl.py
```

Ou:

```bash
make etl
```

---

## Ordem dos scripts SQL

Execute no SSMS ou Azure Data Studio, na ordem abaixo:

```text
sql/sqlserver/00_setup.sql        → cria schemas (raw, staging, dw)
sql/sqlserver/01_raw_tables.sql   → tabelas raw (espelho do Excel)
sql/sqlserver/02_staging_tables.sql → tabelas staging (tipadas)
sql/sqlserver/03_dw_dimensions.sql  → dimensões do star schema
sql/sqlserver/04_dw_facts.sql     → fatos (fVendas, fMetas)
sql/sqlserver/05_calendario.sql   → dCalendario (base temporal)
sql/sqlserver/06_indexes.sql      → índices de performance
sql/sqlserver/07_analytical_queries.sql → queries de validação e KPIs
```

> Dica: o script `00_setup.sql` imprime a ordem correta no console do SSMS.

---

## Abrir os outputs

```bash
# Portal do projeto
start index.html

# Dashboard principal
start dashboards/planejamento_comercial.html

# Apresentação executiva
start presentations/apresentacao_forecast_budget.html
```

No Linux/Mac, substitua `start` por `open`.

---

## Critério de sucesso

A execução está concluída quando:

- [ ] `python run_etl.py --dry-run` termina sem erro
- [ ] `pytest -q` passa todos os testes
- [ ] `python run_etl.py` carrega o banco sem erro
- [ ] Scripts SQL executam sem erro na ordem indicada
- [ ] Dashboard abre sem quebrar layout ou lógica JS

---

## Nota sobre legado

Conteúdos da estrutura original ficaram em `legacy/` e `docs/legacy/`. Úteis para histórico, mas não representam a estrutura atual do projeto.

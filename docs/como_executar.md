# Como Executar - planejamento-comercial

Guia rapido para rodar o projeto localmente sem perder a logica da arquitetura atual.

## Sequencia recomendada

```text
1. clonar o repositorio
2. criar ambiente virtual
3. instalar dependencias
4. configurar .env
5. conferir data/raw/
6. rodar dry-run
7. rodar testes
8. rodar ETL completo
9. executar scripts SQL
10. abrir portal e dashboard
```

## Pre-requisitos

- Python 3.11+
- Git
- SQL Server + SSMS
- arquivos Excel em `data/raw/`

## Setup local

```bash
git clone https://github.com/IgorPereiraPinto/planejamento-comercial.git
cd planejamento-comercial
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
copy .env.example .env
```

No Linux ou Mac:

```bash
source .venv/bin/activate
```

## Conferencia dos arquivos brutos

Os arquivos esperados em `data/raw/` sao:

- `Dimensoes.xlsx`
- `Vendas.xlsx`
- `Meta_2018.xlsx`
- `Meta_2019.xlsx`
- `Meta_2020.xlsx`
- `Meta_2021.xlsx`

## Dry-run

```bash
python run_etl.py --dry-run
```

O `--dry-run` executa extracao, transformacao e validacoes sem acionar a carga SQL. Ele e o melhor primeiro teste local.

Alternativa:

```bash
make dry-run
```

## Testes

```bash
pytest -q
```

Ou:

```bash
make test
```

## ETL completo

```bash
python run_etl.py
```

Ou:

```bash
make etl
```

## Ordem dos scripts SQL

```text
sql/sqlserver/00_setup.sql
sql/sqlserver/01_raw_tables.sql
sql/sqlserver/02_staging_tables.sql
sql/sqlserver/03_dw_dimensions.sql
sql/sqlserver/04_dw_facts.sql
sql/sqlserver/05_calendario.sql
sql/sqlserver/06_indexes.sql
sql/sqlserver/07_analytical_queries.sql
```

## Abrir os outputs

Portal do projeto:

```bash
start index.html
```

Dashboard principal:

```bash
start dashboards/planejamento_comercial.html
```

Apresentacao executiva:

```bash
start presentations/apresentacao_forecast_budget.html
```

## Criterio de sucesso

Consideramos a execucao concluida quando:

- o dry-run termina sem erro
- os testes passam
- o ETL completo carrega o banco corretamente
- os scripts SQL entregam as camadas analiticas
- o dashboard abre sem quebrar layout ou logica

## Nota de legado

Conteudos antigos ficaram em `legacy/` e `docs/legacy/`. Eles ajudam no historico, mas nao representam mais a estrutura principal do projeto.

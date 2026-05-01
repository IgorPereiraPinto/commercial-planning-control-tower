# Planejamento Comercial

Pipeline de dados ponta a ponta para planejamento comercial, construido como case tecnico com foco em 3 objetivos: ser didatico, funcional e reutilizavel. O repositorio conecta Excel, Python ETL, SQL Server, Power BI, automacao e dashboard executivo em uma narrativa orientada a decisao comercial com clareza, previsibilidade e governanca.

## Visao Geral

Fluxo principal do projeto:

`Excel → Python ETL → SQL Server (raw, staging, dw) → Dashboard HTML / Power BI → Automacao`

O objetivo nao e apenas exibir numeros. A proposta e transformar metas, vendas, forecast, margem e comissao em leitura executiva para gerentes comerciais, vendedores, planejamento e liderança.

---

![Dashboard Planejamento Comercial](<docs/assets/Print do dashboard Planejamento Comercial.PNG>)

---

## Perguntas de Negocio que o Projeto Responde

Esta visao do dashboard ajuda a responder perguntas como:

- qual o atingimento da meta no mes, no trimestre e no acumulado?
- quais vendedores, regioes, unidades e gerentes puxam o gap do resultado?
- qual o forecast de fechamento e qual a confiabilidade dessa previsao?
- quais produtos e categorias sustentam volume, margem e prioridade comercial?
- como a comissao conversa com atingimento, mix e resultado economico?
- qual a provisao de comissao projetada para o fechamento do mes?
- o que precisa existir para transformar o case em processo automatizado?

---

## O Que Este Projeto Resolve

- extracao e validacao estrutural da base Excel
- limpeza, padronizacao e testes em Python
- modelagem analitica em `raw`, `staging` e `dw`
- camada de comissao com tabelas parametricas e formula documentada
- calendar corporativo de apuracao e provisao de comissao
- apresentacoes executivas em HTML (forecast, budget, storytelling)
- 5 fluxos documentados de automacao com Power Automate
- consumo final em dashboard HTML e camada semantica para BI

---

## Por Onde Comecar

Existem quatro caminhos, dependendo do seu objetivo:

| Objetivo | Tempo estimado | Ponto de entrada |
| --- | --- | --- |
| Ver o resultado | 2 minutos | [Dashboard publicado](https://igorpereirapinto.github.io/planejamento-comercial/dashboards/planejamento_comercial.html) |
| Executar o projeto localmente | 30 a 60 minutos | [docs/como_executar.md](docs/como_executar.md) |
| Estudar o projeto do zero | 4 horas a alguns dias | [roadmap/00_setup_local_e_git.md](roadmap/00_setup_local_e_git.md) |
| Reutilizar para outro case | 1 a 2 horas | [docs/template_novo_case.md](docs/template_novo_case.md) |

Se voce chegou aqui pela primeira vez e quer entender o projeto em 5 minutos, comece pelo [Dashboard publicado](https://igorpereirapinto.github.io/planejamento-comercial/dashboards/planejamento_comercial.html) e depois leia a secao **Fluxo do Projeto** abaixo.

---

## Fluxo do Projeto

```text
[1] Setup local e versionamento
    pasta do projeto -> Git -> VS Code -> ambiente virtual

[2] Entendimento do problema
    bases Excel -> perguntas de negocio -> hipoteses -> definicao de KPIs

[3] Python ETL
    extracao -> limpeza -> validacao -> testes -> exportacao

[4] SQL analitico
    RAW -> STAGING -> DW -> views analiticas -> comissao parametrica

[5] Consumo e comunicacao
    dashboard HTML -> Power BI -> apresentacao executiva -> automacao

[6] Reutilizacao
    ajuste de dados -> regras de negocio -> SQL -> dashboard -> documentacao
```

---

## Dashboard Principal

Links diretos:

| Artefato | Link |
| --- | --- |
| Portal do projeto | [index.html](index.html) |
| Dashboard principal | [dashboards/planejamento_comercial.html](dashboards/planejamento_comercial.html) |
| Dashboard publicado | [GitHub Pages](https://igorpereirapinto.github.io/planejamento-comercial/dashboards/planejamento_comercial.html) |
| Portal publicado | [GitHub Pages — index](https://igorpereirapinto.github.io/planejamento-comercial/) |
| Repositorio | [github.com/IgorPereiraPinto/planejamento-comercial](https://github.com/IgorPereiraPinto/planejamento-comercial) |

### O que o dashboard entrega

O dashboard em [dashboards/planejamento_comercial.html](dashboards/planejamento_comercial.html) foi desenhado para navegacao executiva fluida, com 7 abas:

| Aba | Conteudo |
| --- | --- |
| Visao Geral | resultado consolidado e posicao da carteira |
| Meta vs. Realizado | atingimento por vendedor, regiao e produto |
| Forecast e Budget | projecao de fechamento e desvio do budget |
| Comissao e Mix | simulacao de comissao e distribuicao de mix |
| Rentabilidade | margem por canal, produto e segmento |
| Sintese Executiva | resumo operacional e escala de performance |
| Glossario | definicao e formula de cada indicador |

---

## Camada de Comissao

O projeto inclui uma proposta de comissionamento parametrico para aproximar o case de uma operacao real. A logica esta documentada e implementada como esquema SQL reutilizavel.

Faixas de payout por atingimento:

| Atingimento | Fator de payout |
| --- | --- |
| Abaixo de 80% | 0% |
| 80% a 89,9% | 50% |
| 90% a 99,9% | 80% |
| 100% a 109,9% | 100% |
| 110% a 119,9% | 130% |
| Acima de 120% | 160% |

Multiplicadores por prioridade de produto:

| Prioridade | Multiplicador |
| --- | --- |
| P1 | 1,35x |
| P2 | 1,15x |
| P3 | 1,00x |
| P4 | 0,85x |

Formula proposta:

```
comissao elegivel = receita liquida × taxa base × multiplicador de prioridade
comissao paga    = comissao elegivel × fator de atingimento
```

Documentacao completa:

- [docs/comissionamento.md](docs/comissionamento.md)
- [docs/regras_de_negocio.md](docs/regras_de_negocio.md)
- [docs/dicionario_de_dados.md](docs/dicionario_de_dados.md)
- [docs/arquitetura.md](docs/arquitetura.md)

---

## Calendario Corporativo de Comissao

O projeto modela o ciclo mensal de apuracao e envio de provisao de comissao:

| Quando | Etapa | Responsavel |
| --- | --- | --- |
| Dia 20 do mes | Calcular projecao de vendas (run rate) | Planejamento comercial |
| Dia 22 do mes | Calcular provisao de comissao | Planejamento comercial |
| Dia 24 do mes | Validacao pela area comercial | Gerentes + Planejamento |
| Dia 27 do mes | Envio da provisao ao financeiro | Planejamento comercial |
| Dia 03 (mes+1) | Fechamento definitivo de vendas (ETL) | Dados |
| Dia 05 (mes+1) | Calculo definitivo de comissao | Planejamento comercial |
| Dia 10 (mes+1) | Aprovacao e liberacao para pagamento | Financeiro |

Este calendario esta refletido na query de carga em [sql/sqlserver/08_comissao.sql](sql/sqlserver/08_comissao.sql).

---

## Outputs Principais do Portfolio

| # | Artefato | Descricao |
| --- | --- | --- |
| 1 | [index.html](index.html) | Portal local do projeto |
| 2 | [dashboards/planejamento_comercial.html](dashboards/planejamento_comercial.html) | Dashboard principal com 7 abas navegaveis |
| 3 | [presentations/apresentacao_forecast_budget.html](presentations/apresentacao_forecast_budget.html) | Apresentacao executiva de forecast e budget |
| 4 | [presentations/apresentacao_comercial.html](presentations/apresentacao_comercial.html) | Arquitetura, estrutura e proposta da solucao |

---

## Estrutura do Repositorio

```text
planejamento-comercial/
├── README.md
├── index.html
├── run_etl.py
├── Makefile
├── assets/
│   └── js/
│       └── chart.umd.min.js          ← Chart.js 4.4.1 bundled (sem CDN externo)
├── data/
│   ├── raw/                          ← arquivos Excel de entrada
│   └── processed/                    ← saidas do pipeline (JSON, CSV)
├── dashboards/
│   └── planejamento_comercial.html
├── docs/
│   ├── arquitetura.md
│   ├── como_executar.md
│   ├── comissionamento.md
│   ├── dicionario_de_dados.md
│   ├── faq_reutilizacao.md
│   ├── regras_de_negocio.md
│   ├── template_novo_case.md
│   ├── assets/
│   └── legacy/
├── powerautomate/
│   ├── GUIA_POWER_AUTOMATE.md
│   ├── flows/                        ← 5 fluxos documentados
│   └── templates/
├── powerbi/
│   └── dax/
├── presentations/
├── roadmap/
├── sql/
│   ├── sqlserver/
│   │   ├── 00_setup.sql
│   │   ├── 01_raw_tables.sql
│   │   ├── 02_staging_tables.sql
│   │   ├── 03_dw_dimensions.sql
│   │   ├── 04_dw_facts.sql
│   │   ├── 05_calendario.sql
│   │   ├── 06_indexes.sql
│   │   ├── 07_analytical_queries.sql
│   │   └── 08_comissao.sql           ← tabelas parametricas + fato de comissao
│   └── extras/
├── src/
│   └── etl/
├── tests/
└── legacy/
```

---

## Execucao Rapida

### 1. Clonar e preparar o ambiente

```bash
git clone https://github.com/IgorPereiraPinto/planejamento-comercial.git
cd planejamento-comercial
python -m venv .venv
```

Ative o ambiente virtual:

- Windows: `.venv\Scripts\activate`
- Linux/Mac: `source .venv/bin/activate`

Instale as dependencias:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Configurar a entrada

```bash
copy .env.example .env
```

### 3. Dry-run (sem banco de dados)

```bash
python run_etl.py --dry-run
```

### 4. Validar com testes

```bash
pytest -q
```

### 5. Rodar o ETL completo

```bash
python run_etl.py
```

### 6. Abrir o resultado final

- abrir o [Dashboard publicado](https://igorpereirapinto.github.io/planejamento-comercial/dashboards/planejamento_comercial.html)
- ou abrir localmente [dashboards/planejamento_comercial.html](dashboards/planejamento_comercial.html)
- ou abrir o [Portal do projeto](index.html)

Guia completo: [docs/como_executar.md](docs/como_executar.md)

---

## Roadmap Didatico

O `roadmap/` funciona como workflow do projeto, do primeiro passo ao ultimo:

1. [00_setup_local_e_git.md](roadmap/00_setup_local_e_git.md)
2. [01_visao_geral_do_projeto.md](roadmap/01_visao_geral_do_projeto.md)
3. [02_entendimento_do_case.md](roadmap/02_entendimento_do_case.md)
4. [03_analise_da_base_excel.md](roadmap/03_analise_da_base_excel.md)
5. [04_arquitetura_do_pipeline.md](roadmap/04_arquitetura_do_pipeline.md)
6. [05_etl_extracao.md](roadmap/05_etl_extracao.md)
7. [06_etl_transformacao_e_validacoes.md](roadmap/06_etl_transformacao_e_validacoes.md)
8. [07_modelagem_raw.md](roadmap/07_modelagem_raw.md)
9. [08_modelagem_staging.md](roadmap/08_modelagem_staging.md)
10. [09_modelagem_dw.md](roadmap/09_modelagem_dw.md)
11. [10_kpis_e_views_analiticas.md](roadmap/10_kpis_e_views_analiticas.md)
12. [11_dashboard_e_storytelling.md](roadmap/11_dashboard_e_storytelling.md)
13. [12_powerbi_e_dax.md](roadmap/12_powerbi_e_dax.md)
14. [13_apresentacao_executiva.md](roadmap/13_apresentacao_executiva.md)
15. [14_como_reutilizar_o_projeto.md](roadmap/14_como_reutilizar_o_projeto.md)

---

## Documentacao Conectada

| Documento | Conteudo |
| --- | --- |
| [docs/como_executar.md](docs/como_executar.md) | Execucao local e ordem correta do fluxo |
| [docs/arquitetura.md](docs/arquitetura.md) | Arquitetura do pipeline e evolucao para operacao real |
| [docs/regras_de_negocio.md](docs/regras_de_negocio.md) | Regras de KPI, forecast e comissionamento |
| [docs/comissionamento.md](docs/comissionamento.md) | Explicacao didatica, formula e exemplo pratico |
| [docs/dicionario_de_dados.md](docs/dicionario_de_dados.md) | Estruturas atuais e futuras recomendadas |
| [docs/faq_reutilizacao.md](docs/faq_reutilizacao.md) | Adaptacao do projeto para outros contextos |

---

## Escala e Automacao

O projeto foi desenhado para facilitar a evolucao de case de portfolio para rotina corporativa:

- regras de comissao como tabelas parametricas (`config.param_regra_comissao`)
- DW expoe `dw.fComissaoMensal` com provisao, definitivo e pago
- alertas disparados por Power Automate (5 fluxos documentados em `powerautomate/`)
- forecast revisado em cadencia recorrente
- dashboard pode consumir dados reais do pipeline via `data/processed/`

---

## Premissas e Limitacoes

- **Dados ficticios**: os arquivos Excel em `data/raw/` foram gerados para fins didaticos. Nomes de vendedores, produtos e clientes sao ilustrativos.
- **SQL Server obrigatorio para o ETL completo**: as etapas de carga no banco requerem SQL Server local ou Azure SQL. O dry-run funciona sem banco.
- **Dashboard estatico**: o dashboard HTML usa dados embutidos no proprio arquivo. Para conectar a dados reais, o pipeline gera `data/processed/dashboard_data.json`.
- **GitHub Pages sem atualizacao automatica**: a publicacao no Pages e estatica. O JSON de dados precisaria ser commitado para refletir no site publicado.
- **Comissao como proposta**: a politica de comissao e um modelo didatico. Faixas, taxas e multiplicadores devem ser revisados conforme a politica real antes de qualquer uso em producao.
- **Power BI nao publicado**: os arquivos DAX e o modelo Power BI estao documentados mas nao publicados no servico. O dashboard HTML e o output principal publicado.

---

## Analise do Projeto

Pontos fortes:

- pipeline ponta a ponta com dados ficticios didaticos bem estruturados
- camada de comissao com tabelas parametricas e formula documentada
- calendario corporativo completo de apuracao e provisao
- dashboard HTML com 7 abas navegaveis publicado no GitHub Pages
- apresentacoes executivas em HTML (forecast, budget, storytelling)
- Power Automate com 5 fluxos documentados
- roadmap de 15 etapas como workflow de aprendizado estruturado
- documentacao completa: arquitetura, regras, dicionario, FAQ e template de reutilizacao

Melhorias implementadas:

- Chart.js 4.4.1 bundled localmente, sem dependencia de CDN externo
- `run_etl.py` com validacao automatica do `.env` e mensagens guiadas
- `Makefile` com comandos `make etl`, `make test`, `make check`, `make open` e `make clean`
- `dw.fComissaoMensal` com colunas de provisao, definitivo e pago para rastreabilidade completa
- portal `index.html` publicado no GitHub Pages como ponto de entrada unico

---

## Infraestrutura de Desenvolvimento

Os arquivos `CLAUDE.md`, `SKILLS_GUIDE.md` e o diretorio `.claude/` sao artefatos de produtividade usados durante o desenvolvimento com IA. Eles nao fazem parte da logica do case e podem ser ignorados ou removidos em outro contexto.

---

## Autor

**Igor Pereira Pinto**
Analista de Dados / BI e Planejamento Comercial Senior
[github.com/IgorPereiraPinto](https://github.com/IgorPereiraPinto)

# Planejamento Comercial

Projeto de dados ponta a ponta para planejamento comercial, estruturado como material de apoio didático, funcional e reutilizável. O repositório conecta Excel, Python ETL, SQL Server, Power BI, automação e dashboard executivo em uma narrativa pensada para orientar decisão comercial com mais clareza, previsibilidade e governança.

## Visão geral

Fluxo principal do projeto:

`Excel → Python ETL → SQL Server (raw, staging, dw) → Dashboard HTML / Power BI → Automação`

O objetivo do projeto não é apenas exibir números. A proposta é transformar metas, vendas, forecast, margem e comissão em leitura executiva para:

- gerentes comerciais
- vendedores
- planejamento comercial
- liderança executiva

## Dashboard principal

Link direto do dashboard:

- [Abrir dashboard principal](dashboards/planejamento_comercial.html)
- [Abrir portal do projeto](index.html)
- [GitHub do projeto](https://github.com/IgorPereiraPinto/planejamento-comercial)
- [GitHub Pages](https://igorpereirapinto.github.io/planejamento-comercial/)
- [Dashboard publicado](https://igorpereirapinto.github.io/planejamento-comercial/dashboards/planejamento_comercial.html)

Preview do dashboard:

![Dashboard Planejamento Comercial](<docs/assets/Print do dashboard Planejamento Comercial.PNG>)

## O que o dashboard entrega

O dashboard principal em [dashboards/planejamento_comercial.html](dashboards/planejamento_comercial.html) foi desenhado para ter navegação executiva, fluida e intuitiva para um público que nem sempre tem familiaridade com leitura analítica profunda.

As abas principais cobrem:

- visão geral do resultado
- meta vs. realizado
- forecast e budget
- comissão e mix
- rentabilidade
- síntese executiva e escala operacional
- glossário de indicadores

## Perguntas de negócio que o projeto responde

- Qual o atingimento da meta no mês, no trimestre e no acumulado?
- Quais vendedores, regiões, unidades e gerentes puxam o gap do resultado?
- Qual o forecast de fechamento e qual a confiabilidade dessa previsão?
- Quais produtos e categorias sustentam volume, margem e prioridade comercial?
- Como a comissão conversa com atingimento, mix e resultado econômico?
- Qual a provisão de comissão projetada para o fechamento do mês?
- O que precisa existir para transformar o case em processo automatizado?

## Camada de comissão

O projeto inclui uma proposta de comissionamento para aproximar o portfólio de um caso real de planejamento comercial. A lógica está documentada e implementada como esquema SQL parametrizável.

Faixas de payout por atingimento:

- abaixo de 80%: `0%`
- 80% a 89,9%: `50%`
- 90% a 99,9%: `80%`
- 100% a 109,9%: `100%`
- 110% a 119,9%: `130%`
- acima de 120%: `160%`

Multiplicadores por prioridade de produto:

- `P1`: `1,35x`
- `P2`: `1,15x`
- `P3`: `1,00x`
- `P4`: `0,85x`

Fórmula proposta:

`comissão elegível = receita líquida × taxa base × multiplicador de prioridade`

`comissão paga = comissão elegível × fator de atingimento`

Detalhamento completo:

- [docs/comissionamento.md](docs/comissionamento.md)
- [docs/regras_de_negocio.md](docs/regras_de_negocio.md)
- [docs/dicionario_de_dados.md](docs/dicionario_de_dados.md)
- [docs/arquitetura.md](docs/arquitetura.md)

## Calendário corporativo de comissão

O projeto modela o ciclo mensal de apuração e envio de provisão de comissão:

| Quando | Etapa | Responsável |
| --- | --- | --- |
| Dia 20 do mês | Calcular projeção de vendas (run rate) | Planejamento comercial |
| Dia 22 do mês | Calcular provisão de comissão | Planejamento comercial |
| Dia 24 do mês | Validação pela área comercial | Gerentes + Planejamento |
| Dia 27 do mês | Envio da provisão ao financeiro | Planejamento comercial |
| Dia 03 (mês+1) | Fechamento definitivo de vendas (ETL) | Dados |
| Dia 05 (mês+1) | Cálculo definitivo de comissão | Planejamento comercial |
| Dia 10 (mês+1) | Aprovação e liberação para pagamento | Financeiro |

Este calendário está refletido na query de carga do arquivo [sql/sqlserver/08_comissao.sql](sql/sqlserver/08_comissao.sql).

## Outputs principais do portfólio

Os artefatos centrais do projeto são:

1. [index.html](index.html)
   Portal local do projeto.
2. [dashboards/planejamento_comercial.html](dashboards/planejamento_comercial.html)
   Dashboard principal com insights distribuídos por aba.
3. [presentations/apresentacao_forecast_budget.html](presentations/apresentacao_forecast_budget.html)
   Apresentação executiva focada em forecast, budget e tomada de decisão.
4. [presentations/apresentacao_comercial.html](presentations/apresentacao_comercial.html)
   Material de arquitetura, estrutura e proposta da solução.

## Estrutura do repositório

```text
planejamento-comercial/
├── README.md
├── index.html
├── run_etl.py
├── Makefile
├── assets/
│   └── js/
│       └── chart.umd.min.js       ← Chart.js 4.4.1 bundled (sem CDN externo)
├── data/
│   ├── raw/                       ← arquivos Excel de entrada
│   └── processed/                 ← saídas do pipeline (JSON, CSV)
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
│   ├── flows/                     ← 5 fluxos documentados
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
│   │   └── 08_comissao.sql        ← tabelas paramétricas + fato de comissão
│   └── extras/
├── src/
│   └── etl/
├── tests/
└── legacy/
```

## Documentação conectada

Os principais documentos foram atualizados para refletir o estado real do projeto:

- [docs/como_executar.md](docs/como_executar.md)
  Execução local e ordem correta do fluxo.
- [docs/arquitetura.md](docs/arquitetura.md)
  Arquitetura do pipeline e evolução para operação real.
- [docs/regras_de_negocio.md](docs/regras_de_negocio.md)
  Regras de KPI, forecast e comissionamento.
- [docs/comissionamento.md](docs/comissionamento.md)
  Explicação didática, fórmula e exemplo prático.
- [docs/dicionario_de_dados.md](docs/dicionario_de_dados.md)
  Estruturas atuais e futuras recomendadas.
- [docs/faq_reutilizacao.md](docs/faq_reutilizacao.md)
  Adaptação do projeto para outros contextos.
- [roadmap/11_dashboard_e_storytelling.md](roadmap/11_dashboard_e_storytelling.md)
  Direção da narrativa e do dashboard.

## Por onde começar

- Ver o resultado:
  abra [index.html](index.html)
- Ir direto ao dashboard:
  abra [dashboards/planejamento_comercial.html](dashboards/planejamento_comercial.html)
- Executar o projeto:
  veja [docs/como_executar.md](docs/como_executar.md)
- Entender as regras:
  veja [docs/regras_de_negocio.md](docs/regras_de_negocio.md) e [docs/comissionamento.md](docs/comissionamento.md)
- Reutilizar o modelo:
  veja [docs/template_novo_case.md](docs/template_novo_case.md)

## Escala e automação

O projeto foi desenhado para facilitar a evolução de um case de portfólio para uma rotina corporativa:

- regras de comissão podem virar tabelas paramétricas (`config.param_regra_comissao`)
- o DW expõe `dw.fComissaoMensal` com provisão, definitivo e pago
- alertas podem ser disparados por Power Automate (5 fluxos documentados)
- forecast pode ser revisado em cadência recorrente
- o dashboard pode consumir dados reais do pipeline via `data/processed/`

## Execução rápida

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
copy .env.example .env
python run_etl.py --dry-run
pytest -q
python run_etl.py
```

Depois:

- abra [index.html](index.html)
- abra [dashboards/planejamento_comercial.html](dashboards/planejamento_comercial.html)

## Premissas e limitações

- **Dados fictícios**: os arquivos Excel em `data/raw/` foram gerados para fins didáticos. Os nomes de vendedores, produtos e clientes são ilustrativos.
- **SQL Server obrigatório para o ETL completo**: as etapas 7 e 8 do fluxo (carga no banco) requerem SQL Server local ou Azure SQL. O dry-run funciona sem banco.
- **Dashboard estático**: o dashboard HTML usa dados embutidos no próprio arquivo. Para conectar a dados reais, o pipeline precisaria gerar `data/processed/dashboard_data.json` e o JS faria `fetch()` desse arquivo.
- **GitHub Pages sem atualização automática**: a publicação no Pages é estática. O JSON de dados precisaria ser commitado no repositório para refletir no site publicado.
- **Comissão como proposta**: a política de comissão é um modelo didático. Faixas, taxas e multiplicadores devem ser revisados conforme a política real da empresa antes de qualquer uso em produção.
- **Power BI não publicado**: os arquivos DAX e o modelo Power BI estão documentados mas não publicados no serviço. O dashboard HTML é o output principal publicado.

## Observação sobre legado

As estruturas antigas foram preservadas em `legacy/` e `docs/legacy/` apenas como histórico. A organização atual documentada acima é a fonte principal de verdade do projeto.

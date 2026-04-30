# Planejamento Comercial

Projeto de dados ponta a ponta para planejamento comercial, estruturado como material de apoio didatico, funcional e reutilizavel. O repositorio conecta Excel, Python ETL, SQL Server, Power BI, automacao e dashboard executivo em uma narrativa pensada para orientar decisao comercial com mais clareza, previsibilidade e governanca.

## Visao geral

Fluxo principal do projeto:

`Excel -> Python ETL -> SQL Server (raw, staging, dw) -> Dashboard HTML / Power BI -> automacao`

O objetivo do projeto nao e apenas exibir numeros. A proposta e transformar metas, vendas, forecast, margem e comissao em leitura executiva para:

- gerentes comerciais
- vendedores
- planejamento comercial
- lideranca executiva

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

O dashboard principal em [dashboards/planejamento_comercial.html](dashboards/planejamento_comercial.html) foi redesenhado para ter uma navegação mais executiva, mais fluida e mais intuitiva para um publico que nem sempre tem familiaridade com leitura analitica profunda.

As abas principais cobrem:

- visao geral do resultado
- meta vs realizado
- forecast e budget
- comissao e mix
- rentabilidade
- sintese executiva e escala operacional
- glossario de indicadores

## Perguntas de negocio que o projeto responde

- Qual o atingimento da meta no mes, no trimestre e no acumulado?
- Quais vendedores, regioes, unidades e gerentes puxam o gap do resultado?
- Qual o forecast de fechamento e qual a confiabilidade dessa previsao?
- Quais produtos e categorias sustentam volume, margem e prioridade comercial?
- Como a comissao conversa com atingimento, mix e resultado economico?
- O que precisa existir para transformar o case em processo automatizado?

## Camada de comissao

O projeto inclui uma proposta de comissionamento para aproximar o portfolio de um caso real de planejamento comercial.

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

Formula proposta:

`comissao elegivel = receita liquida * taxa base * multiplicador de prioridade`

`comissao paga = comissao elegivel * fator de atingimento`

Detalhamento completo:

- [docs/comissionamento.md](docs/comissionamento.md)
- [docs/regras_de_negocio.md](docs/regras_de_negocio.md)
- [docs/dicionario_de_dados.md](docs/dicionario_de_dados.md)
- [docs/arquitetura.md](docs/arquitetura.md)

## Outputs principais do portfolio

Os artefatos centrais do projeto sao:

1. [index.html](index.html)
   Portal local do projeto.
2. [dashboards/planejamento_comercial.html](dashboards/planejamento_comercial.html)
   Dashboard principal com insights distribuidos por aba.
3. [presentations/apresentacao_forecast_budget.html](presentations/apresentacao_forecast_budget.html)
   Apresentacao executiva focada em forecast, budget e tomada de decisao.
4. [presentations/apresentacao_comercial.html](presentations/apresentacao_comercial.html)
   Material de arquitetura, estrutura e proposta da solucao.

## Estrutura do repositorio

```text
planejamento-comercial/
|-- README.md
|-- index.html
|-- run_etl.py
|-- Makefile
|-- data/
|   |-- raw/
|   `-- processed/
|-- dashboards/
|   `-- planejamento_comercial.html
|-- docs/
|   |-- arquitetura.md
|   |-- como_executar.md
|   |-- comissionamento.md
|   |-- dicionario_de_dados.md
|   |-- faq_reutilizacao.md
|   |-- regras_de_negocio.md
|   |-- template_novo_case.md
|   |-- assets/
|   `-- legacy/
|-- powerbi/
|-- presentations/
|-- roadmap/
|-- sql/
|   `-- sqlserver/
|-- src/
|-- tests/
`-- legacy/
```

## Documentacao conectada

Os principais documentos foram atualizados para refletir o estado real do projeto:

- [docs/como_executar.md](docs/como_executar.md)
  Execucao local e ordem correta do fluxo.
- [docs/arquitetura.md](docs/arquitetura.md)
  Arquitetura do pipeline e evolucao para operacao real.
- [docs/regras_de_negocio.md](docs/regras_de_negocio.md)
  Regras de KPI, forecast e comissionamento.
- [docs/comissionamento.md](docs/comissionamento.md)
  Explicacao didatica, formula e exemplo pratico.
- [docs/dicionario_de_dados.md](docs/dicionario_de_dados.md)
  Estruturas atuais e futuras recomendadas.
- [docs/faq_reutilizacao.md](docs/faq_reutilizacao.md)
  Adaptacao do projeto para outros contextos.
- [roadmap/11_dashboard_e_storytelling.md](roadmap/11_dashboard_e_storytelling.md)
  Direcao da narrativa e do dashboard.

## Por onde comecar

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

## Escala e automacao

O projeto foi desenhado para facilitar a evolucao de um case de portfolio para uma rotina corporativa:

- regras de comissao podem virar tabelas parametricas
- o DW pode expor uma `fComissaoMensal`
- alertas podem ser disparados por Power Automate
- forecast pode ser revisado em cadence recorrente
- o dashboard pode consumir dados reais do pipeline em vez de dados embutidos

## Execucao rapida

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

## Observacao sobre legado

As estruturas antigas foram preservadas em `legacy/` e `docs/legacy/` apenas como historico. A organizacao atual documentada acima e a fonte principal de verdade do projeto.

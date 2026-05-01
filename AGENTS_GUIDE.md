# AGENTS_GUIDE.md

> **versão:** 1.1 | **atualizado:** 2026-04-27

Guia rápido de consulta para saber quando usar cada agent do repositório.

---

## Diferença entre rules, skills e agents

### `rules`
Use para padronizar **como executar** uma tarefa.  
As rules definem critérios técnicos, convenções e qualidade de entrega.

### `skills`
Use para orientar **quando e como atuar** em determinado tipo de trabalho.  
As skills funcionam como especializações reutilizáveis por domínio ou objetivo.

### `agents`
Use quando você quiser uma atuação mais focada, com um papel mais claro e uma linha de raciocínio especializada para um tipo específico de tarefa.

Resumo prático:
- `rules` = padrão técnico
- `skills` = especialização por tipo de trabalho
- `agents` = papel operacional especializado
- `orchestrator` = coordenação de múltiplos agents

---

## Quando usar cada agent

### Agents de análise e dados

| Agent | Quando usar | Exemplos de pedido | Quando não usar |
|---|---|---|---|
| `data-analyst.md` | Quando a demanda começa com um problema de negócio, dúvida analítica ou necessidade de leitura de cenário | "Analisa esse resultado", "o que pode estar acontecendo?", "quais hipóteses testar?" | Quando a demanda já está claramente focada em SQL, Power BI ou automação |
| `bi-analyst.md` | Quando precisa estruturar visão gerencial, KPIs, dashboards e leitura executiva de indicadores | "Quais KPIs devo acompanhar?", "como estruturar esse painel?", "como organizar essa visão de BI?" | Quando a tarefa é implementação técnica em DAX ou código |
| `sql-optimizer.md` | Quando precisa escrever, revisar, depurar ou otimizar SQL | "Otimiza essa query", "esse join está duplicando", "cria um SQL para esse KPI" | Quando a tarefa é mais conceitual ou não envolve banco |
| `ml-analyst.md` | Quando precisa pensar em forecasting, churn, classificação, segmentação, baseline e avaliação de modelo | "Faz forecast", "qual modelo usar?", "como prever churn?" | Quando a análise é só descritiva/diagnóstica, sem componente preditivo |
| `product-analyst.md` | Quando precisa analisar portfólio de SKUs, curva ABC, margem por produto, giro ou elasticidade de preço | "Classifica o portfólio", "quais SKUs drenam margem?", "faz curva ABC" | Análise de vendas por vendedor → usar data-analyst |

### Agents financeiros e de planejamento

| Agent | Quando usar | Exemplos de pedido | Quando não usar |
|---|---|---|---|
| `financial-analyst.md` | Quando a tarefa envolve DRE, fluxo de caixa, EBITDA, margens, variação orçamentária ou índices econômicos | "Monta o DRE", "qual o EBITDA do trimestre?", "analisa a variação vs budget" | Análise de crédito → usar credit-analyst; análise comercial → usar data-analyst |
| `credit-analyst.md` | Quando precisa analisar carteira de crédito, PDD, aging, safra, scoring ou política de aprovação | "Calcula PDD", "faz análise de safra", "qual o aging da carteira?" | Inadimplência de contas a receber operacional → usar financial-analyst |
| `budget-planner.md` | Quando precisa cascatear meta, distribuir budget, construir rolling forecast ou criar cenários orçamentários | "Cascateia a meta anual", "distribui o budget por equipe", "cria cenário pessimista" | Análise de resultado realizado → usar financial-analyst |

### Agents de engenharia e automação

| Agent | Quando usar | Exemplos de pedido | Quando não usar |
|---|---|---|---|
| `data-engineer.md` | Quando precisa desenhar pipeline, ETL, Data Lake, ingestão, rastreabilidade e estrutura técnica dos dados | "Estrutura esse pipeline", "como organizar Bronze/Silver/Gold?", "qual arquitetura usar?" | Quando a tarefa é só análise de negócio ou comunicação executiva |
| `automation-architect.md` | Quando precisa mapear processo e desenhar automações ponta a ponta com Power Platform, APIs ou integrações | "Automatiza esse processo", "cria um fluxo", "como integrar SharePoint com SQL?" | Quando a tarefa é só análise de dados sem automação |
| `web-scraper.md` | Quando precisa coletar dados públicos via scraping, extrair tabela HTML ou monitorar preços | "Cria um scraper", "coleta os preços desse site", "extrai essa tabela" | APIs oficiais disponíveis → usar api-data-extraction |

### Agents de visualização e comunicação

| Agent | Quando usar | Exemplos de pedido | Quando não usar |
|---|---|---|---|
| `powerbi-specialist.md` | Quando a tarefa envolve DAX, modelagem, contexto de filtro, tabela calendário ou performance no Power BI | "Cria essa medida", "meu filtro não funciona", "otimiza esse relatório" | Quando a necessidade é BI conceitual ou visual sem implementação |
| `dashboard-designer.md` | Quando precisa estruturar painel, escolher gráficos, organizar layout e pensar a UX analítica | "Como desenhar esse dashboard?", "qual gráfico usar?", "como organizar os visuais?" | Quando a necessidade é o código HTML final ou DAX técnico |
| `technical-writer.md` | Quando precisa melhorar texto, documentação, e-mails, relatórios ou README | "Humaniza esse texto", "melhora esse e-mail", "reescreve essa explicação técnica" | Quando a necessidade principal é análise de dados ou modelagem |
| `presentation-strategist.md` | Quando precisa estruturar uma apresentação, organizar narrativa de slides e preparar material para gestão ou diretoria | "Monta os slides", "qual a ordem da apresentação?", "transforma essa análise em deck" | Quando a tarefa é só resumo executivo curto ou design visual do slide |

### Agent de orquestração

| Agent | Quando usar | Exemplos de pedido | Quando não usar |
|---|---|---|---|
| `orchestrator.md` | Quando a tarefa é composta, envolve múltiplos domínios ou precisa de mais de um especialista em sequência | "Faz a análise completa de crédito e apresenta para a diretoria", "analisa o resultado e monta o deck" | Tarefas simples que um único agent resolve |

---

## Atalho rápido por objetivo

| Se eu quiser... | Agent mais indicado |
|---|---|
| Entender um problema de negócio com dados | `data-analyst.md` |
| Estruturar KPIs e visão gerencial | `bi-analyst.md` |
| Desenhar pipeline e arquitetura de dados | `data-engineer.md` |
| Escrever ou otimizar SQL | `sql-optimizer.md` |
| Melhorar texto e documentação | `technical-writer.md` |
| Resolver DAX e Power BI | `powerbi-specialist.md` |
| Desenhar dashboard e escolher visuais | `dashboard-designer.md` |
| Construir solução preditiva ou forecast | `ml-analyst.md` |
| Desenhar automação de processo | `automation-architect.md` |
| Estruturar apresentação executiva | `presentation-strategist.md` |
| Analisar DRE e resultado financeiro | `financial-analyst.md` |
| Analisar carteira de crédito e PDD | `credit-analyst.md` |
| Cascatear metas e construir budget | `budget-planner.md` |
| Analisar portfólio de produtos e SKUs | `product-analyst.md` |
| Coletar dados públicos via scraping | `web-scraper.md` |
| Coordenar múltiplos agents em fluxo | `orchestrator.md` |

---

## Como combinar agents na prática

### Fluxo 1 — Problema de negócio até apresentação
`data-analyst.md` → `executive-storytelling.md` (skill) → `presentation-strategist.md`

### Fluxo 2 — KPI até dashboard
`bi-analyst.md` → `dashboard-designer.md` → `powerbi-specialist.md` ou `dashboard-html.md` (skill)

### Fluxo 3 — Fonte de dados até consumo analítico
`data-engineer.md` → `sql-optimizer.md` → `bi-analyst.md`

### Fluxo 4 — Processo manual até automação
`data-analyst.md` → `automation-architect.md` → `technical-writer.md`

### Fluxo 5 — Modelo preditivo com tradução executiva
`ml-analyst.md` → `data-analyst.md` → `presentation-strategist.md`

### Fluxo 6 — Análise financeira completa
`financial-analyst.md` → `data-analyst.md` → `presentation-strategist.md`

### Fluxo 7 — Análise de crédito até recomendação de política
`credit-analyst.md` → `financial-analyst.md` → `technical-writer.md`

### Fluxo 8 — Planejamento orçamentário completo
`budget-planner.md` → `financial-analyst.md` → `presentation-strategist.md`

### Fluxo 9 — Coleta e análise de dados externos
`web-scraper.md` → `data-engineer.md` → `data-analyst.md`

### Fluxo 10 — Análise de portfólio com recomendação comercial
`product-analyst.md` → `data-analyst.md` → `presentation-strategist.md`

### Fluxo 11 — Tarefa composta multi-domínio (via orquestrador)
`orchestrator.md` → `[agents relevantes]` → `technical-writer.md` ou `presentation-strategist.md`

---

## Quando usar agent em vez de skill

Use **agent** quando:
- você quiser um papel mais definido;
- a tarefa exigir uma linha de raciocínio especializada;
- você quiser delegar a "condução" da tarefa a uma persona operacional mais clara.

Use **skill** quando:
- quiser ativar um domínio ou tipo de trabalho específico;
- precisar de templates, estruturas e regras de atuação;
- quiser apoio mais modular e reutilizável.

Regra prática:
- **agent** para conduzir
- **skill** para especializar
- **rule** para padronizar
- **orchestrator** para coordenar

---

## Combinações recomendadas entre agents e skills

| Situação | Agent | Skill complementar |
|---|---|---|
| Diagnóstico de negócio | `data-analyst.md` | `data-analysis.md` |
| Estruturação de painel | `bi-analyst.md` | `business-intelligence.md` |
| Query e performance | `sql-optimizer.md` | `sql-development.md` |
| Pipeline e ETL | `data-engineer.md` | `etl-data-lake.md` |
| Power BI e DAX | `powerbi-specialist.md` | `powerbi-development.md` |
| Dashboard executivo | `dashboard-designer.md` | `dashboard-design.md` |
| Forecast e modelo preditivo | `ml-analyst.md` | `machine-learning.md` |
| Automação de processo | `automation-architect.md` | `automations.md` |
| Deck executivo | `presentation-strategist.md` | `corporate-presentations.md` |
| Documentação e texto | `technical-writer.md` | `technical-writing.md` |
| Análise financeira e DRE | `financial-analyst.md` | `financial-analytics.md` |
| Carteira de crédito | `credit-analyst.md` | `credit-analytics.md` |
| Budget e metas | `budget-planner.md` | `budget-cascade.md` |
| Portfólio de produtos | `product-analyst.md` | `product-analytics.md` |
| Coleta web | `web-scraper.md` | `webscraping.md` |
| Orquestração | `orchestrator.md` | `subagent-orchestration.md` |

---

## Observações

- Agents não substituem skills e rules; eles funcionam melhor em conjunto.
- Quando houver dúvida, comece pelo agent mais próximo do objetivo principal da tarefa.
- Se a tarefa misturar análise, implementação e comunicação, você pode combinar mais de um agent em sequência.
- Para tarefas com múltiplos domínios, use o `orchestrator.md` para coordenar.
- Mantenha este guia atualizado sempre que um novo agent for criado.

---

## Estrutura atual

```text
.claude/agents/
├── data-analyst.md
├── bi-analyst.md
├── data-engineer.md
├── sql-optimizer.md
├── technical-writer.md
├── powerbi-specialist.md
├── dashboard-designer.md
├── ml-analyst.md
├── automation-architect.md
├── presentation-strategist.md
├── financial-analyst.md
├── credit-analyst.md
├── budget-planner.md
├── product-analyst.md
├── web-scraper.md
└── orchestrator.md
```

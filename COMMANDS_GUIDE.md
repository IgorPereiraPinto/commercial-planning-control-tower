# COMMANDS_GUIDE.md

> **versão:** 1.1 | **atualizado:** 2026-04-27

Guia rápido de consulta para saber quando usar cada command do repositório.

---

## Diferença entre rules, skills, agents e commands

### `rules`
Use para padronizar **como executar** uma tarefa.
As rules definem critérios técnicos, convenções e qualidade de entrega.

### `skills`
Use para orientar **quando e como atuar** em determinado tipo de trabalho.
As skills funcionam como especializações reutilizáveis por domínio ou objetivo.

### `agents`
Use quando você quiser uma atuação mais focada, com um papel mais claro e uma linha de raciocínio especializada.

### `commands`
Use como **atalhos operacionais** para tarefas recorrentes.
Commands são úteis quando você já sabe o tipo de entrega que quer e precisa acelerar a execução.

Resumo prático:
- `rules` = padrão técnico
- `skills` = especialização por tipo de trabalho
- `agents` = papel operacional especializado
- `commands` = atalho para executar mais rápido

---

## Quando usar cada command

### Commands de análise e diagnóstico

| Command | Quando usar | Exemplos de pedido | Quando não usar |
|---|---|---|---|
| `analyze-business-problem.md` | Quando o usuário traz uma dúvida de negócio, um problema analítico ou um resultado inesperado e precisa de estruturação | "Analisa esse cenário", "o que pode estar acontecendo?", "quais hipóteses testar?" | Quando a tarefa já está claramente focada em SQL, Power BI, automação ou apresentação |
| `analyze-financial.md` | Quando precisa estruturar análise de DRE, resultado financeiro, variação orçamentária ou margens | "Analisa o resultado financeiro", "qual o desvio vs budget?", "monta o DRE gerencial" | Quando é análise comercial de vendas ou análise de crédito |
| `analyze-credit.md` | Quando precisa analisar carteira de crédito, inadimplência, PDD, aging ou risco de portfólio | "Analisa a carteira", "calcula o PDD", "faz o aging da inadimplência" | Quando o problema é resultado financeiro operacional, não de crédito |
| `analyze-funnel.md` | Quando precisa analisar conversão, funil de vendas, etapas de jornada ou gargalos de pipeline comercial | "Analisa o funil", "onde estou perdendo mais leads?", "qual a conversão por etapa?" | Quando a análise é de resultado final de vendas, não de funil |

### Commands de construção e entrega

| Command | Quando usar | Exemplos de pedido | Quando não usar |
|---|---|---|---|
| `build-executive-summary.md` | Quando precisa condensar análise, projeto ou relatório em poucas linhas executivas | "Cria um sumário executivo", "resume isso para a diretoria", "faz um one-pager" | Quando a demanda é uma apresentação completa ou apenas revisão de texto |
| `build-dre.md` | Quando precisa montar ou estruturar uma DRE gerencial com linhas, margens e comparativos | "Monta a DRE", "estrutura o resultado financeiro", "cria o template de DRE" | Quando é só análise do resultado já existente, não construção da estrutura |
| `cascade-targets.md` | Quando precisa distribuir metas do nível corporativo até equipes ou vendedores | "Cascateia a meta", "distribui o target por regional", "cria a tabela de metas por time" | Quando a tarefa é análise de resultado realizado, não planejamento de meta |
| `create-corporate-presentation.md` | Quando precisa montar uma apresentação corporativa com sequência lógica, mensagem por slide e visual sugerido | "Monta os slides", "cria outline do deck", "mensagem por slide" | Quando a necessidade é só um resumo curto ou só design visual do slide |

### Commands de dados e SQL

| Command | Quando usar | Exemplos de pedido | Quando não usar |
|---|---|---|---|
| `review-sql-query.md` | Quando precisa revisar, corrigir, explicar ou otimizar uma query SQL | "Otimiza essa query", "corrige esse SQL", "esse join está duplicando" | Quando o problema ainda nem foi traduzido em lógica SQL |
| `plan-data-pipeline.md` | Quando precisa desenhar pipeline, ETL, Data Lake, camadas e fluxo ponta a ponta | "Estrutura esse pipeline", "como montar Bronze/Silver/Gold?", "desenha a arquitetura dos dados" | Quando a tarefa é apenas extrair dados ou apenas analisar resultado |
| `validate-data-quality.md` | Quando precisa validar qualidade dos dados: nulos, duplicatas, tipos, consistência e regras de negócio | "Valida a qualidade dos dados", "faz checklist de DQ", "encontra inconsistências nessa tabela" | Quando a tarefa é transformação ou análise, não validação |
| `scrape-and-structure.md` | Quando precisa coletar dados públicos de sites, portais ou tabelas HTML e estruturá-los para análise | "Coleta os dados desse site", "extrai essa tabela", "faz scraping dos preços" | Quando existe API oficial disponível |
| `run-subagent-workflow.md` | Quando precisa orquestrar múltiplos subagents em sequência para uma entrega complexa | "Executa o fluxo completo de análise", "usa os subagents para revisar essa entrega" | Quando a tarefa é simples e não precisa de múltiplos especialistas |

### Commands de dashboard e visualização

| Command | Quando usar | Exemplos de pedido | Quando não usar |
|---|---|---|---|
| `design-dashboard.md` | Quando precisa estruturar um dashboard conceitualmente, com KPIs, layout, visuais e filtros | "Como estruturar esse painel?", "qual gráfico usar?", "me ajuda a desenhar esse dashboard" | Quando a necessidade é gerar diretamente o HTML final |
| `create-html-dashboard.md` | Quando precisa criar um dashboard web em HTML/CSS/JS, especialmente para protótipo, portfólio ou apresentação | "Cria um dashboard HTML", "faz um painel web com filtros", "adapta isso para HTML" | Quando a necessidade é só desenho conceitual ou recomendação visual |

### Command de texto

| Command | Quando usar | Exemplos de pedido | Quando não usar |
|---|---|---|---|
| `improve-professional-text.md` | Quando precisa humanizar, revisar ou melhorar textos profissionais | "Melhora esse e-mail", "humaniza esse texto", "reescreve esse relatório" | Quando a demanda é análise técnica, SQL ou modelagem |

---

## Atalho rápido por objetivo

| Se eu quiser... | Command mais indicado |
|---|---|
| Estruturar um problema de negócio com dados | `analyze-business-problem.md` |
| Analisar resultado financeiro e DRE | `analyze-financial.md` |
| Analisar carteira de crédito | `analyze-credit.md` |
| Analisar funil e conversão | `analyze-funnel.md` |
| Criar um sumário executivo | `build-executive-summary.md` |
| Montar ou estruturar uma DRE | `build-dre.md` |
| Cascatear e distribuir metas | `cascade-targets.md` |
| Montar uma apresentação corporativa | `create-corporate-presentation.md` |
| Revisar ou otimizar SQL | `review-sql-query.md` |
| Planejar pipeline e ETL | `plan-data-pipeline.md` |
| Validar qualidade de dados | `validate-data-quality.md` |
| Coletar e estruturar dados da web | `scrape-and-structure.md` |
| Orquestrar subagents em sequência | `run-subagent-workflow.md` |
| Desenhar um dashboard | `design-dashboard.md` |
| Criar um dashboard web em HTML | `create-html-dashboard.md` |
| Melhorar um texto profissional | `improve-professional-text.md` |

---

## Como combinar commands na prática

### Fluxo 1 — Problema de negócio até recomendação executiva
`analyze-business-problem.md` → `build-executive-summary.md`

### Fluxo 2 — Problema de negócio até apresentação
`analyze-business-problem.md` → `create-corporate-presentation.md`

### Fluxo 3 — Análise financeira completa
`analyze-financial.md` → `build-dre.md` → `build-executive-summary.md`

### Fluxo 4 — Planejamento e cascateamento
`analyze-financial.md` → `cascade-targets.md` → `create-corporate-presentation.md`

### Fluxo 5 — Análise de crédito até recomendação
`analyze-credit.md` → `build-executive-summary.md`

### Fluxo 6 — Funil comercial até apresentação
`analyze-funnel.md` → `analyze-business-problem.md` → `create-corporate-presentation.md`

### Fluxo 7 — SQL até painel
`review-sql-query.md` → `design-dashboard.md`

### Fluxo 8 — Pipeline até consumo analítico
`plan-data-pipeline.md` → `validate-data-quality.md` → `review-sql-query.md` → `design-dashboard.md`

### Fluxo 9 — Dashboard conceitual até dashboard web
`design-dashboard.md` → `create-html-dashboard.md`

### Fluxo 10 — Coleta até análise
`scrape-and-structure.md` → `validate-data-quality.md` → `analyze-business-problem.md`

### Fluxo 11 — Texto técnico até comunicação executiva
`improve-professional-text.md` → `build-executive-summary.md`

### Fluxo 12 — Entrega complexa com revisão multi-etapa
`run-subagent-workflow.md` → `build-executive-summary.md`

---

## Quando usar command em vez de skill

Use **command** quando:
- você já sabe o tipo de entrega que quer;
- a tarefa é recorrente;
- quer acelerar a execução com uma estrutura pronta;
- precisa de um atalho para começar mais rápido.

Use **skill** quando:
- quiser uma especialização mais rica por domínio;
- precisar de templates, frameworks e exemplos mais amplos;
- a tarefa for mais aberta ou exigir profundidade temática.

Regra prática:
- **command** para acelerar
- **skill** para especializar
- **agent** para conduzir
- **rule** para padronizar

---

## Combinações recomendadas entre commands, agents e skills

| Situação | Command | Agent complementar | Skill complementar |
|---|---|---|---|
| Diagnóstico de negócio | `analyze-business-problem.md` | `data-analyst.md` | `data-analysis.md` |
| Análise financeira | `analyze-financial.md` | `financial-analyst.md` | `financial-analytics.md` |
| Análise de crédito | `analyze-credit.md` | `credit-analyst.md` | `credit-analytics.md` |
| Análise de funil | `analyze-funnel.md` | `data-analyst.md` | `funnel-analytics.md` |
| Sumário executivo | `build-executive-summary.md` | `technical-writer.md` | `executive-summaries.md` |
| Construção de DRE | `build-dre.md` | `financial-analyst.md` | `financial-analytics.md` |
| Cascateamento de metas | `cascade-targets.md` | `budget-planner.md` | `budget-cascade.md` |
| Deck executivo | `create-corporate-presentation.md` | `presentation-strategist.md` | `corporate-presentations.md` |
| Revisão de SQL | `review-sql-query.md` | `sql-optimizer.md` | `sql-development.md` |
| Planejamento de pipeline | `plan-data-pipeline.md` | `data-engineer.md` | `etl-data-lake.md` |
| Validação de dados | `validate-data-quality.md` | `data-engineer.md` | `data-quality-framework.md` |
| Coleta web | `scrape-and-structure.md` | `web-scraper.md` | `webscraping.md` |
| Workflow multi-agente | `run-subagent-workflow.md` | `orchestrator.md` | `subagent-orchestration.md` |
| Estrutura de dashboard | `design-dashboard.md` | `dashboard-designer.md` | `dashboard-design.md` |
| Dashboard HTML | `create-html-dashboard.md` | `dashboard-designer.md` | `dashboard-html.md` |
| Melhoria de texto | `improve-professional-text.md` | `technical-writer.md` | `technical-writing.md` |

---

## Observações

- Commands não substituem skills, rules ou agents; eles aceleram tarefas recorrentes.
- Quando houver dúvida, escolha o command mais próximo da **entrega final** que você quer.
- Se a tarefa estiver muito aberta, comece por skill ou agent antes do command.
- Mantenha este guia atualizado sempre que um novo command for criado.

---

## Estrutura atual

```text
.claude/commands/
├── analyze-business-problem.md
├── analyze-credit.md
├── analyze-financial.md
├── analyze-funnel.md
├── build-dre.md
├── build-executive-summary.md
├── cascade-targets.md
├── create-corporate-presentation.md
├── create-html-dashboard.md
├── design-dashboard.md
├── improve-professional-text.md
├── plan-data-pipeline.md
├── review-sql-query.md
├── run-subagent-workflow.md
├── scrape-and-structure.md
└── validate-data-quality.md
```

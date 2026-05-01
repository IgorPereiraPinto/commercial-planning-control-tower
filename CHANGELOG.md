# CHANGELOG

Registro de alterações relevantes no repositório `planejamento-comercial`.

---

## [1.3] — 2026-04-30

### Adicionado

- `sql/sqlserver/08_comissao.sql` — camada analítica de comissão com `config.param_regra_comissao` (6 faixas de payout parametrizáveis), `config.param_prioridade_produto` (multiplicadores P1-P4), `dw.fComissaoMensal` (fato mensal com status Provisao/Definitivo/Pago) e scripts de carga, validação e provisão mensal
- Dashboard: dois novos KPI cards — **Previsão de Receita (mês)** e **Provisão de Comissão (mês)** — na aba Comissão e Mix, baseados no run rate do período filtrado
- Dashboard: seção **Calendário corporativo de comissão** com 7 eventos do ciclo mensal (dia 20 → projeção, dia 22 → provisão, dia 24 → validação, dia 27 → envio ao financeiro, dia 03+1 → fechamento, dia 05+1 → definitivo, dia 10+1 → pagamento)
- README: seção **Calendário corporativo de comissão** com tabela de responsáveis por etapa
- README: seção **Premissas e Limitações** documentando dados fictícios, dependências, restrições do Pages e do Power BI

### Atualizado

- `.github/workflows/pages.yml` — adicionado `cp -r assets _site/` para garantir que `assets/js/chart.umd.min.js` seja publicado no GitHub Pages (correção de bug: dashboard ficava sem gráficos no Pages)
- `README.md` — reescrito com acentuação completa (UTF-8), estrutura do repositório atualizada com `assets/` e `powerautomate/`, novo arquivo `08_comissao.sql` listado, seção de automação expandida
- Todos os 31 arquivos não-legacy — substituição de "Commercial Planning Control Tower" por "Planejamento Comercial" para consistência de nomenclatura do projeto
- Dashboard: adicionada classe CSS `.c-violet` para os novos KPI cards de provisão
- Dashboard: adicionados estilos `.cal-grid`, `.cal-item` e variantes de cor para o calendário corporativo

---

## [1.2] — 2026-04-30

### Adicionado

- `assets/js/chart.umd.min.js` — Chart.js 4.4.1 bundled localmente, eliminando dependência de CDN externo
- `sql/extras/README.md` — documentação do diretório de queries extras com convenções de nomenclatura

### Atualizado

- `index.html` — reescrita completa do portal com hierarquia visual executiva, fluxo "Por onde começar" (6 etapas), SVG icons por seção, mapa do repositório (6 cards), seção de pré-requisitos com comandos de instalação, correção de acentuação
- `.env.example` — padrão `[EDITÁVEL]` aplicado por campo com instruções específicas por variável
- `docs/como_executar.md` — reescrita com sequência de setup, modo dry-run documentado (tabela de etapas, saída esperada, arquivos esperados em data/raw/), critérios de sucesso, split de pré-requisitos por escopo
- `dashboards/planejamento_comercial.html` — referência CDN substituída por bundle local; marcadores `// [EDITÁVEL]` adicionados a toda a camada de dados (MONTHS, HISTORY_LABELS, BASE_RATE, PERIODS, sellers, categories, products, history, marginTrend, payoutFactor)
- `sql/sqlserver/00_setup.sql` até `07_analytical_queries.sql` — marcadores `-- [EDITÁVEL]` adicionados ao nome do banco, thresholds e parâmetros ajustáveis
- `src/etl/extract.py` — `[EDITÁVEL]` em VENDAS_SKIPROWS e nas chaves de DIMENSOES_SHEETS
- `src/etl/transform.py` — cabeçalho de constantes de colunas atualizado para `[EDITÁVEL]`
- `src/etl/validate.py` — `[EDITÁVEL]` em STATUS_VALIDOS, QTD_VENDEDORES_ESPERADOS, QTD_MESES_ESPERADOS, VENDAS_COLUNAS_CHAVE, FOREIGN_KEYS
- `powerbi/dax/medidas_completas.dax` — cabeçalho com bloco `[EDITÁVEL]` listando todos os nomes de tabela e instrução de rename via Ctrl+H; `[EDITÁVEL]` no threshold MAPE
- `powerautomate/GUIA_POWER_AUTOMATE.md` — servidor hardcoded substituído por `SEU_SERVIDOR`; padrão `[EDITÁVEL]` aplicado
- `powerautomate/flows/01_alerta_baixo_atingimento.md` — threshold `< 70` marcado como `[EDITÁVEL]` com instrução de ajuste

---

## [1.1] — 2026-04-27

### Adicionado

- `.claude/settings.json` — configuração de hooks, permissões e variáveis de ambiente
- `.claude/agents/financial-analyst.md` — agente para DRE, margens e análise financeira
- `.claude/agents/credit-analyst.md` — agente para carteira de crédito, PDD e aging
- `.claude/agents/budget-planner.md` — agente para cascateamento de metas e forecast
- `.claude/agents/product-analyst.md` — agente para portfólio de produtos e curva ABC
- `.claude/agents/web-scraper.md` — agente para coleta de dados públicos via scraping
- `.claude/agents/orchestrator.md` — agente-mestre de orquestração multi-agent (expandido com 5 workflows completos)
- `.claude/subagents/output-validator.md` — validador final de qualidade de entregáveis
- `.claude/workflows/` — pasta com 5 workflows executáveis ponta a ponta:
  - `financial-analysis-flow.md`
  - `commercial-performance-flow.md`
  - `data-pipeline-review-flow.md`
  - `credit-analysis-flow.md`
  - `executive-report-flow.md`
- `.claude/templates/sql/sales_performance.sql` — template CTE de performance comercial
- `.claude/templates/sql/financial_dre.sql` — template CTE de DRE gerencial
- `.claude/templates/python/pipeline_etl.py` — template de pipeline ETL Bronze→Silver→Gold
- `.claude/templates/python/api_extraction.py` — template de extração via API REST com retry e paginação
- `.claude/templates/html/dashboard_base.html` — template de dashboard executivo single-file
- 8 novos commands: `analyze-credit`, `analyze-financial`, `analyze-funnel`, `build-dre`, `cascade-targets`, `run-subagent-workflow`, `scrape-and-structure`, `validate-data-quality`

### Atualizado

- `AGENTS_GUIDE.md` — incluídos os 16 agentes com novos fluxos e combinações
- `COMMANDS_GUIDE.md` — incluídos os 16 commands com novos fluxos e combinações
- `SKILLS_GUIDE.md` — adicionado header de versão
- `SUBAGENTS_GUIDE.md` — adicionado header de versão
- `.claude/skills/data-analysis.md` — seção "Rules complementares" adicionada
- `.claude/skills/sql-development.md` — seção "Rules complementares" adicionada
- `.claude/skills/financial-analytics.md` — seção "Rules complementares" adicionada
- `.claude/skills/credit-analytics.md` — seção "Rules complementares" adicionada
- `.claude/skills/etl-data-lake.md` — seção "Rules complementares" adicionada
- `.claude/skills/powerbi-development.md` — seção "Rules complementares" adicionada
- `.claude/skills/machine-learning.md` — seção "Rules complementares" adicionada
- `.claude/skills/dashboard-html.md` — seção "Rules complementares" adicionada
- `.claude/skills/business-intelligence.md` — seção "Rules complementares" adicionada
- `.claude/skills/corporate-presentations.md` — seção "Rules complementares" adicionada

---

## [1.0] — 2026-04-09

### Adicionado

- Estrutura inicial do repositório com CLAUDE.md, README.md, SKILLS_GUIDE.md
- 30 rules cobrindo todos os domínios principais
- 43 skills por domínio e tipo de trabalho
- 10 agents base: data-analyst, bi-analyst, data-engineer, sql-optimizer, technical-writer, powerbi-specialist, dashboard-designer, ml-analyst, automation-architect, presentation-strategist
- 8 commands base: analyze-business-problem, build-executive-summary, create-corporate-presentation, review-sql-query, design-dashboard, create-html-dashboard, plan-data-pipeline, improve-professional-text
- 6 subagents: sql-reviewer, data-quality-checker, hypothesis-generator, kpi-validator, insight-writer, code-reviewer
- AGENTS_GUIDE.md, COMMANDS_GUIDE.md, SUBAGENTS_GUIDE.md

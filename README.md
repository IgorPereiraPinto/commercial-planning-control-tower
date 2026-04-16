# Commercial Planning Control Tower

Pipeline de dados ponta a ponta para análise de performance comercial, forecast e budget.  
Consolida 6 fontes Excel em um star schema no SQL Server, com dashboards Power BI, automação via Power Automate e apresentação executiva.

---

## Visão geral

| Camada | Tecnologia | Descrição |
| ------ | ---------- | --------- |
| Extração | Python / pandas | Lê Vendas.xlsx, Dimensões.xlsx e Meta YYYY.xlsx |
| Transformação | Python / pandas | Limpeza, tipagem, UNPIVOT das metas (wide → long) |
| Qualidade | Python (validate.py) | 4 testes RAW + 7 testes STAGING com bloqueio de pipeline |
| Armazenamento | SQL Server | 3 schemas: raw · staging · dw (star schema Kimball) |
| Modelo analítico | Power BI | Star schema com 2 fatos, 8 dimensões e 20+ medidas DAX |
| Automação | Power Automate | 5 fluxos: alertas, resumo semanal, refresh automático |
| Apresentação | HTML / PowerPoint | 14 slides, self-contained, navegação por teclado |

---

## Estrutura do projeto

```text
Planejamento Comercial/
│
├── src/
│   ├── config/
│   │   └── settings.py          # Variáveis de ambiente, conexão, caminhos
│   └── etl/
│       ├── extract.py           # E: lê os arquivos Excel (raw)
│       ├── transform.py         # T: limpa, tipifica, UNPIVOT metas
│       ├── validate.py          # Validações raw e staging
│       ├── load.py              # L: grava em raw.* e staging.*
│       ├── load_dw.py           # L: grava em dw.* via INSERT...SELECT
│       └── pipeline.py          # Orquestrador: 7 etapas end-to-end
│
├── sql/
│   ├── raw/
│   │   └── 01_create_raw_tables.sql
│   ├── staging/
│   │   └── 02_create_staging_tables.sql
│   └── dw/
│       ├── 03_create_dimensions.sql   # 8 dimensões do star schema
│       ├── 04_create_facts.sql        # fVendas + fMetas (com colunas PERSISTED)
│       ├── 05_populate_dCalendario.sql
│       ├── 06_create_indexes.sql
│       └── 07_analytical_queries.sql  # Queries analíticas de referência
│
├── tests/
│   ├── conftest.py              # Setup de env + markers unit/integration
│   ├── test_extract.py          # [integration] testa leitura dos Excel
│   ├── test_transform.py        # [unit] testa transformações com fixtures
│   └── test_validate.py         # [unit] testa todos os validadores
│
├── powerbi/
│   ├── MODELO_POWERBI.md        # Guia de configuração do modelo
│   ├── medidas_dax/
│   │   └── medidas_completas.dax   # 20+ medidas em 6 Display Folders
│   └── rls/
│       └── rls_roles_completo.md   # RLS por gerente: Guardiola, Marta, Zagallo
│
├── powerautomate/
│   ├── GUIA_POWER_AUTOMATE.md
│   ├── flows/
│   │   ├── 01_alerta_baixo_atingimento.md
│   │   ├── 02_resumo_semanal.md
│   │   ├── 03_alerta_meta_em_risco.md
│   │   ├── 04_celebracao_meta_superada.md
│   │   └── 05_refresh_automatico.md
│   └── templates/
│       └── email_html_base.html    # Template reutilizável para e-mails
│
├── apresentacao/
│   ├── apresentacao_comercial.html  # Apresentação 14 slides (self-contained)
│   ├── ESTRUTURA_APRESENTACAO.md    # Guia slide a slide com mensagem central
│   └── SCRIPT_NARRACAO.md          # Script para "Notas do Orador"
│
├── docs/
│   └── GUIA_IMPLEMENTACAO.md    # Guia passo a passo de implementação
│
├── Dimensões/
│   └── Dimensões.xlsx           # 7 abas: dProdutos, dVendedor, dClientes...
├── Extrações/
│   └── Vendas.xlsx              # ~20.004 transações (Jan/2018 – Abr/2021)
├── Metas/
│   ├── Meta 2018.xlsx
│   ├── Meta 2019.xlsx
│   ├── Meta 2020.xlsx
│   └── Meta 2021.xlsx           # Formato wide: vendedor × mês (528 linhas total)
│
├── logs/                        # Gerado automaticamente na primeira execução
├── .env.example                 # Template com todas as variáveis necessárias
├── .gitignore
├── requirements.txt             # Dependências de produção
└── requirements-dev.txt         # + pytest, black, flake8, ipykernel
```

---

## Início rápido

### 1. Ambiente

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements-dev.txt
```

### 2. Configuração

```bash
cp .env.example .env
# Edite .env com as credenciais do SQL Server local
```

Variáveis obrigatórias no `.env`:

```env
DB_SERVER=localhost\SQLEXPRESS
DB_DATABASE=planejamento_comercial
DB_TRUSTED_CONNECTION=yes
```

### 3. Criar o banco

Execute os scripts SQL na ordem numérica no SQL Server Management Studio (SSMS):

```text
sql/raw/01_create_raw_tables.sql
sql/staging/02_create_staging_tables.sql
sql/dw/03_create_dimensions.sql
sql/dw/04_create_facts.sql
sql/dw/05_populate_dCalendario.sql
sql/dw/06_create_indexes.sql
```

### 4. Rodar o pipeline

```bash
# Dry run — valida tudo sem gravar no banco
python -m src.etl.pipeline --dry-run

# Execução completa (raw → staging → dw)
python -m src.etl.pipeline
```

### 5. Testes

```bash
# Testes unitários (não precisam de arquivos Excel nem SQL Server)
pytest tests/ -m unit -v

# Todos os testes (precisa dos arquivos Excel na raiz)
pytest tests/ -v

# Com cobertura de código
pytest tests/ --cov=src -v
```

---

## Pipeline ETL — 7 etapas

```text
1. Extract      → lê Excel (raw)
2. Validate Raw → 4 testes de estrutura: colunas, volume, anos de meta, formato wide
3. Transform    → limpeza, tipagem, UNPIVOT, metadados _etl_*
4. Validate STG → 7 testes de negócio: FK, duplicatas, nulos, status, MAPE
5. Load Raw     → raw.fVendas + raw.dProdutos + raw.dVendedor + ...
6. Load Staging → staging.fVendas + staging.fMetas + staging.d*
7. Load DW      → INSERT...SELECT de staging → dw (star schema completo)
```

Falhas críticas em qualquer etapa interrompem o pipeline antes de gravar.  
O dado raw não é modificado após a carga — base para reprocessamento seguro.

---

## Modelo dimensional (star schema)

```text
                    dw.dCalendario
                          |
  dStatus   dPagamento    |    dUnidades   dCidade
      \          \        |       /            |
       -------  dw.fVendas  ------        dClientes
                    |
          dVendedor |  dProdutos

      dw.fMetas ---- dVendedor
              \----- dCalendario
```

**Colunas calculadas (PERSISTED) em dw.fVendas:**

- `[Margem Bruta]` = Faturamento Total − Custo Total
- `[Resultado Liquido]` = Faturamento − Custo − Despesas − Impostos − Comissão

Calculadas uma vez no SQL Server, não recalculadas no DAX a cada interação.

---

## Power BI

- **Conexão:** SQL Server `noteigor\SQLEXPRESS` → schema `dw`
- **Medidas DAX:** 20+ medidas em 6 Display Folders (`_Medidas` table)
- **RLS:** filtro em `dVendedor[Gerente]` — roles: Guardiola, Marta, Zagallo, Admin
- **Relacionamento inativo:** `fMetas[Data Meta] → dCalendario[Data]` — ativado via `USERELATIONSHIP` na medida `Meta`

Guia completo: [powerbi/MODELO_POWERBI.md](powerbi/MODELO_POWERBI.md)

---

## Power Automate — 5 fluxos

| Fluxo | Gatilho | Ação |
| ----- | ------- | ---- |
| 01 Alerta baixo atingimento | Segunda 08h | E-mail com vendedores < 70% da meta |
| 02 Resumo semanal | Sexta 17h | E-mail com KPIs da semana + ranking |
| 03 Alerta meta em risco | Dia 20 08h | E-mail com projeção e severidade |
| 04 Celebração meta superada | Alerta Power BI | Post no Teams + e-mail |
| 05 Refresh automático | Segunda 06h | Refresh do dataset + e-mail de status |

Guia completo: [powerautomate/GUIA_POWER_AUTOMATE.md](powerautomate/GUIA_POWER_AUTOMATE.md)

---

## Próximos passos (Fase 3)

- **Forecast com ML:** Prophet ou XGBoost sobre série temporal mensal por vendedor
- **LLM narrativo:** Python lê o DW → chama API do Claude → gera diagnóstico em linguagem natural para o Page 7 do dashboard
- **Azure Function:** substituir o Task Scheduler local pelo Cenário A do Fluxo 5

---

## Dados

- **fVendas:** ~20.004 transações · Jan/2018 – Abr/2021
- **fMetas:** 528 registros · 11 vendedores × 12 meses × 4 anos
- **Dimensões:** 8 tabelas (Produtos, Vendedor, Clientes, Cidade, Unidades, Status, Pagamento, Calendário)

---

## Competências e atribuições atendidas

O projeto cobre diretamente as seguintes atribuições de analítica avançada e planejamento orientado por dados:

| Atribuição | Como o projeto atende |
| ---------- | --------------------- |
| **Aplicar técnicas de IA/LLM e análise de dados para geração de insights estratégicos** | 3 cenários de forecast via run rate; pipeline ML-ready (star schema pronto para Prophet/XGBoost); MAPE como métrica de qualidade do planejamento; insights automáticos de tendência, risco de budget e aceleração por vendedor |
| **Benchmark de melhores práticas internas e externas** | Comparação histórica 2018–2021 como benchmark interno; referências de S&OP (MAPE < 10% excelente, revisão trimestral de forecast, semáforo 70/90% como régua comercial padrão de mercado) |
| **Identificar e integrar soluções analíticas às esteiras, validando valor para o negócio** | Pipeline 7 etapas (Extract → Validate RAW → Transform → Validate STAGING → Load DW); 5 fluxos Power Automate integrados à operação; valor validado: detecção de desvio 30–45 dias antes vs processo manual |
| **Mineração e análise de dados para geração de insights e melhorias** | ~20.004 transações processadas + 528 metas; decomposição de desvio (volume × preço × mix); descoberta não óbvia: efeito Janeiro mascarando deterioração real em 2021 (140% → 48% em 4 meses) |
| **Desenvolver análises para apoiar estratégias de jornada, personalização e recuperação** | Semáforo individual por vendedor; aceleração necessária calculada por vendedor (não apenas gap agregado); mapa de risco por nível de atingimento para priorizar intervenção |
| **Atuar com áreas de negócio na geração de análises orientadas por dados** | Dashboard executivo Power BI com RLS por gerente; apresentação executiva HTML (10 slides, auto-navegável); alertas automáticos via Power Automate para o time comercial |
| **Analisar indicadores de qualidade para direcionar melhorias de processo** | 11 testes automatizados de qualidade de dados (4 RAW + 7 STAGING, com bloqueio de pipeline em falha); MAPE como KPI de processo de planejamento; validação de integridade referencial antes de qualquer carga no DW |

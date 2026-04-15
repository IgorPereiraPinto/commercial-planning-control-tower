# Commercial Planning Control Tower — Forecast & Budget

**Versão:** 2.0  
**Data:** Abril de 2026  
**Responsável:** Igor Pereira Pinto — Analista de Dados/BI e Planejamento Comercial Sênior  
**Stack:** Excel → Python → SQL Server → Power BI → Power Automate → PowerPoint

---

## 1. Visão Estratégica do Projeto

### Objetivo central

Construir um **Commercial Planning Control Tower** que unifique planejamento, execução e monitoramento comercial em uma plataforma analítica única — conectando **budget → forecast → realizado** com rastreabilidade, governança e geração de insights acionáveis por vendedor, produto, região e unidade.

### Problema de negócio

As informações de meta e realizado estão fragmentadas em arquivos Excel individuais por ano (2018–2021), sem padronização, sem histórico consolidado e sem visibilidade gerencial em tempo real. Isso impede:

- Comparação de meta vs. realizado em múltiplas dimensões (vendedor, produto, período, unidade)
- Geração de forecast confiável baseado em tendência histórica
- Identificação rápida de desvios e oportunidades comerciais
- Tomada de decisão ágil da liderança

### Decisão que o projeto apoia

> **"Estamos no caminho certo para bater a meta? Onde estão os desvios e qual a ação prioritária?"**

### Os três pilares do Control Tower

| Pilar | Pergunta central | Fonte |
|---|---|---|
| Planejar (Budget) | Qual é a meta por vendedor e período? | fMetas (2018–2021) |
| Prever (Forecast) | O que vamos realizar até o fim do mês/ano? | fVendas + modelo de ritmo |
| Monitorar (Realizado) | Como estamos em relação à meta agora? | fVendas (transacional) |

---

## 2. Inventário de Fontes de Dados

### Dimensões (Dimensões/Dimensões.xlsx)

| Tabela       | Linhas | Granularidade                  | Colunas principais                              |
|--------------|--------|--------------------------------|-------------------------------------------------|
| dProdutos    | 499    | Um produto                     | Id Produto, Produto, Categoria, Subcategoria, Marca |
| dVendedor    | 20     | Um vendedor                    | Id Vendedor, Vendedor, URL Foto, Gerente        |
| dClientes    | 9.760  | Um cliente                     | Id Cliente, Cliente, Id Cidade                  |
| dCidade      | 9.888  | Uma cidade                     | Id Cidade, Cidade, UF, Estado                   |
| dUnidades    | 11     | Uma unidade de negócio         | Id Unidade, Unidade (Filial 1-9 + Matriz)       |
| dStatus      | 3      | Um status de pedido            | Id Status, Status (Válidas / Inválidas)         |
| dPagamento   | 5      | Uma forma de pagamento         | Id Pagamento, Forma de Pagamento                |

### Fato de Vendas (Extrações/Vendas.xlsx)

| Atributo        | Valor                              |
|-----------------|------------------------------------|
| Tabela          | fVendas                            |
| Linhas          | 20.004 transações                  |
| Período         | Janeiro 2018 a Abril 2021          |
| Granularidade   | Uma linha por item de venda        |
| Métricas        | Qtde, Valor Unit, Custo Unit, Despesa Unit, Impostos Unit, Comissão Unit, Faturamento Total, Custo Total |

### Metas (Metas/Meta 2018–2021.xlsx)

| Atributo        | Valor                                                 |
|-----------------|-------------------------------------------------------|
| Estrutura       | Um arquivo por ano, aba "Meta"                        |
| Granularidade   | Uma linha por vendedor, colunas = meses               |
| Vendedores      | 11 (Ronaldo, Rodrigo, Paola, Neymar, Marilia, Luan, Lazaro, Messi, Gustavo, Lilia, Cristiano) |
| Gerentes        | Guardiola, Marta, Zagallo                             |

---

## 3. Arquitetura de Dados

```
[Excel: Dimensões + Vendas + Metas]
          |
          v
  [Python ETL — src/etl/]
  - Ingestão, validação de qualidade
  - Testes automatizados
          |
          v
  [SQL Server — Schema: raw]
  - Espelho fiel das fontes
  - Sem transformação
          |
          v
  [SQL Server — Schema: staging]
  - Limpeza, tipagem, deduplicação
  - Normalização de nomes
  - Unpivot das metas mensais
          |
          v
  [SQL Server — Schema: dw]
  - Star Schema: Fato + Dimensões
  - Tabela de metas consolidada
  - Calendário integrado
          |
          v
  [Power BI — Dataset + Relatório]
  - RLS por gerente
  - Dashboard executivo + analítico
  - Insights automáticos
          |
          v
  [Power Automate — Alertas]
  - Atingimento abaixo do limiar
  - Resumo semanal de performance
```

---

## 4. Modelagem SQL Server

### 4.1 Schema: `raw`

Espelho direto das planilhas Excel, sem alteração. Preserva o dado bruto para auditoria e reprocessamento.

```
raw.fVendas
raw.dProdutos
raw.dVendedor
raw.dClientes
raw.dCidade
raw.dUnidades
raw.dStatus
raw.dPagamento
raw.fMetas_2018
raw.fMetas_2019
raw.fMetas_2020
raw.fMetas_2021
```

### 4.2 Schema: `staging`

Limpeza, tipagem e normalização. Metas unpivotadas de colunas mensais para linhas.

```
staging.fVendas          -- cast de tipos, trim de strings, remoção de nulos críticos
staging.dProdutos        -- normalização de categoria/subcategoria
staging.dVendedor        -- padronização de nomes, gerente normalizado
staging.dClientes        -- validação de id cidade
staging.dCidade          -- validação de UF/Estado
staging.dUnidades        -- sem alteração relevante
staging.fMetas           -- UNPIVOT: Id Vendedor | Ano | Mês | Valor Meta
```

### 4.3 Schema: `dw` — Star Schema

```
dw.fVendas               -- fato central de vendas
dw.fMetas                -- fato de metas consolidadas (todos os anos)
dw.dCalendario           -- dimensão tempo (dCalendario)
dw.dProdutos
dw.dVendedor
dw.dClientes
dw.dCidade
dw.dUnidades
dw.dStatus
dw.dPagamento
```

#### Modelo estrela

```
                    dCalendario
                         |
dStatus    dPagamento   |    dUnidades
    \           \        |       /
     ------- fVendas ----------
                         |
              dVendedor  |  dProdutos
                         |
                    dClientes --- dCidade

       fMetas ---- dVendedor
             \---- dCalendario
```

#### Tabela `dw.dCalendario` (campos principais)

```sql
Data, Ano, Semestre, Trimestre, Mes, NomeMes, Semana,
DiaSemana, NomeDiaSemana, AnoMes, InicioMes, FimMes,
IsDiaUtil, IsUltimoMes, IsAnoAtual, IsMesAtual
```

#### Tabela `dw.fMetas`

```sql
Id Vendedor | Id Data (YYYYMM01) | Ano | Mes | Valor Meta
```

---

## 5. Python ETL

### Estrutura de pastas

```
src/
├── etl/
│   ├── extract.py          -- leitura dos arquivos Excel
│   ├── transform.py        -- limpeza, tipagem, unpivot
│   ├── load.py             -- escrita no SQL Server
│   ├── validate.py         -- testes de qualidade automáticos
│   └── pipeline.py         -- orquestração do fluxo completo
├── config/
│   └── settings.py         -- variáveis de ambiente, paths
tests/
├── test_extract.py
├── test_transform.py
└── test_validate.py
requirements.txt
.env.example
```

### Testes e validações automáticas (validate.py)

| Teste                              | Regra                                                      |
|------------------------------------|------------------------------------------------------------|
| Nulos em chaves primárias          | Id Produto, Id Vendedor, Id Cliente != NULL                |
| Integridade referencial            | Todo Id Vendedor em fVendas existe em dVendedor            |
| Duplicidade de transações          | Num Venda + Id Produto único em fVendas                    |
| Cobertura de metas                 | Todos os 11 vendedores com meta para os 12 meses           |
| Valores negativos em faturamento   | Faturamento Total >= 0                                     |
| Data de envio >= data de venda     | Data Envio >= Data                                         |
| Contagem de linhas pós-carga       | Linhas carregadas == linhas extraídas (por tabela)         |
| Status válidos                     | Id Status em (1, 2, 3)                                     |

### Padrão de logging

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/etl.log"),
        logging.StreamHandler()
    ]
)
```

---

## 6. KPIs e Métricas do Projeto

### KPIs de resultado comercial

| KPI                    | Fórmula                                              | Leitura esperada                      |
|------------------------|------------------------------------------------------|---------------------------------------|
| Faturamento Realizado  | SUM(Faturamento Total)                               | Receita bruta do período              |
| Meta do Período        | SUM(Valor Meta)                                      | Alvo estabelecido para o período      |
| % Atingimento          | Faturamento / Meta                                   | Acima de 100% = meta batida           |
| Desvio Absoluto        | Faturamento - Meta                                   | Positivo = superação, negativo = gap  |
| Margem Bruta (R$)      | Faturamento - Custo Total                            | Resultado bruto da operação           |
| Margem Bruta (%)       | (Faturamento - Custo) / Faturamento                  | Benchmark por categoria/produto       |
| Margem Líquida (%)     | (Fat - Custo - Despesa - Imposto - Comissão) / Fat   | Resultado real após todos os custos   |
| Ticket Médio           | Faturamento / Qtde de Vendas                         | Eficiência por transação              |
| Volume de Vendas       | COUNT(DISTINCT Num Venda)                            | Atividade comercial                   |
| Qtde de Itens          | SUM(Qtde)                                            | Volume de produtos vendidos           |

### KPIs de acompanhamento (forecast e tendência)

| KPI                     | Descrição                                              |
|-------------------------|--------------------------------------------------------|
| Forecast MTD Projetado  | Ritmo atual × dias restantes do mês                   |
| Gap para Meta           | Meta - Forecast Projetado                             |
| YTD Realizado           | Acumulado do ano até o mês atual                      |
| YTD Meta                | Meta acumulada até o mês atual                        |
| YoY Faturamento (%)     | Variação vs mesmo período ano anterior                |
| MoM Faturamento (%)     | Variação vs mês anterior                              |
| Ranking Vendedor        | Posição por % atingimento no período                  |

### KPIs de qualidade do forecast

| KPI                     | Fórmula                                                | Leitura esperada                        |
|-------------------------|--------------------------------------------------------|-----------------------------------------|
| MAPE                    | AVG(ABS(Real - Forecast) / Real) × 100                | < 10% = forecast confiável              |
| Erro Absoluto Médio     | AVG(ABS(Real - Forecast))                              | Em R$ — impacto financeiro do erro      |
| Viés do Forecast        | AVG(Real - Forecast)                                   | Positivo = subestimado, negativo = superestimado |

### KPI de concentração (Pareto)

| KPI                         | Descrição                                           |
|-----------------------------|-----------------------------------------------------|
| % Receita Top 3 Vendedores  | Concentração dos 3 maiores no total                 |
| Índice de Pareto            | Qtde de vendedores responsáveis por 80% da receita  |
| Receita por Vendedor        | Faturamento individual vs média do time             |

---

## 7. Leitura Inicial dos Dados — Hipóteses de Negócio

Antes de qualquer modelo ou dashboard, os dados já permitem formular hipóteses acionáveis com base nos padrões observados nas metas e nas transações.

### Padrões identificados nas metas (2018–2021)

| Vendedor   | Padrão observado                                | Hipótese de negócio                                      |
|------------|-------------------------------------------------|----------------------------------------------------------|
| Ronaldo    | Pico isolado em determinados meses              | Dependência de grandes contratos pontuais — risco de concentração |
| Neymar     | Alta volatilidade entre meses                   | Carteira instável ou sazonalidade forte — risco de previsão elevado |
| Luan       | Crescimento progressivo consistente             | Melhor candidato para expansão de carteira e aumento de meta |
| Messi      | Queda em dezembro em múltiplos anos             | Possível sazonalidade negativa no Q4 ou churn de clientes |
| Time geral | Concentração de receita em poucos vendedores    | Análise de Pareto — 3 vendedores podem representar 80% da receita |

### Hipóteses a validar no projeto

1. Existe sazonalidade recorrente no Q1 vs Q4 que impacta o budget?
2. Quantos vendedores representam 80% da receita total? (Pareto)
3. Há correlação entre volatilidade individual e erro de forecast?
4. Vendedores com crescimento consistente têm metas proporcionalmente maiores?
5. O mix de produtos varia entre vendedores de alta e baixa performance?

---

## 8. Power BI — Estrutura do Relatório

### RLS (Row Level Security)

Filtro hierárquico por gerente:

| Papel RLS    | Acesso                                                |
|--------------|-------------------------------------------------------|
| Guardiola    | Ronaldo, Rodrigo                                      |
| Marta        | Paola, Marilia                                        |
| Zagallo      | Neymar + demais do seu grupo                          |
| Diretoria    | Visão completa (sem filtro)                           |

### Páginas do relatório

#### Página 1 — Executive Summary
- Cartões: Faturamento YTD, Meta YTD, % Atingimento, Margem Bruta %
- Gráfico de barras: Meta vs Realizado por mês (acumulado)
- Velocímetro / KPI card: % atingimento do mês atual
- Texto dinâmico: "Estamos X% acima / abaixo da meta"

#### Página 2 — Meta vs. Realizado
- Filtros: Ano, Mês, Unidade, Gerente
- Tabela: Vendedor | Meta | Realizado | % Atingimento | Desvio R$
- Gráfico de barras horizontais: Ranking por % atingimento
- Linha de tendência: Meta vs Realizado mês a mês
- Pareto: Curva acumulada de receita por vendedor (80/20 visual)

#### Página 3 — Análise de Produtos
- Filtros: Categoria, Subcategoria, Marca, Período
- Treemap: Faturamento por Categoria > Subcategoria
- Top 10 produtos por faturamento e por margem
- Dispersão: Volume x Margem (identificar produtos estratégicos)

#### Página 4 — Análise Geográfica
- Mapa: Faturamento por Estado / Cidade
- Tabela: Estado | Faturamento | % do Total
- Filtros: Unidade, Período, Vendedor

#### Página 5 — Análise Financeira
- Waterfall: Faturamento → (-) Custo → (-) Despesa → (-) Imposto → (-) Comissão → Lucro Líquido
- Comparativo de margem por categoria
- Evolução de margem ao longo do tempo

#### Página 6 — Forecast (Projeção)
- Ritmo do mês: Faturamento diário médio × dias úteis restantes
- Gap visual: Meta vs Projeção do mês
- Histórico de desvios para calibrar expectativa
- MAPE por vendedor e por período (acurácia histórica do forecast)
- Classificação de confiabilidade: Alta / Média / Baixa por vendedor (baseada no MAPE)

#### Página 7 — Diagnóstico
- Alertas visuais: vendedores com queda > X% MoM
- Detecção de outliers: transações ou meses fora do padrão histórico
- Comparativo de volatilidade por vendedor (desvio padrão mensal)
- Narrativa automática gerada por LLM: "O que mudou este mês e por quê?" (campo de texto dinâmico alimentado via Python + API LLM)
- Filtros: Período, Vendedor, Unidade

### Medidas DAX principais

```dax
-- Faturamento Realizado
Faturamento = SUM(fVendas[Faturamento Total])

-- Meta do Período
Meta = SUM(fMetas[Valor Meta])

-- % Atingimento
Atingimento % = DIVIDE([Faturamento], [Meta], 0)

-- Desvio
Desvio = [Faturamento] - [Meta]

-- Margem Bruta %
Margem Bruta % = 
    DIVIDE(
        SUM(fVendas[Faturamento Total]) - SUM(fVendas[Custo Total]),
        SUM(fVendas[Faturamento Total]),
        0
    )

-- Margem Líquida %
Margem Líquida % = 
    DIVIDE(
        SUM(fVendas[Faturamento Total])
        - SUM(fVendas[Custo Total])
        - SUMX(fVendas, fVendas[Qtde] * fVendas[Despesa Unit])
        - SUMX(fVendas, fVendas[Qtde] * fVendas[Impostos Unit])
        - SUMX(fVendas, fVendas[Qtde] * fVendas[Comissão Unit]),
        SUM(fVendas[Faturamento Total]),
        0
    )

-- YTD Faturamento
Faturamento YTD = 
    CALCULATE([Faturamento], DATESYTD(dCalendario[Data]))

-- YoY %
YoY % = 
    DIVIDE(
        [Faturamento] - CALCULATE([Faturamento], SAMEPERIODLASTYEAR(dCalendario[Data])),
        CALCULATE([Faturamento], SAMEPERIODLASTYEAR(dCalendario[Data])),
        0
    )

-- Forecast MTD (ritmo diário × dias restantes)
Forecast MTD = 
    VAR DiaAtual = MAX(dCalendario[Data])
    VAR DiasMes = DAY(EOMONTH(DiaAtual, 0))
    VAR DiasDecorridos = DAY(DiaAtual)
    VAR RitmoDiario = DIVIDE([Faturamento MTD], DiasDecorridos, 0)
    RETURN RitmoDiario * DiasMes
```

---

## 8. Power Automate — Automações e Alertas

### Fluxo 1 — Alerta de Baixo Atingimento

**Gatilho:** Scheduled — toda segunda-feira às 08h00  
**Lógica:**
1. Consulta SQL: % atingimento do mês atual por vendedor
2. Filtrar vendedores com atingimento < 70%
3. Enviar e-mail ao gerente responsável com lista e desvio em R$

**Mensagem:** "Atenção: [Vendedor] está em [X]% da meta. Desvio atual: R$ [Y]."

---

### Fluxo 2 — Resumo Semanal de Performance

**Gatilho:** Scheduled — toda sexta-feira às 17h00  
**Lógica:**
1. Consultar: Faturamento da semana, acumulado do mês, % atingimento MTD
2. Montar card de resumo (HTML)
3. Enviar via e-mail ou Teams para todos os gerentes

---

### Fluxo 3 — Alerta de Meta em Risco no Fechamento

**Gatilho:** Todo dia 20 do mês às 08h00  
**Lógica:**
1. Calcular forecast para o mês (ritmo atual × dias restantes)
2. Comparar com meta
3. Se forecast < 90% da meta: disparar alerta para diretoria com gap e ação sugerida

---

### Fluxo 4 — Notificação de Superação de Meta

**Gatilho:** Em tempo real via conector Power BI (quando atingimento > 100%)  
**Lógica:**
1. Detectar quando meta for superada no dashboard Power BI
2. Enviar mensagem de parabéns no canal do Teams do time

---

### Fluxo 5 — Atualização Automática do Dataset

**Gatilho:** Scheduled — toda segunda-feira às 06h00 (antes do expediente)  
**Lógica:**
1. Acionar pipeline Python via HTTP request (Azure Function ou script agendado)
2. Executar ETL completo: extract → validate → load
3. Disparar refresh do dataset no Power BI via API REST
4. Confirmar atualização com e-mail de status: sucesso ou falha com log anexo

**Por que é importante:** garante que os alertas dos Fluxos 1–4 e o dashboard sempre reflitam os dados mais recentes, sem intervenção manual.

---

## 9. Estrutura de Pastas do Projeto

```
Planejamento Comercial/
├── CLAUDE.md
├── README.md
├── PROJETO_PLANEJAMENTO_COMERCIAL.md   <- este arquivo
├── SKILLS_GUIDE.md
├── .env.example
├── requirements.txt
├── requirements-dev.txt
│
├── Dimensões/
│   └── Dimensões.xlsx
├── Extrações/
│   └── Vendas.xlsx
├── Metas/
│   ├── Meta 2018.xlsx
│   ├── Meta 2019.xlsx
│   ├── Meta 2020.xlsx
│   └── Meta 2021.xlsx
│
├── src/
│   ├── etl/
│   │   ├── extract.py
│   │   ├── transform.py
│   │   ├── validate.py
│   │   ├── load.py
│   │   ├── load_dw.py
│   │   └── pipeline.py
│   └── config/
│       └── settings.py
│
├── sql/
│   ├── raw/
│   │   └── 01_create_raw_tables.sql
│   ├── staging/
│   │   └── 02_create_staging_tables.sql
│   └── dw/
│       ├── 03_create_dimensions.sql
│       ├── 04_create_facts.sql
│       ├── 05_populate_dCalendario.sql
│       ├── 06_create_indexes.sql
│       └── 07_analytical_queries.sql
│
├── tests/
│   ├── conftest.py
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_validate.py
│
├── powerbi/
│   ├── MODELO_POWERBI.md
│   ├── medidas_dax/
│   └── rls/
│
├── powerautomate/
│   ├── GUIA_POWER_AUTOMATE.md
│   ├── flows/
│   └── templates/
│
├── apresentacao/
│   └── apresentacao_comercial.html
│
├── docs/
│   └── GUIA_IMPLEMENTACAO.md
│
└── logs/
    └── etl.log
```

---

## 10. Papéis e Responsabilidades

### Analista de Dados / BI Sênior (Igor Pereira Pinto)

| Responsabilidade                                    | Entregável                                      |
|-----------------------------------------------------|-------------------------------------------------|
| Modelagem de dados (raw, staging, DW)               | Scripts SQL Server + documentação               |
| ETL com Python (extração, validação, carga)         | src/etl/ com testes automatizados               |
| Desenvolvimento do modelo dimensional               | Star schema no SQL Server                       |
| Construção do relatório Power BI + RLS              | .pbix com medidas DAX e segurança por gerente   |
| Automações de alerta via Power Automate             | Fluxos documentados e ativos                    |
| Benchmark de melhores práticas                      | Documentação de padrões e decisões              |
| Apresentação do case em PowerPoint                  | Deck executivo com estrutura e narrativa clara  |

### Stakeholders e Interlocutores

| Papel             | Contribuição esperada                                      |
|-------------------|------------------------------------------------------------|
| Gerentes (Guardiola, Marta, Zagallo) | Validar metas, confirmar regras de negócio |
| Diretoria         | Definir KPIs prioritários e aprovar arquitetura            |
| TI / DBA          | Acesso ao SQL Server e configuração de ambientes           |
| Time Comercial    | Feedback sobre usabilidade e acurácia dos dados            |

---

## 11. Estrutura da Apresentação PowerPoint

### Deck: Case de Planejamento Comercial

| Slide | Título                                  | Mensagem central                                                     |
|-------|-----------------------------------------|----------------------------------------------------------------------|
| 1     | Commercial Planning Control Tower       | Estratégia → Execução → Monitoramento → Decisão em uma plataforma   |
| 2     | O Problema                              | Dados fragmentados = decisão lenta, forecast impreciso e retrabalho  |
| 3     | O Que Tínhamos                          | 6 fontes Excel, 20K transações, 4 anos de metas, 11 vendedores       |
| 4     | Hipóteses de Negócio                    | Pareto, volatilidade, sazonalidade — o que os dados já revelam       |
| 5     | A Arquitetura Proposta                  | Excel → Python → SQL Server → Power BI → Power Automate              |
| 6     | Modelagem de Dados                      | Star schema com 2 fatos, 8 dimensões e dCalendario                   |
| 7     | Qualidade de Dados                      | 8 testes automatizados com logging e rastreabilidade ponta a ponta   |
| 8     | Dashboard Executivo                     | 7 páginas: Executive Summary, Meta vs Realizado, Produtos, Geo, Financeiro, Forecast, Diagnóstico |
| 9     | Acurácia do Forecast (MAPE)             | Como medimos a qualidade da previsão e reduzimos o erro ao longo do tempo |
| 10    | Segurança e Governança (RLS)            | Cada gerente vê apenas o seu time — diretoria vê tudo                |
| 11    | Automação de Alertas                    | 5 fluxos Power Automate: alerta, resumo, risco, celebração, refresh  |
| 12    | Resultados Esperados                    | Decisão mais rápida, previsibilidade, rastreabilidade, sem retrabalho |
| 13    | Próximos Passos                         | Prophet/ML, simulação de metas, forecast por segmento, integração CRM |

---

## 12. Próximos Passos

### Fase 1 — Fundação (prioridade alta)

| # | Ação                                              |
|---|---------------------------------------------------|
| 1 | Configurar ambiente Python + SQL Server + .env    |
| 2 | Implementar ETL: extract.py + validate.py         |
| 3 | Criar schemas raw e staging no SQL Server         |
| 4 | Criar DW (star schema) + dCalendario              |
| 5 | Desenvolver relatório Power BI + medidas DAX      |
| 6 | Configurar RLS por gerente (Guardiola, Marta, Zagallo) |

### Fase 2 — Automação e Apresentação (prioridade média)

| # | Ação                                                        |
|---|-------------------------------------------------------------|
| 7 | Criar 5 fluxos Power Automate (alertas + refresh automático)|
| 8 | Implementar MAPE e página de Diagnóstico no Power BI        |
| 9 | Montar apresentação PowerPoint do case (13 slides)          |

### Fase 3 — Evolução Analítica (futuro)

| # | Ação                                                              |
|---|-------------------------------------------------------------------|
| 10 | Forecast preditivo com Prophet ou XGBoost (série temporal)       |
| 11 | Simulação de metas: "e se a meta fosse X%" — análise de cenários |
| 12 | Forecast por segmento de produto e por unidade                   |
| 13 | Análise de comissão variável (já disponível nos dados)           |
| 14 | Integração com CRM para dados de carteira e pipeline de vendas   |
| 15 | LLM para narrativa automática de diagnóstico ("por que caiu?")   |

---

*Documento v2.0 — 15/04/2026 — Commercial Planning Control Tower — Igor Pereira Pinto*  
*Incorporações v2.0: naming executivo, MAPE, Pareto, hipóteses de negócio, página de Diagnóstico, LLM narrativo, Fluxo 5 Power Automate, evoluções futuras detalhadas, slide de acurácia do forecast.*

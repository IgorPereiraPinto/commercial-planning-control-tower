# Workflow: Análise Financeira Completa

> **domínio:** financeiro | **padrão:** sequencial | **agents:** 3-4 | **tempo estimado:** 30-60 min

## Objetivo
Produzir análise financeira gerencial completa: DRE estruturado, variação vs budget,
margens, hipóteses de desvio e sumário executivo para liderança.

## Quando usar este workflow
- fechamento mensal ou trimestral
- análise de variação orçamentária
- revisão de resultado para CFO ou diretoria
- diagnóstico de deterioração de margem

## Inputs necessários
- dados financeiros do período (lançamentos ou DRE bruto)
- budget ou forecast de referência
- contexto do negócio (produto, segmento, moeda)
- período de análise

---

## Etapas

### Etapa 1 — Construção da DRE e KPIs financeiros
**Agent:** `financial-analyst`
**Input:** dados financeiros + budget + período
**Output:** DRE gerencial, margens (bruta, EBITDA, líquida), variação vs budget em R$ e %
**Prompt sugerido:**
```
Atue como financial-analyst. Monte a DRE gerencial do período [X] comparando
real vs budget. Calcule margens bruta, EBITDA e líquida. Apresente variação
em R$ e %. Base de cálculo: competência. Declare premissas.
```

### Etapa 2 — Validação dos KPIs
**Subagent:** `kpi-validator`
**Input:** KPIs calculados na etapa 1
**Output:** confirmação de consistência ou alertas de divergência
**Prompt sugerido:**
```
Valida os KPIs financeiros abaixo. Verifica fórmulas, bases de cálculo
e consistência entre margens. Alerta se margem EBITDA < margem bruta
ou se variação % não bate com variação absoluta.
[colar KPIs da etapa 1]
```

### Etapa 3 — Hipóteses de desvio
**Subagent:** `hypothesis-generator`
**Input:** variações identificadas na etapa 1
**Output:** hipóteses rankeadas com critérios de validação
**Prompt sugerido:**
```
Gera hipóteses para os desvios abaixo. Rankeia por probabilidade e impacto.
Para cada hipótese, sugere como validar com os dados disponíveis.
[colar variações da etapa 1]
```

### Etapa 4 — Narrativa executiva
**Subagent:** `insight-writer`
**Input:** DRE + variações + hipóteses validadas
**Output:** texto executivo com contexto, achados, causas e recomendação
**Prompt sugerido:**
```
Transforma a análise financeira abaixo em narrativa executiva para o CFO.
Tom: gerencial, objetivo. Máx. 250 palavras. Inclui: contexto, achado
principal, 2-3 causas prováveis, 1 recomendação prioritária.
[colar análise completa]
```

### Etapa 5 — Validação final
**Subagent:** `output-validator`
**Input:** narrativa + DRE
**Output:** checklist de qualidade da entrega

---

## Variações do workflow

### Versão curta (sem validação de KPI)
Etapa 1 → Etapa 3 → Etapa 4

### Versão com deck
Etapa 1 → Etapa 3 → Etapa 4 → `presentation-strategist`

### Versão com forecast
Adicionar após etapa 1: `budget-planner` para projeção do restante do ano

---

## Critérios de qualidade da entrega final
- DRE balanceia (receita - custos = resultado declarado)
- Variações em R$ e % presentes
- Hipóteses separadas de fatos
- Recomendação com ação concreta
- Premissas de cálculo declaradas

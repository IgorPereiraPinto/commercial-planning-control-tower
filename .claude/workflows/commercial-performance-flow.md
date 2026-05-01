# Workflow: Diagnóstico de Performance Comercial

> **domínio:** comercial/vendas | **padrão:** sequencial | **agents:** 3-4 | **tempo estimado:** 30-60 min

## Objetivo
Diagnosticar resultado de vendas, identificar desvios vs meta, propor hipóteses
explicativas e entregar recomendação comercial acionável.

## Quando usar este workflow
- resultado de vendas abaixo ou acima da meta
- necessidade de entender o que está puxando ou freando resultado
- preparação de reunião de performance com gestores
- análise mensal ou trimestral de vendas

## Inputs necessários
- dados de vendas do período (receita, volume, ticket, conversão)
- meta ou budget de referência
- cortes disponíveis (canal, regional, produto, vendedor)
- período de análise

---

## Etapas

### Etapa 1 — Diagnóstico do cenário
**Agent:** `data-analyst`
**Input:** dados de vendas + meta + período
**Output:** KPIs principais, desvios por corte, leitura do cenário
**Prompt sugerido:**
```
Atue como data-analyst. Analisa o resultado de vendas do período [X].
Identifica: (1) desvio total vs meta em R$ e %; (2) desvio por canal,
regional e produto; (3) efeito de volume, preço e mix separados.
Fatos separados de hipóteses.
```

### Etapa 2 — Geração de hipóteses
**Subagent:** `hypothesis-generator`
**Input:** desvios e padrões identificados na etapa 1
**Output:** hipóteses rankeadas com critérios de validação
**Prompt sugerido:**
```
Gera hipóteses explicativas para os desvios de vendas abaixo.
Rankeia por probabilidade e impacto financeiro. Para cada hipótese,
define como validar com os dados disponíveis.
[colar diagnóstico da etapa 1]
```

### Etapa 3 — Validação de KPIs comerciais
**Subagent:** `kpi-validator`
**Input:** KPIs calculados na etapa 1
**Output:** alertas de inconsistência ou confirmação de fórmulas
**Prompt sugerido:**
```
Valida os KPIs comerciais abaixo. Verifica se ticket médio, conversão
e crescimento YoY estão calculados corretamente. Alerta sobre
inconsistências entre KPIs.
[colar KPIs da etapa 1]
```

### Etapa 4 — Narrativa e recomendação
**Subagent:** `insight-writer`
**Input:** diagnóstico + hipóteses + KPIs validados
**Output:** texto executivo com achados, causas e recomendação
**Prompt sugerido:**
```
Transforma a análise comercial abaixo em narrativa executiva para
gestores de vendas. Tom: direto, orientado à ação. Estrutura:
(1) contexto, (2) achado principal, (3) causas prováveis,
(4) recomendação prioritária, (5) próximos passos.
[colar análise completa]
```

### Etapa 5 — Validação final
**Subagent:** `output-validator`
**Input:** entrega completa
**Output:** checklist de qualidade

---

## Variações do workflow

### Versão com apresentação
Adicionar após etapa 4: `presentation-strategist` para montar deck de performance

### Versão com forecast
Adicionar após etapa 4: `budget-planner` para projeção do restante do período

### Versão com análise de funil
Substituir etapa 1 por: `data-analyst` com skill `funnel-analytics`

---

## Critérios de qualidade da entrega final
- desvio em R$ e % presentes
- cortes por canal, regional e produto cobertos
- efeito volume/preço/mix separado
- hipóteses separadas de fatos
- recomendação com ação comercial concreta

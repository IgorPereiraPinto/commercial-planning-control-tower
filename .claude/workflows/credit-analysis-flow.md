# Workflow: Análise de Crédito e Risco de Carteira

> **domínio:** crédito | **padrão:** sequencial | **agents:** 3-4 | **tempo estimado:** 45-90 min

## Objetivo
Produzir análise completa da carteira de crédito: composição, risco, PDD,
aging, tendência e recomendação de política para o comitê de crédito.

## Quando usar este workflow
- revisão periódica da carteira (mensal/trimestral)
- deterioração de inadimplência identificada
- necessidade de revisão de política de aprovação
- preparação para comitê de crédito ou auditoria
- cálculo e justificativa de PDD

## Inputs necessários
- dados da carteira: saldo, produto, segmento, safra, dias de atraso
- histórico de safras (mínimo 6 meses)
- política de classificação vigente (BACEN 2682, IFRS 9 ou interna)
- resultado financeiro anterior (para impacto de PDD)

---

## Etapas

### Etapa 1 — Análise da carteira e KPIs de risco
**Agent:** `credit-analyst`
**Input:** dados da carteira + política de classificação + período
**Output:** KPIs de risco, aging por faixa, PDD calculado, concentrações
**Prompt sugerido:**
```
Atue como credit-analyst. Analisa a carteira de crédito do período [X].
Calcula: (1) inadimplência 15+, 30+, 60+, 90+; (2) aging por faixa de atraso;
(3) PDD por faixa conforme política [BACEN 2682 / IFRS 9 / interna];
(4) concentração top 10 clientes; (5) composição por produto e segmento.
Declara política usada explicitamente.
```

### Etapa 2 — Análise de safra (vintage)
**Agent:** `credit-analyst`
**Input:** histórico de safras + output da etapa 1
**Output:** curva de safra, deterioração por coorte, projeção de perdas
**Prompt sugerido:**
```
Com base nos dados de safra abaixo, faz a análise vintage:
(1) curva de inadimplência por coorte mensal; (2) safras mais problemáticas;
(3) se há deterioração estrutural ou pontual; (4) projeção de perdas
para os próximos 3 meses.
[colar dados de safra]
```

### Etapa 3 — Impacto financeiro do PDD
**Agent:** `financial-analyst`
**Input:** PDD calculado na etapa 1 + resultado financeiro
**Output:** impacto no P&L, variação vs PDD anterior, projeção para o trimestre
**Prompt sugerido:**
```
Atue como financial-analyst. Calcula o impacto do PDD abaixo no resultado
financeiro do período. Compara com PDD do período anterior. Projeta
impacto para os próximos 3 meses com base na tendência da carteira.
[colar PDD da etapa 1]
```

### Etapa 4 — Hipóteses de deterioração
**Subagent:** `hypothesis-generator`
**Input:** tendências da carteira e contexto de negócio
**Output:** hipóteses explicativas priorizadas com critérios de validação
**Prompt sugerido:**
```
Gera hipóteses para a deterioração da carteira abaixo. Considera fatores:
macroeconômicos, sazonalidade, perfil do cliente, produto e canal.
Rankeia por probabilidade. Define como validar cada hipótese.
[colar tendências da etapa 1 e 2]
```

### Etapa 5 — Recomendação de política
**Agent:** `credit-analyst`
**Input:** análise completa + hipóteses + impacto financeiro
**Output:** recomendação de política de aprovação, cobrança e provisionamento
**Prompt sugerido:**
```
Com base na análise completa da carteira abaixo, propõe recomendações de:
(1) política de aprovação (critérios, alçadas, segmentos);
(2) estratégia de cobrança por faixa de atraso;
(3) política de provisionamento para o próximo período.
Prioriza ações por impacto financeiro.
[colar análise completa]
```

### Etapa 6 — Apresentação para comitê
**Agent:** `presentation-strategist`
**Input:** análise + recomendações
**Output:** outline do deck com mensagem por slide

### Etapa 7 — Validação final
**Subagent:** `output-validator`
**Input:** análise completa
**Output:** checklist de qualidade

---

## Variações do workflow

### Versão simplificada (sem vintage)
Etapa 1 → Etapa 3 → Etapa 4 → Etapa 5

### Versão com sumário executivo
Substituir etapa 6 por: `insight-writer` → `technical-writer` para one-pager

---

## Critérios de qualidade da entrega final
- política de classificação declarada explicitamente
- PDD por faixa calculado corretamente
- distinção clara entre inadimplência 15+ e 90+
- concentração top 10 avaliada
- recomendação com ação priorizada
- impacto financeiro quantificado

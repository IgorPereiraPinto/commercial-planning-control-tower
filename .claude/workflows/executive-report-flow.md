# Workflow: Relatório Executivo Completo

> **domínio:** comunicação executiva | **padrão:** sequencial | **agents:** 2-3 | **tempo estimado:** 20-45 min

## Objetivo
Transformar qualquer análise técnica (dados, SQL, financeiro, comercial)
em relatório executivo pronto para liderança: sumário, narrativa e deck.

## Quando usar este workflow
- preparação de material para diretoria ou board
- fechamento de ciclo analítico com entrega executiva
- transformação de análise técnica em comunicação gerencial
- criação de one-pager ou executive briefing

## Inputs necessários
- análise ou dados já processados (de qualquer domínio)
- público-alvo (CEO, CFO, Diretores, Gestores)
- formato desejado (sumário, deck, one-pager, e-mail)
- tom desejado (formal, direto, estratégico)

---

## Etapas

### Etapa 1 — Narrativa executiva
**Subagent:** `insight-writer`
**Input:** análise técnica + contexto + público
**Output:** narrativa executiva com contexto, achados, causas, recomendação
**Prompt sugerido:**
```
Transforma a análise abaixo em narrativa executiva para [público].
Tom: [tom desejado]. Estrutura obrigatória: (1) contexto do período;
(2) achado principal com número; (3) 2-3 causas prováveis;
(4) recomendação com ação; (5) próximos passos.
Máx. [X] palavras.
[colar análise técnica]
```

### Etapa 2 — Revisão de texto
**Agent:** `technical-writer`
**Input:** narrativa da etapa 1
**Output:** texto revisado, humanizado, sem jargões, adequado ao canal
**Prompt sugerido:**
```
Revisa o texto abaixo para [canal: e-mail / relatório / apresentação].
Remove jargões, reduz formalidade excessiva, torna mais natural e direto.
Preserva todos os números e a recomendação principal.
[colar narrativa da etapa 1]
```

### Etapa 3a — Sumário executivo (se formato for one-pager)
**Agent:** `technical-writer` com skill `executive-summaries`
**Input:** texto revisado + dados
**Output:** one-pager estruturado em até 5 parágrafos

### Etapa 3b — Deck (se formato for apresentação)
**Agent:** `presentation-strategist`
**Input:** texto revisado + dados + público
**Output:** outline do deck com mensagem e visual sugerido por slide
**Prompt sugerido:**
```
Atue como presentation-strategist. Monta o outline do deck para [público].
Para cada slide: título conclusivo + mensagem principal + visual sugerido.
Máx. [X] slides. Começa pelo achado mais importante.
[colar texto revisado]
```

### Etapa 4 — Validação final
**Subagent:** `output-validator`
**Input:** entrega final (narrativa ou deck)
**Output:** checklist de qualidade de narrativa executiva

---

## Variações do workflow

### Versão ultra-rápida (sem revisão de texto)
Etapa 1 → Etapa 3a ou 3b

### Versão com análise prévia
Adicionar antes da etapa 1: qualquer workflow analítico (financeiro, comercial, crédito)

### Versão para e-mail executivo
Etapa 1 → Etapa 2 (com instrução de tom para e-mail)

---

## Critérios de qualidade da entrega final
- começa pelo contexto e achado principal
- números presentes com comparativo (vs meta / vs período anterior)
- fatos separados de hipóteses
- recomendação com ação concreta
- tom adequado ao público
- sem jargões vazios

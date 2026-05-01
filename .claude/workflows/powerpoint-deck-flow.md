# Workflow: Construção de Deck PowerPoint

> **domínio:** apresentações | **padrão:** sequencial | **agents:** 2-3 | **tempo estimado:** 20-40 min

## Objetivo
Produzir um deck PowerPoint completo: estrutura, conteúdo por slide, narrativa
executiva e, quando necessário, código python-pptx para geração automática.

## Quando usar este workflow
- transformar análise de dados em apresentação para diretoria ou gestão
- montar deck de resultados periódicos (mensal, trimestral)
- criar apresentação de projeto, proposta ou comitê
- gerar .pptx automaticamente a partir de dados com python-pptx
- refatorar deck existente com mensagem mais clara e estrutura lógica

## Inputs necessários
- análise, dados ou conteúdo a transformar em slides
- público-alvo e decisão esperada da apresentação
- número aproximado de slides
- tom desejado (estratégico, operacional, técnico, comercial)
- ferramenta de destino (PowerPoint, Google Slides, Gamma)
- se deseja código python-pptx para geração automática

---

## Etapas

### Etapa 1 — Estrutura e mensagem central
**Agent:** `presentation-strategist`
**Input:** análise ou conteúdo + público + objetivo
**Output:** mensagem central, outline dos slides com título e tipo de visual
**Prompt sugerido:**
```
Atue como presentation-strategist. Tenho o seguinte conteúdo para transformar
em apresentação para [público]. Objetivo: [decidir / informar / aprovar].
Define: (1) mensagem central em 1 frase; (2) outline dos slides com título
conclusivo e tipo de visual por slide. Máx. [N] slides.
[colar análise ou conteúdo]
```

### Etapa 2 — Conteúdo completo por slide
**Command:** `build-powerpoint-deck`
**Input:** outline da etapa 1 + dados ou análise
**Output:** título, mensagem, bullets, visual e nota de fala por slide
**Prompt sugerido:**
```
Com base no outline abaixo, gera o conteúdo completo de cada slide:
título conclusivo, mensagem principal, máx. 3 bullets com dado ou argumento,
visual recomendado e nota de fala (2-3 frases). Tom: [tom desejado].
[colar outline da etapa 1]
```

### Etapa 3 — Revisão de narrativa
**Subagent:** `insight-writer`
**Input:** conteúdo dos slides
**Output:** ajustes de tom, números traduzidos em impacto, linguagem executiva
**Prompt sugerido:**
```
Revisa o conteúdo dos slides abaixo. Garante que: (1) cada título é conclusivo,
não temático; (2) números têm impacto de negócio; (3) fatos separados de hipóteses;
(4) tom é [tom desejado] para [público]. Sugere ajustes slide a slide.
[colar conteúdo da etapa 2]
```

### Etapa 4a — Validação final (entrega manual)
**Subagent:** `output-validator`
**Input:** conteúdo revisado
**Output:** checklist de qualidade de narrativa executiva

### Etapa 4b — Código python-pptx (entrega automatizada)
**Agent:** `excel-specialist` ou resposta direta
**Input:** conteúdo revisado + template `pptx_report.py`
**Output:** código python-pptx pronto para gerar o .pptx
**Prompt sugerido:**
```
Com base no conteúdo dos slides abaixo e no template pptx_report.py,
gera o código Python completo para criar o arquivo .pptx. Adapta os dados
reais no slide de KPIs e na tabela de resultados.
[colar conteúdo + referência ao template]
```

---

## Variações do workflow

### Versão rápida (outline já existe)
Pular etapa 1 — iniciar direto na etapa 2

### Versão com análise prévia
Adicionar antes da etapa 1: qualquer workflow analítico (financeiro, comercial, crédito)
depois transformar o output em slides na etapa 1

### Versão Gamma
Usar etapas 1 e 2, depois colar o conteúdo no Gamma para geração visual automática

### Versão para comitê de crédito
Combinar com `credit-analysis-flow.md` — usar output daquele workflow como input aqui

---

## Critérios de qualidade da entrega final
- cada slide com uma única mensagem clara
- títulos conclusivos (não "Análise de X")
- máx. 3 bullets por slide
- números com comparativo (vs meta / vs período anterior)
- fatos separados de hipóteses
- recomendação presente no fechamento
- nota de fala cobrindo o que não cabe no slide

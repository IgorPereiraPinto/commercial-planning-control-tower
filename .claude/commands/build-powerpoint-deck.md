---
name: build-powerpoint-deck
description: >
  Atalho para gerar o conteúdo completo de um deck PowerPoint: título, mensagem,
  texto de corpo e visual por slide. Vai além do outline — entrega o conteúdo
  pronto para colar nos slides ou gerar via python-pptx. Use quando o objetivo
  for ter os slides prontos para uso, não apenas a estrutura conceitual.
---

# Build PowerPoint Deck

## Objetivo
Produzir o conteúdo completo dos slides: título conclusivo, mensagem principal,
corpo de texto (máx. 3 bullets), visual recomendado e nota de fala para cada slide.
Diferente de `create-corporate-presentation` (que entrega outline), este command
entrega o material pronto para construir o deck.

## Quando usar
- quando o outline já existe e precisa do conteúdo de cada slide
- quando precisa gerar slides prontos com texto, dados e visual
- quando quer o script de fala junto com o conteúdo
- quando quer o código python-pptx para gerar o .pptx automaticamente
- para decks de resultados, projetos, propostas ou comitê

## Quando NÃO usar
- quando ainda está definindo a estrutura → usar `create-corporate-presentation`
- quando é só narrativa executiva em texto → usar `build-executive-summary`
- quando é one-pager → usar `build-executive-summary`

## Entradas esperadas
- análise, dados ou conteúdo a ser transformado em slides
- público-alvo e objetivo da apresentação
- número de slides ou tópicos a cobrir
- tom desejado (estratégico, operacional, técnico)
- ferramenta de destino (PowerPoint / Google Slides / Gamma)
- se deseja código python-pptx para geração automática

## Como atuar
1. confirmar objetivo, público e mensagem central
2. para cada slide entregar:
   - título conclusivo (não temático)
   - mensagem principal (1 frase)
   - corpo (máx. 3 bullets com dado ou argumento)
   - visual recomendado (tipo de gráfico, tabela, diagrama)
   - nota de fala (opcional, 2-3 frases de apoio)
3. se solicitado, gerar código python-pptx com o conteúdo

## Formato de saída

```
--- SLIDE [N] ---
Título: [conclusão em frase curta]
Mensagem: [1 frase que resume a mensagem do slide]

Corpo:
• [bullet 1 com dado ou argumento]
• [bullet 2 com dado ou argumento]
• [bullet 3 com dado ou argumento — opcional]

Visual: [tipo de gráfico / tabela / diagrama + dados a usar]
Fala de apoio: [2-3 frases para o apresentador]
```

## Rules complementares
- `12_corporate-presentations.md` — padrões de título conclusivo, texto por slide e hierarquia
- `11_executive-storytelling.md` — sequência lógica entre contexto, achado e recomendação
- `22_slide-design.md` — hierarquia visual, equilíbrio de conteúdo e design executivo

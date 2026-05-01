---
name: cowork-notebooklm
description: >
  Especialista em fluxos de trabalho integrados entre Claude Cowork e Google NotebookLM.
  Cobre preparação de documentos com Claude para ingestão no NotebookLM, criação de fontes
  estruturadas (relatórios, sumários, transcrições, análises), extração de insights do
  NotebookLM via guias de perguntas gerados pelo Claude, geração de podcasts automáticos
  a partir de análises, e workflows de pesquisa e síntese de conhecimento.
  Use sempre que o usuário mencionar NotebookLM, preparar documento para NotebookLM,
  criar fonte para notebook, gerar podcast de análise, pesquisa com NotebookLM, síntese
  de documentos, base de conhecimento, ou qualquer workflow combinando Claude e NotebookLM.
  Trigger para: "usa NotebookLM", "prepara documento para NotebookLM", "cria fonte para
  notebook", "gera podcast da análise", "pesquisa no NotebookLM", "cria base de conhecimento",
  "fluxo Claude com NotebookLM", "sintetiza esses documentos no notebook".
---

# Cowork + NotebookLM — Fluxos de Conhecimento Integrados

## Identidade

Especialista em fluxos de pesquisa e síntese de conhecimento que combina o poder analítico
do Claude Cowork com a capacidade de digestão de documentos do Google NotebookLM. Projeta
workflows end-to-end: Claude prepara, estrutura e enriquece o material — NotebookLM ingere,
indexa e permite navegação inteligente. O resultado é muito mais rápido e preciso do que
usar cada ferramenta isoladamente.

---

## Quando Usar

Use esta skill quando você quiser:
- Transformar análises, relatórios ou dados brutos em fontes organizadas para NotebookLM
- Criar guias de perguntas para extrair insights estruturados do NotebookLM
- Gerar podcasts automáticos a partir de análises de negócio
- Construir bases de conhecimento sobre um tema (concorrentes, mercado, regulação)
- Combinar múltiplos documentos em uma fonte coesa para o NotebookLM processar
- Usar o NotebookLM como "segundo cérebro" para projetos longos

---

## O que é cada ferramenta

### Claude Cowork
Ferramenta desktop da Anthropic para não-desenvolvedores. Executa tarefas de arquivo,
análise e automação em linguagem natural — sem terminal, sem código visível.
**Melhor em:** analisar, transformar, redigir, estruturar, resumir, gerar código.

### Google NotebookLM
Plataforma do Google que ingere documentos (PDF, Google Docs, texto, URL, YouTube, áudio)
e cria um modelo de linguagem personalizado sobre aquele corpus específico.
**Melhor em:** responder perguntas sobre um corpus fechado, gerar podcast de áudio,
criar guias de estudo, encontrar conexões entre documentos, sintetizar fontes diversas.

### A combinação ideal

```
Dados brutos / Análises / Relatórios
          ↓
    Claude Cowork
    (prepara, estrutura, enriquece)
          ↓
    Documentos prontos para ingestão
          ↓
    Google NotebookLM
    (indexa, responde, sintetiza, gera podcast)
          ↓
    Insights navegáveis + Áudio podcast
          ↓
    Claude Cowork (opcional)
    (refina insights, formata output final)
```

---

## Padrão 1 — Análise de Negócio → NotebookLM

**Caso de uso:** transformar uma análise de performance em fonte consumível no NotebookLM
para que a equipe possa fazer perguntas em linguagem natural sobre os resultados.

### Passo 1 — Preparar o documento com Claude Cowork

Peça ao Claude Cowork:

```
Transforma essa análise de vendas de março em um documento NotebookLM-ready.
Estruture assim:
1. Contexto do período (1 parágrafo)
2. Principais KPIs com valores e variações
3. Análise por dimensão (regional, canal, produto)
4. Desvios e hipóteses explicativas
5. Recomendações priorizadas
6. Glossário de termos e métricas usadas

Use linguagem clara. Evite abreviações sem explicação.
Salva como "analise_vendas_marco2025_notebooklm.md"
```

### Por que o glossário?

O NotebookLM responde com base no que está nos documentos. Se os termos técnicos não
estiverem explicados, as respostas serão vagas. Claude prepara o glossário; NotebookLM
usa para contextualizar as respostas.

### Passo 2 — Carregar no NotebookLM

1. Acesse [notebooklm.google.com](https://notebooklm.google.com)
2. Crie um novo Notebook (ex: "Performance Comercial — 2025")
3. Clique em "+" → "Upload file" → sobe o `.md` gerado pelo Claude
4. Aguarde o processamento (geralmente < 30 segundos)

### Passo 3 — Guia de perguntas (gerado pelo Claude)

Peça ao Claude antes de entrar no NotebookLM:

```
Gera um guia com 15 perguntas de alta qualidade para extrair os principais insights
desta análise de vendas no NotebookLM. Organize as perguntas em 3 categorias:
- Diagnóstico (o que aconteceu)
- Causa raiz (por que aconteceu)
- Decisão (o que fazer)
```

Use esse guia diretamente no chat do NotebookLM — as respostas serão muito mais ricas.

---

## Padrão 2 — Base de Conhecimento Temática

**Caso de uso:** criar um repositório de conhecimento sobre um tema (regulação, concorrentes,
mercado, produto) que a equipe pode consultar em linguagem natural.

### Etapa 1 — Coletar e preparar fontes com Claude

```
Tenho esses 8 documentos sobre regulação do setor financeiro (PDFs em anexo).
Para cada um:
1. Extrai os pontos principais em bullet points
2. Identifica: órgão regulador, data, impacto, prazo de adequação
3. Gera um resumo de 200 palavras em linguagem executiva

Consolida tudo em um único documento com índice.
Nome: "base_regulacao_financeira_2025.md"
```

### Etapa 2 — Estrutura recomendada do documento para NotebookLM

```markdown
# [Tema da Base de Conhecimento]
**Última atualização:** [data]
**Fontes:** [lista de fontes]

---

## Índice
1. [Tema A]
2. [Tema B]
3. Glossário
4. Cronologia
5. Perguntas frequentes

---

## [Tema A]
### Contexto
[Parágrafo de contexto]

### Pontos principais
- [Ponto 1]: [explicação]
- [Ponto 2]: [explicação]

### Implicações para o negócio
[1-2 parágrafos]

### Fonte original
[Nome, data, URL se disponível]

---
[... demais seções ...]

## Glossário
**[Termo]:** [definição clara]

## Cronologia
| Data | Evento | Impacto |
|------|--------|---------|
| [data] | [evento] | [impacto] |

## Perguntas Frequentes
**P: [pergunta comum]**
R: [resposta direta]
```

### Por que essa estrutura?

NotebookLM recupera trechos específicos dos documentos. Documentos bem estruturados com
seções claras e perguntas frequentes pré-respondidas aumentam significativamente a qualidade
das respostas geradas.

---

## Padrão 3 — Geração de Podcast de Análise

**Caso de uso:** transformar uma análise de dados em episódio de podcast para consumo
rápido pela liderança ou time.

### Por que funciona

O NotebookLM tem uma funcionalidade nativa de geração de podcast ("Audio Overview") que
cria um diálogo entre dois apresentadores discutindo o conteúdo das fontes. A qualidade
do podcast depende diretamente da qualidade dos documentos carregados.

### Workflow completo

**1. Claude prepara o script-base:**

```
Tenho essa análise de NPS do Q1 2025. Transforma em um documento otimizado para
geração de podcast no NotebookLM.

O documento deve:
- Ter linguagem oral, não formal (como se fosse falado)
- Incluir dados com contexto narrativo, não só números
- Ter momentos de tensão: "o que surpreendeu", "o que preocupa", "o que vai mudar"
- Ter perguntas retóricas que um apresentador faria
- Ter conclusão com call-to-action claro

Salva como "nps_q1_2025_podcast_source.md"
```

**2. Carrega no NotebookLM e gera o podcast:**

1. Cria notebook novo → carrega o arquivo
2. Clique em "Audio Overview" (canto superior direito)
3. Clique em "Customize" e adicione instruções:
   - "Foque nos 3 principais desvios de NPS"
   - "Mencione a comparação com Q4 2024"
   - "Encerre com as ações recomendadas"
4. Clique em "Generate"
5. Em 2-5 minutos o podcast está pronto (8-12 minutos de áudio)

**3. Claude finaliza:**

```
Transcreve esse podcast (texto em anexo) e transforma em:
1. Resumo executivo de 1 página
2. E-mail para o time com os 5 pontos principais
3. Slide de abertura para a reunião de resultados
```

---

## Padrão 4 — Pesquisa de Concorrentes / Mercado

**Caso de uso:** criar um repositório de inteligência competitiva navegável.

### Workflow

**1. Claude coleta e organiza:**

```
Tenho esses relatórios anuais dos 3 principais concorrentes (PDFs).
Para cada um, extrai:
- Receita, crescimento, margens (3 últimos anos)
- Principais iniciativas estratégicas
- Citações relevantes do CEO/CFO
- Diferenciais competitivos mencionados
- Riscos declarados

Consolida em uma tabela comparativa + texto por empresa.
Salva como "inteligencia_competitiva_2025.md"
```

**2. Carrega no NotebookLM com fontes múltiplas:**

NotebookLM aceita até 50 fontes por notebook. Para inteligência competitiva:
- 1 arquivo por concorrente (Claude prepara cada um)
- 1 arquivo de tendências de mercado (Claude consolida de múltiplos artigos)
- 1 arquivo com dados próprios da empresa (para comparação)
- 1 arquivo de glossário do setor

**3. Perguntas estratégicas para fazer no NotebookLM:**

```
Claude, gera 20 perguntas de inteligência competitiva para usar no NotebookLM,
cobrindo: posicionamento, pricing, diferenciais, riscos e oportunidades.
```

---

## Padrão 5 — Preparação de Reunião / Comitê

**Caso de uso:** preparar-se para uma reunião importante usando todas as fontes relevantes.

```
Tenho reunião de comitê de crédito amanhã. Os documentos em anexo são:
- Política de crédito atual (PDF)
- Relatório de carteira do mês (Excel já analisado)
- Ata da última reunião (Word)
- 3 casos especiais de aprovação pendente

Faz o seguinte:
1. Transforma cada documento em fonte para NotebookLM (clara, bem estruturada)
2. Gera um guia de 20 perguntas que posso fazer no NotebookLM para me preparar
3. Cria uma "cheat sheet" com os pontos que não posso esquecer de mencionar
4. Sugere 3 perguntas difíceis que podem me fazer e como responder

Salva tudo na pasta "prep_comite_credito_[data]/"
```

---

## Templates de Instruções para o NotebookLM

Use esses prompts diretamente no chat do NotebookLM depois de carregar os documentos:

```
# Diagnóstico
"Quais são os 5 principais problemas ou desvios identificados nos documentos?"
"O que mais surpreende positivamente? O que mais preocupa?"
"Há contradições ou tensões entre os documentos carregados?"

# Síntese
"Resume os documentos em 10 bullet points para uma apresentação executiva"
"Quais decisões são urgentes com base nas informações disponíveis?"
"Crie um FAQ com as 10 perguntas mais prováveis de uma liderança sobre esse tema"

# Comparação
"Compare [empresa/produto/período A] com [empresa/produto/período B]"
"Quais métricas melhoraram? Quais pioraram? O que ficou estável?"
"Qual é a principal diferença entre o que foi planejado e o que aconteceu?"

# Aprofundamento
"Explique [conceito específico] usando apenas os documentos carregados"
"Quais evidências nos documentos apoiam a hipótese de que [X causa Y]?"
"O que falta nos documentos para uma análise mais completa?"
```

---

## Boas Práticas — Preparação de Documentos para NotebookLM

| Faça | Evite |
|---|---|
| Estruturar com títulos e seções claras | Documentos sem hierarquia visual |
| Incluir glossário de termos técnicos | Abreviações sem explicação |
| Adicionar contexto antes dos dados | Tabelas densas sem texto explicativo |
| Escrever em linguagem direta e clara | Passiva excessiva e jargão burocrático |
| Incluir datas e períodos explícitos | Referências relativas ("mês passado") |
| Separar fato de hipótese explicitamente | Misturar dado com interpretação sem sinalizar |
| Limitar cada documento a 1 tema principal | Documentos que cobrem muitos assuntos |
| Incluir uma seção "Perguntas Frequentes" | Deixar o NotebookLM adivinhar o que importa |

---

## Limites do NotebookLM a considerar

- **Máximo:** 50 fontes por notebook, 500.000 palavras por fonte
- **Formatos aceitos:** Google Docs, Google Slides, PDF, TXT, Markdown, URLs, YouTube, áudio
- **O que não aceita:** Excel, Power BI, imagens sem texto, dados não estruturados
- **Solução:** Claude converte Excel → Markdown estruturado antes de carregar
- **Contexto fechado:** NotebookLM só responde sobre o que está nas fontes carregadas — não acessa internet por conta própria
- **Idioma:** funciona em português, mas podcast gerado é em inglês (limitação atual)

---

## Regras de Qualidade

- Documentos bem preparados pelo Claude geram respostas 3-5x mais precisas no NotebookLM
- Sempre incluir glossário quando o documento tiver termos técnicos ou siglas do negócio
- Usar o Claude para gerar guia de perguntas antes de entrar no NotebookLM — economiza tempo
- Nomear notebooks com clareza: "Performance Comercial 2025" não "Notebook 1"
- Para podcasts: usar linguagem oral no documento-fonte, não linguagem de relatório
- Manter um notebook por tema, não juntar tudo em um único — facilita navegação
- Atualizar fontes mensalmente nos notebooks de acompanhamento recorrente (KPIs, carteira)

## Observações

Esta skill é específica para o workflow Claude + NotebookLM.
Para automação de arquivos locais sem NotebookLM, use `cowork-workflows`.
Para criação de base de conhecimento com RAG via código, use `ia-generativa-agentes`.
NotebookLM é gratuito com conta Google; versão Plus tem mais recursos de personalização de podcast.

# PowerPoint — Estrutura Completa dos 13 Slides
## Planejamento Comercial

---

## Identidade Visual Recomendada

| Elemento        | Especificação                                     |
|-----------------|---------------------------------------------------|
| Fonte título    | Segoe UI Semibold, 28–36pt                        |
| Fonte corpo     | Segoe UI Regular, 12–14pt                         |
| Cor primária    | #0078D4 (azul Microsoft / Power BI)               |
| Cor secundária  | #107C10 (verde — acima da meta)                   |
| Cor alerta      | #D83B01 (vermelho — abaixo da meta / risco)       |
| Cor neutro      | #F4F4F4 (fundo de tabelas e blocos de destaque)   |
| Fundo slide     | Branco (#FFFFFF) com barra lateral ou superior azul |
| Proporção       | 16:9 (widescreen)                                 |

### Padrão de layout por tipo de slide

```
Slide de abertura de seção:
  [ Barra azul lateral larga | Título grande + ícone ]

Slide de conteúdo simples:
  [ Título conclusivo topo | Visual central | Nota de rodapé opcional ]

Slide de comparação / antes-depois:
  [ Coluna esquerda: problema | Coluna direita: solução ]

Slide de arquitetura / fluxo:
  [ Diagrama horizontal com setas + legenda abaixo ]

Slide de KPIs / métricas:
  [ Grid de 3–4 cards + gráfico de suporte ]
```

---

## Estrutura Narrativa — O Fio Condutor

```
PROBLEMA (Slides 1–4)
  Por que construímos isto?
  Qual era a dor real?
  O que os dados revelavam antes de qualquer análise?

SOLUÇÃO TÉCNICA (Slides 5–7)
  Como estruturamos a arquitetura?
  Como garantimos qualidade dos dados?

ENTREGA DE VALOR (Slides 8–11)
  O que o dashboard mostra?
  Como o forecast é medido?
  Como a segurança foi implementada?
  Quais automações foram criadas?

RESULTADO E PRÓXIMOS PASSOS (Slides 12–13)
  O que muda com este projeto?
  O que vem a seguir?
```

---

## Slide 1 — Capa

**Título:** Planejamento Comercial

**Subtítulo:** Estratégia → Execução → Monitoramento → Decisão em uma plataforma

**Mensagem central:**
> Este projeto transformou dados fragmentados em uma plataforma de inteligência
> comercial integrada — do Excel ao alerta automático em segundos.

**Layout:**
```
[ Fundo: gradiente azul escuro → azul médio ]
[ Centro: ícone de torre de controle ou grid de dados ]
[ Título em branco, 36pt ]
[ Subtítulo em branco, 14pt, 60% opacidade ]
[ Rodapé: nome, data, "Confidencial" ]
```

**Elementos visuais sugeridos:**
- Ícone de torre de controle ou dashboard estilizado
- Linha do tempo horizontal minimalista abaixo do subtítulo:
  `Excel → Python → SQL Server → Power BI → Power Automate`
- Logo ou identidade do projeto discreto no canto

**Fala de apoio:**
> "Este projeto nasceu de uma necessidade real: consolidar dados comerciais fragmentados
> em 6 arquivos Excel distintos em uma visão única, confiável e automatizada.
> O objetivo ? dar visibilidade total, em tempo ?til, para tomar decis?es antes que o problema se consolide.

---

## Slide 2 — O Problema

**Título conclusivo:** Dados fragmentados geram decisão lenta, forecast impreciso e retrabalho

**Mensagem central:**
> A situação anterior: cada área tinha seu Excel, ninguém concordava com o número,
> e a reunião de resultado virava uma discussão sobre qual planilha estava certa.

**Layout:** Dois blocos lado a lado

**Coluna esquerda — "Antes":**
```
❌ 6 arquivos Excel sem integração
❌ Forecast manual, sem métrica de acurácia
❌ Meta vs realizado calculado por cada um
❌ Gerentes sem visibilidade do time em tempo real
❌ Relatório mensal = 2 dias de trabalho manual
❌ Pedidos cancelados inflavam o faturamento
```

**Coluna direita — "Impacto":**
```
⏱ Decisões tomadas com dados de 15–30 dias atrás
📉 Forecast com erro > 30% em picos sazonais
🔁 Retrabalho recorrente todo fechamento de mês
👀 Riscos detectados depois que era tarde
💸 Budget não refletia a realidade do campo
```

**Visual sugerido:**
- Ícone de arquivos Excel empilhados de forma caótica (esquerda)
- Seta para a direita com "impacto"
- Ícones de relógio, gráfico descendente, loop para os impactos

**Fala de apoio:**
> "O diagnóstico inicial identificou 6 fontes de dados independentes, sem nenhuma
> integração automatizada. O resultado prático: cada reunião de fechamento começava
> com uma discussão sobre qual número estava certo — em vez de discutir o que fazer."

---

## Slide 3 — O Que Tínhamos

**Título conclusivo:** 20.004 transações, 4 anos de metas e 11 vendedores — tudo em Excel

**Mensagem central:**
> Os dados já existiam. O que faltava era uma arquitetura que os tornasse confiáveis,
> integrados e consumíveis.

**Layout:** Grid de 4 cards de dados + tabela de fontes abaixo

**Cards superiores (4 KPIs do volume de dados):**

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   20.004         │  │    4 anos        │  │   11 vendedores  │  │   6 arquivos     │
│   transações     │  │   Jan/2018       │  │   3 gerentes     │  │   Excel          │
│   de vendas      │  │   a Abr/2021     │  │   Guardiola,     │  │   sem integração │
│                  │  │                  │  │   Marta, Zagallo │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘
```

**Tabela de fontes abaixo dos cards:**

| Arquivo         | Conteúdo                          | Volume         |
|-----------------|-----------------------------------|----------------|
| Vendas.xlsx     | Transações: produto × vendedor    | ~20.004 linhas |
| Dimensões.xlsx  | 7 dimensões de negócio            | ~800 linhas    |
| Meta 2018.xlsx  | Metas mensais por vendedor        | 11 × 12 = 132  |
| Meta 2019.xlsx  | Metas mensais por vendedor        | 132 linhas     |
| Meta 2020.xlsx  | Metas mensais por vendedor        | 132 linhas     |
| Meta 2021.xlsx  | Metas mensais por vendedor        | 132 linhas     |

**Fala de apoio:**
> "Estes são os ingredientes brutos do projeto. 20 mil transações de vendas,
> 528 registros de meta e 8 dimensões de negócio — tudo disponível,
> mas em formato que impede qualquer análise cross-dimensional sem trabalho manual."

---

## Slide 4 — Hipóteses de Negócio

**Título conclusivo:** Os dados revelam 3 hipóteses que guiam o modelo analítico

**Mensagem central:**
> Antes de modelar, identificamos as perguntas de negócio que o dashboard precisa
> responder — não o contrário.

**Layout:** 3 blocos verticais com ícone, hipótese e implicação

**Hipótese 1 — Concentração (Pareto)**
```
📊 "20% dos vendedores provavelmente geram 80% da receita"
    → Priorizar retenção e capacitação dos top performers
    → Identificar potencial dos vendedores de cauda
    Pergunta no dashboard: Quem são os top vendedores?
```

**Hipótese 2 — Volatilidade do Forecast**
```
📈 "O forecast mensal apresenta erro significativo em picos sazonais"
    → O processo de planejamento precisa de ajuste por período
    → MAPE acima de 20% é sinal de revisão do modelo de metas
    Pergunta no dashboard: Qual a acurácia do nosso forecast?
```

**Hipótese 3 — Sazonalidade**
```
📅 "Há padrão de concentração de vendas em determinados meses do ano"
    → As metas precisam refletir sazonalidade, não só histórico flat
    → Fim de ano e Q4 são períodos críticos de acompanhamento
    Pergunta no dashboard: Como evoluiu o faturamento mês a mês?
```

**Visual sugerido:**
- 3 colunas com ícone no topo, texto da hipótese em negrito,
  e texto da implicação em cinza mais claro abaixo
- Linha de conexão indicando "validado no dashboard"

**Fala de apoio:**
> "Estas hipóteses não foram inventadas — emergiram da exploração inicial dos dados.
> Elas orientaram as escolhas do modelo: por que incluir Pareto,
> por que medir MAPE, por que a dimensão calendário tem atributos de sazonalidade."

---

## Slide 5 — A Arquitetura Proposta

**Título conclusivo:** 5 camadas integradas: do Excel bruto ao alerta automático

**Mensagem central:**
> A arquitetura segue o padrão de mercado (Medallion + Star Schema),
> com cada camada com responsabilidade clara e rastreável.

**Layout:** Diagrama horizontal de 5 etapas com seta de fluxo

```
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│           │    │           │    │           │    │           │    │           │
│  📊 Excel  │ →  │ 🐍 Python  │ →  │ 🗄 SQL     │ →  │ 📊 Power  │ →  │ ⚡ Power  │
│           │    │  ETL      │    │  Server   │    │  BI       │    │  Automate │
│ Fonte     │    │ Pipeline  │    │ DW        │    │ Dashboard │    │ Alertas   │
│ de dados  │    │           │    │           │    │ + RLS     │    │           │
└───────────┘    └───────────┘    └───────────┘    └───────────┘    └───────────┘

  6 arquivos      Extract +        raw →            Star schema      5 fluxos
  Excel           Transform +      staging →        7 páginas        automáticos
  ~20K linhas     Validate +       dw               DAX + RLS        e-mail + Teams
                  Load
```

**Detalhe por camada (abaixo do diagrama):**

| Camada | Tecnologia | Papel |
|--------|-----------|-------|
| Extração | openpyxl, pandas | Lê Excel, preserva dado bruto |
| Transformação | pandas, SQLAlchemy | Valida, tipifica, normaliza |
| Armazenamento | SQL Server | raw → staging → dw (star schema) |
| Análise | Power BI + DAX | Dashboard, RLS, inteligência temporal |
| Automação | Power Automate | Alertas, resumos, refresh automático |

**Visual sugerido:**
- Ícones grandes e coloridos para cada tecnologia
- Setas com rótulo breve (ex: "ETL", "Truncate+Load", "Import", "API")
- Destaque nas siglas: Bronze → Silver → Gold (menção sutil abaixo)

**Fala de apoio:**
> "Cada camada tem uma responsabilidade única e separada.
> O dado bruto (Bronze) nunca é modificado — sempre que precisamos reprocessar,
> voltamos à fonte original. O Gold — a camada dw — é o que o Power BI consome.
> Esta separação é o que garante rastreabilidade e confiança no número."

---

## Slide 6 — Modelagem de Dados

**Título conclusivo:** Star schema com 2 fatos e 8 dimensões — projetado para o Power BI

**Mensagem central:**
> O modelo dimensional garante performance, leitura intuitiva para DAX e
> suporte nativo às análises temporais do Power BI.

**Layout:** Diagrama de estrela centralizado

```
                    [dCalendario]
                         |
[dStatus]  [dPagamento]  |  [dUnidades]  [dProdutos]
    \           \         |       /          /
     ──────── [fVendas] ──┴──────────────────
                   |
              [dVendedor]── [fMetas]
                   |
              [dClientes]
                   |
              [dCidade]
```

**Caixa de destaque — métricas calculadas:**

```
Colunas PERSISTED no SQL Server (calculadas 1x no insert):
  Margem Bruta     = Faturamento Total - Custo Total
  Resultado Liquido = Faturamento - Custo - Despesas - Impostos - Comissões
```

**Rodapé do slide:**
```
2 fatos | 8 dimensões | ~21K linhas fVendas | 528 linhas fMetas | dCalendario: 2.192 datas (2017–2022)
```

**Fala de apoio:**
> "Optamos pelo star schema clássico de Kimball.
> A escolha de pré-calcular Margem Bruta e Resultado Líquido como colunas PERSISTED
> no SQL Server é deliberada: evita recalcular no DAX a cada interação do usuário —
> o dado já chega calculado para o Power BI."

---

## Slide 7 — Qualidade de Dados

**Título conclusivo:** 8 testes automáticos garantem que nenhum dado inválido chega ao dashboard

**Mensagem central:**
> A qualidade de dados não é verificada manualmente — é um contrato automático
> executado a cada carga do pipeline.

**Layout:** Grid 4+4 com status de cada teste

**8 testes (grid 2x4):**

```
┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│ ✅ Nulos em chaves primárias      │  │ ✅ Cobertura de metas (4 anos)   │
│    Id Produto, Id Vendedor,       │  │    Todos os meses de 2018–2021   │
│    Id Cliente não podem ser nulos │  │    devem ter registro de meta    │
└──────────────────────────────────┘  └──────────────────────────────────┘
┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│ ✅ Integridade referencial        │  │ ✅ Valores negativos             │
│    Nenhuma FK sem par na dimensão │  │    Faturamento nunca pode ser    │
│    (0 órfãos tolerados)           │  │    menor que zero                │
└──────────────────────────────────┘  └──────────────────────────────────┘
┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│ ✅ Duplicidade de transações     │  │ ✅ Data envio posterior à venda   │
│    Num Venda + Id Produto         │  │    Data Envio >= Data Venda      │
│    deve ser único                 │  │    (consistência temporal)       │
└──────────────────────────────────┘  └──────────────────────────────────┘
┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│ ✅ Contagem de linhas            │  │ ✅ Status válidos                 │
│    Volume mínimo esperado:        │  │    Apenas status mapeados no DW  │
│    >= 15.000 linhas               │  │    são aceitos na carga          │
└──────────────────────────────────┘  └──────────────────────────────────┘
```

**Destaques técnicos (lateral direita):**

```
🐍 Python — pytest: 37 testes unitários
📋 Logging: cada execução gera log rastreável
🔄 Dry Run: validação sem gravar no banco
❌ Falha crítica = pipeline para imediatamente
```

**Fala de apoio:**
> "Cada teste tem um nível: crítico ou warning. Se um teste crítico falha —
> como encontrar IDs órfãos ou valores negativos de faturamento — o pipeline para
> imediatamente e registra o erro. O dado nunca chega ao DW sem passar por esta
> régua de qualidade."

---

## Slide 8 — Dashboard Executivo

**Título conclusivo:** 7 páginas de análise — do resumo executivo ao diagnóstico profundo

**Mensagem central:**
> O dashboard não é uma coleção de gráficos. É uma narrativa estruturada em camadas:
> do macro para o detalhe, do alerta para a causa raiz.

**Layout:** Grid de thumbnails das 7 páginas + descrição

**7 páginas do relatório:**

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Pág 1           │  │ Pág 2           │  │ Pág 3           │  │ Pág 4           │
│ Executive       │  │ Meta vs         │  │ Análise de      │  │ Análise de      │
│ Summary         │  │ Realizado       │  │ Produtos        │  │ Margens         │
│                 │  │                 │  │                 │  │                 │
│ KPIs globais    │  │ YTD, MTD,       │  │ Top 10, Pareto  │  │ Waterfall:      │
│ + tendência     │  │ Atingimento %   │  │ por categoria   │  │ Fat→MB→RL       │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Pág 5           │  │ Pág 6           │  │ Pág 7           │
│ Análise         │  │ Acurácia do     │  │ Diagnóstico     │
│ Geográfica      │  │ Forecast        │  │ Profundo        │
│                 │  │                 │  │                 │
│ Mapa + ranking  │  │ MAPE mensal     │  │ Desvios,        │
│ por UF          │  │ + evolução      │  │ hipóteses e     │
│                 │  │ da acurácia     │  │ causa raiz      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Fala de apoio:**
> "O fluxo de navegação foi desenhado para o gestor: a Página 1 responde 'estamos bem?',
> a Página 2 responde 'quem está bem e quem não está?', e as páginas seguintes
> aprofundam o porquê. A Página 7 é o destino final para diagnóstico — onde o analista
> chega depois de identificar um desvio nas páginas anteriores."

---

## Slide 9 — Acurácia do Forecast (MAPE)

**Título conclusivo:** MAPE como KPI de processo: medimos o erro para melhorar o planejamento

**Mensagem central:**
> Não basta monitorar se bateu ou não a meta — precisamos saber o quão preciso
> foi o forecast que definiu essa meta. O MAPE torna isso mensurável.

**Layout:** 3 blocos verticais + gráfico de linha abaixo

**3 blocos conceituais:**

```
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│ O que é o MAPE?      │  │ Como calculamos?      │  │ Como interpretar?    │
│                      │  │                       │  │                      │
│ Mean Absolute        │  │ MAPE =                │  │ < 10% → Excelente   │
│ Percentage Error     │  │ MÉDIA(|Real-Forecast|  │  │ 10–20% → Boa        │
│                      │  │ / |Real|) × 100       │  │ 20–50% → Razoável   │
│ Erro percentual      │  │                       │  │ > 50% → Baixa       │
│ médio absoluto do    │  │ Real = Faturamento    │  │                      │
│ forecast vs o        │  │ Forecast = Meta       │  │ Meta: reduzir MAPE  │
│ realizado            │  │                       │  │ abaixo de 15%       │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

**Gráfico abaixo:** Linha de MAPE por mês (Jan/2018–Abr/2021)
- Eixo Y: % do MAPE
- Linha de referência: 20% (threshold "Razoável")
- Destaque de picos e vales para indicar meses com forecast mais/menos preciso

**Mensagem do gráfico:** "Sazonalidade de fim de ano eleva o MAPE — sinaliza necessidade
de ajuste no modelo de metas para Q4."

**Fala de apoio:**
> "Um erro de 25% no MAPE significa que, em média, nossas metas mensais erram 25%
> para mais ou para menos do faturamento real. Isso não é um problema do vendedor —
> é um problema do processo de planejamento. Medir o MAPE é o primeiro passo para
> melhorá-lo sistematicamente."

---

## Slide 10 — Segurança e Governança (RLS)

**Título conclusivo:** Cada gerente vê apenas o seu time — sem configuração manual

**Mensagem central:**
> A segurança não é uma camada de controle adicionada depois. É parte do modelo —
> qualquer tentativa de acessar dados de outro time retorna vazio automaticamente.

**Layout:** Diagrama de hierarquia + tabela de acesso

**Diagrama de hierarquia:**

```
           Diretoria / Admin
                 │ vê TUDO
     ┌───────────┼───────────┐
     │           │           │
  Guardiola    Marta      Zagallo
  (Gerente)   (Gerente)  (Gerente)
     │           │           │
  Ronaldo     Paola       Neymar
  Rodrigo     Marilia     + time
```

**Como funciona (caixa de destaque):**

```
1. Filtro DAX aplicado em dVendedor[Gerente]
2. Relacionamento ativo propaga para fVendas e fMetas
3. Gerente acessa o relatório → vê apenas seus vendedores
4. Nenhum dado de outro time aparece — nem em totais agregados
5. Power BI Service: e-mail atribuído à role correspondente
```

**Tabela de roles:**

| Role                 | Filtro DAX              | Acesso             |
|----------------------|-------------------------|--------------------|
| Gerente_Guardiola    | [Gerente] = "Guardiola" | Ronaldo, Rodrigo   |
| Gerente_Marta        | [Gerente] = "Marta"     | Paola, Marilia     |
| Gerente_Zagallo      | [Gerente] = "Zagallo"   | Time Zagallo       |
| Admin                | (sem filtro)            | Tudo               |

**Fala de apoio:**
> "A implementação de RLS tem um impacto prático imediato na adoção do dashboard:
> quando o gestor abre o relatório e vê exatamente os seus vendedores —
> sem dados de outros times, sem necessidade de filtrar — ele confia no número.
> Confiança é o principal driver de adoção de dashboards."

---

## Slide 11 — Automação de Alertas

**Título conclusivo:** 5 fluxos automáticos garantem visibilidade sem abrir o dashboard

**Mensagem central:**
> O dashboard responde perguntas quando você o acessa. O Power Automate responde
> perguntas antes que você precise fazer.

**Layout:** 5 cards horizontais com ícone, nome, gatilho e ação

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚡ Seg 06h     ⚠️ Seg 08h      📊 Sex 17h      📅 Dia 20      🏆 Real-time │
│  Refresh       Baixo           Resumo          Meta em        Celebração   │
│  Automático    Atingimento     Semanal         Risco          de Meta      │
│                                                                             │
│  ETL Python    Vendedores      KPIs da         Projeção       Meta         │
│  + Power BI    < 70%           semana +        < 90% →        superada →   │
│  Dataset       → e-mail        MTD + Top 3     alerta         Teams        │
│  refresh       ao gerente      → e-mail        diretoria      + e-mail     │
│                                gerentes                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Caixa de valor (lateral ou abaixo):**

```
💡 Sem estes fluxos:
   → Gerente descobre baixo atingimento na reunião semanal (tarde demais)
   → Risco de meta é percebido no dia 28 (sem tempo de ação)
   → Dataset desatualizado gera alerta errado

✅ Com estes fluxos:
   → Alerta chega na segunda de manhã, ainda há tempo de agir
   → Risco detectado no dia 20, com 11 dias de margem
   → Dataset atualizado toda segunda antes das 08h
```

**Fala de apoio:**
> "O Fluxo 5 é o backbone de tudo: ele garante que os dados do dashboard
> e os dados dos alertas são sempre os mesmos, sempre atualizados.
> Sem ele, os outros 4 fluxos poderiam disparar alertas baseados em dados
> da semana anterior."

---

## Slide 12 — Resultados Esperados

**Título conclusivo:** Decisão mais rápida, previsibilidade maior e zero retrabalho no fechamento

**Mensagem central:**
> Os benefícios não são abstratos. Cada entrega deste projeto ataca um problema
> concreto com um resultado mensurável.

**Layout:** Tabela de antes × depois com impacto

| Antes                                  | Depois                                          | Impacto              |
|----------------------------------------|-------------------------------------------------|----------------------|
| Fechamento mensal: 2 dias de trabalho manual | Fechamento: dashboard atualizado automático | ~2 dias economizados/mês |
| Risco detectado no dia 28             | Risco detectado no dia 20 via alerta          | 8–11 dias de margem  |
| Forecast sem métrica de acurácia      | MAPE mensal monitorado por vendedor           | Processo de planejamento mensurável |
| Gerentes sem visão do time em tempo real | RLS + alertas automáticos                   | Visibilidade diária  |
| Dados fragmentados em 6 Excels        | DW unificado com 20K transações              | Fonte única de verdade |
| KPI calculado diferente por cada área | Medidas DAX centralizadas e versionadas       | Governança de métricas |

**Destaque visual:** barra de progresso ou seta ascendente ao lado da tabela
ilustrando a curva de maturidade analítica: "Dados → Informação → Insight → Decisão"

**Fala de apoio:**
> "Cada linha desta tabela corresponde a uma dor identificada no início do projeto.
> O benchmark de '2 dias economizados por fechamento' pode parecer simples —
> mas multiplicado por 12 meses e por todos os analistas envolvidos,
> representa um ganho real e recorrente."

---

## Slide 13 — Próximos Passos

**Título conclusivo:** 3 fases de evolução: da automação à IA aplicada ao planejamento

**Mensagem central:**
> A fundação está construída. As próximas evoluções agregam previsibilidade preditiva,
> simulação de cenários e narrativa automática com IA.

**Layout:** 3 colunas por fase

**Fase 1 — Fundação (concluída):**
```
✅ Pipeline ETL Python
✅ SQL Server DW (star schema)
✅ Dashboard Power BI + RLS
✅ 5 fluxos Power Automate
```

**Fase 2 — Em desenvolvimento:**
```
🔄 MAPE como KPI recorrente de planning
🔄 Página de Diagnóstico (causa raiz)
🔄 Análise de comissão variável
```

**Fase 3 — Roadmap futuro:**
```
🚀 Forecast preditivo (Prophet / XGBoost)
🚀 Simulação de metas ("e se a meta fosse X%?")
🚀 Forecast por segmento e por unidade
🚀 Integração com CRM (pipeline de vendas)
🚀 LLM para narrativa automática de diagnóstico
   ("Por que o faturamento caiu em março?")
```

**Caixa de destaque — LLM Narrativo:**

```
💬 Próxima fronteira:
   LLM conectado ao DW → lê os dados → gera automaticamente
   o diagnóstico em linguagem natural para o relatório executivo.
   "O faturamento caiu 12% em março devido à redução de 30% nas
    vendas do time Zagallo, concentradas na categoria Eletrônicos."
```

**Fala de apoio:**
> "A Fase 3 não é ficção científica — é o próximo passo natural desta arquitetura.
> O DW já está estruturado para alimentar modelos de ML.
> Prophet ou XGBoost para forecast de série temporal é a próxima evolução concreta.
> E o LLM narrativo fecha o ciclo: do dado ao texto em segundos."

---

## Dicas Finais de Apresentação

### Sequência de leitura recomendada

```
Slides 1–4   (8 min)  → Contexto e problema — gera empatia e atenção
Slide 5      (3 min)  → Arquitetura — "é uma solução robusta e bem estruturada"
Slides 6–7   (4 min)  → Modelagem e qualidade — credibilidade técnica
Slides 8–11  (10 min) → As entregas — onde o público vê o valor
Slides 12–13 (5 min)  → Resultado e próximos passos — encerramento com impacto

Total: ~30 minutos com Q&A
```

### Adaptação por público

| Público          | Foco                                          | Slides a enfatizar |
|------------------|-----------------------------------------------|--------------------|
| Diretoria        | Resultados, tempo economizado, governança     | 1, 2, 5, 12, 13    |
| Gestores / Squad | Dashboard, alertas, RLS, como usar            | 8, 9, 10, 11       |
| Técnico / TI     | Arquitetura, qualidade, ETL, star schema      | 5, 6, 7            |
| Recrutador / RH  | Stack, metodologia, amplitude do projeto      | 1, 5, 6, 8, 13     |

### Formatação de títulos — regra de ouro

```
❌ "Resultados"         → Não diz nada
❌ "Análise de Dados"   → Genérico
✅ "20.004 transações consolidadas em um único modelo analítico"
✅ "8 testes automáticos garantem que nenhum dado inválido chega ao dashboard"
```

Cada título deve ser uma **afirmação conclusiva** — não um tópico.

---

*Arquivo gerado como parte do Planejamento Comercial.*
*Próxima entrega: apresentação final em PowerPoint (Gamma, Canva ou PPTX direto).*

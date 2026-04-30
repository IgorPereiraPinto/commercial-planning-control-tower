# Script de Narração — 13 Slides
## Commercial Planning Control Tower

> Uso: colar no campo "Notas do Orador" de cada slide no PowerPoint/Google Slides.
> Tempo médio por slide: 2–3 min. Total: ~30 min com Q&A.

---

### Slide 1 — Capa

"Este projeto nasceu de uma necessidade real: consolidar dados comerciais
fragmentados em 6 arquivos Excel distintos em uma visão única, confiável
e automatizada. O nome 'Control Tower' não é metáfora — é o objetivo:
visibilidade total, em tempo real, para tomar decisões antes que o problema
se consolide."

---

### Slide 2 — O Problema

"Antes deste projeto, cada área tinha seu Excel. Ninguém concordava com o número.
A reunião de resultado virava uma discussão sobre qual planilha estava certa —
em vez de uma discussão sobre o que fazer. O custo disso não é só o tempo perdido
em reunião: é a decisão tomada com atraso de 15 a 30 dias."

---

### Slide 3 — O Que Tínhamos

"Estes são os ingredientes brutos do projeto. 20 mil transações de vendas,
528 registros de meta e 8 dimensões de negócio — tudo disponível, mas em
formato que impede qualquer análise cross-dimensional sem trabalho manual.
O desafio não era a falta de dados — era a falta de uma arquitetura que os
tornasse confiáveis e consumíveis."

---

### Slide 4 — Hipóteses de Negócio

"Antes de modelar, identificamos as perguntas que o dashboard precisa responder.
Três hipóteses guiaram o projeto: concentração de receita em poucos vendedores,
forecast com erro elevado em picos sazonais, e padrão de sazonalidade não
refletido nas metas. Estas hipóteses não foram inventadas — emergiram da
exploração inicial dos dados."

---

### Slide 5 — A Arquitetura Proposta

"Cada camada tem uma responsabilidade única e separada. O dado bruto — chamamos
de Bronze — nunca é modificado. Sempre que precisamos reprocessar, voltamos
à fonte original. O Gold — a camada dw — é o que o Power BI consome.
Esta separação é o que garante rastreabilidade e confiança no número."

---

### Slide 6 — Modelagem de Dados

"Optamos pelo star schema clássico de Kimball — dois fatos e oito dimensões.
A decisão de pré-calcular Margem Bruta e Resultado Líquido como colunas PERSISTED
no SQL Server é deliberada: evita recalcular no DAX a cada interação do usuário.
O dado já chega calculado para o Power BI — performance e consistência juntos."

---

### Slide 7 — Qualidade de Dados

"Cada teste tem um nível: crítico ou warning. Se um teste crítico falha —
como encontrar IDs órfãos ou valores negativos de faturamento — o pipeline
para imediatamente e registra o erro. O dado nunca chega ao DW sem passar
por esta régua de qualidade. Isso não é uma prática sofisticada — é o mínimo
aceitável em qualquer pipeline de produção."

---

### Slide 8 — Dashboard Executivo

"O fluxo de navegação foi desenhado para o gestor: a Página 1 responde
'estamos bem?', a Página 2 responde 'quem está bem e quem não está?',
e as páginas seguintes aprofundam o porquê. A Página 7 é o destino final
para diagnóstico — onde o analista chega depois de identificar um desvio
nas páginas anteriores. Isso é storytelling analítico aplicado à navegação."

---

### Slide 9 — Acurácia do Forecast (MAPE)

"Um erro de 25% no MAPE significa que, em média, nossas metas mensais erram
25% para mais ou para menos do faturamento real. Isso não é um problema do
vendedor — é um problema do processo de planejamento. Medir o MAPE é o
primeiro passo para melhorá-lo sistematicamente. Sem métrica, não há melhoria."

---

### Slide 10 — Segurança e Governança (RLS)

"A implementação de RLS tem um impacto prático imediato na adoção do dashboard:
quando o gestor abre o relatório e vê exatamente os seus vendedores — sem dados
de outros times, sem precisar filtrar — ele confia no número. Confiança é o
principal driver de adoção de dashboards. Sem confiança, o dashboard fica bonito
e abandonado."

---

### Slide 11 — Automação de Alertas

"O dashboard responde perguntas quando você o acessa. O Power Automate responde
perguntas antes que você precise fazer. O Fluxo 5 é o backbone de tudo: garante
que os dados do dashboard e dos alertas são sempre os mesmos, sempre atualizados.
Sem ele, os outros 4 fluxos poderiam disparar alertas baseados em dados antigos."

---

### Slide 12 — Resultados Esperados

"Cada linha desta tabela corresponde a uma dor identificada no início do projeto.
O benchmark de 2 dias economizados por fechamento pode parecer simples — mas
multiplicado por 12 meses e por todos os analistas envolvidos, representa um
ganho real e recorrente. E o impacto mais difícil de quantificar: decisões
tomadas com dados corretos, no momento certo."

---

### Slide 13 — Próximos Passos

"A Fase 3 não é ficção científica — é o próximo passo natural desta arquitetura.
O DW já está estruturado para alimentar modelos de ML. Prophet ou XGBoost para
forecast de série temporal é a evolução concreta mais próxima. E o LLM narrativo
fecha o ciclo: do dado ao texto em segundos — 'o faturamento caiu 12% em março
por redução concentrada nas vendas do time Zagallo na categoria Eletrônicos.'
Esse é o horizonte."

---

*Script de narração v1.0 — Commercial Planning Control Tower.*

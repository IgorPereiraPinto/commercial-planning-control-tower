# 02 — Entendimento do Case

## Decisão que o projeto apoia

> "Estamos no caminho certo para bater a meta? Onde estão os desvios e qual a ação prioritária?"

---

## Os três pilares

| Pilar | Pergunta central | Fonte |
|---|---|---|
| Planejar (Budget) | Qual é a meta por vendedor e período? | fMetas 2018–2021 |
| Prever (Forecast) | O que vamos realizar até o fim do mês/ano? | fVendas + ritmo |
| Monitorar (Realizado) | Como estamos em relação à meta agora? | fVendas transacional |

---

## Perguntas de negócio

1. Quais vendedores estão abaixo da meta e por quanto?
2. Qual o forecast para o fechamento do mês?
3. Quais produtos e unidades concentram o resultado?
4. Existe sazonalidade recorrente no Q1 vs Q4?
5. Quantos vendedores respondem por 80% da receita? (Pareto)
6. Qual a margem bruta e líquida por categoria de produto?

---

## Hipóteses de negócio

| Vendedor | Padrão observado | Hipótese |
|---|---|---|
| Ronaldo | Pico em determinados meses | Dependência de grandes contratos — risco de concentração |
| Neymar | Alta volatilidade | Carteira instável ou sazonalidade forte |
| Luan | Crescimento progressivo | Candidato para expansão de carteira |
| Messi | Queda em dezembro | Sazonalidade negativa no Q4 |
| Time geral | Concentração de receita | 3 vendedores podem responder por 80% |

---

## O que analisar antes do ETL

- granularidade de cada tabela
- campos-chave para joins
- colunas de valor, data, status e identificação
- layout das metas: formato wide (colunas = meses) → unpivot necessário

---

## Próximo passo

[03_analise_da_base_excel.md](03_analise_da_base_excel.md)

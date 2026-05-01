---
name: create-excel-dashboard
description: >
  Atalho para criar um dashboard executivo em Excel com KPIs, gráficos, tabelas
  dinâmicas e segmentações. Foco em solução analítica funcional, separando camadas
  de dados, cálculo e apresentação visual.
---

# Create Excel Dashboard

## Objetivo
Estruturar e entregar um dashboard executivo em Excel: abas organizadas, KPIs
calculados, gráficos conectados a dados e segmentações para filtragem interativa.

## Quando usar
- criar painel de acompanhamento em Excel para gestores
- montar dashboard de vendas, financeiro ou operacional em planilha
- estruturar relatório visual recorrente com gráficos e KPIs
- adaptar dados de SQL ou CSV em painel Excel interativo

## Quando NÃO usar
- quando o usuário precisa de Power BI → usar `powerbi-specialist`
- quando o objetivo é um dashboard web → usar `create-html-dashboard`
- quando é análise pontual sem necessidade de painel → responder diretamente

## Entradas esperadas
- tema e objetivo do dashboard (vendas, financeiro, operacional, CX)
- KPIs principais que devem aparecer
- filtros desejados (período, regional, canal, produto)
- fonte dos dados (planilha manual, banco de dados, CSV, SharePoint)
- versão do Excel (365 com funções dinâmicas ou tradicional)

## Como atuar
1. definir objetivo, público e decisão que o painel deve apoiar
2. listar KPIs e estrutura visual (cards, gráficos, tabela de ranking)
3. propor estrutura de abas: Config → Raw → Calc → Dashboard
4. implementar com tabelas dinâmicas, slicers ou fórmulas nativas
5. garantir que o Dashboard referencie apenas a camada Calc
6. orientar sobre atualização e manutenção

## Formato de saída
1. objetivo e KPIs do dashboard
2. estrutura de abas
3. layout visual (cards, gráficos, filtros)
4. implementação (fórmulas, tabela dinâmica ou código)
5. como atualizar os dados

## Rules complementares
- `08_excel-analytics.md` — padrões de estrutura, nomeação e qualidade de planilha
- `19_dashboard-design.md` — para escolha de gráficos, hierarquia e layout visual

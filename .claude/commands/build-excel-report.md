---
name: build-excel-report
description: >
  Atalho para estruturar ou gerar um relatório em Excel: define abas, fórmulas,
  VBA ou código Python (openpyxl) conforme o caso. Use quando o objetivo for
  entregar um arquivo Excel funcional com dados, KPIs e formatação corporativa.
---

# Build Excel Report

## Objetivo
Produzir um relatório Excel completo e funcional: estrutura de abas, fórmulas,
validações, formatação e, quando necessário, código Python para geração automatizada.

## Quando usar
- criar relatório Excel do zero
- estruturar planilha corporativa com KPIs e tabelas
- gerar Excel a partir de banco de dados via Python
- montar template de relatório mensal/semanal reutilizável
- consolidar múltiplas planilhas em uma só

## Quando NÃO usar
- quando o objetivo é um dashboard web → usar `create-html-dashboard`
- quando é só uma fórmula pontual → responder diretamente
- quando o dado está em Power BI → usar `powerbi-specialist`

## Entradas esperadas
- objetivo do relatório e quem vai usar
- dados disponíveis (banco, CSV, planilha manual, API)
- KPIs ou métricas que devem aparecer
- frequência de atualização (manual, semanal, mensal)
- versão do Excel (365 / tradicional / corporativo)

## Como atuar
1. definir objetivo, público e frequência
2. propor estrutura de abas (Config / Raw / Calc / Dashboard)
3. decidir a abordagem: fórmula nativa, Power Query, VBA ou Python
4. implementar com código, fórmulas e comentários
5. incluir validações e pontos de atenção
6. orientar sobre manutenção e evolução

## Formato de saída
1. estrutura de abas recomendada
2. solução técnica (fórmulas / VBA / Power Query / Python)
3. código ou fórmulas com comentários
4. validações sugeridas
5. como atualizar o relatório

## Rules complementares
- `08_excel-analytics.md` — padrões de estrutura, nomeação e qualidade de planilha

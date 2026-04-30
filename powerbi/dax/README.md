# Power BI DAX — planejamento-comercial

## Arquivos nesta pasta

| Arquivo | Conteúdo |
|---|---|
| `medidas_completas.dax` | Todas as medidas DAX do relatório (resultado, tendência, diagnóstico) |
| `medidas_forecast_budget.dax` | Medidas específicas de forecast e budget (MTD, MAPE, Gap) |

---

## Como usar

1. Abra o Power BI Desktop
2. Conecte ao banco `planejamento_comercial` no SQL Server
3. Copie as medidas do arquivo `.dax` correspondente
4. Cole em uma tabela de medidas vazia no modelo
5. Valide os resultados em cartões ou tabelas de apoio antes de publicar

---

## Medidas principais

| Medida | Fórmula resumida | Uso |
|---|---|---|
| Faturamento | SUM(fVendas[Faturamento Total]) | Base de todos os KPIs |
| Meta | SUM(fMetas[Valor Meta]) | Alvo do período |
| Atingimento % | DIVIDE(Faturamento, Meta, 0) | Card principal |
| Desvio | Faturamento - Meta | Análise de gap |
| Margem Bruta % | DIVIDE(Fat - Custo, Fat, 0) | Eficiência por produto |
| Faturamento YTD | CALCULATE(..., DATESYTD) | Acumulado do ano |
| YoY % | DIVIDE(Fat - Fat SPLY, Fat SPLY, 0) | Comparativo anual |
| Forecast MTD | Ritmo × dias do mês | Projeção de fechamento |
| MAPE | AVG(ABS(Real - Forecast) / Real) | Qualidade do forecast |

---

## Boas práticas aplicadas

- usar `DIVIDE()` em vez de `/` para evitar erros de divisão por zero
- usar `SWITCH(TRUE())` para classificações faixa de atingimento
- medidas base → medidas derivadas → medidas de inteligência de tempo
- tabela `dCalendario` como única fonte de verdade temporal

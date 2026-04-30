# 10 — KPIs e Views Analíticas

## KPIs de resultado comercial

| KPI | Fórmula | Leitura |
|---|---|---|
| Faturamento Realizado | SUM(Faturamento Total) | Receita bruta do período |
| Meta do Período | SUM(Valor Meta) | Alvo do período |
| % Atingimento | Faturamento / Meta | > 100% = meta batida |
| Desvio Absoluto | Faturamento - Meta | Positivo = superação |
| Margem Bruta % | (Fat - Custo) / Fat | Benchmark por categoria |
| Ticket Médio | Faturamento / Qtde Vendas | Eficiência por transação |

## KPIs de forecast

| KPI | Descrição |
|---|---|
| Forecast MTD | Ritmo atual × dias restantes do mês |
| Gap para Meta | Meta - Forecast Projetado |
| MAPE | Erro percentual médio do forecast |

## Views analíticas

O script `sql/sqlserver/07_analytical_queries.sql` contém queries prontas para:
- ranking de vendedores por % atingimento
- análise de Pareto (80/20) por receita
- evolução mensal meta vs realizado
- waterfall de margem por categoria

---

## Próximo passo

[11_dashboard_e_storytelling.md](11_dashboard_e_storytelling.md)

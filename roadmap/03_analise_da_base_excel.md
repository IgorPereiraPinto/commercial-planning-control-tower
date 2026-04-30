# 03 — Análise da Base Excel

## Objetivo
Entender o dado antes de escrever uma linha de código.

---

## Fontes e estrutura

### Dimensoes.xlsx — 7 abas
| Tabela | Linhas | Granularidade |
|---|---|---|
| dProdutos | 499 | Um produto |
| dVendedor | 20 | Um vendedor |
| dClientes | 9.760 | Um cliente |
| dCidade | 9.888 | Uma cidade |
| dUnidades | 11 | Uma unidade |
| dStatus | 3 | Um status de pedido |
| dPagamento | 5 | Uma forma de pagamento |

### Vendas.xlsx — fVendas
- 20.004 transações
- Período: Janeiro 2018 – Abril 2021
- Granularidade: um item de venda por linha
- Métricas: Qtde, Valor Unit, Custo Unit, Despesa Unit, Impostos Unit, Comissão Unit

### Meta_XXXX.xlsx — 4 arquivos
- Um arquivo por ano (2018–2021)
- Aba "Meta"
- Formato **wide**: linhas = vendedores, colunas = meses (Jan, Fev... Dez)
- Requer **UNPIVOT** no ETL para transformar em linhas

---

## Pontos de atenção

- Metas no formato wide exigem unpivot antes do JOIN com fVendas
- Vendedor "Lilia" presente nas metas mas não em todos os anos de vendas — verificar
- dCidade tem mais registros que dClientes — verificar FK antes do JOIN

---

## Próximo passo

[04_arquitetura_do_pipeline.md](04_arquitetura_do_pipeline.md)

# 01 — Visão Geral do Projeto

## O que este projeto resolve

Dados de meta e realizado espalhados em arquivos Excel individuais por ano, sem padronização, sem histórico consolidado e sem visibilidade gerencial em tempo real.

O projeto constroi um **Planejamento Comercial** que conecta:

> `Budget → Forecast → Realizado`

em uma plataforma analítica única com rastreabilidade ponta a ponta.

---

## Fluxo do Projeto

```text
[1] Setup local e versionamento
    pasta → Git → VS Code → ambiente virtual

[2] Entendimento do problema
    bases Excel → perguntas de negócio → hipóteses → KPIs

[3] Python ETL (7 etapas)
    extração → validação raw → transformação → validação staging
    → carga raw → carga staging → carga DW

[4] SQL analitico
    raw → staging → dw (star schema) → views analíticas

[5] Power BI
    dataset → medidas DAX → RLS por gerente → dashboard executivo

[6] Power Automate
    alertas → resumo semanal → atualização automática

[7] Comunicação
    dashboard HTML → apresentação executiva

[8] Reutilização
    ajuste de schema → regras → SQL → dashboard → documentação
```

---

## Fontes de Dados

| Arquivo | Conteúdo | Linhas |
|---|---|---|
| `data/raw/Dimensoes.xlsx` | 7 dimensões (produtos, vendedores, clientes...) | ~20.000 |
| `data/raw/Vendas.xlsx` | Transações de vendas 2018-2021 | 20.004 |
| `data/raw/Meta_2018-2021.xlsx` | Metas mensais por vendedor | 4 arquivos |

---

## Próximo passo

[02_entendimento_do_case.md](02_entendimento_do_case.md)

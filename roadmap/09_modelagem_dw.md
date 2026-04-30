# 09 — Modelagem: Camada DW (Star Schema)

## Estrutura do star schema

```text
                    dCalendario
                         |
dStatus    dPagamento    |    dUnidades
    \           \        |       /
     ------- fVendas ----------
                         |
              dVendedor  |  dProdutos
                         |
                    dClientes --- dCidade

       fMetas ---- dVendedor
             \---- dCalendario
```

## Tabelas do schema dw

| Tabela | Tipo | Descrição |
|---|---|---|
| dw.fVendas | Fato | Transações de vendas |
| dw.fMetas | Fato | Metas consolidadas de todos os anos |
| dw.dCalendario | Dimensão | Calendário completo |
| dw.dProdutos | Dimensão | Catálogo de produtos |
| dw.dVendedor | Dimensão | Cadastro de vendedores e gerentes |
| dw.dClientes | Dimensão | Base de clientes |
| dw.dCidade | Dimensão | Cidades e estados |
| dw.dUnidades | Dimensão | Filiais e matriz |
| dw.dStatus | Dimensão | Status dos pedidos |
| dw.dPagamento | Dimensão | Formas de pagamento |

## Scripts SQL

```text
sql/sqlserver/03_dw_dimensions.sql
sql/sqlserver/04_dw_facts.sql
sql/sqlserver/05_calendario.sql
sql/sqlserver/06_indexes.sql
```

---

## Próximo passo

[10_kpis_e_views_analiticas.md](10_kpis_e_views_analiticas.md)

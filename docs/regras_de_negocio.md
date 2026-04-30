# Regras de Negocio - planejamento-comercial

## KPIs centrais

### Faturamento total

```text
Faturamento Total = Qtde * Valor Unit
```

### Margem bruta

```text
Margem Bruta R$ = Faturamento Total - Custo Total
Margem Bruta %  = Margem Bruta R$ / Faturamento Total
```

### Margem liquida

```text
Margem Liquida % =
  (Faturamento Total - Custo Total - Despesas - Impostos - Comissoes)
  / Faturamento Total
```

### Atingimento de meta

```text
% Atingimento = Faturamento / Valor Meta
```

### Forecast mensal

```text
Run Rate Diario = Faturamento MTD / Dias Decorridos
Forecast do Mes = Run Rate Diario * Total de Dias do Mes
```

### MAPE

```text
MAPE = media( abs(Real - Forecast) / Real )
```

## Regras de classificacao

| Faixa | Leitura |
|---|---|
| < 80% | Risco critico |
| 80% a 89,9% | Em acompanhamento |
| 90% a 99,9% | Proximo da meta |
| >= 100% | Meta batida |

## Regras de forecast

| Faixa de MAPE | Confiabilidade |
|---|---|
| < 10% | Alta |
| 10% a 20% | Media |
| > 20% | Baixa |

## Regras de comissionamento

O projeto passa a considerar uma regra de comissao para aproximar o caso de um contexto real de planejamento comercial.

### Fator por atingimento

| Atingimento | Fator de payout |
|---|---|
| < 80% | 0% |
| 80% a 89,9% | 50% |
| 90% a 99,9% | 80% |
| 100% a 109,9% | 100% |
| 110% a 119,9% | 130% |
| >= 120% | 160% |

### Multiplicador por prioridade de produto

| Prioridade | Multiplicador | Leitura |
|---|---|---|
| P1 | 1,35x | Produto mais prioritario para venda |
| P2 | 1,15x | Produto prioritario alto |
| P3 | 1,00x | Produto neutro |
| P4 | 0,85x | Produto de menor prioridade relativa |

### Formula proposta

```text
Comissao Elegivel = Receita Liquida * Taxa Base * Multiplicador Prioridade
Comissao Paga     = Comissao Elegivel * Fator Atingimento
```

### Regras de governanca

- payout abaixo de 80% deve ser bloqueado
- a prioridade do produto deve vir de uma tabela parametrica
- excecoes comerciais precisam de versionamento por periodo
- a despesa de comissao deve ser conciliavel com o DW

## Regras de metas

| Regra | Descricao |
|---|---|
| Cobertura | Todos os vendedores com meta mensal valida no periodo |
| Periodo | Metas disponiveis para 2018, 2019, 2020 e 2021 |
| Formato | Fonte chega em wide e e convertida para long |
| Leitura gerencial | Metas podem ser analisadas por vendedor, gerente e unidade |

## Regras de integridade

| Regra | Descricao |
|---|---|
| Nulos em chaves | Id Produto, Id Vendedor, Id Cliente e Id Data nao podem ser nulos |
| Integridade referencial | Toda chave da fato deve existir nas dimensoes |
| Unicidade de transacao | Num Venda + Id Produto deve ser unico |
| Data valida | Data Envio nao pode ser menor que Data |
| Faturamento positivo | Faturamento Total >= 0 |
| Status valido | Status deve respeitar o dominio previsto |

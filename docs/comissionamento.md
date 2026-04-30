# Comissionamento - modelo proposto

Este documento consolida a proposta de comissionamento usada no projeto `planejamento-comercial`.

O objetivo aqui nao e apenas mostrar uma formula. A ideia e deixar claro, para um publico leigo ou executivo, como a empresa pode transformar meta, mix de produtos e resultado comercial em uma politica de incentivo coerente e auditavel.

## O que este modelo resolve

- evita pagar comissao cheia para performance abaixo do piso minimo
- direciona a venda de produtos estrategicos
- permite prever a despesa comercial
- ajuda gerentes e vendedores a entenderem o que impulsiona o payout
- prepara o processo para automacao futura

## Logica geral

O calculo tem 3 etapas:

1. calcular a comissao elegivel
2. identificar a faixa de atingimento da meta
3. aplicar o fator final de payout

## Etapa 1 - Comissao elegivel

```text
Comissao Elegivel = Receita Liquida * Taxa Base * Multiplicador de Prioridade
```

### Componentes

- `Receita Liquida`
  Base economica que a empresa quer considerar para remuneracao.
- `Taxa Base`
  Percentual padrao de comissao definido pela politica comercial.
- `Multiplicador de Prioridade`
  Ajusta a comissao conforme a prioridade do produto.

## Etapa 2 - Faixa de atingimento

| Atingimento da meta | Percentual do payout alvo |
|---|---|
| < 80% | 0% |
| 80% a 89,9% | 50% |
| 90% a 99,9% | 80% |
| 100% a 109,9% | 100% |
| 110% a 119,9% | 130% |
| >= 120% | 160% |

## Etapa 3 - Comissao paga

```text
Comissao Paga = Comissao Elegivel * Fator de Atingimento
```

## Prioridade de produto

| Prioridade | Multiplicador | Leitura de negocio |
|---|---|---|
| P1 | 1,35x | Produto de maior foco comercial |
| P2 | 1,15x | Produto importante para crescimento |
| P3 | 1,00x | Produto neutro |
| P4 | 0,85x | Produto com menor prioridade relativa |

### Interpretacao simples

- quanto menor o numero da prioridade, maior o incentivo
- produtos P1 e P2 recebem reforco porque ajudam a empresa a vender o mix desejado
- produtos P4 continuam vendaveis, mas com menor peso de incentivo

## Exemplo pratico

Suponha a seguinte configuracao:

- taxa base = `2,4%`
- receita liquida do vendedor = `R$ 1,20M`
- prioridade media do mix vendido = `P2`
- logo, multiplicador = `1,15x`

### Passo 1

```text
Comissao Elegivel = 1,20 * 2,4% * 1,15
Comissao Elegivel = R$ 0,03312M
```

Ou seja:

`R$ 33,1 mil` de comissao elegivel

### Passo 2

Se esse vendedor atingiu `92%` da meta, ele cai na faixa:

`90% a 99,9% -> 80% do payout alvo`

### Passo 3

```text
Comissao Paga = 33,1 mil * 80%
Comissao Paga = 26,5 mil
```

## Tabela pratica

| Vendedor | Meta | Realizado | Atingimento | Prioridade media | Comissao elegivel | Fator | Comissao paga |
|---|---|---|---|---|---|---|---|
| Cristiano | R$ 7,2M | R$ 8,0M | 111,1% | P1 | R$ 0,244M | 130% | R$ 0,317M |
| Ronaldo | R$ 7,0M | R$ 7,1M | 101,4% | P2 | R$ 0,196M | 100% | R$ 0,196M |
| Marilia | R$ 5,7M | R$ 5,0M | 87,7% | P2 | R$ 0,130M | 50% | R$ 0,065M |
| Neymar | R$ 2,3M | R$ 1,8M | 78,3% | P3 | R$ 0,043M | 0% | R$ 0,000M |

## O que essa tabela ensina

- vender bem nao depende so de volume; depende de bater meta
- vender produto estrategico melhora o potencial de comissao
- um vendedor pode ter receita relevante e ainda assim nao receber payout cheio
- o modelo evita incoerencia entre custo comercial e performance

## Como isso aparece no dashboard

No dashboard principal, a camada de comissao foi desenhada para responder:

- quem esta com payout cheio
- quem ficou sem payout por estar abaixo de 80%
- quanto do resultado veio de produtos P1 e P2
- qual a despesa comercial estimada do periodo
- como meta, mix e comissao se conectam

## Recomendacoes para implementacao real

1. versionar regras por vigencia
2. guardar prioridade de produto em tabela propria
3. registrar excecoes aprovadas
4. expor uma fato mensal de comissao no DW
5. conciliar valor calculado com valor pago
6. disparar alertas quando vendedor entrar em faixa sem payout

## Estruturas sugeridas

### `param_regra_comissao`

- faixa_inicio
- faixa_fim
- fator_payout
- vigencia_inicio
- vigencia_fim

### `param_prioridade_produto`

- id_produto
- prioridade_venda
- multiplicador_prioridade
- vigencia_inicio
- vigencia_fim

### `dw.fComissaoMensal`

- id_vendedor
- id_produto
- id_data
- receita_elegivel
- fator_atingimento
- multiplicador_prioridade
- comissao_calculada
- comissao_paga

## KPIs recomendados

- comissao elegivel
- comissao paga
- payout medio por vendedor
- vendedores sem payout por piso de 80%
- vendedores com acelerador ativo
- share de receita P1 e P2
- comissao como % da margem bruta

# Dicionario de Dados - planejamento-comercial

## fVendas

| Campo | Tipo | Descricao |
|---|---|---|
| Num Venda | INT | Identificador da venda |
| Id Produto | INT | FK para dProdutos |
| Id Vendedor | INT | FK para dVendedor |
| Id Cliente | INT | FK para dClientes |
| Id Unidade | INT | FK para dUnidades |
| Id Status | INT | FK para dStatus |
| Id Pagamento | INT | FK para dPagamento |
| Data | DATE | Data da venda |
| Data Envio | DATE | Data de envio do pedido |
| Qtde | INT | Quantidade |
| Valor Unit | DECIMAL | Valor unitario |
| Custo Unit | DECIMAL | Custo unitario |
| Despesa Unit | DECIMAL | Despesa operacional unit |
| Impostos Unit | DECIMAL | Imposto unitario |
| Comissao Unit | DECIMAL | Comissao unit da venda |
| Faturamento Total | DECIMAL | Qtde * Valor Unit |
| Custo Total | DECIMAL | Qtde * Custo Unit |

## fMetas

| Campo | Tipo | Descricao |
|---|---|---|
| Id Vendedor | INT | FK para dVendedor |
| Ano | INT | Ano da meta |
| Mes | INT | Mes da meta |
| Id Data | INT | Chave calendario YYYYMM01 |
| Valor Meta | DECIMAL | Meta mensal |

## dProdutos

| Campo | Tipo | Descricao |
|---|---|---|
| Id Produto | INT | PK |
| Produto | VARCHAR | Nome do produto |
| Categoria | VARCHAR | Categoria principal |
| Subcategoria | VARCHAR | Subcategoria |
| Marca | VARCHAR | Marca |
| Prioridade Venda | VARCHAR | P1, P2, P3 ou P4 |
| Multiplicador Prioridade | DECIMAL | Fator aplicado no calculo de comissao |

## dVendedor

| Campo | Tipo | Descricao |
|---|---|---|
| Id Vendedor | INT | PK |
| Vendedor | VARCHAR | Nome do vendedor |
| URL Foto | VARCHAR | Foto ou avatar |
| Gerente | VARCHAR | Lider responsavel |
| Time Comercial | VARCHAR | Grupo ou estrutura comercial |

## dClientes

| Campo | Tipo | Descricao |
|---|---|---|
| Id Cliente | INT | PK |
| Cliente | VARCHAR | Nome do cliente |
| Id Cidade | INT | FK para dCidade |

## dCidade

| Campo | Tipo | Descricao |
|---|---|---|
| Id Cidade | INT | PK |
| Cidade | VARCHAR | Nome da cidade |
| UF | CHAR(2) | Sigla |
| Estado | VARCHAR | Nome do estado |

## dCalendario

| Campo | Tipo | Descricao |
|---|---|---|
| Data | DATE | PK |
| Ano | INT | Ano |
| Semestre | INT | 1 ou 2 |
| Trimestre | INT | 1 a 4 |
| Mes | INT | 1 a 12 |
| NomeMes | VARCHAR | Nome do mes |
| Semana | INT | Semana do ano |
| AnoMes | INT | Chave YYYYMM |
| IsDiaUtil | BIT | 1 se dia util |

## Estruturas futuras recomendadas

### param_regra_comissao

| Campo | Tipo | Descricao |
|---|---|---|
| Faixa Inicio | DECIMAL | Percentual minimo de atingimento |
| Faixa Fim | DECIMAL | Percentual maximo de atingimento |
| Fator Payout | DECIMAL | Percentual do payout alvo |
| Vigencia Inicio | DATE | Inicio da regra |
| Vigencia Fim | DATE | Fim da regra |

### param_prioridade_produto

| Campo | Tipo | Descricao |
|---|---|---|
| Id Produto | INT | Produto |
| Prioridade Venda | VARCHAR | P1 a P4 |
| Multiplicador Prioridade | DECIMAL | Multiplicador aplicado |
| Vigencia Inicio | DATE | Inicio da vigencia |
| Vigencia Fim | DATE | Fim da vigencia |

### fComissaoMensal

| Campo | Tipo | Descricao |
|---|---|---|
| Id Vendedor | INT | FK para dVendedor |
| Id Produto | INT | FK para dProdutos |
| Id Data | INT | Mes de referencia |
| Receita Elegivel | DECIMAL | Base da comissao |
| Fator Atingimento | DECIMAL | Fator por meta batida |
| Multiplicador Prioridade | DECIMAL | Fator do produto |
| Comissao Calculada | DECIMAL | Valor calculado |
| Comissao Paga | DECIMAL | Valor final pago |

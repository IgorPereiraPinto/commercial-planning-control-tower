# Arquitetura do Pipeline - planejamento-comercial

## Visao geral

O projeto segue uma arquitetura medallion adaptada para um contexto de planejamento comercial:

```text
Excel -> Python ETL -> SQL Server raw/staging/dw -> Power BI / dashboard HTML -> automacao
```

## Camadas

### Fonte

- `Dimensoes.xlsx`
- `Vendas.xlsx`
- `Meta_20XX.xlsx`

### Python ETL

- `extract.py`
  leitura dos arquivos
- `transform.py`
  limpeza, normalizacao e unpivot das metas
- `validate.py`
  regras estruturais e de negocio
- `load.py` e `load_dw.py`
  carga nas camadas SQL
- `pipeline.py`
  orquestracao ponta a ponta

### SQL Server

- `raw`
  espelho validado da fonte
- `staging`
  dado tratado e normalizado
- `dw`
  camada analitica para dashboard, Power BI e automacao

### Consumo

- dashboard HTML
- Power BI com DAX e RLS
- apresentacao executiva
- alertas e fluxos automatizados

## Por que essa arquitetura faz sentido

- separa validacao de fonte e validacao de regra de negocio
- facilita reuso do pipeline para outros casos
- permite expor KPIs em mais de um output
- prepara o projeto para escala sem recomeçar a modelagem

## Camada nova de comissao

Para tornar o portfolio mais aderente a um caso real, o projeto passa a considerar uma camada de comissionamento.

### Desenho recomendado

```text
dw.fVendas
  + dw.fMetas
  + param_regra_comissao
  + param_prioridade_produto
  -> dw.fComissaoMensal
```

### Beneficios

- auditoria do payout
- simulacao de politica comercial
- previsao de despesa de comissao
- alinhamento entre incentivo, prioridade de produto e resultado

## Escala para uma operacao real

O projeto ja foi organizado para facilitar a transicao de portfolio para rotina corporativa.

### Recomendacoes de evolucao

1. transformar regras de comissao em tabelas parametricas
2. criar fato mensal de comissao no DW
3. expor visoes para alertas e consumo automatico
4. agendar ETL e refresh com janela definida
5. disparar alertas para:
   - vendedor abaixo de 80%
   - forecast base abaixo de 95% da meta
   - queda de mix P1/P2 abaixo do limite

### Exemplo de fluxo operacional

```text
refresh diario
-> recalculo do forecast
-> recalculo da comissao estimada
-> comparacao com regras de risco
-> alerta para gerente / planejamento / diretoria
```

## Dry-run e desacoplamento

O pipeline foi ajustado para que `python run_etl.py --dry-run` valide extracao, transformacao e regras sem depender da camada SQL no momento do import. Isso deixa o projeto mais robusto para desenvolvimento local e onboarding.

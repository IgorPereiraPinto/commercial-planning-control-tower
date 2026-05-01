# Analyze Credit

## Objetivo
Atalho para análise de carteira de crédito com indicadores de risco, aging, PDD e recomendação.

## Quando usar
Use este command quando o usuário trazer dados de carteira de crédito, posição de contratos
ou dados de inadimplência e precisar de leitura de risco estruturada.

## Instrução de execução
Conduza a resposta nesta ordem:
1. contextualizar a carteira: saldo, segmento, produto, período
2. calcular KPIs: inadimplência 15+, 30+, 90+, cobertura de provisão
3. montar aging (faixas de atraso com saldo e % do total)
4. calcular PDD requerido vs constituído
5. identificar concentrações de risco (cliente, segmento, produto)
6. analisar tendência da inadimplência (melhora ou piora)
7. recomendar ação de crédito: política, cobrança, provisionamento

## Formato de saída
1. visão da carteira (saldo, composição)
2. KPIs de risco
3. aging por faixa
4. PDD requerido vs constituído
5. concentrações e riscos
6. tendência
7. recomendação priorizada (política, cobrança, provisão)

## Skill principal
credit-analytics.md

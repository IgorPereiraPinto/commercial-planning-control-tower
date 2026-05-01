# Validate Data Quality

## Objetivo
Atalho para executar framework de qualidade de dados sobre um dataset ou tabela.

## Quando usar
Use este command quando o usuário precisar validar formalmente um dataset antes de uma
carga, publicação de relatório, ou entrega de análise.

## Instrução de execução
Conduza a resposta nesta ordem:
1. identificar o dataset, fonte e objetivo da validação
2. definir as regras por dimensão: estrutural, domínio, unicidade, negócio, reconciliação, auditoria
3. executar (ou gerar código para executar) cada regra
4. classificar cada resultado: PASSOU / FALHOU / ALERTA
5. separar falhas críticas de alertas
6. gerar relatório de qualidade estruturado
7. recomendar ação: aprovar, corrigir ou bloquear carga

## Formato de saída
1. escopo da validação (dataset, período, fonte)
2. regras definidas por dimensão
3. resultado por regra (tabela)
4. resumo: total passou / falhou / críticos
5. falhas críticas detalhadas
6. recomendação: aprovar / corrigir / bloquear
7. próximos passos

## Skill principal
data-quality-framework.md

# Run Subagent Workflow

## Objetivo
Atalho para decompor uma tarefa complexa em subagents especializados e coordenar a execução.

## Quando usar
Use este command quando a tarefa tiver partes independentes ou sequenciais que se beneficiam
de execução por agentes especializados distintos.

## Instrução de execução
Conduza a resposta nesta ordem:
1. entender a tarefa principal e o entregável final esperado
2. decompor em workstreams: identificar partes independentes e dependentes
3. para cada workstream, definir: agente responsável, input, output esperado, dependências
4. propor o padrão de orquestração: paralelo, sequencial ou híbrido
5. criar os prompts específicos para cada subagent
6. definir como os resultados serão consolidados
7. indicar o que o orchestrator faz com cada output

## Formato de saída
1. tarefa central e entregável final
2. decomposição em workstreams
3. matriz de subagents (quem faz o quê)
4. prompts prontos para cada subagent
5. ordem de execução e dependências
6. plano de consolidação dos resultados

## Skill principal
subagent-orchestration.md

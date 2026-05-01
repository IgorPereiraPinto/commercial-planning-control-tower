# SUBAGENTS_GUIDE.md

> **versão:** 1.1 | **atualizado:** 2026-04-27

Guia de uso dos subagents do repositório.

---

## O que são subagents?

Subagents são agentes especializados de **escopo muito estreito**, projetados para executar
uma única função dentro de um fluxo maior. Ao contrário dos agents (que conduzem tarefas),
subagents são **chamados pelo orchestrator** ou pelo próprio usuário para executar uma
etapa específica — revisão, geração de hipóteses, validação ou escrita.

### Diferença prática

| | Rules | Skills | Agents | **Subagents** |
|---|---|---|---|---|
| **Para quê** | Padronizar como | Especializar o quê | Conduzir tarefa | Executar etapa |
| **Escopo** | Técnico/transversal | Por domínio | Por tipo de trabalho | Pontual e estreito |
| **Ativação** | Automática | Por trigger | Por demanda | Por orchestrator ou revisor |

---

## Quando usar subagents

Use subagent (em vez de agent) quando:

- Você quer **revisão independente** do trabalho de outro agent
- A tarefa tem uma etapa muito específica que não é o core de nenhum agent
- Você quer executar etapas **em paralelo** com contextos diferentes
- Quer garantir uma **segunda opinião** antes da entrega final

### Exemplo de uso encadeado

```
Usuário pede análise mensal completa
        ↓
Orchestrator decompõe:
  ├── sql-optimizer escreve as queries
  │        ↓ sql-reviewer revisa antes de entregar
  ├── data-analyst gera análise e insights
  │        ↓ hypothesis-generator gera hipóteses complementares
  ├── financial-analyst lê o resultado financeiro
  │        ↓ kpi-validator valida os indicadores usados
  └── technical-writer monta a narrativa
           ↓ insight-writer afina o sumário executivo
```

---

## Subagents disponíveis

| Subagent | Função | Quando ativar |
|---|---|---|
| `sql-reviewer` | Revisa queries SQL (lógica, performance, qualidade) | Antes de entregar qualquer query |
| `hypothesis-generator` | Gera hipóteses ordenadas para desvios | Após identificar resultado inesperado |
| `kpi-validator` | Valida definição e fórmula de KPIs | Na definição de indicadores e dashboards |
| `data-quality-checker` | Executa checklist DQ sobre dataset | Antes de carga Silver/Gold ou análise |
| `insight-writer` | Transforma números em narrativa executiva | Após análise concluída |
| `code-reviewer` | Revisa código Python (qualidade, robustez, segurança) | Antes de entregar pipelines/scripts |

---

## Como criar um novo subagent

Todo subagent fica em `.claude/subagents/` e segue esta estrutura:

```markdown
---
name: nome-do-subagent
description: >
  [O que faz, quando ativar — até 3 linhas]
---

# Subagent: [Nome]

## Papel
[Uma frase clara do que o subagent faz e o que ele NÃO faz]

## Input esperado
[O que ele recebe para trabalhar]

## O que fazer / Checklist
[Passos ou checklist obrigatório]

## Output esperado
[Formato exato de saída — preferencialmente com template]

## Regras
[O que nunca deve fazer, casos de borda, restrições]
```

### Princípios de design

- **Escopo estreito:** um subagent faz UMA coisa bem feita
- **Output estruturado:** sempre template fixo de saída
- **Sem recursão:** subagent não chama outros subagents
- **Sem estado:** cada chamada é independente
- **Crítico ou não:** declarar o que bloqueia vs o que é sugestão

---

## Como ativar subagents no Claude Code

### Manualmente pelo usuário
```
@sql-reviewer revisa essa query antes de eu rodar:
SELECT * FROM vendas WHERE ano = 2024
```

### Pelo orchestrator agent
```
Orchestrator: "A query foi gerada pelo sql-optimizer.
Agora preciso que o @sql-reviewer revise antes de entregar."
```

### Via prompt de sistema (CLAUDE.md do projeto)
```markdown
## Workflow de revisão automática
Toda query SQL gerada neste projeto deve ser revisada pelo
subagent sql-reviewer antes de ser entregue ao usuário.
Todo código Python de pipeline deve passar pelo code-reviewer.
```

---

## Estrutura de pastas esperada

```text
.claude/subagents/
├── sql-reviewer.md
├── hypothesis-generator.md
├── kpi-validator.md
├── data-quality-checker.md
├── insight-writer.md
└── code-reviewer.md
```

---

## Observações

- Subagents não têm memória entre chamadas — passar o contexto necessário a cada vez
- O orchestrator agent (`orchestrator.md`) é o responsável por coordenar subagents em fluxos complexos
- Para tarefas simples e diretas, um agent ou skill é suficiente — não use subagent por burocracia

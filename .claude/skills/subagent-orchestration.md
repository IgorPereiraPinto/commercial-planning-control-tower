---
name: subagent-orchestration
description: >
  Especialista em orquestração de múltiplos agentes e subagents no Claude Code. Cobre design
  de fluxos paralelos e sequenciais, criação de CLAUDE.md específico por subagent, passagem
  de contexto entre agentes, agregação de resultados, padrões do repositório anthropic-cookbook
  multiagent, e uso de extended thinking para tarefas complexas de análise.
  Use sempre que o usuário mencionar subagents, múltiplos agentes, orquestração, tarefa paralela,
  delegação de subtarefa, análise multiagente, ou qualquer fluxo que exija dividir trabalho
  entre especialistas coordenados.
  Trigger para: "usa subagents", "divide essa tarefa em paralelo", "orquestra múltiplos agentes",
  "como usar subagents aqui", "cria um fluxo multiagente", "delega para especialistas".
---

# Subagent Orchestration — Orquestração de Múltiplos Agentes

## Identidade

Arquiteto de sistemas multiagente. Decompõe tarefas complexas em workstreams paralelos,
atribui cada um ao agent especializado correto e integra os resultados em uma entrega
coerente. O orchestrator nunca faz o trabalho técnico — ele coordena quem faz.

---

## Quando Usar

Use orquestração de subagents quando:
- A tarefa tem partes independentes que podem rodar em paralelo
- Diferentes partes exigem especialistas distintos
- O contexto da tarefa completa é grande demais para um único agente
- Você quer revisão independente (ex: subagent revisor após subagent executor)

---

## 1. Estrutura de Subagent — CLAUDE.md Padrão

```markdown
# CLAUDE.md — Subagent: [Nome do Especialista]

## Papel
Você é um [especialidade] sênior. Sua única responsabilidade neste fluxo
é [tarefa específica]. Não faça nada além disso.

## Input esperado
[Descrição do que você vai receber como contexto]

## Critérios de qualidade
- [Regra 1]
- [Regra 2]
- [Regra 3]

## Formato de output
[Exatamente como deve retornar — JSON, markdown, tabela, etc.]

## O que NÃO fazer
- Não executar tarefas fora do escopo acima
- Não assumir informações não fornecidas
- Não inventar dados
```

---

## 2. Padrões de Orquestração

### Padrão 1 — Paralelo (Fan-out → Fan-in)

```
Orchestrator
├── Subagent A: Análise SQL (query de receita)
├── Subagent B: Análise de metas (atingimento)
└── Subagent C: Análise de CX (NPS e SLA)
        ↓
Orchestrator consolida → Relatório Executivo
```

**Quando usar:** partes independentes, sem dependência entre si.

### Padrão 2 — Sequencial (Pipeline)

```
Subagent 1: Extrai dados do SQL Server
        ↓
Subagent 2: Limpa e valida a qualidade dos dados
        ↓
Subagent 3: Calcula KPIs e métricas
        ↓
Subagent 4: Gera narrativa executiva
```

**Quando usar:** cada etapa depende do output da anterior.

### Padrão 3 — Revisor (Executor → Reviewer)

```
Subagent A: Escreve a query SQL
        ↓
Subagent B: Revisa a query (performance, lógica, qualidade)
        ↓
Subagent A (ou Orchestrator): Aplica correções sugeridas
```

**Quando usar:** tarefas técnicas que se beneficiam de segunda opinião.

---

## 3. Prompt do Orchestrator — Template

```
Você é o Orchestrator deste fluxo de análise. Sua função é coordenar,
não executar o trabalho técnico diretamente.

## Tarefa recebida
{descricao_da_tarefa}

## Subagents disponíveis
- sql-optimizer: escreve e revisa queries SQL
- data-analyst: analisa resultados e gera hipóteses
- technical-writer: transforma análise em narrativa executiva
- powerbi-specialist: cria medidas DAX e estrutura dashboards
- financial-analyst: analisa resultados financeiros

## Plano de orquestração
1. Decomponha a tarefa em workstreams paralelos ou sequenciais
2. Para cada workstream, defina:
   - Qual subagent executa
   - Qual o input específico dele
   - Qual o output esperado
   - Quais dependências entre workstreams
3. Ao receber os outputs, consolide em uma entrega coerente

## Regras de orquestração
- Nunca assumir o resultado antes de receber o output do subagent
- Se um subagent falhar, registrar o erro e prosseguir com os demais
- Output final: resumo executivo + outputs técnicos dos subagents
```

---

## 4. Exemplo Real — Análise Mensal Completa

**Tarefa:** "Gera o pacote de análise mensal de performance comercial"

**Decomposição em subagents paralelos:**

```
Workstream A (sql-optimizer):
  Input: "Extraia receita, meta e atingimento por vendedor do mês de março/2025"
  Output: Query SQL + tabela de resultado

Workstream B (data-analyst):
  Input: resultado do Workstream A
  Output: análise de desvios, hipóteses e top 3 insights

Workstream C (powerbi-specialist):
  Input: estrutura de KPIs disponíveis
  Output: medidas DAX necessárias para o dashboard

Workstream D (technical-writer):
  Input: outputs de B + análise de CX separada
  Output: narrativa executiva 3 parágrafos

Orchestrator consolida:
  → Sumário executivo
  → Tabela de dados (A)
  → Análise (B)
  → Medidas DAX (C)
  → Narrativa (D)
```

---

## 5. Uso de Extended Thinking em Subagents

```python
import anthropic

client = anthropic.Anthropic()

def subagent_com_thinking(prompt: str,
                           system: str,
                           budget_tokens: int = 8000) -> str:
    """
    Subagent com extended thinking para análises complexas.
    Usar quando a tarefa exige raciocínio encadeado longo
    (ex: validação de modelo financeiro, análise de crédito complexa).
    """
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=16000,
        thinking={
            "type": "enabled",
            "budget_tokens": budget_tokens
        },
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )

    # Separar thinking do output final
    thinking_text = ""
    output_text = ""
    for block in response.content:
        if block.type == "thinking":
            thinking_text = block.thinking
        elif block.type == "text":
            output_text = block.text

    return output_text, thinking_text
```

---

## 6. Prompt Caching para Subagents com Contexto Longo

```python
def subagent_com_cache(sistema_longo: str, prompt_usuario: str) -> str:
    """
    Usa prompt caching para skill context longo (ex: regras de negócio extensas).
    O conteúdo marcado com cache_control é reutilizado entre chamadas.
    """
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        system=[
            {
                "type": "text",
                "text": sistema_longo,
                "cache_control": {"type": "ephemeral"}  # cache por 5 min
            }
        ],
        messages=[{"role": "user", "content": prompt_usuario}]
    )
    return response.content[0].text
```

---

## Regras de Qualidade

- Orchestrator não deve fazer trabalho técnico — só coordenar e consolidar
- Cada subagent deve ter CLAUDE.md próprio com escopo muito claro
- Passar contexto mínimo necessário — não inundar subagent com informação irrelevante
- Subagents paralelos: independentes, sem dependência entre si
- Subagents sequenciais: output estruturado do anterior é input do próximo
- Extended thinking: usar apenas quando a tarefa genuinamente exige raciocínio complexo (adiciona latência e custo)
- Prompt caching: usar quando o system prompt tem mais de 1024 tokens reutilizados entre chamadas

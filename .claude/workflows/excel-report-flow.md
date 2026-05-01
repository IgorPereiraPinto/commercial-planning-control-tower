# Workflow: Construção de Relatório ou Dashboard Excel

> **domínio:** Excel | **padrão:** sequencial | **agents:** 2-3 | **tempo estimado:** 20-45 min

## Objetivo
Entregar um relatório ou dashboard Excel funcional: estrutura de abas organizada,
KPIs calculados, fórmulas ou código Python, validações e orientação de manutenção.

## Quando usar este workflow
- criar relatório recorrente em Excel (semanal, mensal, fechamento)
- estruturar dashboard executivo em planilha para gestores
- consolidar múltiplas fontes em um único arquivo Excel
- gerar Excel automaticamente via Python a partir de banco de dados
- reformular planilha existente com estrutura mais robusta

## Inputs necessários
- objetivo do relatório e quem vai usar
- dados disponíveis (banco, CSV, SharePoint, planilha manual)
- KPIs ou métricas que devem aparecer
- frequência de atualização (manual, automática, agendada)
- versão do Excel (365 com funções dinâmicas ou tradicional)

---

## Etapas

### Etapa 1 — Diagnóstico e estrutura
**Agent:** `excel-specialist`
**Input:** objetivo + dados disponíveis + público
**Output:** estrutura de abas, escolha de ferramenta (fórmula / VBA / Power Query / Python), esboço dos KPIs
**Prompt sugerido:**
```
Atue como excel-specialist. Preciso de um relatório Excel para [objetivo].
Dados disponíveis: [fonte]. Público: [quem vai usar]. Frequência: [periodicidade].
Proponha: (1) estrutura de abas; (2) ferramenta mais adequada; (3) KPIs principais.
```

### Etapa 2 — Implementação da solução
**Agent:** `excel-specialist`
**Input:** estrutura definida na etapa 1
**Output:** fórmulas / código VBA / Power Query M / Python (openpyxl) com comentários
**Prompt sugerido:**
```
Com base na estrutura definida, implementa a solução com:
(1) fórmulas ou código comentados; (2) validações de entrada; (3) lógica de KPIs.
Adaptar para Excel [versão].
```

### Etapa 3 — Validação de qualidade
**Subagent:** `output-validator`
**Input:** solução da etapa 2
**Output:** checklist de qualidade (nomes de tabelas, proteções, duplicidades, fórmulas)
**Prompt sugerido:**
```
Valida a solução Excel abaixo. Verifica: nomeação de tabelas e ranges, separação
de camadas (Raw/Calc/Dashboard), proteção de abas, tratamento de erros nas
fórmulas e clareza das fórmulas VBA.
[colar solução da etapa 2]
```

### Etapa 4 — Documentação e orientação de uso
**Agent:** `technical-writer`
**Input:** solução validada
**Output:** instruções de uso, como atualizar os dados, o que não editar
**Prompt sugerido:**
```
Escreve um guia de uso curto (máx. 1 página) para o relatório Excel abaixo.
Inclui: (1) como atualizar os dados; (2) o que não editar; (3) onde estão os KPIs;
(4) como interpretar o dashboard. Tom: direto, para usuário não técnico.
```

---

## Variações do workflow

### Versão rápida (fórmula pontual)
Apenas etapa 2 — sem diagnóstico formal

### Versão Python (relatório automatizado)
Etapa 1 → Etapa 2 com template `excel_report.py` → Etapa 3

### Versão com apresentação
Adicionar após etapa 3: `presentation-strategist` para transformar o Excel em deck

---

## Critérios de qualidade da entrega final
- abas separadas por camada: Raw / Calc / Dashboard
- tabelas e ranges nomeados de forma clara
- fórmulas protegidas contra edição acidental
- VBA com `Option Explicit` e tratamento de erro
- Power Query com tipos definidos explicitamente
- sem `SELECT *` equivalente — colunas explicitadas no Power Query

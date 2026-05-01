# Workflow: Revisão e Construção de Pipeline de Dados

> **domínio:** engenharia de dados | **padrão:** sequencial com revisão paralela | **agents:** 3 | **tempo estimado:** 60-120 min

## Objetivo
Desenhar, implementar e validar um pipeline de dados ponta a ponta:
da ingestão até a camada Gold pronta para consumo analítico.

## Quando usar este workflow
- criação de pipeline novo
- refatoração de pipeline existente
- migração de fonte de dados
- implementação de arquitetura medallion
- revisão de qualidade de dados de um pipeline ativo

## Inputs necessários
- descrição da fonte de dados (banco, API, arquivo, scraping)
- requisitos analíticos (quem vai consumir, quais perguntas responder)
- frequência de atualização desejada
- ambiente de destino (AWS, Fabric, SQL Server, BigQuery)

---

## Etapas

### Etapa 1 — Arquitetura do pipeline
**Agent:** `data-engineer`
**Input:** descrição da fonte + requisitos analíticos + ambiente
**Output:** arquitetura Bronze/Silver/Gold com ferramentas, frequência, metadados
**Prompt sugerido:**
```
Atue como data-engineer. Desenha a arquitetura do pipeline para a fonte
[X] com destino [Y]. Define: (1) camadas Bronze/Silver/Gold; (2) ferramentas
por camada; (3) frequência de carga; (4) metadados _etl_*; (5) tratamento
de reprocessamento. Ambiente: [ambiente].
```

### Etapa 2 — SQL de transformação
**Agent:** `sql-optimizer`
**Input:** estrutura do dado bruto + regras de negócio + arquitetura da etapa 1
**Output:** queries CTEs para Silver (limpeza) e Gold (regras de negócio)
**Prompt sugerido:**
```
Atue como sql-optimizer. Escreve as queries de transformação para:
(1) Silver: limpeza, deduplicação, tipagem, normalização;
(2) Gold: aplicação das regras de negócio e agregações finais.
Segue arquitetura definida: [colar etapa 1]. Banco: [banco].
```

### Etapa 2b — Revisão do SQL em paralelo
**Subagent:** `sql-reviewer`
**Input:** queries da etapa 2
**Output:** checklist técnico de qualidade das queries
**Prompt sugerido:**
```
Revisa as queries abaixo com foco em: SELECT *, proteção de divisão,
risco de duplicidade por join, filtros de partição, lógica de negócio.
Usa o checklist padrão e classifica cada item como OK/ALERTA/CRÍTICO.
[colar queries da etapa 2]
```

### Etapa 3 — Checklist de qualidade de dados
**Subagent:** `data-quality-checker`
**Input:** definição das tabelas + regras de negócio
**Output:** checklist DQ com testes a implementar por camada
**Prompt sugerido:**
```
Executa o checklist de qualidade de dados para as tabelas abaixo.
Cobre: unicidade, nulos, tipos, valores esperados, regras de negócio,
reconciliação entre camadas. Classifica por prioridade de implementação.
[colar definição das tabelas]
```

### Etapa 4 — Estrutura de consumo analítico
**Agent:** `bi-analyst`
**Input:** modelo de dados final + requisitos analíticos
**Output:** KPIs, perguntas de negócio respondidas, sugestão de visão de dados
**Prompt sugerido:**
```
Atue como bi-analyst. Com base no modelo de dados abaixo, define:
(1) KPIs que podem ser respondidos; (2) perguntas de negócio cobertas;
(3) lacunas que precisam de mais dados; (4) sugestão de estrutura de painel.
[colar modelo de dados final]
```

### Etapa 5 — Validação final
**Subagent:** `output-validator`
**Input:** entrega completa (arquitetura + SQL + checklist DQ)
**Output:** veredito de prontidão para produção

---

## Variações do workflow

### Versão com scraping
Adicionar antes da etapa 1: `web-scraper` para coleta da fonte externa

### Versão com código Python
Adicionar entre etapas 1 e 2: `data-engineer` para código de ingestão Python

### Versão de revisão de pipeline existente
Pular etapa 1, focar em etapas 2b, 3 e 5

---

## Critérios de qualidade da entrega final
- Bronze imutável, Silver limpo, Gold pronto para BI
- Metadados _etl_* definidos
- Testes de qualidade mapeados por camada
- SQL revisado sem itens CRÍTICO
- Estratégia de reprocessamento definida

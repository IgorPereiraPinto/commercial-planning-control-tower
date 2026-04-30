# Power BI — Modelo, Conexão e Configuração
## Planejamento Comercial

---

## Sumário

1. [Visão geral do modelo](#1-visão-geral-do-modelo)
2. [Conexão ao SQL Server](#2-conexão-ao-sql-server)
3. [Tabelas e relacionamentos](#3-tabelas-e-relacionamentos)
4. [Configuração do modelo no Power BI](#4-configuração-do-modelo-no-power-bi)
5. [Organização das medidas DAX](#5-organização-das-medidas-dax)
6. [Tabela de medidas (estrutura recomendada)](#6-tabela-de-medidas-estrutura-recomendada)
7. [RLS — Row Level Security](#7-rls--row-level-security)
8. [Boas práticas e performance](#8-boas-práticas-e-performance)
9. [Checklist de configuração](#9-checklist-de-configuração)

---

## 1. Visão Geral do Modelo

O modelo do Power BI consome diretamente o schema `dw` do SQL Server, que está
estruturado como **star schema** seguindo o padrão Kimball.

```
Perguntas respondidas pelo modelo:
  1. Qual o faturamento realizado vs meta por vendedor, mês e produto?
  2. Quem são os top 20% de vendedores que geram 80% da receita? (Pareto)
  3. Qual a margem bruta e resultado líquido por categoria de produto?
  4. Como evolui o faturamento YoY (ano sobre ano)?
  5. Qual a precisão do nosso forecast? (MAPE)
  6. Qual a distribuição geográfica da receita?
```

### Star Schema — visão simplificada

```
                    ┌─────────────────┐
                    │  dw.dCalendario  │
                    │  PK: Data        │
                    └────────┬────────┘
                             │ 1:N (via Data)
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────┴────┐  ┌──────┴──────┐  ┌───┴──────────┐
    │ dw.dVendedor │  │ dw.fVendas  │  │  dw.fMetas   │
    │ PK:IdVendedor│  │  FATO PRINCIPAL│  │ Relação inativa│
    └─────────┬────┘  └──────┬──────┘  └──────────────┘
              │     FK ←─────┘ FK ─────────────────────→ dw.dVendedor
              │
    ┌──────────────────────────────────────────────────────────────┐
    │  Outras dimensões conectadas a fVendas:                      │
    │   dw.dProdutos   (Id Produto)                                │
    │   dw.dClientes   (Id Cliente) ──→ dw.dCidade (Id Cidade)    │
    │   dw.dUnidades   (Id Unidade)                                │
    │   dw.dStatus     (Id Status)                                 │
    │   dw.dPagamento  (Id Pgto)                                   │
    └──────────────────────────────────────────────────────────────┘
```

---

## 2. Conexão ao SQL Server

### Passo a passo no Power BI Desktop

1. **Obter Dados** → SQL Server
2. Preencher:
   - **Servidor:** `noteigor`
   - **Banco de dados:** `planejamento_comercial`
   - **Modo de conectividade:** `Import` (recomendado para este volume)
3. **Autenticação:** Windows (usa as credenciais do usuário logado)
4. **Seleção de tabelas:** marcar APENAS as tabelas do schema `dw`:

```
Tabelas a importar (schema dw):
  ✅ dw.fVendas
  ✅ dw.fMetas
  ✅ dw.dCalendario
  ✅ dw.dProdutos
  ✅ dw.dVendedor
  ✅ dw.dClientes
  ✅ dw.dCidade
  ✅ dw.dUnidades
  ✅ dw.dStatus
  ✅ dw.dPagamento

Tabelas a NÃO importar (staging/raw — dado intermediário):
  ❌ staging.*
  ❌ raw.*
```

### Por que Import e não DirectQuery?

| Critério            | Import (recomendado)    | DirectQuery               |
|---------------------|-------------------------|---------------------------|
| Volume (~20k linhas)| Ideal                   | Desnecessário             |
| Performance visual  | Muito rápido (in-memory)| Depende do SQL Server     |
| DAX de inteligência temporal | Funciona 100% | Limitações              |
| Refresh agendado    | Sim (Power BI Service)  | Sim                       |

> [REUTILIZAÇÃO]: Para volumes acima de 500k linhas ou atualização em tempo real,
> considere DirectQuery ou Dual Mode (dimensões Import + fatos DirectQuery).

---

## 3. Tabelas e Relacionamentos

### Relacionamentos a configurar no Power BI

Após importar as tabelas, vá em **Exibição de Modelo** e configure:

| Tabela origem     | Coluna origem  | Tabela destino    | Coluna destino  | Cardinalidade | Ativo? | Direção filtro |
|-------------------|----------------|-------------------|-----------------|---------------|--------|----------------|
| dw.fVendas        | Data           | dw.dCalendario    | Data            | Muitos:1      | Sim    | Single         |
| dw.fVendas        | Id Produto     | dw.dProdutos      | Id Produto      | Muitos:1      | Sim    | Single         |
| dw.fVendas        | Id Vendedor    | dw.dVendedor      | Id Vendedor     | Muitos:1      | Sim    | Single         |
| dw.fVendas        | Id Cliente     | dw.dClientes      | Id Cliente      | Muitos:1      | Sim    | Single         |
| dw.fVendas        | Id Unidade     | dw.dUnidades      | Id Unidade      | Muitos:1      | Sim    | Single         |
| dw.fVendas        | Id Status      | dw.dStatus        | Id Status       | Muitos:1      | Sim    | Single         |
| dw.fVendas        | Id Pgto        | dw.dPagamento     | Id Pagamento    | Muitos:1      | Sim    | Single         |
| dw.dClientes      | Id Cidade      | dw.dCidade        | Id Cidade       | Muitos:1      | Sim    | Single         |
| dw.fMetas         | Id Vendedor    | dw.dVendedor      | Id Vendedor     | Muitos:1      | Sim    | Single         |
| dw.fMetas         | Data Meta      | dw.dCalendario    | Data            | Muitos:1      | **Não** | Single       |

> **Atenção — relacionamento inativo entre fMetas e dCalendario:**
> Este relacionamento DEVE ser marcado como inativo porque dCalendario já tem um
> relacionamento ativo com fVendas. Para ativar o filtro em fMetas, usamos a função
> DAX `USERELATIONSHIP(fMetas[Data Meta], dCalendario[Data])` dentro das medidas de meta.

---

## 4. Configuração do Modelo no Power BI

### 4.1 Tabela Calendário

Após importar `dw.dCalendario`, marque-a como **Tabela de Data**:
- Clique com o direito na tabela → **Marcar como tabela de datas**
- Coluna de data: `Data`

Isso habilita as funções DAX de inteligência temporal:
`TOTALYTD`, `SAMEPERIODLASTYEAR`, `DATESINPERIOD`, etc.

### 4.2 Ocultar colunas técnicas

Oculte as colunas de metadados para manter o modelo limpo para o usuário:

```
Ocultar em TODAS as tabelas:
  _dw_loaded_at
  _dw_source

Ocultar nas tabelas fato (FKs são redundantes com as dimensões):
  fVendas[Id Produto]     → já está em dProdutos
  fVendas[Id Vendedor]    → já está em dVendedor
  fVendas[Id Cliente]     → já está em dClientes
  fVendas[Id Unidade]     → já está em dUnidades
  fVendas[Id Status]      → já está em dStatus
  fVendas[Id Pgto]        → já está em dPagamento
  fMetas[Id Vendedor]     → já está em dVendedor
  fMetas[Data Meta]       → usar dCalendario para filtros
```

### 4.3 Colunas a manter visíveis na fVendas (métricas base)

```
Visíveis e usáveis nas medidas:
  fVendas[Faturamento Total]
  fVendas[Custo Total]
  fVendas[Margem Bruta]         ← coluna computada PERSISTED do SQL Server
  fVendas[Resultado Liquido]    ← coluna computada PERSISTED do SQL Server
  fVendas[Qtde]
  fVendas[Valor Unit]
  fVendas[Custo Unit]
  fVendas[Despesa Unit]
  fVendas[Impostos Unit]
  fVendas[Comissão Unit]
  fVendas[Num Venda]            ← para DISTINCTCOUNT (qtd pedidos)
  fVendas[Data]                 ← FK para dCalendario
  fVendas[Data Envio]           ← análise de lead time
```

### 4.4 Configurar formatações padrão nas colunas

| Tabela         | Coluna           | Formato sugerido         |
|----------------|------------------|--------------------------|
| dCalendario    | Ano              | Sem decimais, sem mil    |
| dCalendario    | AnoMes           | Ocultar (usar NomeMes)   |
| dCalendario    | NomeMes          | Ordenar por Mes (número) |
| dVendedor      | URL Foto         | Categoria: URL da Imagem |
| dCidade        | UF               | Categoria: Estado/Prov.  |
| dCidade        | Estado           | Categoria: Estado/Prov.  |
| dCidade        | Cidade           | Categoria: Cidade        |

> **Ordenação do NomeMes:** Selecione a coluna `NomeMes` → Ferramentas de Coluna
> → "Classificar por Coluna" → selecione `Mes`. Isso garante que Jan, Fev, Mar...
> aparece na ordem correta (não alfabética) em todos os visuais.

---

## 5. Organização das Medidas DAX

### Estrutura recomendada — Tabela de medidas isolada

Crie uma tabela vazia chamada `[_Medidas]` para centralizar todas as medidas:

```
No Power Query Editor:
  Início → Inserir Dados → Criar tabela com 1 coluna e 1 linha vazia
  Renomear para: _Medidas
  Ocultar a coluna interna
```

> **Por que uma tabela separada?**
> - Mantém as medidas organizadas, longe das colunas das tabelas de dados
> - Facilita encontrar medidas no painel de campos
> - Padrão amplamente adotado em Power BI enterprise

### Pastas de medidas (Display Folder)

Organize as medidas nas pastas abaixo dentro da tabela `[_Medidas]`:

```
_Medidas/
├── 📁 01 - Base
│   ├── Faturamento
│   ├── Custo Total
│   ├── Margem Bruta R$
│   ├── Resultado Liquido R$
│   ├── Qtde Vendida
│   └── Qtd Pedidos
│
├── 📁 02 - Percentuais
│   ├── Margem Bruta %
│   ├── Resultado Liquido %
│   └── Ticket Medio
│
├── 📁 03 - Meta
│   ├── Meta
│   ├── Atingimento Meta %
│   ├── Desvio vs Meta R$
│   └── Desvio vs Meta %
│
├── 📁 04 - Temporal (YTD / LY / MTD)
│   ├── Faturamento YTD
│   ├── Meta YTD
│   ├── Atingimento Meta YTD %
│   ├── Faturamento Ano Anterior
│   ├── Variacao vs Ano Anterior %
│   └── Faturamento MTD
│
├── 📁 05 - Forecast / MAPE
│   ├── MAPE Mensal
│   ├── Acuracia Forecast %
│   └── Classificacao Acuracia
│
└── 📁 06 - Pareto / Ranking
    ├── Rank Vendedor
    ├── Faturamento Acumulado %
    └── Classificacao Pareto
```

---

## 6. Tabela de Medidas (Estrutura Recomendada)

Consulte o arquivo `powerbi/dax/medidas_completas.dax` para o código
completo de todas as medidas organizadas por pasta.

### Resumo das medidas e suas funções DAX chave

| Medida                      | Função DAX principal            | Pasta          |
|-----------------------------|---------------------------------|----------------|
| Faturamento                 | SUM                             | 01 - Base      |
| Meta                        | CALCULATE + USERELATIONSHIP     | 03 - Meta      |
| Atingimento Meta %          | DIVIDE                          | 03 - Meta      |
| Faturamento YTD             | TOTALYTD                        | 04 - Temporal  |
| Faturamento Ano Anterior    | CALCULATE + SAMEPERIODLASTYEAR  | 04 - Temporal  |
| MAPE Mensal                 | AVERAGEX + ABS + DIVIDE         | 05 - Forecast  |
| Rank Vendedor               | RANKX + ALL                     | 06 - Pareto    |
| Faturamento Acumulado %     | CALCULATE + ALLSELECTED         | 06 - Pareto    |

---

## 7. RLS — Row Level Security

### Hierarquia de acesso

```
Nível 1 — Gerente (vê apenas os vendedores do seu time)
  Guardiola  → Ronaldo, Rodrigo
  Marta      → Paola, Marilia
  Zagallo    → Neymar + demais vendedores do time

Nível 2 — Diretoria / Admin (vê tudo — sem filtro RLS)
```

### Configuração passo a passo

**1. No Power BI Desktop → Modelagem → Gerenciar Funções**

Crie as seguintes roles:

#### Role: `Gerente_Guardiola`
```dax
-- Aplicada na tabela dw.dVendedor
[Gerente] = "Guardiola"
```

#### Role: `Gerente_Marta`
```dax
-- Aplicada na tabela dw.dVendedor
[Gerente] = "Marta"
```

#### Role: `Gerente_Zagallo`
```dax
-- Aplicada na tabela dw.dVendedor
[Gerente] = "Zagallo"
```

#### Role: `Admin`
```dax
-- Sem filtro: role vazia — o usuário vê tudo
-- (apenas para controle formal, não precisa de DAX)
```

**2. Por que o filtro em dVendedor se propaga para fVendas e fMetas?**

O relacionamento ativo `fVendas[Id Vendedor] → dVendedor[Id Vendedor]` com
direção de filtro **Single (dVendedor → fVendas)** garante que o filtro de RLS
aplicado em dVendedor automaticamente filtra fVendas e fMetas.

Não é necessário criar filtro RLS diretamente nas tabelas fato.

**3. Testar o RLS antes de publicar**

No Power BI Desktop:
- Modelagem → Exibir como → selecione uma role
- Verifique se os visuais mostram apenas os dados do gerente correspondente

**4. No Power BI Service — atribuir usuários às roles**

Após publicar:
- Workspace → Dataset → Segurança
- Adicione o e-mail do gerente à role correspondente:

```
Gerente_Guardiola:  e-mail do Guardiola
Gerente_Marta:      e-mail da Marta
Gerente_Zagallo:    e-mail do Zagallo
Admin:              e-mail da diretoria / Igor
```

Consulte o arquivo `powerbi/rls/rls_roles_completo.md` para o guia completo
com DAX de validação e cenários de teste.

---

## 8. Boas Práticas e Performance

### 8.1 Ordem de filtros no visual (impacto direto na DAX)

O Power BI avalia medidas dentro do contexto de filtro dos visuais. Para garantir
que as medidas de TOTALYTD e SAMEPERIODLASTYEAR funcionem corretamente:

- Use SEMPRE a coluna `dCalendario[Data]` (ou atributos dela) nos eixos de visuais
- **NUNCA** use `fVendas[Data]` diretamente nos eixos — perde o benefício do calendário
- Nos slicers de período, use `dCalendario[Ano]` e `dCalendario[NomeMes]`

### 8.2 Evitar colunas calculadas desnecessárias

As colunas `Margem Bruta` e `Resultado Liquido` já vêm calculadas do SQL Server
como colunas PERSISTED. Não recrie-as como colunas calculadas no Power BI.

Use apenas MEDIDAS (measures) para qualquer cálculo de agregação.

### 8.3 Performance — boas práticas

```
✅ Use DIVIDE() em vez de / para evitar erro de divisão por zero
✅ Use CALCULATE() para modificar contexto de filtro
✅ Prefira ALL() a REMOVEFILTERS() para limpeza de contexto quando compatível
✅ Use SELECTEDVALUE() em vez de VALUES() quando espera um único valor
✅ Use ISBLANK() para verificar ausência de dado antes de calcular
✅ Use VAR...RETURN para variáveis em medidas longas (legibilidade + performance)
✅ Valide medidas novas em uma tabela Matrix antes de usá-las em cards
```

### 8.4 Nomeação de medidas

Convenção adotada neste projeto:

```
[Faturamento]                → KPI base sem sufixo
[Faturamento YTD]            → sufixo do período
[Faturamento Ano Anterior]   → sufixo descritivo
[Margem Bruta %]             → sufixo % para percentuais
[Margem Bruta R$]            → sufixo R$ quando há versão em % junto
[Atingimento Meta %]         → nome completo, sem abreviação
[MAPE Mensal]                → sigla conhecida + granularidade
```

---

## 9. Checklist de Configuração

Use esta lista para garantir que o modelo está 100% configurado antes de criar os visuais:

### Conexão e importação
- [ ] Conectado ao servidor `noteigor`, banco `planejamento_comercial`
- [ ] Todas as 10 tabelas do schema `dw` importadas
- [ ] Nenhuma tabela de `raw` ou `staging` no modelo

### Relacionamentos
- [ ] 9 relacionamentos ativos configurados (conforme tabela na Seção 3)
- [ ] Relacionamento `fMetas[Data Meta] → dCalendario[Data]` marcado como **INATIVO**
- [ ] Nenhum relacionamento many-to-many não intencional

### Calendário
- [ ] `dCalendario` marcada como Tabela de Data
- [ ] Coluna `Data` selecionada como campo de data da tabela
- [ ] Coluna `NomeMes` configurada para ordenar por `Mes`

### Modelo
- [ ] Colunas técnicas `_dw_loaded_at` e `_dw_source` ocultas
- [ ] FKs da tabela fato ocultas (redundantes com as dimensões)
- [ ] Coluna `URL Foto` de dVendedor categorizada como URL de Imagem
- [ ] Colunas geográficas (UF, Estado, Cidade) categorizadas corretamente

### Medidas
- [ ] Tabela `_Medidas` criada e vazia
- [ ] Todas as medidas criadas dentro de `_Medidas` (não nas tabelas de dados)
- [ ] Medidas organizadas em pastas (Display Folder)
- [ ] Medida `Meta` usa `USERELATIONSHIP` para o relacionamento inativo

### RLS
- [ ] 3 roles criadas: Gerente_Guardiola, Gerente_Marta, Gerente_Zagallo
- [ ] Filtro DAX aplicado na tabela `dw.dVendedor`
- [ ] Testado com "Exibir como" no Power BI Desktop
- [ ] Usuários atribuídos às roles no Power BI Service

---

*Arquivo gerado como parte do Planejamento Comercial.*
*Próximos entregáveis: `dax/medidas_completas.dax` e `rls/rls_roles_completo.md`*

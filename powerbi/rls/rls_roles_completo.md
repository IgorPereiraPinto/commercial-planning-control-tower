# RLS — Row Level Security
## Planejamento Comercial

---

## O que é o RLS aqui

O RLS garante que cada gerente veja **apenas os dados dos vendedores do seu time**
ao acessar o relatório no Power BI Service, sem nenhuma ação manual.

A configuração se baseia na coluna `dw.dVendedor[Gerente]`, que já foi populada
no pipeline ETL com os valores: `Guardiola`, `Marta` e `Zagallo`.

---

## Hierarquia de acesso

```
Diretoria / Admin
  └── Vê TUDO (sem filtro)

Gerente Guardiola
  └── Ronaldo
  └── Rodrigo

Gerente Marta
  └── Paola
  └── Marilia

Gerente Zagallo
  └── Neymar
  └── (demais vendedores do time Zagallo)
```

---

## Passo 1 — Criar as roles no Power BI Desktop

### Caminho: Modelagem → Segurança → Gerenciar Funções

---

### Role: `Gerente_Guardiola`

**Tabela:** `dw dVendedor`

**Expressão DAX do filtro:**
```dax
[Gerente] = "Guardiola"
```

**O que essa role faz:**
Filtra a dimensão `dVendedor` para mostrar apenas os vendedores onde
`Gerente = "Guardiola"`. Como `dVendedor` está conectada a `fVendas` e
`fMetas` por relacionamentos ativos, o filtro se propaga automaticamente:
o gerente Guardiola só verá faturamento, metas e rankings dos seus vendedores.

---

### Role: `Gerente_Marta`

**Tabela:** `dw dVendedor`

**Expressão DAX do filtro:**
```dax
[Gerente] = "Marta"
```

---

### Role: `Gerente_Zagallo`

**Tabela:** `dw dVendedor`

**Expressão DAX do filtro:**
```dax
[Gerente] = "Zagallo"
```

---

### Role: `Admin`

**Tabela:** (nenhuma — role vazia)

**Expressão DAX do filtro:** (vazia)

**O que essa role faz:**
Usuários na role Admin não têm filtro aplicado. Veem todos os dados.
Use esta role para a Diretoria e para o próprio Igor durante desenvolvimento.

> **Nota:** No Power BI Service, qualquer usuário com permissão de `Membro`
> ou `Administrador` no workspace NÃO é afetado pelo RLS. O RLS aplica-se
> apenas a usuários com permissão de `Visualizador` ou acesso via app.
> Garanta que os gerentes tenham acesso como Viewer, não como Member.

---

## Passo 2 — Testar as roles no Power BI Desktop

Antes de publicar, simule cada role:

**Caminho:** Modelagem → Exibir como → selecione a role

### Checklist de validação por role

#### Gerente_Guardiola
- [ ] Slicer de Vendedor mostra apenas: Ronaldo, Rodrigo
- [ ] KPI Faturamento total = soma de Ronaldo + Rodrigo
- [ ] Pareto mostra apenas 2 vendedores
- [ ] Mapa (se houver) mostra apenas os clientes desses vendedores

#### Gerente_Marta
- [ ] Slicer de Vendedor mostra apenas: Paola, Marilia
- [ ] KPI Faturamento total = soma de Paola + Marilia
- [ ] Meta (fMetas) filtrada apenas para esses vendedores

#### Gerente_Zagallo
- [ ] Slicer de Vendedor mostra apenas os vendedores do time Zagallo
- [ ] Sem vazamento de dados de outros times

#### Admin (exibir como)
- [ ] Todos os 11 vendedores visíveis
- [ ] Faturamento total = total geral do dataset

---

## Passo 3 — Publicar e atribuir usuários no Power BI Service

Após publicar o relatório:

1. Acesse o **Workspace** do Power BI Service
2. Clique em **…** ao lado do **Dataset** (não do relatório)
3. Selecione **Segurança**
4. Na tela de segurança:

| Role                 | E-mail do usuário         |
|----------------------|---------------------------|
| Gerente_Guardiola    | guardiola@empresa.com.br  |
| Gerente_Marta        | marta@empresa.com.br      |
| Gerente_Zagallo      | zagallo@empresa.com.br    |
| Admin                | igor@empresa.com.br       |
| Admin                | diretoria@empresa.com.br  |

> [REUTILIZAÇÃO]: Substitua os e-mails pelos reais do novo projeto.
> Em ambientes com Azure AD, você pode usar grupos de segurança em vez
> de e-mails individuais para facilitar a manutenção.

---

## Passo 4 — Validar no Power BI Service

Após atribuir os usuários:

1. Na tela de Segurança do dataset → clique em **Testar como role**
2. Selecione cada role e confirme que os dados filtrados estão corretos
3. Como alternativa, peça para cada gerente acessar o relatório e confirmar
   que vê apenas os dados do seu time

---

## Comportamento das medidas com RLS

### Medidas que funcionam corretamente com RLS ativo

Todas as medidas criadas em `medidas_completas.dax` foram projetadas para
funcionar com RLS, com uma ressalva importante:

### Medida `Rank Vendedor` — atenção especial

```dax
Rank Vendedor =
IF(
    ISBLANK( [Faturamento] ),
    BLANK(),
    RANKX(
        ALL( 'dw dVendedor'[Vendedor] ),
        [Faturamento],
        ,
        DESC,
        Dense
    )
)
```

`ALL(dVendedor[Vendedor])` remove os filtros de RLS **dentro da medida**.
Isso significa que, com RLS ativo, o ranking do Gerente Guardiola mostrará
as posições absolutas (ex: Ronaldo = posição 3 no ranking geral, Rodrigo = posição 7).

**Se você quiser que o ranking seja relativo ao time do gerente** (posição 1 e 2 dentro do time),
use `ALLSELECTED` em vez de `ALL`:

```dax
Rank Vendedor (Relativo ao Time) =
IF(
    ISBLANK( [Faturamento] ),
    BLANK(),
    RANKX(
        ALLSELECTED( 'dw dVendedor'[Vendedor] ),
        [Faturamento],
        ,
        DESC,
        Dense
    )
)
```

### Medida `Faturamento Acumulado %` com RLS

Com RLS ativo, `ALLSELECTED` respeita o filtro de RLS — o percentual acumulado
será calculado apenas sobre os vendedores visíveis. Isso é o comportamento correto
para o gerente: ele vê seu próprio Pareto, não o Pareto global.

---

## Resumo da propagação de filtros com RLS

```
dVendedor [Gerente = "Guardiola"]  (filtro de RLS)
    │
    ▼ filtro se propaga via relacionamentos ativos
    │
    ├── fVendas (faturamento, custos, margem)
    │       Relacionamento: fVendas[Id Vendedor] → dVendedor[Id Vendedor]
    │
    └── fMetas (metas do vendedor)
            Relacionamento: fMetas[Id Vendedor] → dVendedor[Id Vendedor]
            (ativo — RLS funciona direto)
```

O filtro de RLS **NÃO** precisa ser configurado nas tabelas fato.
Ele propaga automaticamente pelas Foreign Keys com relacionamento ativo.

---

## Troubleshooting comum

| Problema                                  | Causa provável                              | Solução                                      |
|-------------------------------------------|---------------------------------------------|----------------------------------------------|
| Gerente vê dados de outros times          | Role não configurada corretamente           | Revisar a expressão DAX da role              |
| Usuário não vê nenhum dado               | E-mail errado na atribuição                 | Confirmar o e-mail exato no Azure AD         |
| Admin ainda é filtrado                    | Admin está com role de Gerente também       | Remover o usuário da role de Gerente         |
| Meta aparece para todos os gerentes       | Relacionamento fMetas→dVendedor inativo     | Confirmar que o relacionamento está ativo    |
| Rank mostra posição global, não do time   | ALL() usado em vez de ALLSELECTED()         | Usar a versão "Relativo ao Time" da medida   |

---

*Arquivo gerado como parte do Planejamento Comercial.*

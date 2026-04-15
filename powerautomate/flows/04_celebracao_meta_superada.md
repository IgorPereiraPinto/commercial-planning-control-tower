# Fluxo 4 — Celebração de Meta Superada
## Commercial Planning Control Tower — Power Automate

---

## Propósito

Quando um vendedor supera 100% da meta mensal, o Power Automate detecta o evento
em tempo (quase) real via gatilho de alerta do Power BI e posta uma mensagem de
parabéns no canal do Microsoft Teams do time — reconhecimento instantâneo e visível
para toda a equipe.

**Problema que resolve:** conquistas comerciais passam despercebidas no dia a dia.
Este fluxo garante que superação de meta gera reconhecimento público e imediato,
sem depender da memória do gestor.

---

## Configuração do Gatilho — Power BI Alert

### Pré-requisito: criar o alerta no Power BI Service

Antes de configurar o fluxo, é necessário criar um **Alerta de Dados** no
dashboard do Power BI:

1. Publique o relatório e acesse o **Dashboard** (não o Report) no Power BI Service
2. No cartão de KPI de "Atingimento Meta %", clique nos **…** → Gerenciar alertas
3. Clique em **+ Adicionar regra de alerta**:

```
Nome:        Meta Superada — Atingimento > 100%
Condição:    Acima de
Limite:      100
Frequência:  Máximo de uma notificação por hora
```

4. Salve o alerta. O Power BI verificará o KPI conforme o dataset é atualizado.

> **Limitação importante:** o gatilho de alerta do Power BI no Power Automate
> dispara com o ritmo de atualização do dataset, não em tempo real absoluto.
> Com dataset atualizado semanalmente (Fluxo 5), o reconhecimento ocorre na
> próxima segunda-feira. Para refresh mais frequente, configure o dataset para
> atualizar diariamente.

---

## Configuração do Fluxo

### Gatilho — Power BI (alerta de dados)

```
Tipo:          Power BI — Quando um alerta de dados for disparado
               (When a data alert is triggered)
Alert ID:      Selecione o alerta "Meta Superada — Atingimento > 100%"
               criado no Power BI Service
```

---

## Ações — Sequência Completa

### Ação 1 — Consultar SQL: quem superou a meta no mês atual?

**Tipo:** SQL Server — Execute a SQL query

**Nome:** `SQL_Superadores_Meta`

**Query:**

```sql
-- Identifica todos os vendedores que atingiram >= 100% da meta no mês corrente
SELECT
    v.[Vendedor],
    v.[Gerente],
    ROUND( SUM(f.[Faturamento Total]), 2 ) AS Faturamento,
    ROUND( SUM(m.[Valor Meta]),         2 ) AS Meta,
    ROUND(
        SUM(f.[Faturamento Total])
        / NULLIF(SUM(m.[Valor Meta]), 0) * 100,
        1
    )                                        AS AtingimentoPct,
    -- Superavit: quanto acima da meta
    ROUND(
        SUM(f.[Faturamento Total]) - SUM(m.[Valor Meta]),
        2
    )                                        AS Superavit
FROM [dw].[dVendedor] v
INNER JOIN [dw].[fVendas] f
    ON f.[Id Vendedor] = v.[Id Vendedor]
    AND MONTH(f.[Data]) = MONTH(GETDATE())
    AND YEAR(f.[Data])  = YEAR(GETDATE())
INNER JOIN [dw].[fMetas] m
    ON m.[Id Vendedor] = v.[Id Vendedor]
    AND m.[Mes]  = MONTH(GETDATE())
    AND m.[Ano]  = YEAR(GETDATE())
GROUP BY v.[Vendedor], v.[Gerente]
HAVING
    SUM(f.[Faturamento Total]) >= SUM(m.[Valor Meta])
ORDER BY AtingimentoPct DESC;
```

---

### Ação 2 — Verificar se há superadores

**Tipo:** Condição

```
Expressão: length(outputs('SQL_Superadores_Meta')?['body/resultsets/Table1']) is greater than 0
```

**Se Não:** encerrar sem ação (o alerta pode ter sido disparado por KPI antigo).

**Se Sim:** continuar para Ação 3.

---

### Ação 3 — Loop: construir lista de superadores para a mensagem

**Tipo:** Aplicar a cada um

**Entrada:** resultado da query `SQL_Superadores_Meta`

**Dentro do loop:**

**Tipo:** Variável — Acrescentar à variável de string

**Variável:** `strListaVendedores`

```
@{items('Apply_to_each')?['Vendedor']} (@{items('Apply_to_each')?['AtingimentoPct']}% da meta — superavit de R$ @{formatNumber(float(items('Apply_to_each')?['Superavit']),'#,##0.00')})
```

(Separar com quebra de linha: `\n`)

---

### Ação 4 — Postar mensagem no Microsoft Teams

**Tipo:** Microsoft Teams — Postar uma mensagem em um canal (Post a message in a chat or channel)

**Configuração:**

```
Post as:         Flow bot
Post in:         Channel
Team:            [Nome do time — ex: "Comercial - Vendas"]
Channel:         [Nome do canal — ex: "geral" ou "resultados"]
```

**Mensagem:**

```markdown
🎉 **META SUPERADA!** 🎉

Os seguintes vendedores atingiram 100% ou mais da meta em
**@{formatDateTime(utcNow(), 'MMMM/yyyy')}**:

@{variables('strListaVendedores')}

Parabéns pelo resultado excepcional! 💪

_Acesse o [dashboard completo]([URL_DO_DASHBOARD]) para ver o desempenho detalhado._
```

---

### Ação 5 — Enviar e-mail complementar ao gerente

**Tipo:** Office 365 Outlook — Enviar um email (V2)

**Para:** [e-mails dos gerentes]

**Assunto:**
```
🏆 META SUPERADA — @{formatDateTime(utcNow(), 'MMMM/yyyy')}
```

**Corpo (HTML):**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; color: #333; margin: 0; }
    .header { background: linear-gradient(135deg, #107C10, #0078D4);
              color: white; padding: 24px 30px; text-align: center; }
    .header h1 { margin: 0; font-size: 24px; }
    .content { padding: 24px 30px; }
    .destaque { text-align: center; padding: 20px; background: #F0FFF0;
                border-radius: 8px; margin-bottom: 20px; }
    .destaque .numero { font-size: 48px; }
    table { border-collapse: collapse; width: 100%; }
    th { background: #F4F4F4; padding: 10px; text-align: left; font-size: 12px; }
    td { padding: 9px 10px; border-bottom: 1px solid #eee; }
    .footer { background: #F8F8F8; padding: 14px 30px; font-size: 11px;
              color: #888; border-top: 1px solid #ddd; }
  </style>
</head>
<body>

<div class="header">
  <div style="font-size:48px">🏆</div>
  <h1>Meta Superada!</h1>
  <p style="margin:4px 0 0; opacity:.85;">@{formatDateTime(utcNow(), 'MMMM/yyyy')}</p>
</div>

<div class="content">

  <div class="destaque">
    <div class="numero">🎉</div>
    <p style="font-size:16px; margin: 8px 0 0">
      <strong>@{length(outputs('SQL_Superadores_Meta')?['body/resultsets/Table1'])}</strong>
      vendedor(es) atingiram 100% da meta este mês!
    </p>
  </div>

  <table>
    <thead>
      <tr>
        <th>Vendedor</th>
        <th>Gerente</th>
        <th style="text-align:right">Realizado</th>
        <th style="text-align:right">Meta</th>
        <th style="text-align:center">Atingimento</th>
        <th style="text-align:right">Superávit</th>
      </tr>
    </thead>
    <tbody>
      @{variables('strLinhasVendedores')}
    </tbody>
  </table>

  <p style="margin-top:20px; color:#555; font-size:13px;">
    Parabenize sua equipe pelo resultado! O reconhecimento é combustível para
    a próxima meta.
  </p>

</div>

<div class="footer">
  Notificação automática do Commercial Planning Control Tower.<br>
  <a href="[URL_DO_DASHBOARD]">Ver dashboard completo</a>
</div>

</body>
</html>
```

---

### Ação 6 — Tratamento de erro

Scope com fallback padrão: e-mail de erro ao Igor com detalhes da falha.

---

## Resultado esperado

Quando qualquer vendedor supera 100% da meta:

**Teams** (visível para toda a equipe):
```
🎉 META SUPERADA! 🎉
Os seguintes vendedores atingiram 100% ou mais da meta em Janeiro/2021:
Ronaldo (127,3% da meta — superavit de R$ 13.650,00)
Parabéns pelo resultado excepcional! 💪
```

**E-mail** (para os gerentes): tabela completa com Atingimento % e Superávit R$.

---

## Variações e melhorias

### Disparar celebração individual por gerente

Adicione um Filter Array por `Gerente` antes de postar no Teams,
postando em canais separados por time (ex: #time-guardiola, #time-marta).

### Adicionar foto do vendedor na mensagem

A coluna `dVendedor[URL Foto]` está disponível no DW. Adicione à query e use
a URL na mensagem do Teams para incluir a foto do vendedor no card de celebração.

### Integração com Badge / Reconhecimento

Se a empresa usa plataformas de reconhecimento (ex: Viva Engage, Kudos), o mesmo
gatilho pode disparar um badge automático para o vendedor.

---

## Checklist de teste

- [ ] Alerta de dados criado corretamente no Power BI Service
- [ ] Conexão Power BI configurada no fluxo
- [ ] Canal do Teams correto selecionado
- [ ] Testar manualmente: publicar dataset com um vendedor > 100%
- [ ] Confirmar que o bot do Teams posta com formatação correta
- [ ] Confirmar que o e-mail HTML renderiza corretamente
- [ ] Confirmar que fluxo NÃO dispara quando ninguém superou a meta

---

*Fluxo 4 de 5 — Commercial Planning Control Tower.*

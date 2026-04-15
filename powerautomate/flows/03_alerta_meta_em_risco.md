# Fluxo 3 — Alerta de Meta em Risco no Fechamento
## Commercial Planning Control Tower — Power Automate

---

## Propósito

Todo dia 20 do mês às 08h, o fluxo calcula a projeção de fechamento do mês
baseada no ritmo atual de vendas. Se a projeção indica que a empresa fechará
abaixo de 90% da meta, dispara um alerta imediato para a diretoria com o gap
e sugestões de ação — a tempo de ainda intervir antes do fechamento.

**Problema que resolve:** descobrir no dia 31 que a meta não foi batida quando
já não há mais nada a fazer. O dia 20 é o ponto de virada: ainda há tempo hábil
para acelerar esforços comerciais.

---

## Configuração do Fluxo

### Gatilho — Recorrência

```
Tipo:         Recorrência (Scheduled)
Frequência:   Mês
Intervalo:    1
Nos dias:     20
Às:           08:00
Fuso:         America/Sao_Paulo
```

> **Nota sobre o gatilho mensal no Power Automate:**
> O gatilho de Recorrência com Frequência = Mês executa no mesmo dia do mês
> configurado no início (dia 20). Atenção: em fevereiro, o dia 20 existe sempre.
> Mas para dias 29, 30, 31 pode haver inconsistência em alguns meses.

---

## Ações — Sequência Completa

### Ação 1 — Consulta SQL: projeção de fechamento do mês

**Tipo:** SQL Server — Execute a SQL query

**Nome:** `SQL_Projecao_Fechamento`

**Query:**

```sql
-- Calcula a projeção de fechamento e compara com a meta
-- Lógica: ritmo diário médio dos 20 primeiros dias × total de dias do mês
WITH
DiasPassados AS (
    SELECT DAY(CAST(GETDATE() AS DATE)) AS Dias
),
RitmoDiario AS (
    SELECT
        SUM(f.[Faturamento Total]) AS FaturamentoAte20,
        DAY(CAST(GETDATE() AS DATE)) AS DiasPassados
    FROM [dw].[fVendas] f
    WHERE
        MONTH(f.[Data]) = MONTH(GETDATE())
        AND YEAR(f.[Data])  = YEAR(GETDATE())
),
MetaMensal AS (
    SELECT SUM(m.[Valor Meta]) AS MetaTotal
    FROM [dw].[fMetas] m
    WHERE
        m.[Mes] = MONTH(GETDATE())
        AND m.[Ano] = YEAR(GETDATE())
)
SELECT
    r.FaturamentoAte20,
    mm.MetaTotal,
    -- Projeção linear: faturamento até hoje / dias passados × total de dias do mês
    ROUND(
        r.FaturamentoAte20
        / NULLIF(r.DiasPassados, 0)
        * DAY(EOMONTH(GETDATE())),
        2
    )                                AS ProjecaoFechamento,
    -- Atingimento projetado: projeção / meta
    ROUND(
        (r.FaturamentoAte20
         / NULLIF(r.DiasPassados, 0)
         * DAY(EOMONTH(GETDATE())))
        / NULLIF(mm.MetaTotal, 0) * 100,
        1
    )                                AS AtingimentoProjetadoPct,
    -- Gap: quanto falta para atingir 100% da meta
    ROUND(
        mm.MetaTotal
        - (r.FaturamentoAte20
           / NULLIF(r.DiasPassados, 0)
           * DAY(EOMONTH(GETDATE()))),
        2
    )                                AS GapParaMeta,
    -- Dias restantes no mês a partir de hoje
    DAY(EOMONTH(GETDATE())) - DAY(CAST(GETDATE() AS DATE)) AS DiasRestantes,
    -- Faturamento diário necessário para recuperar
    ROUND(
        (mm.MetaTotal - r.FaturamentoAte20)
        / NULLIF(DAY(EOMONTH(GETDATE())) - DAY(CAST(GETDATE() AS DATE)), 0),
        2
    )                                AS FaturamentoDiarioNecessario
FROM RitmoDiario r
CROSS JOIN MetaMensal mm;
```

---

### Ação 2 — Extrair resultado da query em variáveis

**Tipo:** Variável — Inicializar variável (uma por KPI)

```
varAtingimentoProjetado  = float(first(outputs('SQL_Projecao_Fechamento')?['body/resultsets/Table1'])?['AtingimentoProjetadoPct'])
varGapParaMeta           = float(first(outputs('SQL_Projecao_Fechamento')?['body/resultsets/Table1'])?['GapParaMeta'])
varProjecaoFechamento    = float(first(outputs('SQL_Projecao_Fechamento')?['body/resultsets/Table1'])?['ProjecaoFechamento'])
varMetaMensal            = float(first(outputs('SQL_Projecao_Fechamento')?['body/resultsets/Table1'])?['MetaTotal'])
varDiasRestantes         = int(first(outputs('SQL_Projecao_Fechamento')?['body/resultsets/Table1'])?['DiasRestantes'])
varFatDiarioNecessario   = float(first(outputs('SQL_Projecao_Fechamento')?['body/resultsets/Table1'])?['FaturamentoDiarioNecessario'])
```

---

### Ação 3 — Condição: a projeção está abaixo de 90%?

**Tipo:** Condição (Condition)

```
Expressão: variables('varAtingimentoProjetado') is less than 90
```

**Se Não (projeção >= 90%):** encerrar o fluxo. Nenhum alerta necessário.

**Se Sim (projeção < 90%):** continuar para Ação 4.

> Por que 90%? O threshold de 90% é o ponto em que ainda há tempo e margem para
> intervir. Abaixo disso, a recuperação requer aceleração significativa.
> [REUTILIZAÇÃO]: Ajuste o threshold conforme a tolerância da empresa.

---

### Ação 4 — Consulta SQL complementar: atingimento por vendedor no dia 20

**Tipo:** SQL Server — Execute a SQL query

**Nome:** `SQL_Ranking_Vendedores_Dia20`

**Query:**

```sql
-- Quem está puxando para baixo? Ranking de atingimento no dia 20
SELECT
    v.[Vendedor],
    v.[Gerente],
    ROUND( COALESCE(SUM(f.[Faturamento Total]), 0), 2 ) AS FaturamentoAcum,
    ROUND( COALESCE(SUM(m.[Valor Meta]),        0), 2 ) AS MetaMensal,
    ROUND(
        COALESCE(SUM(f.[Faturamento Total]), 0)
        / NULLIF(SUM(m.[Valor Meta]), 0) * 100,
        1
    )                                                   AS AtingimentoPct
FROM [dw].[dVendedor] v
LEFT JOIN [dw].[fVendas] f
    ON f.[Id Vendedor] = v.[Id Vendedor]
    AND MONTH(f.[Data]) = MONTH(GETDATE())
    AND YEAR(f.[Data])  = YEAR(GETDATE())
LEFT JOIN [dw].[fMetas] m
    ON m.[Id Vendedor] = v.[Id Vendedor]
    AND m.[Mes]  = MONTH(GETDATE())
    AND m.[Ano]  = YEAR(GETDATE())
GROUP BY v.[Vendedor], v.[Gerente]
ORDER BY AtingimentoPct ASC;
```

---

### Ação 5 — Loop: construir linhas HTML dos vendedores

**Tipo:** Aplicar a cada um (Apply to each)

**Entrada:** resultado da `SQL_Ranking_Vendedores_Dia20`

**Dentro do loop:** concatenar linha HTML com cor semafórica (mesma lógica do Fluxo 1).

---

### Ação 6 — Determinar nível de severidade do alerta

**Tipo:** Condição aninhada

```
Se varAtingimentoProjetado < 70  → severidade = "CRÍTICO"  / cor = "#D83B01"
Se varAtingimentoProjetado < 80  → severidade = "ALTO"     / cor = "#E67E22"
Se varAtingimentoProjetado < 90  → severidade = "MÉDIO"    / cor = "#FFC107"
```

---

### Ação 7 — Enviar alerta para diretoria

**Tipo:** Office 365 Outlook — Enviar um email (V2)

**Para:** diretoria + todos os gerentes

**Assunto:**
```
🚨 [@{variables('varSeveridade')}] Meta em Risco — Projeção @{variables('varAtingimentoProjetado')}% | @{formatDateTime(utcNow(), 'MMMM/yyyy')}
```

**Corpo (HTML):**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; color: #333; margin: 0; }
    .header { background: @{variables('varCorSeveridade')}; color: white; padding: 20px 30px; }
    .header h1 { margin: 0; font-size: 18px; }
    .content { padding: 20px 30px; }
    .risco-box { background: #FFF3CD; border-left: 5px solid @{variables('varCorSeveridade')};
                 padding: 16px 20px; margin-bottom: 20px; border-radius: 4px; }
    .risco-box .nivel { font-size: 13px; font-weight: bold; color: @{variables('varCorSeveridade')}; }
    .kpi-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin-bottom: 24px; }
    .kpi { background: #F8F8F8; border-radius: 6px; padding: 14px; text-align: center; }
    .kpi .val { font-size: 22px; font-weight: bold; color: #0078D4; }
    .kpi .lbl { font-size: 11px; color: #888; }
    .acao-box { background: #E8F5E9; border-left: 4px solid #4CAF50;
                padding: 14px 18px; border-radius: 4px; margin-top: 20px; }
    table { border-collapse: collapse; width: 100%; margin-top: 10px; }
    th { background: #F4F4F4; padding: 8px; text-align: left; font-size: 12px; }
    h3 { color: #333; font-size: 14px; margin: 20px 0 8px; }
    .footer { background: #F8F8F8; padding: 14px 30px; font-size: 11px;
              color: #888; border-top: 1px solid #ddd; }
  </style>
</head>
<body>

<div class="header">
  <h1>🚨 Alerta de Meta em Risco — Nível @{variables('varSeveridade')}</h1>
  <p>@{formatDateTime(utcNow(), 'MMMM/yyyy')} | Avaliação do Dia 20</p>
</div>

<div class="content">

  <div class="risco-box">
    <div class="nivel">Nível de Risco: @{variables('varSeveridade')}</div>
    <p style="margin:8px 0 0">
      Com base no ritmo de vendas dos últimos 20 dias, a projeção indica que o mês de
      <strong>@{formatDateTime(utcNow(), 'MMMM/yyyy')}</strong> fechará em
      <strong style="color:@{variables('varCorSeveridade')}">@{variables('varAtingimentoProjetado')}%</strong>
      da meta — @{formatNumber(variables('varGapParaMeta'),'R$ #,##0.00')} abaixo do budget.
      Restam <strong>@{variables('varDiasRestantes')} dias úteis</strong> para recuperação.
    </p>
  </div>

  <h3>📊 Resumo do Cenário</h3>
  <table>
    <tr>
      <td style="padding:10px; background:#EFF6FF; border-radius:4px; width:33%">
        <div style="font-size:18px;font-weight:bold;color:#0078D4;">
          @{variables('varAtingimentoProjetado')}%
        </div>
        <div style="font-size:11px;color:#666;">Atingimento Projetado</div>
      </td>
      <td style="padding:10px; background:#FDECEA; border-radius:4px; width:33%; margin:0 8px">
        <div style="font-size:18px;font-weight:bold;color:#D83B01;">
          @{formatNumber(variables('varGapParaMeta'),'R$ #,##0.00')}
        </div>
        <div style="font-size:11px;color:#666;">Gap para a Meta</div>
      </td>
      <td style="padding:10px; background:#FFF8EE; border-radius:4px; width:33%">
        <div style="font-size:18px;font-weight:bold;color:#8B5000;">
          @{formatNumber(variables('varFatDiarioNecessario'),'R$ #,##0.00')}/dia
        </div>
        <div style="font-size:11px;color:#666;">Necessário por Dia</div>
      </td>
    </tr>
  </table>

  <h3>📋 Atingimento por Vendedor (Dia 20)</h3>
  <table>
    <thead>
      <tr>
        <th>Vendedor</th><th>Gerente</th>
        <th style="text-align:right">Realizado</th>
        <th style="text-align:right">Meta</th>
        <th style="text-align:center">Atingimento</th>
      </tr>
    </thead>
    <tbody>
      @{variables('strLinhasVendedores')}
    </tbody>
  </table>

  <div class="acao-box">
    <strong>💡 Ações recomendadas:</strong>
    <ul style="margin:8px 0 0; padding-left:20px;">
      <li>Acionar campanhas de incentivo para os vendedores com atingimento abaixo de 70%</li>
      <li>Revisar carteira de oportunidades em aberto para antecipação de fechamentos</li>
      <li>Avaliar se há pedidos pendentes de aprovação que possam ser liberados</li>
      <li>Considerar extensão de prazo de pagamento como alavanca de fechamento</li>
    </ul>
  </div>

</div>

<div class="footer">
  Alerta gerado em @{formatDateTime(utcNow(), 'dd/MM/yyyy HH:mm')} pelo Commercial Planning Control Tower.<br>
  <a href="[URL_DO_DASHBOARD]">Acesse o dashboard</a> para análise completa por produto e região.
</div>

</body>
</html>
```

---

### Ação 8 — Tratamento de erro

Mesmo padrão dos fluxos anteriores: Scope com fallback para e-mail de erro ao Igor.

---

## Resultado esperado

E-mail recebido pela diretoria no dia 20 de cada mês (somente quando há risco):

```
Assunto: 🚨 [ALTO] Meta em Risco — Projeção 83,2% | Janeiro/2021

Mensagem: "Com base no ritmo dos últimos 20 dias, a projeção indica que
o mês fechará em 83,2% da meta — R$ 84.000,00 abaixo do budget.
Restam 11 dias para recuperação. Faturamento necessário: R$ 7.636/dia."

+ Tabela de atingimento por vendedor com cores semafóricas
+ Lista de ações recomendadas
```

---

## Checklist de teste

- [ ] Testar a query principal no SSMS com dados reais do dia 20
- [ ] Validar a lógica de projeção linear (ritmo atual × dias totais)
- [ ] Confirmar que o fluxo **não envia e-mail** quando projeção >= 90%
- [ ] Testar os 3 níveis de severidade (CRÍTICO, ALTO, MÉDIO)
- [ ] Confirmar que os dias restantes calculam corretamente
- [ ] Substituir `[URL_DO_DASHBOARD]` pela URL real antes de ativar

---

*Fluxo 3 de 5 — Commercial Planning Control Tower.*

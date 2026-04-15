# Fluxo 2 — Resumo Semanal de Performance
## Commercial Planning Control Tower — Power Automate

---

## Propósito

Toda sexta-feira às 17h, o fluxo consolida os números da semana e do mês acumulado
e envia um e-mail de resumo para todos os gerentes — um fechamento semanal automático
que substitui reuniões de status operacional e relatórios manuais.

**Problema que resolve:** gestores chegam na reunião de sexta sem saber os números
da semana. Este fluxo entrega o resumo no momento certo, sem trabalho manual.

---

## Configuração do Fluxo

### Gatilho — Recorrência

```
Tipo:         Recorrência (Scheduled)
Frequência:   Semana
Intervalo:    1
Nos dias:     Sexta-feira
Às:           17:00
Fuso:         America/Sao_Paulo
```

---

## Ações — Sequência Completa

### Ação 1 — Consulta SQL 1: KPIs da semana atual

**Tipo:** SQL Server — Execute a SQL query

**Nome da ação:** `SQL_KPIs_Semana`

**Query:**

```sql
-- KPIs da semana atual (segunda a sexta corrente)
SELECT
    COUNT(DISTINCT f.[Num Venda])         AS PedidosSemana,
    ROUND(SUM(f.[Faturamento Total]), 2)  AS FaturamentoSemana,
    ROUND(SUM(f.[Margem Bruta]), 2)       AS MargemBrutaSemana,
    ROUND(
        SUM(f.[Margem Bruta])
        / NULLIF(SUM(f.[Faturamento Total]), 0) * 100,
        1
    )                                     AS MargemBrutaPctSemana,
    COUNT(DISTINCT f.[Id Vendedor])       AS VendedoresAtivos
FROM [dw].[fVendas] f
WHERE
    f.[Data] >= DATEADD(DAY, -(DATEPART(WEEKDAY, GETDATE()) - 2), CAST(GETDATE() AS DATE))
    AND f.[Data] <= CAST(GETDATE() AS DATE);
```

---

### Ação 2 — Consulta SQL 2: KPIs acumulados do mês (MTD)

**Tipo:** SQL Server — Execute a SQL query

**Nome da ação:** `SQL_KPIs_MTD`

**Query:**

```sql
-- Faturamento MTD vs Meta MTD
SELECT
    ROUND( SUM(f.[Faturamento Total]), 2 )  AS FaturamentoMTD,
    ROUND( SUM(m.[Valor Meta]), 2 )         AS MetaMensal,
    ROUND(
        SUM(f.[Faturamento Total])
        / NULLIF(SUM(m.[Valor Meta]), 0) * 100,
        1
    )                                       AS AtingimentoMTDPct,
    -- Projeção linear para o mês: ritmo atual × dias totais do mês / dias passados
    ROUND(
        SUM(f.[Faturamento Total])
        / NULLIF(DAY(CAST(GETDATE() AS DATE)), 0)
        * DAY(EOMONTH(GETDATE())),
        2
    )                                       AS ProjecaoMes
FROM [dw].[fVendas] f
LEFT JOIN [dw].[fMetas] m
    ON m.[Mes]  = MONTH(GETDATE())
    AND m.[Ano] = YEAR(GETDATE())
WHERE
    MONTH(f.[Data]) = MONTH(GETDATE())
    AND YEAR(f.[Data])  = YEAR(GETDATE());
```

---

### Ação 3 — Consulta SQL 3: Top 3 vendedores da semana

**Tipo:** SQL Server — Execute a SQL query

**Nome da ação:** `SQL_Top3_Semana`

**Query:**

```sql
SELECT TOP 3
    v.[Vendedor],
    v.[Gerente],
    COUNT(DISTINCT f.[Num Venda])        AS Pedidos,
    ROUND( SUM(f.[Faturamento Total]), 2 ) AS Faturamento
FROM [dw].[fVendas] f
INNER JOIN [dw].[dVendedor] v ON f.[Id Vendedor] = v.[Id Vendedor]
WHERE
    f.[Data] >= DATEADD(DAY, -(DATEPART(WEEKDAY, GETDATE()) - 2), CAST(GETDATE() AS DATE))
    AND f.[Data] <= CAST(GETDATE() AS DATE)
GROUP BY v.[Vendedor], v.[Gerente]
ORDER BY Faturamento DESC;
```

---

### Ação 4 — Consulta SQL 4: Atingimento MTD por vendedor (tabela completa)

**Tipo:** SQL Server — Execute a SQL query

**Nome da ação:** `SQL_Atingimento_Vendedores`

**Query:**

```sql
SELECT
    v.[Vendedor],
    v.[Gerente],
    ROUND( COALESCE(SUM(f.[Faturamento Total]), 0), 2 )  AS FaturamentoMTD,
    ROUND( COALESCE(SUM(m.[Valor Meta]),         0), 2 ) AS MetaMensal,
    ROUND(
        COALESCE(SUM(f.[Faturamento Total]), 0)
        / NULLIF(SUM(m.[Valor Meta]), 0) * 100,
        1
    )                                                    AS AtingimentoPct
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
ORDER BY AtingimentoPct DESC;
```

---

### Ação 5 — Inicializar variável para as linhas da tabela de vendedores

**Tipo:** Variável — Inicializar variável

```
Nome:  strLinhasVendedores
Tipo:  String
Valor: (vazio)
```

---

### Ação 6 — Loop: construir linhas HTML dos vendedores

**Tipo:** Controle — Aplicar a cada um

**Entrada:** `outputs('SQL_Atingimento_Vendedores')?['body/resultsets/Table1']`

**Dentro do loop — determinar cor de fundo da linha:**

```
Se AtingimentoPct >= 100  → corLinha = "#E6F4EA"   (verde claro)
Se AtingimentoPct >= 90   → corLinha = "#FFFDE7"   (amarelo claro)
Senão                     → corLinha = "#FDECEA"   (vermelho claro)
```

**Dentro do loop — concatenar linha:**

```html
<tr style="background-color:@{variables('corLinha')}">
  <td style="padding:7px 10px;">@{items('Apply_to_each')?['Vendedor']}</td>
  <td style="padding:7px 10px; color:#555;">@{items('Apply_to_each')?['Gerente']}</td>
  <td style="padding:7px 10px; text-align:right;">
    R$ @{formatNumber(float(items('Apply_to_each')?['FaturamentoMTD']),'#,##0.00')}
  </td>
  <td style="padding:7px 10px; text-align:right;">
    R$ @{formatNumber(float(items('Apply_to_each')?['MetaMensal']),'#,##0.00')}
  </td>
  <td style="padding:7px 10px; text-align:center; font-weight:bold;">
    @{items('Apply_to_each')?['AtingimentoPct']}%
  </td>
</tr>
```

---

### Ação 7 — Montar e enviar e-mail de resumo

**Tipo:** Office 365 Outlook — Enviar um email (V2)

**Para:** todos os gerentes + diretoria

**Assunto:**
```
📊 Resumo de Performance — Semana @{formatDateTime(utcNow(), 'dd/MM')} | @{formatDateTime(utcNow(), 'MMMM/yyyy')}
```

**Corpo (HTML):**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; color: #333; margin: 0; }
    .header { background: #0078D4; color: white; padding: 20px 30px; }
    .header h1 { margin: 0; font-size: 18px; }
    .content { padding: 20px 30px; }
    .kpi-row { display: flex; gap: 16px; margin-bottom: 24px; }
    .kpi-box { flex: 1; background: #F4F4F4; border-radius: 8px;
               padding: 16px; text-align: center; }
    .kpi-box .valor { font-size: 22px; font-weight: bold; color: #0078D4; }
    .kpi-box .label { font-size: 11px; color: #666; margin-top: 4px; }
    h3 { color: #0078D4; margin-top: 24px; margin-bottom: 8px; font-size: 14px; }
    table { border-collapse: collapse; width: 100%; }
    th { background: #F0F0F0; padding: 8px 10px; text-align: left;
         font-size: 12px; border-bottom: 2px solid #ddd; }
    .footer { background: #F8F8F8; padding: 14px 30px; font-size: 11px;
              color: #888; border-top: 1px solid #ddd; margin-top: 24px; }
    .top-badge { background: #107C10; color: white; border-radius: 4px;
                 padding: 2px 8px; font-size: 11px; margin-left: 6px; }
  </style>
</head>
<body>

<div class="header">
  <h1>📊 Resumo Semanal de Performance</h1>
  <p>Semana encerrada em @{formatDateTime(utcNow(), 'dddd, dd/MM/yyyy')} |
     @{formatDateTime(utcNow(), 'MMMM/yyyy')}</p>
</div>

<div class="content">

  <!-- KPIs da semana -->
  <h3>📅 Esta semana</h3>
  <table>
    <tr>
      <td style="padding:8px 16px; background:#EFF6FF; border-radius:6px; width:25%">
        <div style="font-size:20px; font-weight:bold; color:#0078D4;">
          R$ @{formatNumber(float(first(outputs('SQL_KPIs_Semana')?['body/resultsets/Table1'])?['FaturamentoSemana']),'#,##0.00')}
        </div>
        <div style="font-size:11px; color:#666;">Faturamento da Semana</div>
      </td>
      <td style="padding:8px 16px; background:#F0FFF0; border-radius:6px; width:25%">
        <div style="font-size:20px; font-weight:bold; color:#107C10;">
          @{first(outputs('SQL_KPIs_Semana')?['body/resultsets/Table1'])?['MargemBrutaPctSemana']}%
        </div>
        <div style="font-size:11px; color:#666;">Margem Bruta</div>
      </td>
      <td style="padding:8px 16px; background:#FFF8EE; border-radius:6px; width:25%">
        <div style="font-size:20px; font-weight:bold; color:#8B5000;">
          @{first(outputs('SQL_KPIs_Semana')?['body/resultsets/Table1'])?['PedidosSemana']}
        </div>
        <div style="font-size:11px; color:#666;">Pedidos</div>
      </td>
      <td style="padding:8px 16px; background:#F5F0FF; border-radius:6px; width:25%">
        <div style="font-size:20px; font-weight:bold; color:#5B2D8E;">
          @{first(outputs('SQL_KPIs_Semana')?['body/resultsets/Table1'])?['VendedoresAtivos']}
        </div>
        <div style="font-size:11px; color:#666;">Vendedores Ativos</div>
      </td>
    </tr>
  </table>

  <!-- KPIs MTD -->
  <h3>📈 Acumulado do mês (@{formatDateTime(utcNow(), 'MMMM/yyyy')})</h3>
  <table>
    <tr>
      <td style="padding:8px 16px; background:#EFF6FF; border-radius:6px; width:33%">
        <div style="font-size:20px; font-weight:bold; color:#0078D4;">
          R$ @{formatNumber(float(first(outputs('SQL_KPIs_MTD')?['body/resultsets/Table1'])?['FaturamentoMTD']),'#,##0.00')}
        </div>
        <div style="font-size:11px; color:#666;">Faturamento MTD</div>
      </td>
      <td style="padding:8px 16px; background:#F4F4F4; border-radius:6px; width:33%">
        <div style="font-size:20px; font-weight:bold; color:#333;">
          @{first(outputs('SQL_KPIs_MTD')?['body/resultsets/Table1'])?['AtingimentoMTDPct']}%
        </div>
        <div style="font-size:11px; color:#666;">Atingimento da Meta</div>
      </td>
      <td style="padding:8px 16px; background:#F0FFF0; border-radius:6px; width:33%">
        <div style="font-size:20px; font-weight:bold; color:#107C10;">
          R$ @{formatNumber(float(first(outputs('SQL_KPIs_MTD')?['body/resultsets/Table1'])?['ProjecaoMes']),'#,##0.00')}
        </div>
        <div style="font-size:11px; color:#666;">Projeção do Mês</div>
      </td>
    </tr>
  </table>

  <!-- Top 3 da semana -->
  <h3>🏆 Destaques da Semana — Top 3</h3>
  <table>
    <thead>
      <tr>
        <th>#</th><th>Vendedor</th><th>Gerente</th>
        <th style="text-align:right">Faturamento</th><th style="text-align:right">Pedidos</th>
      </tr>
    </thead>
    <tbody>
@{body('SQL_Top3_Semana_HTML')}
    </tbody>
  </table>

  <!-- Atingimento por vendedor -->
  <h3>📋 Atingimento de Meta MTD — Todos os Vendedores</h3>
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

</div>

<div class="footer">
  Resumo gerado automaticamente às @{formatDateTime(utcNow(), 'HH:mm')} de
  @{formatDateTime(utcNow(), 'dd/MM/yyyy')} pelo Commercial Planning Control Tower.<br>
  <a href="[URL_DO_DASHBOARD]">Acesse o dashboard completo</a> para drill-down e análise detalhada.
</div>

</body>
</html>
```

---

### Ação 8 — Tratamento de erro

**Tipo:** Escopo (Scope) com `Configure run after → has failed`

```
Enviar e-mail para igor@empresa.com
Assunto: ❌ ERRO — Fluxo 2 (Resumo Semanal) — @{formatDateTime(utcNow(), 'dd/MM/yyyy')}
```

---

## Resultado esperado

E-mail recebido por todos os gerentes toda sexta às 17h com:
- 4 KPIs de destaque da semana (Faturamento, Margem, Pedidos, Vendedores Ativos)
- 3 KPIs de MTD (Faturamento acumulado, % Atingimento, Projeção do mês)
- Top 3 vendedores da semana
- Tabela completa de atingimento por vendedor com cores semafóricas

---

## Checklist de teste

- [ ] Testar as 4 queries no SSMS e confirmar que retornam dados
- [ ] Executar o fluxo manualmente às 17h de uma quinta (simular sexta)
- [ ] Confirmar renderização do HTML no Outlook Web + Desktop
- [ ] Verificar as expressões `first()` das queries de KPI único
- [ ] Confirmar que a projeção do mês faz sentido (ritmo × dias)

---

*Fluxo 2 de 5 — Commercial Planning Control Tower.*

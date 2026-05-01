# Fluxo 1 — Alerta de Baixo Atingimento
## Planejamento Comercial — Power Automate

---

## Propósito

Toda segunda-feira às 08h, o fluxo consulta o SQL Server, identifica vendedores com
atingimento de meta abaixo de 70% no mês corrente e envia um e-mail ao gerente
responsável — antes que o gestor precise abrir o Power BI.

**Problema que resolve:** gestores descobrem problemas de performance tarde demais.
Este fluxo garante visibilidade proativa logo no início da semana.

---

## Configuração do Fluxo

### Gatilho — Recorrência

```
Tipo:         Recorrência (Scheduled)
Frequência:   Semana
Intervalo:    1
Nos dias:     Segunda-feira
Às:           08:00
Fuso:         America/Sao_Paulo
```

---

## Ações — Sequência Completa

### Ação 1 — Inicializar variáveis de controle

**Tipo:** Variável — Inicializar variável

Crie 3 variáveis:

| Nome da variável    | Tipo    | Valor inicial |
|---------------------|---------|---------------|
| varMesAtual         | Integer | `@utcNow()` → use expression: `int(formatDateTime(utcNow(),'M'))` |
| varAnoAtual         | Integer | use expression: `int(formatDateTime(utcNow(),'yyyy'))` |
| strHtmlLinhas       | String  | (vazio)       |

> Por que inicializar separado? O Power Automate não permite criar variáveis
> dentro de loops. Todas precisam ser declaradas antes do primeiro loop.

---

### Ação 2 — Consultar SQL: atingimento por vendedor no mês atual

**Tipo:** SQL Server — Execute a SQL query

**Query:**

```sql
SELECT
    v.[Vendedor],
    v.[Gerente],
    COALESCE(
        ROUND(
            CAST(SUM(f.[Faturamento Total]) AS FLOAT)
            / NULLIF(SUM(m.[Valor Meta]), 0) * 100,
            1
        ),
        0
    )                                    AS AtingimentoPct,
    COALESCE( SUM(f.[Faturamento Total]), 0 ) AS FaturamentoRealizado,
    COALESCE( SUM(m.[Valor Meta]),        0 ) AS MetaMensal,
    COALESCE( SUM(m.[Valor Meta]), 0 )
        - COALESCE( SUM(f.[Faturamento Total]), 0 ) AS GapParaMeta
FROM [dw].[dVendedor] v
LEFT JOIN [dw].[fVendas] f
    ON f.[Id Vendedor] = v.[Id Vendedor]
    AND MONTH(f.[Data]) = MONTH(GETDATE())
    AND YEAR(f.[Data])  = YEAR(GETDATE())
LEFT JOIN [dw].[fMetas] m
    ON m.[Id Vendedor] = v.[Id Vendedor]
    AND m.[Mes]  = MONTH(GETDATE())
    AND m.[Ano]  = YEAR(GETDATE())
WHERE
    -- [EDITÁVEL] threshold de atingimento para disparar o alerta (ex: 70 = abaixo de 70%)
    COALESCE(
        CAST(SUM(f.[Faturamento Total]) AS FLOAT)
        / NULLIF(SUM(m.[Valor Meta]), 0) * 100,
        0
    ) < 70  -- [EDITÁVEL] ajuste o limiar conforme a régua de performance da empresa
GROUP BY
    v.[Vendedor], v.[Gerente]
ORDER BY
    AtingimentoPct ASC;
```

> A query usa LEFT JOIN para incluir vendedores sem vendas no mês (atingimento = 0%).
> **[EDITÁVEL]** O threshold `< 70` é o principal parâmetro a ajustar: defina conforme
> a régua de performance da empresa (ex: `< 80` para times com meta mais agressiva).

---

### Ação 3 — Verificar se há vendedores em alerta

**Tipo:** Condição (Control — Condition)

```
Expressão: length(outputs('Execute_a_SQL_query')?['body/resultsets/Table1']) is greater than 0
```

**Se Sim (há vendedores abaixo de 70%):** continua para Ação 4
**Se Não (todos OK):** termina o fluxo normalmente (sem enviar e-mail)

> Evita enviar e-mail vazio. Boa prática: só disparar quando há algo acionável.

---

### Ação 4 — Construir linhas HTML da tabela (loop)

**Tipo:** Controle — Aplicar a cada um (Apply to each)

**Entrada:** `outputs('Execute_a_SQL_query')?['body/resultsets/Table1']`

**Dentro do loop — Ação 4.1: Determinar cor do semáforo**

**Tipo:** Condição aninhada

```
Se AtingimentoPct >= 90  → corSemaforo = "#FFC300"  (amarelo — quase lá)
Se AtingimentoPct < 90   → corSemaforo = "#D83B01"  (vermelho — crítico)
```

Expression da condição:
```
float(items('Apply_to_each')?['AtingimentoPct']) is greater than or equal to 90
```

**Dentro do loop — Ação 4.2: Concatenar linha HTML**

**Tipo:** Variável — Acrescentar à variável de string (Append to string variable)

**Variável:** `strHtmlLinhas`

**Valor:**

```html
<tr>
  <td style="padding:8px; border-bottom:1px solid #eee;">@{items('Apply_to_each')?['Vendedor']}</td>
  <td style="padding:8px; border-bottom:1px solid #eee;">@{items('Apply_to_each')?['Gerente']}</td>
  <td style="padding:8px; border-bottom:1px solid #eee; color:@{variables('corSemaforo')}; font-weight:bold;">
    @{items('Apply_to_each')?['AtingimentoPct']}%
  </td>
  <td style="padding:8px; border-bottom:1px solid #eee;">
    R$ @{formatNumber(float(items('Apply_to_each')?['FaturamentoRealizado']),'#,##0.00')}
  </td>
  <td style="padding:8px; border-bottom:1px solid #eee;">
    R$ @{formatNumber(float(items('Apply_to_each')?['MetaMensal']),'#,##0.00')}
  </td>
  <td style="padding:8px; border-bottom:1px solid #eee; color:#D83B01; font-weight:bold;">
    R$ @{formatNumber(float(items('Apply_to_each')?['GapParaMeta']),'#,##0.00')}
  </td>
</tr>
```

---

### Ação 5 — Montar e-mail HTML completo

**Tipo:** Variável — Definir variável (Set variable)

**Variável:** `strEmailHtml`

**Valor (HTML completo):**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; color: #333; margin: 0; padding: 0; }
    .header { background-color: #0078D4; color: white; padding: 20px 30px; }
    .header h1 { margin: 0; font-size: 18px; }
    .header p  { margin: 4px 0 0; font-size: 13px; opacity: 0.85; }
    .content { padding: 24px 30px; }
    .alerta-box { background: #FFF3CD; border-left: 4px solid #FFC107;
                  padding: 12px 16px; margin-bottom: 20px; border-radius: 4px; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th { background: #F4F4F4; padding: 10px 8px; text-align: left;
         font-size: 12px; color: #555; border-bottom: 2px solid #ddd; }
    .footer { background: #F8F8F8; padding: 16px 30px; font-size: 11px; color: #888;
              border-top: 1px solid #ddd; margin-top: 24px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>⚠️ Alerta de Baixo Atingimento de Meta</h1>
    <p>Planejamento Comercial — @{formatDateTime(utcNow(), 'MMMM yyyy')}</p>
  </div>
  <div class="content">
    <div class="alerta-box">
      Os vendedores abaixo estão com atingimento inferior a <strong>70%</strong> da meta
      no mês de <strong>@{formatDateTime(utcNow(), 'MMMM/yyyy')}</strong>.
      Ação gerencial recomendada.
    </div>
    <table>
      <thead>
        <tr>
          <th>Vendedor</th>
          <th>Gerente</th>
          <th>Atingimento</th>
          <th>Realizado</th>
          <th>Meta</th>
          <th>Gap</th>
        </tr>
      </thead>
      <tbody>
        @{variables('strHtmlLinhas')}
      </tbody>
    </table>
  </div>
  <div class="footer">
    Este alerta foi gerado automaticamente pelo Planejamento Comercial.<br>
    Acesse o <a href="[URL_DO_DASHBOARD]">dashboard completo</a> para mais detalhes.<br>
    Para cancelar estes alertas, contate o administrador.
  </div>
</body>
</html>
```

> [REUTILIZAÇÃO]: Substitua `[URL_DO_DASHBOARD]` pela URL do relatório publicado
> no Power BI Service.

---

### Ação 6 — Enviar e-mail ao gerente

**Tipo:** Office 365 Outlook — Enviar um email (V2)

```
Para:      [e-mail dos gerentes — use ponto e vírgula para múltiplos]
           Exemplo: guardiola@empresa.com; marta@empresa.com; zagallo@empresa.com
CC:        [e-mail da diretoria / Igor]
Assunto:   ⚠️ Alerta: Vendedores abaixo de 70% da meta — @{formatDateTime(utcNow(), 'MMMM/yyyy')}
Corpo:     @{variables('strEmailHtml')}
É HTML:    Sim
```

> [REUTILIZAÇÃO]: Substitua os e-mails pelos reais do projeto.
> Para envio segmentado por gerente (cada gerente recebe só seu time),
> ver variação avançada no final deste arquivo.

---

### Ação 7 — Tratamento de erro (Scope de fallback)

**Tipo:** Controle — Escopo (Scope)

**Configuração:** `Configure run after` → marque **has failed** e **has timed out**

**Dentro do escopo:**

**Tipo:** Office 365 Outlook — Enviar um email

```
Para:      igor@empresa.com
Assunto:   ❌ ERRO — Fluxo 1 (Alerta Baixo Atingimento) — @{formatDateTime(utcNow(), 'dd/MM/yyyy')}
Corpo:
  <p>O fluxo <strong>Alerta de Baixo Atingimento</strong> falhou em
  @{formatDateTime(utcNow(), 'dd/MM/yyyy HH:mm')}.</p>
  <p><strong>Etapa com erro:</strong> verificar o histórico de execução no Power Automate.</p>
  <p>Acesse: Power Automate → Meus fluxos → Fluxo 1 → Histórico de execuções</p>
```

---

## Variação Avançada — E-mail Segmentado por Gerente

Se quiser que cada gerente receba apenas os dados do próprio time (compatível com RLS):

**Após a Ação 2**, adicione um **Filter Array** para cada gerente:

```
Filter Array — Time Guardiola
  Entrada: outputs da query SQL
  Condição: items()?['Gerente'] is equal to 'Guardiola'
  → Envie e-mail apenas para guardiola@empresa.com com este array filtrado
```

Repita para Marta e Zagallo. Cada gerente só recebe os alertas do seu time.

---

## Resultado esperado

E-mail recebido pelo gerente toda segunda-feira com:

```
Assunto: ⚠️ Alerta: Vendedores abaixo de 70% da meta — Janeiro/2021

Tabela:
  Vendedor    Gerente     Atingimento   Realizado        Meta          Gap
  Rodrigo     Guardiola   52,3%         R$ 26.150,00     R$ 50.000,00  R$ 23.850,00
  Marilia     Marta       61,8%         R$ 30.900,00     R$ 50.000,00  R$ 19.100,00
```

---

## Checklist de teste

- [ ] Executar manualmente pelo botão "Testar" no Power Automate
- [ ] Confirmar que a query retorna registros (verificar no SSMS primeiro)
- [ ] Verificar se o e-mail HTML renderiza corretamente no Outlook
- [ ] Confirmar que o fluxo termina sem erro quando todos estão acima de 70%
- [ ] Testar o bloco de erro (desabilitar temporariamente a conexão SQL)

---

*Fluxo 1 de 5 — Planejamento Comercial.*

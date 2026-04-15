# Fluxo 5 — Atualização Automática do Dataset
## Commercial Planning Control Tower — Power Automate

---

## Propósito

Todo domingo à noite (às 06h de segunda, antes do expediente), o fluxo dispara
o refresh do dataset do Power BI e, após a conclusão, envia um e-mail de confirmação
— garantindo que o dashboard e os alertas dos Fluxos 1–4 sempre trabalham com
os dados mais recentes, sem intervenção manual.

**Problema que resolve:** dataset desatualizado gera alertas errados e dashboards
que não refletem a realidade. Este fluxo é o "lastro" de confiabilidade de todo o
Control Tower.

> **Nota sobre arquitetura:** o pipeline Python (ETL) é executado antes do refresh
> do Power BI. Neste projeto, o pipeline roda localmente na máquina do Igor.
> Para automação completa, o ideal é hospedá-lo em Azure Function, Azure Automation
> ou Task Scheduler do Windows Server. Esta documentação cobre as duas abordagens.

---

## Configuração do Fluxo

### Gatilho — Recorrência

```
Tipo:         Recorrência (Scheduled)
Frequência:   Semana
Intervalo:    1
Nos dias:     Segunda-feira
Às:           06:00
Fuso:         America/Sao_Paulo
```

> Executar às 06h garante que o refresh esteja concluído antes das 08h,
> quando o Fluxo 1 (Alerta de Baixo Atingimento) é executado.
> A ordem importa: Fluxo 5 às 06h → Fluxo 1 às 08h.

---

## Arquitetura do Fluxo — Dois cenários

### Cenário A — Pipeline hospedado no Azure (recomendado para produção)

```
[Power Automate] → HTTP POST → [Azure Function]
                                     ↓
                              Executa ETL Python
                              (extract → transform → load)
                                     ↓
                              Retorna { "status": "success", "linhas": N }
                                     ↓
[Power Automate] → Power BI API → Dispara refresh do dataset
                                     ↓
                              Aguarda conclusão
                                     ↓
[Power Automate] → Enviar e-mail de confirmação
```

### Cenário B — Pipeline executado localmente via Windows Task Scheduler

```
[Windows Task Scheduler] → Executa ETL Python (06h00)
                                     ↓
                              Escreve status em arquivo de log

[Power Automate] → Aguarda 30 min (recorrência paralela)
                                     ↓
[Power Automate] → Power BI API → Dispara refresh do dataset
                                     ↓
[Power Automate] → Enviar e-mail de confirmação
```

> [REUTILIZAÇÃO]: Para projetos em Azure, use o Cenário A.
> Para projetos locais ou em SQL Server on-premises, use o Cenário B.
> Este guia documenta o Cenário B (local) por ser o contexto atual do projeto.

---

## Ações — Cenário B (Pipeline Local + Power Automate para Refresh)

### Ação 1 — Aguardar até que o ETL tenha executado

**Tipo:** Controle — Atraso (Delay)

```
Duração: 30 minutos
```

> O ETL Python leva ~2–5 minutos para rodar. Os 30 minutos garantem folga.
> Se o ETL for mais pesado, ajuste para 45–60 minutos.

---

### Ação 2 — Disparar refresh do dataset no Power BI

**Tipo:** Power BI — Atualizar um conjunto de dados (Refresh a dataset)

```
Workspace:   [Nome do workspace — ex: "Planejamento Comercial"]
Dataset:     [Nome do dataset — ex: "Commercial Planning Control Tower"]
```

> Este step envia o comando de refresh. O Power BI executa em background.
> O step seguinte monitora a conclusão.

---

### Ação 3 — Aguardar conclusão do refresh (loop de monitoramento)

**Tipo:** Controle — Fazer Até (Do Until)

**Condição de saída:**
```
Status do refresh <> "Unknown"  (ou seja, saiu do estado "processando")
```

**Dentro do loop:**

**3.1 — Verificar status do refresh**

**Tipo:** HTTP (Premium)

```
Método:  GET
URI:     https://api.powerbi.com/v1.0/myorg/groups/{groupId}/datasets/{datasetId}/refreshes?$top=1
Headers: Authorization: Bearer @{outputs('Get_Power_BI_Token')?['body/access_token']}
```

> Esta chamada consulta a API REST do Power BI para verificar o status do
> último refresh. `groupId` = ID do workspace; `datasetId` = ID do dataset.
> Ambos podem ser obtidos na URL do Power BI Service.

**3.2 — Extrair status**

**Tipo:** Parse JSON (com schema do response da API)

```json
{
  "type": "object",
  "properties": {
    "value": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "status": { "type": "string" },
          "endTime": { "type": "string" },
          "startTime": { "type": "string" }
        }
      }
    }
  }
}
```

**3.3 — Atraso entre verificações**

**Tipo:** Atraso (Delay)

```
Duração: 2 minutos
```

**Configuração do Do Until:**
```
Máximo de iterações: 30   (60 minutos total)
Timeout:             PT1H  (1 hora)
```

---

### Ação 4 — Verificar se o refresh foi bem-sucedido

**Tipo:** Condição

```
Status == "Completed"   → Ação 5A (sucesso)
Status == "Failed"      → Ação 5B (falha)
```

---

### Ação 5A — E-mail de sucesso

**Tipo:** Office 365 Outlook — Enviar um email (V2)

**Para:** igor@empresa.com (responsável técnico)

**Assunto:**
```
✅ Refresh Concluído — Commercial Planning Control Tower | @{formatDateTime(utcNow(), 'dd/MM/yyyy')}
```

**Corpo (HTML):**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; color: #333; }
    .header { background: #107C10; color: white; padding: 18px 24px; }
    .header h1 { margin: 0; font-size: 16px; }
    .content { padding: 20px 24px; }
    .ok-box { background: #E8F5E9; border-left: 4px solid #107C10;
              padding: 14px 18px; border-radius: 4px; margin-bottom: 16px; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    td { padding: 8px 10px; border-bottom: 1px solid #eee; }
    .footer { padding: 12px 24px; font-size: 11px; color: #888; }
  </style>
</head>
<body>

<div class="header">
  <h1>✅ Refresh do Dataset Concluído com Sucesso</h1>
</div>

<div class="content">
  <div class="ok-box">
    O dataset <strong>Commercial Planning Control Tower</strong> foi atualizado com sucesso.
    O dashboard e os alertas automáticos estão com os dados mais recentes.
  </div>

  <table>
    <tr><td><strong>Data / Hora</strong></td>
        <td>@{formatDateTime(utcNow(), 'dd/MM/yyyy HH:mm')}</td></tr>
    <tr><td><strong>Status</strong></td>
        <td style="color:#107C10; font-weight:bold;">Completed</td></tr>
    <tr><td><strong>Próximo refresh</strong></td>
        <td>@{formatDateTime(addDays(utcNow(), 7), 'dd/MM/yyyy')} às 06:00</td></tr>
    <tr><td><strong>Fluxo 1 (Alertas)</strong></td>
        <td>Executa às 08:00 com os dados atualizados</td></tr>
  </table>
</div>

<div class="footer">
  Commercial Planning Control Tower — Notificação automática
</div>
</body>
</html>
```

---

### Ação 5B — E-mail de falha

**Tipo:** Office 365 Outlook — Enviar um email (V2)

**Para:** igor@empresa.com

**Assunto:**
```
❌ FALHA no Refresh — Commercial Planning Control Tower | @{formatDateTime(utcNow(), 'dd/MM/yyyy')}
```

**Corpo (HTML):**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; color: #333; }
    .header { background: #D83B01; color: white; padding: 18px 24px; }
    .content { padding: 20px 24px; }
    .erro-box { background: #FDECEA; border-left: 4px solid #D83B01;
                padding: 14px 18px; border-radius: 4px; }
    .steps { background: #F8F8F8; padding: 14px 18px; margin-top: 16px;
             border-radius: 4px; }
    ol { margin: 8px 0; padding-left: 18px; }
  </style>
</head>
<body>

<div class="header">
  <h1>❌ Falha no Refresh do Dataset</h1>
</div>

<div class="content">
  <div class="erro-box">
    O refresh do dataset <strong>Commercial Planning Control Tower</strong>
    falhou em @{formatDateTime(utcNow(), 'dd/MM/yyyy HH:mm')}.
    Os alertas automáticos desta semana podem ter dados desatualizados.
  </div>

  <div class="steps">
    <strong>Diagnóstico sugerido:</strong>
    <ol>
      <li>Verificar se o pipeline Python foi executado com sucesso
          (logs em <code>logs/etl.log</code>)</li>
      <li>Verificar conectividade do Power BI Service com o SQL Server
          (gateway on-premises, se configurado)</li>
      <li>Acessar Power BI Service → Workspace → Dataset → Histórico de refresh</li>
      <li>Executar refresh manual e verificar a mensagem de erro detalhada</li>
    </ol>
  </div>

  <p style="margin-top:16px">
    <strong>Status retornado pela API:</strong>
    @{body('Parse_JSON_Refresh_Status')?['value'][0]['status']}
  </p>
</div>

</body>
</html>
```

---

### Ação 6 — Tratamento de erro (Scope de fallback)

Scope com `Configure run after → has failed` para capturar erros de configuração
do próprio fluxo (ex: token expirado, conector indisponível):

```
E-mail para: igor@empresa.com
Assunto: ❌ ERRO CRÍTICO — Fluxo 5 (Refresh) parou de funcionar
Corpo: incluir o resultado da ação com erro para diagnóstico
```

---

## Configuração do Windows Task Scheduler (ETL local)

Para que o ETL Python rode automaticamente toda segunda às 05h30
(antes do Power Automate disparar o refresh às 06h):

**Criar tarefa agendada no Windows:**

```bat
:: Salvar como: run_etl_comercial.bat
@echo off
cd /d "C:\Users\letra\Desktop\Planejamento Comercial"
call venv\Scripts\activate.bat
python -m src.etl.pipeline >> logs\etl_agendado.log 2>&1
deactivate
```

**No Windows Task Scheduler:**
```
Nome:          ETL - Planejamento Comercial
Gatilho:       Semanal, toda Segunda-feira, às 05:30
Ação:          Iniciar programa → run_etl_comercial.bat
Executar como: NOTEIGOR\letra (usuário atual)
```

> [REUTILIZAÇÃO]: Para ambiente de servidor (on-premises ou VM Azure),
> use o mesmo script .bat com caminhos absolutos e o Task Scheduler do Windows Server.

---

## Obter IDs do Power BI para a API REST

Para as chamadas HTTP à API do Power BI, você precisa do `groupId` (workspace)
e `datasetId`. Para obtê-los:

1. Acesse o Power BI Service → seu workspace
2. Abra o dataset → URL do browser terá o formato:
   ```
   https://app.powerbi.com/groups/{groupId}/datasets/{datasetId}/...
   ```
3. Copie os dois GUIDs e use nas chamadas HTTP do Fluxo 5.

---

## Resultado esperado

Toda segunda-feira, antes das 08h:
- ETL Python roda às 05h30 (Task Scheduler): dados atualizados no SQL Server
- Power Automate aguarda 30 min e dispara refresh do dataset às 06h
- E-mail de confirmação chega ao Igor ~20–40 min depois:

```
Assunto: ✅ Refresh Concluído — Commercial Planning Control Tower | 13/01/2025

"O dataset foi atualizado com sucesso.
O dashboard e os alertas automáticos estão com os dados mais recentes.
Próximo refresh: 20/01/2025 às 06:00"
```

---

## Checklist de teste

- [ ] Task Scheduler criado e testado manualmente (rodar o .bat)
- [ ] Confirmar que o log `logs/etl_agendado.log` é gerado corretamente
- [ ] Dataset publicado no Power BI Service
- [ ] IDs de groupId e datasetId coletados da URL do Power BI
- [ ] Conexão HTTP autenticada corretamente (token de serviço)
- [ ] Testar refresh manual via Power Automate
- [ ] Confirmar recebimento do e-mail de sucesso
- [ ] Simular falha (desligar o SQL Server) e confirmar e-mail de erro
- [ ] Confirmar que o Fluxo 1 (08h) usa dados atualizados pelo Fluxo 5 (06h)

---

*Fluxo 5 de 5 — Commercial Planning Control Tower.*

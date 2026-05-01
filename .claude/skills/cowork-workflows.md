---
name: cowork-workflows
description: >
  Especialista em automação de tarefas e criação de workflows com Claude Cowork e Claude
  Desktop. Cobre automação de arquivos locais, criação de rotinas de análise recorrente,
  integração com desktop, agendamento de tarefas, workflows para não-desenvolvedores e
  padrões de uso do Claude Code em modo agente autônomo.
  Use sempre que o usuário mencionar Claude Cowork, automação de arquivo local, workflow
  recorrente, tarefa agendada sem terminal, rotina automática, workflow para não-dev,
  processamento em batch de arquivos locais, ou qualquer tarefa de automação via Claude
  em ambiente desktop.
  Trigger para: "automação no Cowork", "cria workflow no Cowork", "agenda essa análise",
  "workflow para não-dev", "automatiza esse processo no desktop", "processa esses arquivos".
---

# Cowork Workflows — Automação com Claude Cowork e Desktop

## Identidade

Especialista em automação de produtividade com Claude. Projeta workflows que qualquer
pessoa pode executar no desktop sem abrir terminal — transformando tarefas manuais
recorrentes em rotinas automáticas confiáveis.

---

## Quando Usar

Use esta skill para automação de tarefas de arquivo, análise recorrente e workflows
desktop via Claude Cowork. Para automação corporativa com Power Platform, use
`automacoes-power-platform`. Para pipelines de dados em produção, use `etl-data-lake`.

---

## 1. Padrões de Workflow no Cowork

### Workflow de Análise Mensal Recorrente

```
Trigger: Novo arquivo Excel chega na pasta "Relatórios/Entrada"

Passo 1 — Leitura e validação
  Claude lê o arquivo, verifica se as abas esperadas existem,
  valida se as colunas estão no formato correto.

Passo 2 — Processamento
  Claude executa análise conforme template definido:
  - consolida dados de múltiplas abas
  - calcula KPIs definidos no template de análise
  - identifica desvios e outliers

Passo 3 — Output
  Claude salva:
  - /Relatórios/Saída/analise_YYYYMM.xlsx (com formatação)
  - /Relatórios/Saída/sumario_executivo_YYYYMM.md
  - /Relatórios/Log/log_YYYYMMDD_HHMMSS.txt

Passo 4 — Notificação (opcional)
  Claude envia e-mail via Power Automate ou Teams com o sumário.
```

---

## 2. Template de CLAUDE.md para Workflow Cowork

```markdown
# CLAUDE.md — Workflow: Análise Mensal de Vendas

## Objetivo
Processar o relatório mensal de vendas e gerar análise executiva automaticamente.

## Gatilho
Quando o usuário pedir "processa o relatório de [mês]" ou quando um arquivo
.xlsx aparecer na pasta /Relatórios/Entrada/.

## Input esperado
- Arquivo Excel em /Relatórios/Entrada/ com abas: "Vendas", "Metas", "Carteira"
- Mês de referência no nome do arquivo: vendas_YYYYMM.xlsx

## O que fazer (passo a passo)
1. Ler o arquivo Excel e validar estrutura (abas e colunas)
2. Calcular: receita total, meta, atingimento%, gap, top 5 vendedores
3. Identificar 3 desvios mais relevantes com hipótese
4. Gerar sumário executivo em markdown (máx 300 palavras)
5. Salvar Excel formatado em /Relatórios/Saída/
6. Salvar sumário em /Relatórios/Saída/
7. Registrar log em /Relatórios/Log/

## Formato do sumário (usar sempre este template)
### Resultado de [Mês/Ano]
**Receita:** R$ X,XX | **Meta:** R$ X,XX | **Atingimento:** X%
**Top vendedor:** [Nome] — R$ X,XX
**Desvio principal:** [Descrição em 1 frase]
**Ação recomendada:** [1 ação concreta]

## Regras
- Nunca sobrescrever arquivos já existentes na pasta Saída
- Se colunas esperadas estiverem ausentes, parar e notificar o usuário
- Usar separador decimal vírgula e milhar ponto nos valores BRL
```

---

## 3. Workflows de Arquivo em Python (para Claude Code)

```python
from pathlib import Path
import pandas as pd
import shutil
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


def workflow_processar_pasta(pasta_entrada: str,
                              pasta_saida: str,
                              pasta_processados: str,
                              extensoes: list = ['.xlsx', '.csv']) -> dict:
    """
    Processa todos os arquivos de uma pasta e move para /processados.
    Padrão Cowork: entrada → processamento → saída + arquivo movido.
    """
    pasta_in  = Path(pasta_entrada)
    pasta_out = Path(pasta_saida)
    pasta_prc = Path(pasta_processados)

    for pasta in [pasta_out, pasta_prc]:
        pasta.mkdir(parents=True, exist_ok=True)

    arquivos = [f for f in pasta_in.iterdir()
                if f.is_file() and f.suffix.lower() in extensoes]

    resumo = {'processados': 0, 'erros': 0, 'arquivos': []}

    for arquivo in arquivos:
        try:
            logger.info(f"Processando: {arquivo.name}")

            # Lê o arquivo
            if arquivo.suffix == '.xlsx':
                df = pd.read_excel(arquivo, engine='openpyxl')
            else:
                df = pd.read_csv(arquivo, sep=';', encoding='utf-8-sig')

            # ── Coloque aqui a lógica de processamento ────────────
            df_processado = processar_dados(df)  # sua função de negócio
            # ──────────────────────────────────────────────────────

            # Salva output
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_saida = pasta_out / f"{arquivo.stem}_processado_{timestamp}.xlsx"
            df_processado.to_excel(nome_saida, index=False)

            # Move original para /processados
            shutil.move(str(arquivo), pasta_prc / arquivo.name)

            resumo['processados'] += 1
            resumo['arquivos'].append({'arquivo': arquivo.name, 'status': 'OK'})
            logger.info(f"✅ {arquivo.name} → {nome_saida.name}")

        except Exception as e:
            logger.error(f"❌ {arquivo.name}: {e}")
            resumo['erros'] += 1
            resumo['arquivos'].append({'arquivo': arquivo.name, 'status': f'ERRO: {e}'})

    logger.info(f"Concluído: {resumo['processados']} OK | {resumo['erros']} erros")
    return resumo


def processar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """Substitua esta função pela lógica de negócio do workflow."""
    # Exemplo: limpa, calcula e formata
    df = df.copy()
    df['_processado_em'] = datetime.now()
    return df


def monitorar_pasta(pasta: str, callback, intervalo_seg: int = 60):
    """
    Monitora pasta por novos arquivos e chama callback quando detectar.
    Use com Task Scheduler (Windows) ou cron (Linux/Mac).
    """
    import time
    pasta_path = Path(pasta)
    processados = set()

    logger.info(f"Monitorando: {pasta} (a cada {intervalo_seg}s)")
    while True:
        novos = {f for f in pasta_path.iterdir() if f.is_file()} - processados
        for arquivo in novos:
            logger.info(f"Novo arquivo detectado: {arquivo.name}")
            callback(arquivo)
            processados.add(arquivo)
        time.sleep(intervalo_seg)
```

---

## 4. Agendamento com Task Scheduler (Windows)

```powershell
# Criar tarefa agendada para rodar workflow diariamente às 08:00
$action = New-ScheduledTaskAction `
    -Execute "python.exe" `
    -Argument "C:\workflows\analise_diaria.py" `
    -WorkingDirectory "C:\workflows"

$trigger = New-ScheduledTaskTrigger -Daily -At "08:00"

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 5)

Register-ScheduledTask `
    -TaskName "AnaliseVendasDiaria" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Highest
```

---

## 5. Estrutura de Pastas Recomendada para Workflows Cowork

```
C:\Workflows\
├── analise_vendas\
│   ├── CLAUDE.md          ← instrução do workflow
│   ├── entrada\           ← arquivos chegam aqui
│   ├── saida\             ← outputs gerados
│   ├── processados\       ← arquivos já tratados
│   ├── log\               ← logs de execução
│   └── workflow.py        ← código do workflow
├── relatorio_financeiro\
│   └── (mesma estrutura)
└── conciliacao_bancaria\
    └── (mesma estrutura)
```

---

## Regras de Qualidade

- Todo workflow deve ter um CLAUDE.md claro com gatilho, passos e formato de output
- Nunca sobrescrever arquivos de saída — sempre usar timestamp no nome
- Mover arquivos processados para subpasta separada — nunca apagar
- Registrar log de cada execução com timestamp, arquivos processados e erros
- Workflows para não-dev: linguagem simples no CLAUDE.md, sem jargão técnico
- Testar o workflow com arquivo sintético antes de apontar para pasta de produção

## Observações

Para automação corporativa com aprovação e formulários, use `automacoes-power-platform`.
Para pipelines de dados com múltiplas fontes e camadas, use `etl-data-lake`.

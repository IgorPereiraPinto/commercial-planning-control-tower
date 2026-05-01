---
name: glue-etl-advanced
description: >
  Especialista avançado em AWS Glue para ETL em produção. Cobre Glue Studio visual,
  Glue Data Quality (regras nativas DQDL), Glue DataBrew para transformação no-code,
  job bookmarks para carga incremental, DynamicFrame vs DataFrame, pushdown predicates,
  otimização de DPU e custo, Glue Workflows para orquestração, e integração com S3,
  Athena e Redshift. Complementa aws-data-stack com profundidade em Glue.
  Use sempre que o usuário mencionar Glue com bookmark, DynamicFrame, Glue DataBrew,
  Glue Data Quality, Glue Workflow, pushdown predicate, DPU, Glue Studio, ou qualquer
  funcionalidade avançada do AWS Glue além do básico.
  Trigger para: "Glue com bookmark", "DynamicFrame", "Glue DataBrew", "Glue Data Quality",
  "Glue Workflow", "pushdown predicate", "otimiza DPU", "Glue Studio visual", "DQDL".
---

# AWS Glue — ETL Avançado em Produção

## Identidade

Engenheiro de Dados especializado em AWS Glue. Constrói jobs robustos, econômicos e
rastreáveis. Sabe quando usar DynamicFrame (schema flexível) vs DataFrame (transformações
pesadas) e como evitar os armadilhas de custo e performance do Glue em produção.

---

## 1. Job Bookmarks — Carga Incremental

```python
# glue_job_incremental_com_bookmark.py
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'source_path', 'target_path'])
sc   = SparkContext()
glue = GlueContext(sc)
spark = glue.spark_session
job  = Job(glue)
job.init(args['JOB_NAME'], args)  # bookmark ativado via console/CloudFormation

# ── Com bookmark: lê apenas arquivos novos desde a última execução ──
dyf = glue.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={
        "paths": [args['source_path']],
        "recurse": True,
        "useS3ListImplementation": True,
    },
    format="parquet",
    transformation_ctx="dyf_source"  # ctx = chave do bookmark
)

if dyf.count() == 0:
    print("[BOOKMARK] Nenhum dado novo desde a última execução. Job concluído.")
    job.commit()
    import sys; sys.exit(0)

print(f"[BOOKMARK] {dyf.count():,} novos registros carregados")

# Transformações
df = dyf.toDF()
df_silver = (df
    .filter(F.col("status").isin(["ATIVO", "PROCESSADO"]))
    .withColumn("_etl_job",    F.lit(args['JOB_NAME']))
    .withColumn("_etl_ts",     F.current_timestamp())
    .dropDuplicates(["id_registro"])
)

# Escrita na Silver
glue.write_dynamic_frame.from_options(
    frame=DynamicFrame.fromDF(df_silver, glue, "output"),
    connection_type="s3",
    connection_options={"path": args['target_path'], "partitionKeys": ["ano", "mes"]},
    format="glueparquet",
    transformation_ctx="output_sink"
)

job.commit()  # confirma bookmark
```

---

## 2. Glue Data Quality — DQDL

```python
# Definição de regras DQDL (Glue Data Quality Definition Language)
# Pode ser aplicado via Glue Studio ou via API

REGRAS_DQDL = """
Rules = [
    # Completude
    IsComplete "id_venda",
    IsComplete "valor_liquido",
    IsComplete "data_venda",

    # Unicidade
    IsUnique "id_venda",

    # Domínio de valores
    ColumnValues "status" in ["APROVADO", "PENDENTE", "CANCELADO"],
    ColumnValues "valor_liquido" > 0,

    # Frescor dos dados
    DataFreshness "data_venda" <= 1,

    # Distribuição estatística
    ColumnStatistics "valor_liquido" between 10 and 1000000,

    # Referencial
    ReferentialIntegrity "id_cliente" "dim_clientes.id_cliente"
]
"""

# Aplicar no job Glue via transform
def aplicar_dq_glue(dyf, glue_context, regras_dqdl: str,
                     action: str = "QUARANTINE"):
    """
    action: 'FAIL'       → job falha se regra crítica não passa
            'QUARANTINE' → registros ruins vão para caminho separado
            'LOG'        → só registra, não bloqueia
    """
    from awsglue.transforms import EvaluateDataQuality

    result = EvaluateDataQuality.apply(
        frame=dyf,
        ruleset=regras_dqdl,
        publishing_options={
            "dataQualityEvaluationContext": "dq_vendas",
            "enableDataQualityResultsPublishing": True,
        },
        additional_options={"observations.scope": "ALL"}
    )

    dq_results = result.select_fields(["Rule", "Outcome", "FailureReason"])
    falhas = dq_results.filter(lambda r: r["Outcome"] == "Failed")

    if falhas.count() > 0:
        print(f"[DQ] {falhas.count()} regras falharam:")
        falhas.toDF().show(truncate=False)
        if action == "FAIL":
            raise ValueError("❌ Data Quality crítico falhou. Job abortado.")

    return result
```

---

## 3. DynamicFrame vs DataFrame — Quando Usar Cada Um

```python
# DynamicFrame: ideal para dados com schema variável ou inconsistente
# DataFrame: ideal para transformações pesadas e SQL complexo

# Converter para DataFrame quando:
# - Precisar de window functions
# - Precisar de joins complexos
# - Usar SQL via SparkSQL
# - Precisar de groupBy/agg pesado

df = dyf.toDF()  # DynamicFrame → DataFrame

# Pushdown predicate: SEMPRE usar para filtrar antes de ler
# Reduz custo e tempo de leitura — essencial em tabelas particionadas
dyf_filtrado = glue.create_dynamic_frame.from_catalog(
    database="meu_banco",
    table_name="vendas",
    push_down_predicate="(ano == '2024' and mes == '12')",  # filtra partição no S3
    transformation_ctx="vendas_src"
)

# Converter de volta para DynamicFrame quando:
# - Escrever via sink do Glue
# - Usar transforms nativos do Glue (ResolveChoice, DropNullFields)
dyf_final = DynamicFrame.fromDF(df, glue_context, "final")
```

---

## 4. Otimização de DPU e Custo

```python
# Configurações de job para produção (CloudFormation / Terraform)

CONFIGURACOES_JOB = {
    "tiny_job": {           # < 1M registros, transformações simples
        "WorkerType": "G.025X",   # 0.25 DPU por worker
        "NumberOfWorkers": 2,
        "GlueVersion": "4.0",
    },
    "standard_job": {       # 1M-100M registros
        "WorkerType": "G.1X",     # 1 DPU por worker
        "NumberOfWorkers": 5,
        "GlueVersion": "4.0",
    },
    "heavy_job": {          # 100M+ registros ou joins complexos
        "WorkerType": "G.2X",     # 2 DPU por worker
        "NumberOfWorkers": 10,
        "GlueVersion": "4.0",
    },
    "memory_optimized": {   # Joins de tabelas muito grandes
        "WorkerType": "G.8X",
        "NumberOfWorkers": 5,
        "GlueVersion": "4.0",
    }
}

# Dicas de custo:
# - G.025X custa 4x menos que G.1X — usar sempre que possível
# - Auto Scaling: min_workers + max_workers para jobs variáveis
# - Job timeout: sempre definir (padrão 2880 min = 48h = $$$$)
# - Prefer Parquet+Snappy sobre CSV: 5-10x mais rápido no Glue

# Configuração de timeout e retry (via boto3)
import boto3
glue_client = boto3.client('glue')

glue_client.update_job(
    JobName='meu_job',
    JobUpdate={
        'Timeout': 60,        # 60 minutos — não deixar aberto
        'MaxRetries': 1,
        'ExecutionProperty': {'MaxConcurrentRuns': 1},
    }
)
```

---

## 5. Glue Workflow — Orquestração

```python
import boto3

glue = boto3.client('glue')

def criar_workflow_etl(nome: str) -> None:
    """Cria workflow: Crawler → Bronze Job → Silver Job → DQ Check."""

    # 1. Workflow container
    glue.create_workflow(Name=nome)

    # 2. Trigger inicial (agendado às 06:00 UTC)
    glue.create_trigger(
        Name=f"{nome}-inicio",
        WorkflowName=nome,
        Type='SCHEDULED',
        Schedule='cron(0 6 * * ? *)',
        Actions=[{'CrawlerName': f"{nome}-crawler-bronze"}],
        StartOnCreation=True,
    )

    # 3. Trigger: crawler concluiu → roda job Bronze→Silver
    glue.create_trigger(
        Name=f"{nome}-apos-crawler",
        WorkflowName=nome,
        Type='CONDITIONAL',
        Predicate={
            'Conditions': [{'CrawlerName': f"{nome}-crawler-bronze",
                             'CrawlState': 'SUCCEEDED'}]
        },
        Actions=[{'JobName': f"{nome}-bronze-to-silver"}],
    )

    # 4. Trigger: Silver concluiu → roda job Silver→Gold
    glue.create_trigger(
        Name=f"{nome}-apos-silver",
        WorkflowName=nome,
        Type='CONDITIONAL',
        Predicate={
            'Conditions': [{'JobName': f"{nome}-bronze-to-silver",
                             'State': 'SUCCEEDED'}]
        },
        Actions=[{'JobName': f"{nome}-silver-to-gold"}],
    )

    print(f"✅ Workflow '{nome}' criado com 3 etapas")
```

---

## Regras de Qualidade

- **Sempre** definir `timeout` no job — o padrão de 48h pode custar caro
- **Sempre** usar `push_down_predicate` em tabelas particionadas
- **Bookmark** deve ser ativado no console OU via `--job-bookmark-option=job-bookmark-enable`
- G.025X para jobs pequenos — economiza ~75% vs G.1X
- `transformation_ctx` é obrigatório para bookmark funcionar corretamente por etapa
- Prefira Parquet sobre JSON/CSV para inputs — 5-10x mais eficiente no Glue
- Glue Data Quality: usar QUARANTINE, não FAIL em primeira implantação

## Observações

Esta skill é extensão aprofundada de `aws-data-stack`.
Para orquestração mais complexa com dependências externas, considere Step Functions.

"""
Template: Pipeline ETL — Extração, Transformação e Carga
Adaptar: conexões, lógica de transformação e destino
Padrão: Bronze (raw) → Silver (limpo) → Gold (negócio)
"""

import os
import logging
from datetime import datetime, date
from typing import Optional
import pandas as pd

# ---------------------------------------------------------------------------
# Configuração de logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuração: use variáveis de ambiente — nunca hardcode credenciais
# ---------------------------------------------------------------------------
DB_HOST     = os.environ["DB_HOST"]
DB_PORT     = os.environ.get("DB_PORT", "1433")
DB_USER     = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME     = os.environ["DB_NAME"]
S3_BUCKET   = os.environ.get("S3_BUCKET", "")     # opcional para ambientes cloud
ENV         = os.environ.get("ENV", "development")


# ---------------------------------------------------------------------------
# Metadados de carga — sempre registrar rastreabilidade
# ---------------------------------------------------------------------------
def build_etl_metadata(source: str, layer: str) -> dict:
    return {
        "_etl_source": source,
        "_etl_layer": layer,
        "_etl_loaded_at": datetime.utcnow().isoformat(),
        "_etl_env": ENV,
    }


# ---------------------------------------------------------------------------
# Extração — salvar Bronze sem modificar o dado
# ---------------------------------------------------------------------------
def extract(query: str, connection, reference_date: date) -> pd.DataFrame:
    """Extrai dados da fonte e retorna DataFrame bruto."""
    log.info("Iniciando extração | data_referencia=%s", reference_date)

    df = pd.read_sql(query, connection, params={"dt_ref": reference_date})

    # Adiciona metadados de rastreabilidade
    meta = build_etl_metadata(source="db_origem", layer="bronze")
    for col, val in meta.items():
        df[col] = val

    log.info("Extração concluída | linhas=%d colunas=%d", len(df), len(df.columns))
    return df


# ---------------------------------------------------------------------------
# Transformação Silver — limpeza, tipagem, deduplicação
# ---------------------------------------------------------------------------
def transform_silver(df_bronze: pd.DataFrame) -> pd.DataFrame:
    """Limpa, tipar e deduplica. Bronze → Silver."""
    log.info("Iniciando transformação Silver | linhas_entrada=%d", len(df_bronze))

    df = df_bronze.copy()

    # 1. Remover colunas de controle do bronze antes de transformar
    meta_cols = [c for c in df.columns if c.startswith("_etl_")]
    df = df.drop(columns=meta_cols)

    # 2. Renomear colunas para snake_case
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    # 3. Tipagem explícita — ajustar conforme schema real
    df["dt_referencia"]  = pd.to_datetime(df["dt_referencia"], errors="coerce")
    df["vl_valor"]       = pd.to_numeric(df["vl_valor"],       errors="coerce")
    df["cd_identificador"] = df["cd_identificador"].astype(str).str.strip()

    # 4. Tratar nulos com estratégia explícita
    df["nm_descricao"] = df["nm_descricao"].fillna("SEM_DESCRICAO")
    df = df.dropna(subset=["cd_identificador", "dt_referencia"])  # chaves não podem ser nulas

    # 5. Deduplicação — definir subset explicitamente
    linhas_antes = len(df)
    df = df.drop_duplicates(subset=["cd_identificador", "dt_referencia"], keep="last")
    log.info("Deduplicação | removidas=%d", linhas_antes - len(df))

    # 6. Metadados Silver
    meta = build_etl_metadata(source="bronze", layer="silver")
    for col, val in meta.items():
        df[col] = val

    log.info("Transformação Silver concluída | linhas_saida=%d", len(df))
    return df


# ---------------------------------------------------------------------------
# Transformação Gold — regras de negócio, KPIs, agregações
# ---------------------------------------------------------------------------
def transform_gold(df_silver: pd.DataFrame) -> pd.DataFrame:
    """Aplica regras de negócio. Silver → Gold (pronto para BI)."""
    log.info("Iniciando transformação Gold | linhas_entrada=%d", len(df_silver))

    df = df_silver.copy()

    # Remover metadados do silver antes de aplicar regras
    meta_cols = [c for c in df.columns if c.startswith("_etl_")]
    df = df.drop(columns=meta_cols)

    # --- Adicionar regras de negócio específicas aqui ---
    # Exemplo: calcular margem, classificar segmento, derivar KPI
    # df["margem_bruta"] = df["vl_receita"] - df["vl_custo"]
    # df["margem_pct"]   = df["margem_bruta"] / df["vl_receita"].replace(0, float("nan"))
    # df["classe_abc"]   = pd.cut(df["vl_receita"], bins=[0, 1000, 5000, float("inf")],
    #                             labels=["C", "B", "A"])

    # Metadados Gold
    meta = build_etl_metadata(source="silver", layer="gold")
    for col, val in meta.items():
        df[col] = val

    log.info("Transformação Gold concluída | linhas_saida=%d", len(df))
    return df


# ---------------------------------------------------------------------------
# Carga — persistir no destino
# ---------------------------------------------------------------------------
def load(df: pd.DataFrame, destination: str, mode: str = "append") -> None:
    """
    Persiste o DataFrame no destino.
    mode: 'append' para carga incremental, 'replace' para full refresh.
    """
    log.info("Iniciando carga | destino=%s mode=%s linhas=%d", destination, mode, len(df))

    # Adaptar para o destino real:
    # df.to_sql(destination, con=connection, if_exists=mode, index=False)
    # df.to_parquet(f"s3://{S3_BUCKET}/{destination}.parquet")
    # df.to_csv(f"{destination}.csv", index=False)

    log.info("Carga concluída | destino=%s", destination)


# ---------------------------------------------------------------------------
# Validação pós-carga
# ---------------------------------------------------------------------------
def validate(df: pd.DataFrame, expected_min_rows: int = 1) -> bool:
    """Validações mínimas antes de considerar a carga bem-sucedida."""
    checks = {
        "linhas_suficientes": len(df) >= expected_min_rows,
        "sem_nulos_em_chaves": df["cd_identificador"].notna().all(),
        "datas_validas":       df["dt_referencia"].notna().all(),
    }

    for check, result in checks.items():
        status = "OK" if result else "FALHOU"
        log.info("Validação | %s → %s", check, status)

    return all(checks.values())


# ---------------------------------------------------------------------------
# Orquestrador principal
# ---------------------------------------------------------------------------
def run_pipeline(reference_date: Optional[date] = None) -> None:
    reference_date = reference_date or date.today()
    log.info("Pipeline iniciado | data_referencia=%s env=%s", reference_date, ENV)

    connection = None  # substituir por conexão real
    query = "SELECT * FROM schema.tabela WHERE dt_referencia = :dt_ref"

    try:
        # Bronze
        df_bronze = extract(query, connection, reference_date)

        # Silver
        df_silver = transform_silver(df_bronze)

        # Gold
        df_gold = transform_gold(df_silver)

        # Validação
        if not validate(df_gold):
            raise ValueError("Validação falhou — pipeline interrompido antes da carga.")

        # Carga
        load(df_gold, destination="gold.tabela_final", mode="append")

        log.info("Pipeline concluído com sucesso | data_referencia=%s", reference_date)

    except Exception as e:
        log.error("Pipeline falhou | erro=%s", str(e))
        raise


if __name__ == "__main__":
    run_pipeline()

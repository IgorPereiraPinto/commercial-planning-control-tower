"""
Template: Extração de Dados via API REST
Adaptar: base_url, autenticação, endpoints e schema de resposta
Padrão: extrair → salvar raw → validar schema mínimo
"""

import os
import time
import logging
from datetime import datetime
from typing import Any, Optional
import requests

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuração — credenciais sempre via variáveis de ambiente
# ---------------------------------------------------------------------------
API_BASE_URL  = os.environ["API_BASE_URL"]
API_KEY       = os.environ["API_KEY"]
API_CLIENT_ID = os.environ.get("API_CLIENT_ID", "")
TIMEOUT_SEC   = int(os.environ.get("API_TIMEOUT", "30"))
MAX_RETRIES   = int(os.environ.get("API_MAX_RETRIES", "3"))
RATE_LIMIT_SEC = float(os.environ.get("API_RATE_LIMIT", "1.0"))  # pausa entre requisições


# ---------------------------------------------------------------------------
# Sessão HTTP reutilizável com autenticação
# ---------------------------------------------------------------------------
def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    return session


# ---------------------------------------------------------------------------
# Requisição com retry e backoff
# ---------------------------------------------------------------------------
def make_request(
    session: requests.Session,
    endpoint: str,
    params: Optional[dict] = None,
    attempt: int = 1,
) -> dict:
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
    log.info("GET %s | params=%s | tentativa=%d", url, params, attempt)

    try:
        response = session.get(url, params=params, timeout=TIMEOUT_SEC)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else "?"
        if status == 429 and attempt <= MAX_RETRIES:
            wait = 2 ** attempt
            log.warning("Rate limit atingido. Aguardando %ds antes de tentar novamente.", wait)
            time.sleep(wait)
            return make_request(session, endpoint, params, attempt + 1)
        log.error("HTTP error | status=%s url=%s", status, url)
        raise

    except requests.exceptions.Timeout:
        if attempt <= MAX_RETRIES:
            log.warning("Timeout. Tentativa %d de %d.", attempt, MAX_RETRIES)
            time.sleep(RATE_LIMIT_SEC * attempt)
            return make_request(session, endpoint, params, attempt + 1)
        log.error("Timeout máximo atingido | url=%s", url)
        raise

    except requests.exceptions.RequestException as e:
        log.error("Erro de conexão | url=%s erro=%s", url, str(e))
        raise


# ---------------------------------------------------------------------------
# Paginação automática
# ---------------------------------------------------------------------------
def fetch_all_pages(
    session: requests.Session,
    endpoint: str,
    base_params: Optional[dict] = None,
    page_param: str = "page",
    page_size_param: str = "per_page",
    page_size: int = 100,
    data_key: str = "data",
    next_key: Optional[str] = "next_page",
) -> list[dict]:
    """
    Busca todos os registros paginados.
    Adaptar page_param, data_key e next_key conforme o padrão da API alvo.
    """
    all_records = []
    params = {**(base_params or {}), page_param: 1, page_size_param: page_size}
    page = 1

    while True:
        params[page_param] = page
        response = make_request(session, endpoint, params)

        records = response.get(data_key, [])
        all_records.extend(records)

        log.info("Página %d | registros=%d | total_acumulado=%d", page, len(records), len(all_records))

        # Verificar se há próxima página (adaptar conforme a API)
        has_next = (
            response.get(next_key) is not None  # padrão 1: campo next_page
            if next_key else
            len(records) == page_size             # padrão 2: se retornou página cheia, assume que há mais
        )

        if not has_next or not records:
            break

        page += 1
        time.sleep(RATE_LIMIT_SEC)  # respeitar rate limit

    log.info("Paginação concluída | total_registros=%d", len(all_records))
    return all_records


# ---------------------------------------------------------------------------
# Validação de schema mínimo
# ---------------------------------------------------------------------------
def validate_schema(records: list[dict], required_fields: list[str]) -> bool:
    """Valida que os campos obrigatórios estão presentes nos registros."""
    if not records:
        log.warning("Nenhum registro retornado pela API.")
        return False

    sample = records[0]
    missing = [f for f in required_fields if f not in sample]

    if missing:
        log.error("Campos obrigatórios ausentes | campos=%s", missing)
        return False

    log.info("Schema validado | campos_presentes=%d", len(required_fields))
    return True


# ---------------------------------------------------------------------------
# Persistência com metadados de extração
# ---------------------------------------------------------------------------
def save_raw(records: list[dict], source: str) -> list[dict]:
    """Adiciona metadados de rastreabilidade antes de persistir."""
    metadata = {
        "_etl_source":      source,
        "_etl_layer":       "bronze",
        "_etl_extracted_at": datetime.utcnow().isoformat(),
        "_etl_record_count": len(records),
    }

    enriched = []
    for record in records:
        enriched.append({**record, **metadata})

    # Persistir conforme ambiente:
    # import json; json.dump(enriched, open("raw_output.json", "w"), ensure_ascii=False)
    # pd.DataFrame(enriched).to_parquet("s3://bucket/raw/output.parquet")
    # pd.DataFrame(enriched).to_csv("raw_output.csv", index=False)

    log.info("Raw salvo | registros=%d source=%s", len(enriched), source)
    return enriched


# ---------------------------------------------------------------------------
# Orquestrador principal
# ---------------------------------------------------------------------------
def run_extraction(
    endpoint: str,
    params: Optional[dict] = None,
    required_fields: Optional[list[str]] = None,
) -> list[dict]:
    required_fields = required_fields or ["id"]  # adaptar campos obrigatórios

    log.info("Extração iniciada | endpoint=%s", endpoint)
    session = build_session()

    records = fetch_all_pages(session, endpoint, base_params=params)

    if not validate_schema(records, required_fields):
        raise ValueError(f"Schema inválido — extração cancelada | endpoint={endpoint}")

    raw = save_raw(records, source=endpoint)
    log.info("Extração concluída | registros=%d", len(raw))
    return raw


if __name__ == "__main__":
    # Exemplo de uso — adaptar endpoint e parâmetros
    data = run_extraction(
        endpoint="/vendas",
        params={"data_inicio": "2026-01-01", "data_fim": "2026-01-31"},
        required_fields=["id", "data", "valor", "cliente_id"],
    )
    print(f"Total extraído: {len(data)} registros")

"""Runner do pipeline ETL — ponto de entrada da raiz do projeto.

Executa o pipeline completo em 7 etapas:
    extract → validate raw → transform → validate staging → load raw → load staging → load dw

Uso:
    python run_etl.py              # execução completa (grava no banco)
    python run_etl.py --dry-run    # só valida e transforma, sem gravar
"""
import sys
from pathlib import Path

# Garante que src/ está no path para importação do pacote
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()

from src.etl.pipeline import run_pipeline

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    run_pipeline(dry_run=dry_run)

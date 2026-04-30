# ================================================================
# Makefile — planejamento-comercial
# Requer: GNU Make (nativo em Linux/Mac · no Windows use Git Bash ou WSL)
# Alternativa Windows: python run_etl.py | python -m pytest -q
# ================================================================

.DEFAULT_GOAL := help
.PHONY: help setup etl test dry-run open clean

help:  ## Mostra este menu de ajuda
	@echo ""
	@echo "  planejamento-comercial — comandos disponíveis"
	@echo "  ─────────────────────────────────────────────"
	@echo "  make setup     instala dependências (requirements.txt + dev)"
	@echo "  make etl       roda o pipeline ETL completo (7 etapas)"
	@echo "  make dry-run   valida e transforma sem gravar no banco"
	@echo "  make test      executa a suite de testes (pytest -q)"
	@echo "  make open      abre o dashboard no navegador padrão"
	@echo "  make clean     remove arquivos gerados em data/processed/"
	@echo ""

setup:  ## Instala dependências de produção e desenvolvimento
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

etl:  ## Roda o pipeline ETL completo (extract → validate → transform → load)
	python run_etl.py

dry-run:  ## Valida e transforma os dados sem gravar no banco
	python run_etl.py --dry-run

test:  ## Executa a suite de testes com saída compacta
	pytest -q

open:  ## Abre o dashboard HTML no navegador padrão
	@python -c "\
import webbrowser, pathlib; \
	p = pathlib.Path('dashboards/planejamento_comercial.html').resolve(); \
webbrowser.open(p.as_uri()); \
print('Dashboard aberto:', p); \
"

clean:  ## Remove arquivos gerados pelo ETL (mantém .gitkeep)
	@python -c "\
import glob, os; \
files = [f for f in glob.glob('data/processed/*') if '.gitkeep' not in f]; \
[os.remove(f) for f in files]; \
print(f'Removido: {len(files)} arquivo(s) de data/processed/'); \
"

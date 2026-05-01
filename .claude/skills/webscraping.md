---
name: webscraping
description: >
  Especialista em coleta de dados públicos via web scraping com Python. Cobre BeautifulSoup,
  Playwright, Selenium, Scrapy, extração de tabelas HTML, monitoramento de preços, paginação,
  anti-bot, armazenamento estruturado e integração com pipelines de dados. Use sempre que
  o usuário mencionar scraping, coleta de dados de site, extração de tabela HTML, monitoramento
  de preço, crawler, spider, dados públicos de site, ou qualquer coleta automatizada de
  conteúdo web.
  Trigger para: "faz scraping de", "extrai dados do site", "monitora preço", "coleta tabela do
  HTML", "cria um crawler", "raspa dados do site", "extrai informações do portal", "spider".
---

# Web Scraping — Coleta Automatizada de Dados Públicos

## Identidade

Especialista em web scraping responsável e eficiente. Avalia viabilidade (robots.txt, termos
de uso, estrutura da página), escolhe a ferramenta certa para cada caso, e entrega dados
estruturados prontos para análise. Prioriza scraping ético, com rate limiting e rastreabilidade.

---

## Quando Usar

Use esta skill para coleta de dados de sites públicos: portais governamentais, marketplaces,
sites de notícias, tabelas de preços, rankings. Sempre verificar robots.txt e termos de uso
antes de raspar. Não usar para sites que exigem autenticação sem permissão explícita.

---

## Como Atuar

1. Avaliar viabilidade: robots.txt, termos de uso, necessidade de autenticação
2. Analisar estrutura da página: estática (HTML puro) ou dinâmica (JavaScript)
3. Escolher a ferramenta: requests+BS4 para estática, Playwright para dinâmica
4. Implementar paginação, retry e rate limiting
5. Estruturar os dados em DataFrame e persistir (CSV, Parquet ou banco)
6. Documentar a fonte, data da extração e estrutura dos dados

---

## 1. Avaliação Inicial — Checklist

```python
import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin

def verificar_permissao(url_site: str, user_agent: str = '*') -> dict:
    """Verifica robots.txt antes de iniciar qualquer scraping."""
    robots_url = urljoin(url_site, '/robots.txt')
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        permitido = rp.can_fetch(user_agent, url_site)
    except Exception:
        permitido = True  # Se não há robots.txt, assumir permitido com cautela

    return {
        'url': url_site,
        'robots_url': robots_url,
        'permitido': permitido,
        'crawl_delay': rp.crawl_delay(user_agent),
        'recomendacao': 'PROSSEGUIR' if permitido else 'VERIFICAR MANUALMENTE'
    }
```

---

## 2. BeautifulSoup — Sites Estáticos

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; DataCollector/1.0; research purposes)',
    'Accept-Language': 'pt-BR,pt;q=0.9',
    'Accept': 'text/html,application/xhtml+xml',
}

def fetch_page(url: str, max_retries: int = 3,
               delay: float = 1.5) -> Optional[BeautifulSoup]:
    """Busca página com retry, delay e headers realistas."""
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding
            time.sleep(delay)
            return BeautifulSoup(resp.text, 'html.parser')
        except requests.RequestException as e:
            logger.warning(f"Tentativa {attempt+1}/{max_retries} falhou: {e}")
            time.sleep(delay * (attempt + 1))
    logger.error(f"Falha após {max_retries} tentativas: {url}")
    return None


def extrair_tabela_html(url: str, indice_tabela: int = 0) -> pd.DataFrame:
    """Extrai tabela HTML diretamente com pandas (o mais rápido)."""
    tabelas = pd.read_html(url, flavor='bs4', encoding='utf-8')
    if not tabelas:
        raise ValueError(f"Nenhuma tabela encontrada em {url}")
    df = tabelas[indice_tabela]
    df['_fonte'] = url
    df['_extraido_em'] = pd.Timestamp.now()
    return df


def scrape_listagem_paginada(url_base: str,
                              seletor_item: str,
                              seletor_prox_pag: str,
                              campos: dict,
                              max_paginas: int = 50) -> pd.DataFrame:
    """
    Scraping de listagem com paginação.

    Args:
        url_base: URL da primeira página
        seletor_item: CSS selector do elemento de cada item
        seletor_prox_pag: CSS selector do botão/link 'próxima página'
        campos: dict {nome_campo: css_selector_dentro_do_item}
        max_paginas: limite de segurança

    Exemplo:
        campos = {
            'nome': 'h2.produto-nome',
            'preco': 'span.preco',
            'disponibilidade': 'div.estoque',
        }
    """
    todos = []
    url_atual = url_base
    pagina = 1

    while url_atual and pagina <= max_paginas:
        logger.info(f"Scraping página {pagina}: {url_atual}")
        soup = fetch_page(url_atual)
        if not soup:
            break

        itens = soup.select(seletor_item)
        for item in itens:
            registro = {}
            for campo, seletor in campos.items():
                elem = item.select_one(seletor)
                registro[campo] = elem.get_text(strip=True) if elem else None
            registro['_url_origem'] = url_atual
            todos.append(registro)

        # Próxima página
        prox = soup.select_one(seletor_prox_pag)
        if prox and prox.get('href'):
            url_atual = urljoin(url_base, prox['href'])
            pagina += 1
        else:
            break

    df = pd.DataFrame(todos)
    df['_extraido_em'] = pd.Timestamp.now()
    logger.info(f"Total: {len(df):,} registros de {pagina-1} páginas")
    return df
```

---

## 3. Playwright — Sites Dinâmicos (JavaScript)

```python
# pip install playwright && playwright install chromium
from playwright.sync_api import sync_playwright
import pandas as pd
import time

def scrape_com_playwright(url: str,
                           seletor_espera: str,
                           seletor_dados: str,
                           campos: dict,
                           headless: bool = True,
                           timeout: int = 30000) -> pd.DataFrame:
    """
    Scraping de página com JavaScript usando Playwright.

    Use quando: carrossel, lazy loading, SPAs, conteúdo carregado via JS.

    Args:
        seletor_espera: elemento para esperar (garante que a página carregou)
        seletor_dados: CSS selector dos itens a raspar
        campos: {nome_campo: css_selector_relativo}
    """
    registros = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120',
            locale='pt-BR',
            viewport={'width': 1280, 'height': 720},
        )
        page = ctx.new_page()

        page.goto(url, timeout=timeout)
        page.wait_for_selector(seletor_espera, timeout=timeout)
        time.sleep(2)  # aguarda render completo

        itens = page.query_selector_all(seletor_dados)
        for item in itens:
            reg = {}
            for campo, sel in campos.items():
                elem = item.query_selector(sel)
                reg[campo] = elem.inner_text().strip() if elem else None
            registros.append(reg)

        browser.close()

    df = pd.DataFrame(registros)
    df['_fonte'] = url
    df['_extraido_em'] = pd.Timestamp.now()
    return df


def scrape_paginacao_scroll(url: str,
                             seletor_item: str,
                             campos: dict,
                             max_scrolls: int = 20) -> pd.DataFrame:
    """Scraping de scroll infinito (infinite scroll)."""
    registros = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        scroll_count = 0
        anterior = 0

        while scroll_count < max_scrolls:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            atual = page.evaluate("document.body.scrollHeight")
            if atual == anterior:
                break
            anterior = atual
            scroll_count += 1

        # Extrai após scroll completo
        itens = page.query_selector_all(seletor_item)
        for item in itens:
            reg = {}
            for campo, sel in campos.items():
                elem = item.query_selector(sel)
                reg[campo] = elem.inner_text().strip() if elem else None
            registros.append(reg)

        browser.close()

    return pd.DataFrame(registros)
```

---

## 4. Monitoramento de Preços — Exemplo Prático

```python
import sqlite3
from datetime import datetime

def monitorar_preco(urls_produtos: dict,
                    seletor_preco: str,
                    db_path: str = 'precos.db') -> pd.DataFrame:
    """
    Monitora preços de múltiplos produtos e armazena histórico em SQLite.

    urls_produtos = {
        'Produto A': 'https://site.com/produto-a',
        'Produto B': 'https://site.com/produto-b',
    }
    """
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS historico_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT, url TEXT, preco REAL,
            preco_raw TEXT, coletado_em TIMESTAMP
        )
    """)

    resultados = []
    for produto, url in urls_produtos.items():
        soup = fetch_page(url)
        if not soup:
            continue
        elem = soup.select_one(seletor_preco)
        preco_raw = elem.get_text(strip=True) if elem else None
        # Converte "R$ 1.299,99" → 1299.99
        preco = None
        if preco_raw:
            preco = float(
                preco_raw.replace('R$', '').replace('.', '').replace(',', '.').strip()
            )

        registro = {
            'produto': produto, 'url': url,
            'preco': preco, 'preco_raw': preco_raw,
            'coletado_em': datetime.now()
        }
        resultados.append(registro)
        conn.execute(
            "INSERT INTO historico_precos (produto, url, preco, preco_raw, coletado_em) VALUES (?,?,?,?,?)",
            list(registro.values())
        )
        logger.info(f"{produto}: {preco_raw}")

    conn.commit()
    conn.close()
    return pd.DataFrame(resultados)
```

---

## 5. Estrutura de Saída Padrão

```python
def salvar_dados_scraping(df: pd.DataFrame,
                           nome_base: str,
                           formato: str = 'parquet') -> str:
    """Salva dados coletados com metadados de rastreabilidade."""
    from pathlib import Path
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    pasta = Path('data/raw/scraping')
    pasta.mkdir(parents=True, exist_ok=True)

    # Adiciona metadados obrigatórios
    df['_run_id'] = timestamp
    df['_fonte_tipo'] = 'web_scraping'

    arquivo = pasta / f"{nome_base}_{timestamp}.{formato}"
    if formato == 'parquet':
        df.to_parquet(arquivo, index=False, compression='snappy')
    elif formato == 'csv':
        df.to_csv(arquivo, index=False, encoding='utf-8-sig', sep=';')

    print(f"✅ {len(df):,} registros → {arquivo}")
    return str(arquivo)
```

---

## Regras de Qualidade

- Sempre verificar `robots.txt` antes de iniciar — `verificar_permissao()` é obrigatório
- Rate limiting: mínimo 1-2 segundos entre requisições para não sobrecarregar o servidor
- User-Agent realista — nunca usar o padrão do requests sem customizar
- Usar BeautifulSoup para HTML estático, Playwright para conteúdo JS
- Nunca raspar dados que exijam autenticação sem permissão explícita
- Salvar sempre o HTML bruto ou dado raw antes de transformar (princípio Bronze)
- Registrar URL de origem, data/hora de extração e run_id em todo registro

## Observações

Para APIs oficiais (BACEN, IBGE, portais gov), prefira `bacen-api` ou `api-data-extraction`.
Playwright MCP no Claude Code permite scraping diretamente sem escrever código — usar quando possível.

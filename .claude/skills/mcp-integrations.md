---
name: mcp-integrations
description: >
  Especialista em configuração, uso e criação de MCP Servers (Model Context Protocol) para
  Claude Code e Claude Desktop. Cobre setup de servidores stdio e SSE, configuração do
  claude_desktop_config.json, debugging de conexão, lista de servidores úteis para stack
  de dados (SQL Server, Excel, Power BI, GitHub, Playwright, Google Sheets), e criação de
  MCP servers customizados em Python com FastMCP.
  Use sempre que o usuário mencionar MCP, Model Context Protocol, configurar servidor MCP,
  integrar Claude com ferramenta externa, claude_desktop_config, FastMCP, stdio, SSE,
  ou qualquer integração de ferramenta no Claude Code/Desktop.
  Trigger para: "configura MCP", "cria um MCP server", "integra Claude com", "como conectar
  Claude ao SQL Server", "MCP para Excel", "claude_desktop_config", "FastMCP", "SSE server".
---

# MCP Integrations — Model Context Protocol

## Identidade

Especialista em integração de ferramentas via MCP. Configura servidores, resolve problemas
de conexão e cria ferramentas customizadas que ampliam o que o Claude Code e Claude Desktop
conseguem fazer diretamente no ambiente de dados.

---

## 1. claude_desktop_config.json — Estrutura Base

```json
{
  "mcpServers": {
    "power-bi": {
      "command": "npx",
      "args": ["-y", "@microsoft/mcp-server-powerbi"],
      "type": "stdio"
    },
    "sql-server": {
      "command": "python",
      "args": ["-m", "mcp_server_sqlserver"],
      "env": {
        "SQL_SERVER": "seu_servidor",
        "SQL_DATABASE": "seu_banco",
        "SQL_USER": "usuario",
        "SQL_PASSWORD": "senha"
      },
      "type": "stdio"
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp"],
      "type": "stdio"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem",
               "C:/Users/Igor/Documents", "C:/dados"],
      "type": "stdio"
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."},
      "type": "stdio"
    },
    "google-sheets": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google-sheets"],
      "env": {"GOOGLE_CREDENTIALS_JSON": "/caminho/credentials.json"},
      "type": "stdio"
    }
  }
}
```

---

## 2. Localização do Arquivo por OS

```
Windows:  %APPDATA%\Claude\claude_desktop_config.json
macOS:    ~/Library/Application Support/Claude/claude_desktop_config.json
Linux:    ~/.config/claude/claude_desktop_config.json

Claude Code (projeto): .claude/settings.json
```

---

## 3. MCP Server Customizado com FastMCP (Python)

```python
# pip install fastmcp pyodbc pandas
from fastmcp import FastMCP
import pyodbc
import pandas as pd
import os

mcp = FastMCP("SQL Server Analytics")

# Conexão reutilizável
def get_conn():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
        f"UID={os.getenv('SQL_USER')};"
        f"PWD={os.getenv('SQL_PASSWORD')}"
    )


@mcp.tool()
def listar_tabelas(schema: str = 'dbo') -> str:
    """Lista todas as tabelas de um schema do SQL Server."""
    with get_conn() as conn:
        df = pd.read_sql(
            f"SELECT TABLE_NAME, TABLE_TYPE FROM INFORMATION_SCHEMA.TABLES "
            f"WHERE TABLE_SCHEMA = '{schema}' ORDER BY TABLE_NAME",
            conn
        )
    return df.to_string(index=False)


@mcp.tool()
def executar_query(sql: str, max_linhas: int = 500) -> str:
    """
    Executa query SELECT no SQL Server e retorna resultado.
    Limitado a SELECT — não aceita INSERT, UPDATE, DELETE.
    """
    sql_limpo = sql.strip()
    if not sql_limpo.upper().startswith('SELECT'):
        return "❌ Apenas queries SELECT são permitidas."
    try:
        with get_conn() as conn:
            df = pd.read_sql(sql_limpo, conn)
        if len(df) > max_linhas:
            df = df.head(max_linhas)
            return f"[Limitado a {max_linhas} linhas]\n" + df.to_string(index=False)
        return df.to_string(index=False)
    except Exception as e:
        return f"❌ Erro: {e}"


@mcp.tool()
def descrever_tabela(tabela: str, schema: str = 'dbo') -> str:
    """Retorna colunas, tipos e nulabilidade de uma tabela."""
    with get_conn() as conn:
        df = pd.read_sql(f"""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH,
                   IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{tabela}'
            ORDER BY ORDINAL_POSITION
        """, conn)
    return df.to_string(index=False)


@mcp.tool()
def preview_tabela(tabela: str, schema: str = 'dbo', n: int = 10) -> str:
    """Retorna as primeiras N linhas de uma tabela."""
    return executar_query(f"SELECT TOP {n} * FROM [{schema}].[{tabela}]")


@mcp.tool()
def contar_registros(tabela: str, schema: str = 'dbo') -> str:
    """Conta registros de uma tabela."""
    return executar_query(f"SELECT COUNT(*) AS total FROM [{schema}].[{tabela}]")


if __name__ == "__main__":
    mcp.run()
```

---

## 4. Registrar o Server Customizado

```json
{
  "mcpServers": {
    "sql-analytics": {
      "command": "python",
      "args": ["C:/projetos/mcp_servers/sql_analytics_server.py"],
      "env": {
        "SQL_SERVER": "servidor\\instancia",
        "SQL_DATABASE": "seu_banco",
        "SQL_USER": "usuario",
        "SQL_PASSWORD": "senha"
      },
      "type": "stdio"
    }
  }
}
```

---

## 5. Servidores Recomendados para Stack de Dados

| Servidor | Instalação | Uso |
|---|---|---|
| Power BI | `@microsoft/mcp-server-powerbi` | Lê modelos, medidas, dados |
| Playwright | `@playwright/mcp` | Browser automation, scraping |
| Filesystem | `@modelcontextprotocol/server-filesystem` | Lê/escreve arquivos locais |
| GitHub | `@modelcontextprotocol/server-github` | Issues, PRs, código |
| Google Sheets | `@modelcontextprotocol/server-google-sheets` | Leitura/escrita em planilhas |
| Excel | `@microsoft/mcp-server-excel` | Manipula .xlsx locais |
| SQLite | `@modelcontextprotocol/server-sqlite` | Banco local leve |
| Fetch/HTTP | `@modelcontextprotocol/server-fetch` | Consumo de APIs REST |

---

## 6. Debugging de Conexão MCP

```bash
# Testa o servidor diretamente no terminal
npx @modelcontextprotocol/inspector python mcp_server.py

# Vê logs do Claude Desktop (Windows)
type %APPDATA%\Claude\logs\mcp*.log

# Vê logs do Claude Desktop (macOS)
cat ~/Library/Logs/Claude/mcp*.log

# Testa server Python isoladamente
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python meu_server.py
```

---

## Regras de Qualidade

- Nunca commitar credenciais no `claude_desktop_config.json` — usar variáveis de ambiente
- Servidores stdio: processo filho, sincrono, mais simples; SSE: HTTP, permite multiplos clientes
- Reiniciar o Claude Desktop após qualquer mudança no config.json
- Ferramentas MCP devem retornar string — serializar DataFrames com `.to_string()` ou `.to_json()`
- Limitar queries a SELECT no server SQL — nunca expor capacidade de escrita sem controle explícito
- Para servidor em produção, adicionar timeout e tratamento de erro em toda tool

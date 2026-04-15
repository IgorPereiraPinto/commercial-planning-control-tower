# Guia de Implementação — Commercial Planning Control Tower

**Versão:** 1.0 | **Data:** Abril de 2026  
**Responsável:** Igor Pereira Pinto

---

## Índice

1. [Visão Geral do Projeto](#1-visão-geral)
2. [Pré-requisitos](#2-pré-requisitos)
3. [Configuração do Ambiente Python](#3-configuração-do-ambiente-python)
4. [Bibliotecas Utilizadas](#4-bibliotecas-utilizadas)
5. [Configuração do SQL Server](#5-configuração-do-sql-server)
6. [Configuração do Arquivo .env](#6-configuração-do-arquivo-env)
7. [Estrutura do Projeto](#7-estrutura-do-projeto)
8. [Executando o Pipeline ETL](#8-executando-o-pipeline-etl)
9. [Executando os Testes](#9-executando-os-testes)
10. [Fluxo Completo do Pipeline](#10-fluxo-completo-do-pipeline)
11. [Guia de Reutilização](#11-guia-de-reutilização)
12. [Troubleshooting](#12-troubleshooting)
13. [Configuração do Power BI](#13-configuração-do-power-bi)

---

## 1. Visão Geral

Este projeto implementa um pipeline ETL end-to-end para Planejamento Comercial,
transformando arquivos Excel de vendas e metas em um modelo dimensional no SQL Server,
consumível pelo Power BI com RLS e alertas automáticos via Power Automate.

**Fluxo resumido:**

```text
Excel (Vendas + Metas + Dimensões)
    → Python ETL (7 etapas: extract → validate raw → transform
                            → validate staging → load raw
                            → load staging → load dw)
    → SQL Server (raw → staging → dw / star schema Kimball)
    → Power BI (dashboard + RLS)
    → Power Automate (5 fluxos de alertas e refresh)
```

---

## 2. Pré-requisitos

### 2.1 Python

| Item | Versão mínima | Como verificar |
| ---- | ------------- | -------------- |
| Python | 3.11+ | `python --version` |
| pip | 23+ | `pip --version` |

**Instalação do Python:**
Baixe em python.org e marque **"Add Python to PATH"** durante a instalação.

### 2.2 SQL Server

| Item | Observação |
| ---- | ---------- |
| SQL Server | Express (gratuito) ou qualquer edição corporativa |
| ODBC Driver 17 ou 18 | Obrigatório para conexão via Python |

**Como verificar drivers ODBC instalados:**

```python
import pyodbc
print(pyodbc.drivers())
# Esperado: ['ODBC Driver 17 for SQL Server', ...]
```

**Download do ODBC Driver:**
Microsoft Learn → "Download ODBC Driver for SQL Server"

### 2.3 Git (opcional, recomendado)

Para versionamento do código. Não é obrigatório para rodar o ETL.

---

## 3. Configuração do Ambiente Python

### Por que usar ambiente virtual?

Um ambiente virtual (`venv`) cria uma instalação Python isolada para o projeto.
Isso evita conflitos de versões entre projetos diferentes na mesma máquina.
É uma prática obrigatória em projetos de dados profissionais.

### Passo a passo

```bash
# 1. Abra o terminal na pasta raiz do projeto
cd "c:/Users/letra/Desktop/Planejamento Comercial"

# 2. Cria o ambiente virtual (pasta .venv dentro do projeto)
python -m venv .venv

# 3. Ativa o ambiente virtual
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Windows (CMD):
.venv\Scripts\activate.bat

# Mac/Linux:
source .venv/bin/activate

# Confirmação: o prompt deve mostrar (.venv) no início
# (.venv) PS C:\Users\letra\Desktop\Planejamento Comercial>

# 4. Atualiza o pip (boa prática sempre fazer isso primeiro)
python -m pip install --upgrade pip

# 5. Instala dependências de produção
pip install -r requirements.txt

# 6. Instala dependências de desenvolvimento (inclui testes e formatação)
pip install -r requirements-dev.txt

# 7. Confirma instalação
pip list
```

### Como desativar o ambiente virtual

```bash
deactivate
```

---

## 4. Bibliotecas Utilizadas

### 4.1 Dependências de Produção (`requirements.txt`)

#### pandas `2.2.2`

**O que é:** Biblioteca central de manipulação de dados em Python.
É o "Excel do Python" — permite criar, filtrar, transformar e agregar dados
em DataFrames (estrutura similar a tabelas).

**Por que foi escolhida:**

- Suporte nativo a leitura de Excel (`read_excel`)
- Operação de UNPIVOT via `pd.melt` (essencial para transformar metas wide→long)
- Integração direta com SQLAlchemy para escrita em banco (`to_sql`)
- Tipagem nullable moderna (Int64, Float64) compatível com SQL

**Como foi instalada:**

```bash
pip install pandas==2.2.2
```

**Onde é usada no projeto:**

- `extract.py`: `pd.read_excel()` para leitura dos arquivos
- `transform.py`: `pd.melt()`, `pd.to_datetime()`, `pd.to_numeric()`
- `validate.py`: filtros, groupby e comparações
- `load.py`: `df.to_sql()` para escrita no SQL Server

---

#### numpy `1.26.4`

**O que é:** Biblioteca de computação numérica. É a base sobre a qual o pandas
é construído — provê tipos de dados como `np.nan` e operações vetorizadas.

**Por que foi escolhida:**

- Suporte ao tipo `np.nan` para representar valores nulos
- Operações matemáticas vetorizadas (mais rápidas que loops Python)
- Dependência direta do pandas (é instalado automaticamente com ele)

**Como foi instalada:**

```bash
pip install numpy==1.26.4
```

**Onde é usada no projeto:**

- `transform.py`: `np.nan` para tratar strings "nan" geradas pela leitura

---

#### openpyxl `3.1.2`

**O que é:** Engine de leitura e escrita de arquivos `.xlsx` (formato Excel moderno).
O pandas por si só não consegue ler arquivos Excel — ele delega essa tarefa
ao openpyxl nos bastidores.

**Por que foi escolhida:**

- Engine padrão e mais completa para arquivos `.xlsx`
- Suporte a múltiplas abas, formatação e fórmulas
- Mantida ativamente e compatível com pandas 2.x
- Alternativa `xlrd` só funciona com `.xls` (formato antigo)

**Como foi instalada:**

```bash
pip install openpyxl==3.1.2
```

**Como é usada:**

```python
# pandas usa openpyxl internamente quando o arquivo é .xlsx
df = pd.read_excel("arquivo.xlsx", engine="openpyxl")
# ou simplesmente (pandas detecta .xlsx automaticamente):
df = pd.read_excel("arquivo.xlsx")
```

---

#### pyodbc `5.1.0`

**O que é:** Driver Python para conectar a bancos de dados via ODBC
(Open Database Connectivity). É a camada de comunicação entre Python
e o SQL Server.

**Por que foi escolhida:**

- Única forma nativa de conectar Python ao SQL Server no Windows
- Suporta Windows Authentication (sem precisar de usuário/senha)
- Compatível com SQLAlchemy como backend
- `fast_executemany=True` reduz drasticamente o tempo de inserção em lote

**Como foi instalada:**

```bash
pip install pyodbc==5.1.0
```

**Pré-requisito de sistema:** O driver ODBC deve estar instalado no Windows
(não é só uma biblioteca Python — é um driver do sistema operacional).

---

#### SQLAlchemy `2.0.30`

**O que é:** ORM (Object Relational Mapper) e toolkit de banco de dados.
Aqui usamos apenas como engine de conexão — não usamos os recursos de ORM.

**Por que foi escolhida:**

- Interface limpa entre pandas e qualquer banco de dados
- `df.to_sql(con=engine)` exige um engine SQLAlchemy
- Gerencia pool de conexões automaticamente
- `pool_pre_ping=True` verifica conexão antes de cada operação

**Como foi instalada:**

```bash
pip install SQLAlchemy==2.0.30
```

**Atenção:** SQLAlchemy 2.x tem mudanças de API em relação ao 1.x.
Se migrar de código legado, revise os imports (`from sqlalchemy import text`
substituindo queries string diretas).

---

#### python-dotenv `1.0.1`

**O que é:** Biblioteca que lê arquivos `.env` e injeta as variáveis
no `os.environ` do Python.

**Por que foi escolhida:**

- Separa configuração de código (12-Factor App principle)
- Impede hardcode de senhas e caminhos no código-fonte
- Permite configurações diferentes por ambiente (dev/prod)
- Padrão da indústria para projetos Python

**Como foi instalada:**

```bash
pip install python-dotenv==1.0.1
```

**Como funciona:**

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Lê o arquivo .env
servidor = os.getenv("DB_SERVER")  # Acessa a variável
```

---

### 4.2 Dependências de Desenvolvimento (`requirements-dev.txt`)

#### pytest `8.2.0`

**O que é:** Framework de testes automatizados para Python.

**Por que foi escolhido:**

- Sintaxe simples (`assert` ao invés de `assertEqual`)
- Fixtures poderosas para reutilização de dados de teste
- Descoberta automática de testes (`test_*.py`)
- Integração com pytest-cov para cobertura de código

**Como foi instalado:**

```bash
pip install pytest==8.2.0
```

**Como usar:**

```bash
pytest tests/ -v                    # Roda todos os testes com verbosidade
pytest tests/test_extract.py -v    # Roda só os testes de extração
pytest tests/ --cov=src -v         # Com relatório de cobertura
```

---

#### pytest-cov `5.0.0`

**O que é:** Plugin do pytest para medir cobertura de código.

**Por que foi escolhido:**

- Mostra quais linhas do ETL foram testadas e quais foram ignoradas
- Meta de cobertura para projetos de dados: >= 80%
- Gera relatório visual no terminal

**Como usar:**

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

---

#### black `24.4.2`

**O que é:** Formatador automático de código Python (opinionado).

**Por que foi escolhido:**

- Elimina debates de estilo em equipe
- Aplicação determinística — o mesmo código sempre produz a mesma formatação
- Integração com VS Code (formatar ao salvar)

**Como usar:**

```bash
black src/ tests/                   # Formata todos os arquivos
black --check src/ tests/           # Apenas verifica sem alterar
```

---

#### flake8 `7.0.0`

**O que é:** Linter de código — verifica erros de sintaxe, imports não usados
e violações de estilo que o black não cobre.

**Como usar:**

```bash
flake8 src/ tests/
```

---

## 5. Configuração do SQL Server

### 5.1 Criar o banco de dados

Conecte ao SQL Server (via SSMS ou Azure Data Studio) e execute:

```sql
-- Cria o banco de dados do projeto
-- [REUTILIZAÇÃO]: Altere o nome conforme o novo projeto
CREATE DATABASE planejamento_comercial;
GO

-- Os schemas (raw, staging, dw) são criados automaticamente
-- pelo load.py na primeira execução do pipeline
```

### 5.2 Permissões necessárias

O usuário de conexão precisa de:

- `CREATE TABLE` no banco
- `INSERT`, `SELECT`, `TRUNCATE` nas tabelas
- `CREATE SCHEMA` (para criar raw, staging, dw)

Para Windows Authentication, o usuário Windows que executa o Python
precisa ter essas permissões no SQL Server.

---

## 6. Configuração do Arquivo .env

```bash
# 1. Copie o template
cp .env.example .env

# 2. Edite com os valores do seu ambiente
notepad .env    # Windows
# ou no VS Code: code .env
```

**Campos obrigatórios a preencher:**

```env
# Ajuste para o servidor real do SQL Server
DB_SERVER=SEU_SERVIDOR\INSTANCIA

# Nome do banco criado no passo 5.1
DB_DATABASE=planejamento_comercial

# Mantenha "yes" para Windows Authentication
DB_TRUSTED_CONNECTION=yes

# Verifique qual versão está instalada:
# python -c "import pyodbc; print(pyodbc.drivers())"
DB_DRIVER=ODBC Driver 17 for SQL Server
```

---

## 7. Estrutura do Projeto

```text
Planejamento Comercial/
│
├── .env                        ← NÃO versionado (contém senhas)
├── .env.example                ← Template versionado (sem senhas)
├── .gitignore                  ← Exclui .env, .venv, logs, __pycache__
├── requirements.txt            ← Dependências de produção
├── requirements-dev.txt        ← Dependências de desenvolvimento
│
├── Dimensões/                  ← Fonte: tabelas de referência
├── Extrações/                  ← Fonte: transações de vendas
├── Metas/                      ← Fonte: targets anuais por vendedor
│
├── src/
│   ├── config/
│   │   └── settings.py         ← Configurações centrais (lê .env)
│   └── etl/
│       ├── extract.py          ← Leitura dos arquivos Excel
│       ├── transform.py        ← Limpeza, tipagem, UNPIVOT
│       ├── validate.py         ← Validações raw (4) + staging (7)
│       ├── load.py             ← Escrita no SQL Server (raw + staging)
│       ├── load_dw.py          ← Carga DW via INSERT...SELECT (staging → dw)
│       └── pipeline.py         ← Orquestrador: 7 etapas end-to-end
│
├── tests/
│   ├── conftest.py             ← Setup de env + markers unit/integration
│   ├── test_extract.py         ← [integration] lê arquivos Excel reais
│   ├── test_transform.py       ← [unit] fixtures em memória
│   └── test_validate.py        ← [unit] fixtures em memória
│
├── sql/                        ← Scripts DDL do SQL Server (01–07)
├── powerbi/                    ← Modelo, medidas DAX e configuração RLS
├── powerautomate/              ← 5 fluxos + template de e-mail
├── apresentacao/               ← HTML 14 slides + estrutura + script
├── docs/                       ← Documentação (este arquivo)
└── logs/
    └── etl.log                 ← Log automático gerado pelo pipeline
```

---

## 8. Executando o Pipeline ETL

### 8.1 Dry Run (testar sem gravar no banco)

Recomendado na **primeira execução** para validar que tudo está configurado:

```bash
# Ativa o ambiente virtual (se ainda não estiver ativo)
.venv\Scripts\Activate.ps1

# Executa o pipeline em modo de teste (sem gravação)
python -m src.etl.pipeline --dry-run
```

Saída esperada:

```text
2026-04-15 08:30:00 | INFO     | pipeline        | PIPELINE ETL INICIADO — 2026-04-15 08:30:00
2026-04-15 08:30:00 | INFO     | pipeline        | Modo: DRY RUN (sem gravação)
2026-04-15 08:30:01 | INFO     | extract         | Lendo arquivo de dimensões: ...
...
2026-04-15 08:30:05 | INFO     | pipeline        | DRY RUN CONCLUÍDO — Nenhuma gravação realizada.
```

### 8.2 Execução Completa

```bash
python -m src.etl.pipeline
```

### 8.3 Executar módulos individualmente (para debug)

```bash
# Testar apenas a extração
python -m src.etl.extract

# Verificar conexão com o banco
python -c "from src.etl.load import criar_engine; criar_engine(); print('Conexão OK')"
```

---

## 9. Executando os Testes

```bash
# Roda todos os testes
pytest tests/ -v

# Com relatório de cobertura de código
pytest tests/ -v --cov=src --cov-report=term-missing

# Apenas um arquivo de teste
pytest tests/test_transform.py -v

# Apenas um teste específico
pytest tests/test_transform.py::TestTransformMetas::test_formato_long_tem_mais_linhas_que_wide -v
```

**Categorias de testes:**

```bash
# Apenas unit (rodam sem Excel nem SQL Server — para CI)
pytest tests/ -m unit -v

# Apenas integration (precisam dos arquivos Excel)
pytest tests/ -m integration -v
```

**Saída esperada (todos passando):**

```text
tests/test_extract.py ...         [integration]
tests/test_transform.py ...       [unit]
tests/test_validate.py ...        [unit]
========================== 47 passed in X.XXs ==========================
```

---

## 10. Fluxo Completo do Pipeline

```text
INÍCIO
  │
  ├─ [1] EXTRACT
  │    ├─ extract_dimensoes()  → dict {nome: DataFrame}
  │    ├─ extract_vendas()     → DataFrame (20K linhas)
  │    └─ extract_metas()      → dict {ano: DataFrame}
  │
  ├─ [2] VALIDATE RAW  ← valida ESTRUTURA da fonte (4 testes)
  │    ├─ Teste 1: Colunas mínimas em fVendas
  │    ├─ Teste 2: Volume mínimo de transações
  │    ├─ Teste 3: Anos de metas presentes e completos
  │    └─ Teste 4: Estrutura wide das planilhas de meta
  │         ↓
  │    Se CRÍTICO falhar → PARA o pipeline (sys.exit(1))
  │
  ├─ [3] TRANSFORM
  │    ├─ transform_vendas()    → cast tipos, strip, metadados _etl_*
  │    ├─ transform_dimensoes() → normalização básica
  │    └─ transform_metas()     → UNPIVOT wide→long + consolidação
  │
  ├─ [4] VALIDATE STAGING  ← valida REGRAS DE NEGÓCIO (7 testes)
  │    ├─ Teste 1: Nulos em chaves primárias
  │    ├─ Teste 2: Integridade referencial (FK)
  │    ├─ Teste 3: Duplicidade de transações
  │    ├─ Teste 4: Cobertura de metas (11 vendedores × 12 meses)
  │    ├─ Teste 5: Valores negativos em faturamento
  │    ├─ Teste 6: Data envio >= data venda
  │    └─ Teste 7: Status válidos
  │         ↓
  │    Se CRÍTICO falhar → PARA o pipeline (sys.exit(1))
  │    [--dry-run para aqui — nenhuma gravação realizada]
  │
  ├─ [5] LOAD RAW
  │    ├─ raw.fVendas
  │    ├─ raw.dProdutos, dVendedor, dClientes, dCidade, dUnidades, dStatus, dPagamento
  │    └─ raw.fMetas_2018, fMetas_2019, fMetas_2020, fMetas_2021
  │
  ├─ [6] LOAD STAGING
  │    ├─ staging.fVendas
  │    ├─ staging.dProdutos, dVendedor, dClientes, dCidade, dUnidades, dStatus, dPagamento
  │    └─ staging.fMetas  (todos os anos consolidados em formato long)
  │
  └─ [7] LOAD DW  ← INSERT...SELECT de staging → star schema
       ├─ dw.dProdutos, dVendedor, dClientes, dCidade, dUnidades, dStatus, dPagamento
       ├─ dw.fVendas  (Margem Bruta e Resultado Líquido: colunas PERSISTED)
       └─ dw.fMetas

FIM → Log de resumo + tempo de execução
```

---

## 11. Guia de Reutilização

Este projeto foi construído como template reutilizável. Para adaptar a um
**novo projeto de planejamento comercial**, siga estes passos:

### O que NUNCA precisa mudar (estrutura do código)

- `pipeline.py` — o orquestrador funciona para qualquer projeto
- `validate.py` — os testes são genéricos e parametrizáveis
- `load.py` — a lógica de carga é agnóstica aos dados
- `settings.py` — lê tudo do `.env`, não tem nada hardcoded

### O que SEMPRE precisa ajustar

| Arquivo | O que ajustar | Por quê |
| ------- | ------------- | ------- |
| `.env` | Caminhos, servidor, banco, anos | Cada projeto tem fontes e ambientes diferentes |
| `extract.py` | `VENDAS_SKIPROWS`, `DIMENSOES_SHEETS`, nomes de abas | Layout do Excel pode variar |
| `transform.py` | Constantes de nomes de colunas, `MESES_PT` | Colunas têm nomes diferentes por projeto |
| `validate.py` | `STATUS_VALIDOS`, `QTD_VENDEDORES_ESPERADOS`, colunas obrigatórias | Regras de negócio mudam por projeto |

### Checklist de adaptação para novo projeto

```text
[ ] 1. Copiar o projeto para nova pasta
[ ] 2. Ajustar caminhos das fontes no .env
[ ] 3. Verificar nomes das abas em extract.py
[ ] 4. Verificar se VENDAS_SKIPROWS é correto para o novo Excel
[ ] 5. Atualizar constantes de colunas em transform.py
[ ] 6. Atualizar regras de validação em validate.py
[ ] 7. Criar novo banco no SQL Server e atualizar .env
[ ] 8. Rodar dry run: python -m src.etl.pipeline --dry-run
[ ] 9. Rodar testes: pytest tests/ -v
[ ] 10. Rodar pipeline completo: python -m src.etl.pipeline
```

### Como adicionar um novo teste de validação

```python
# Em validate.py, adicione uma função seguindo o padrão:
def validar_meu_novo_teste(df: pd.DataFrame) -> ValidationResult:
    """Descrição do que o teste verifica."""
    # Lógica do teste
    passou = ...  # True ou False
    return ValidationResult(
        nome="meu_novo_teste",
        passou=passou,
        mensagem="OK — ..." if passou else "FALHA — ...",
        critico=True,  # True = para o pipeline; False = só avisa
    )

# Em run_all_validations(), adicione na lista de testes:
testes = [
    ...testes_existentes...,
    validar_meu_novo_teste(df_vendas),  # <- adicione aqui
]
```

---

## 12. Troubleshooting

### Erro: `No module named 'src'`

**Causa:** Python não reconhece `src` como pacote porque o terminal não está
na raiz do projeto.

**Solução:**

```bash
# Certifique-se de estar na raiz do projeto
cd "c:/Users/letra/Desktop/Planejamento Comercial"
python -m src.etl.pipeline
```

---

### Erro: `ModuleNotFoundError: No module named 'pyodbc'`

**Causa:** O ambiente virtual não está ativo ou a instalação falhou.

**Solução:**

```bash
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### Erro: `[Microsoft][ODBC Driver Manager] Data source name not found`

**Causa:** O driver ODBC não está instalado no sistema operacional.

**Solução:**

1. Verifique drivers instalados: `python -c "import pyodbc; print(pyodbc.drivers())"`
2. Instale o "ODBC Driver 17 for SQL Server" da Microsoft
3. Atualize `DB_DRIVER` no `.env` para o driver instalado

---

### Erro: `FileNotFoundError: Arquivo 'Vendas' não encontrado`

**Causa:** O caminho configurado no `.env` não existe.

**Solução:**

```bash
# Verifique se o arquivo existe
ls "Extrações/Vendas.xlsx"

# Se o caminho estiver errado, corrija no .env:
DATA_PATH_VENDAS=Extrações/Vendas.xlsx
```

---

### Pipeline interrompido pela validação

**Causa:** Um ou mais testes críticos falharam. O log indicará exatamente qual.

**Como investigar:**

```bash
# Veja as últimas linhas do log
tail -50 logs/etl.log

# Ou rode em dry run para ver o relatório sem tentar gravar
python -m src.etl.pipeline --dry-run
```

---

---

## 13. Configuração do Power BI

### Sequência de configuração

Após o pipeline ETL estar rodando e os dados carregados no schema `dw`:

#### Passo 1 — Conectar ao SQL Server

```text
Power BI Desktop → Obter Dados → SQL Server
  Servidor:  noteigor
  Banco:     planejamento_comercial
  Modo:      Import
  Auth:      Windows
```

Selecionar apenas as 10 tabelas do schema `dw` (fVendas, fMetas + 8 dimensões).

#### Passo 2 — Configurar o modelo

Consultar o guia detalhado em: `powerbi/MODELO_POWERBI.md`

Itens críticos:

- Criar 9 relacionamentos ativos + 1 inativo (fMetas[Data Meta] → dCalendario[Data])
- Marcar `dCalendario` como Tabela de Data
- Configurar `NomeMes` para ordenar por `Mes` (número)
- Ocultar colunas técnicas `_dw_loaded_at` e `_dw_source`

#### Passo 3 — Criar as medidas DAX

Criar tabela vazia `_Medidas` e importar todas as medidas do arquivo:
`powerbi/medidas_dax/medidas_completas.dax`

O arquivo contém 20+ medidas organizadas em 6 pastas:

- 01 - Base (Faturamento, Custo, Margem, Resultado)
- 02 - Percentuais (Margem %, Resultado %, Ticket Médio)
- 03 - Meta (Meta, Atingimento %, Desvio)
- 04 - Temporal (YTD, Ano Anterior, MTD)
- 05 - Forecast / MAPE (MAPE, Acurácia, Classificação)
- 06 - Pareto / Ranking (Rank, Acumulado %, Classificação)

#### Passo 4 — Configurar RLS

Consultar o guia completo em: `powerbi/rls/rls_roles_completo.md`

Criar 4 roles: Gerente_Guardiola, Gerente_Marta, Gerente_Zagallo, Admin.
O filtro DAX é aplicado na tabela `dVendedor` e propaga automaticamente
para `fVendas` e `fMetas` pelos relacionamentos.

#### Passo 5 — Publicar e atribuir usuários

Publicar no Power BI Service e, no dataset → Segurança,
atribuir o e-mail de cada gerente à sua role correspondente.

### Estrutura de arquivos Power BI

```text
powerbi/
├── MODELO_POWERBI.md               ← guia completo de modelo e conexão
├── medidas_dax/
│   └── medidas_completas.dax       ← código de todas as 20+ medidas DAX
└── rls/
    └── rls_roles_completo.md       ← guia de RLS com checklist de teste
```

---

Guia de Implementação v2.0 — Commercial Planning Control Tower — Igor Pereira Pinto

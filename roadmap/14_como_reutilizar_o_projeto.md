# 14 — Como Reutilizar Este Projeto

## Mapa de clone vs reescrita

| Componente | O que muda | O que fica igual |
|---|---|---|
| `data/raw/` | Seus arquivos Excel | Estrutura da pasta |
| `.env` | Caminhos, banco, credenciais | Variáveis de configuração |
| `src/etl/extract.py` | Nomes das abas e colunas | Lógica de leitura |
| `src/etl/transform.py` | Regras de limpeza | Padrão de retorno |
| `sql/sqlserver/` | Nomes de tabelas e colunas | Estrutura raw/staging/dw |
| `powerbi/dax/` | Medidas do novo domínio | Padrão de nomenclatura |
| `roadmap/` | Ajustar contexto do case | Estrutura didática |

## Passos para um novo case

1. Clone o repositório
2. Substitua os arquivos em `data/raw/`
3. Ajuste o `.env` com novos caminhos e banco
4. Adapte `src/etl/extract.py` para suas abas e colunas
5. Revise as validações em `src/etl/validate.py`
6. Ajuste o star schema em `sql/sqlserver/`
7. Atualize as medidas DAX em `powerbi/dax/`
8. Reescreva o `README.md` para o novo contexto
9. Documente em `docs/`

## Ver também

- [docs/template_novo_case.md](../docs/template_novo_case.md)
- [docs/regras_de_negocio.md](../docs/regras_de_negocio.md)
- [docs/dicionario_de_dados.md](../docs/dicionario_de_dados.md)

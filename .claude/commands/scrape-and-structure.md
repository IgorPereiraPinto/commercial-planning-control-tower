# Scrape and Structure

## Objetivo
Atalho para coleta e estruturação de dados de sites públicos via web scraping.

## Quando usar
Use este command quando o usuário precisar coletar dados de um site ou portal
e estruturá-los em formato analítico (tabela, CSV, DataFrame).

## Instrução de execução
Conduza a resposta nesta ordem:
1. avaliar viabilidade: verificar robots.txt e tipo de conteúdo (estático vs JS)
2. escolher ferramenta: requests+BS4 para estático, Playwright para dinâmico
3. identificar seletores CSS ou XPath dos elementos desejados
4. implementar lógica de paginação se necessário
5. adicionar rate limiting e tratamento de erro
6. estruturar os dados em DataFrame com metadados de rastreabilidade
7. propor formato de persistência (CSV, Parquet, SQLite)

## Formato de saída
1. viabilidade e estratégia de coleta
2. código Python funcional e comentado
3. estrutura dos dados de saída
4. como executar e agendar
5. observações sobre rate limit e boas práticas
6. como persistir os dados

## Skill principal
webscraping.md

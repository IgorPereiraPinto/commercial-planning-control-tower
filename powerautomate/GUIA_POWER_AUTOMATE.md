# Power Automate — Guia Geral dos 5 Fluxos de Automação
## Commercial Planning Control Tower

---

## Visão Geral

Os 5 fluxos de Power Automate fecham o ciclo do Commercial Planning Control Tower:
o dado sai do Excel, passa pelo Python ETL, vai para o SQL Server, alimenta o Power BI
e, via Power Automate, **dispara alertas proativos para os gestores** — sem que ninguém
precise abrir o dashboard para perceber um problema.

```
Ciclo de automação:

  [SQL Server DW]
       │
       ├──→ Fluxo 1 (Segunda, 08h): Alerta de baixo atingimento
       ├──→ Fluxo 2 (Sexta, 17h):   Resumo semanal de performance
       ├──→ Fluxo 3 (Dia 20, 08h):  Alerta de meta em risco
       ├──→ Fluxo 4 (Real-time):    Celebração de meta superada
       └──→ Fluxo 5 (Segunda, 06h): Refresh automático do dataset
```

---

## Os 5 Fluxos — Resumo

| # | Nome                           | Gatilho              | Canal     | Público-alvo     |
|---|--------------------------------|----------------------|-----------|------------------|
| 1 | Alerta de Baixo Atingimento    | Seg, 08h (recorrente)| E-mail    | Gerente do time  |
| 2 | Resumo Semanal de Performance  | Sex, 17h (recorrente)| E-mail    | Todos os gerentes|
| 3 | Alerta de Meta em Risco        | Dia 20, 08h          | E-mail    | Diretoria        |
| 4 | Celebração de Meta Superada    | Power BI (real-time) | Teams     | Canal do time    |
| 5 | Refresh Automático do Dataset  | Seg, 06h (recorrente)| E-mail    | Igor (admin)     |

---

## Pré-requisitos

### 1. Licença

- Power Automate: plano **Premium** (necessário para o conector SQL Server)
  - Alternativa sem licença Premium: usar SharePoint ou Dataverse como intermediário
- Power BI: plano **Pro** ou **Premium** (para refresh via API)
- Microsoft 365: Outlook + Teams já incluídos

### 2. Conectores necessários

| Conector                  | Fluxos que usam | Tipo de autenticação |
|---------------------------|-----------------|----------------------|
| SQL Server                | 1, 2, 3, 5      | SQL Server Auth ou Windows Auth |
| Office 365 Outlook        | 1, 2, 3, 5      | Microsoft 365        |
| Microsoft Teams           | 4               | Microsoft 365        |
| Power BI                  | 4, 5            | Microsoft 365        |
| HTTP (Premium)            | 5               | Sem auth ou Basic    |

### 3. Configurar a conexão SQL Server nos fluxos

Ao adicionar o primeiro step de SQL Server em cada fluxo:
- **Tipo de autenticação:** SQL Server Authentication
- **Servidor:** `noteigor`
- **Banco de dados:** `planejamento_comercial`
- **Usuário / Senha:** as credenciais SQL criadas para o Power Automate

> [REUTILIZAÇÃO]: Para novos projetos, apenas o servidor e banco de dados mudam.
> A estrutura das queries muda conforme as tabelas do novo schema DW.

### 4. Criar um usuário SQL exclusivo para o Power Automate

Execute no SQL Server (SSMS):

```sql
-- Criar usuário com acesso somente-leitura ao schema dw
CREATE LOGIN powerautomate_reader
WITH PASSWORD = 'SuaSenhaAqui#2024';

USE planejamento_comercial;
CREATE USER powerautomate_reader FOR LOGIN powerautomate_reader;
EXEC sp_addrolemember 'db_datareader', 'powerautomate_reader';

-- Permissão de execução de SELECTs apenas no schema dw
GRANT SELECT ON SCHEMA::dw TO powerautomate_reader;
```

> Nunca use a conta de admin (sa) nos conectores do Power Automate.
> O usuário de leitura garante que um fluxo com bug não pode apagar dados.

---

## Estrutura dos arquivos deste diretório

```
powerautomate/
├── GUIA_POWER_AUTOMATE.md              ← este arquivo (visão geral)
├── flows/
│   ├── 01_alerta_baixo_atingimento.md  ← configuração detalhada do Fluxo 1
│   ├── 02_resumo_semanal.md            ← configuração detalhada do Fluxo 2
│   ├── 03_alerta_meta_em_risco.md      ← configuração detalhada do Fluxo 3
│   ├── 04_celebracao_meta_superada.md  ← configuração detalhada do Fluxo 4
│   └── 05_refresh_automatico.md        ← configuração detalhada do Fluxo 5
└── templates/
    └── email_html_base.html            ← template HTML base para e-mails
```

---

## Convenções adotadas nos fluxos

### Nomeação de variáveis

```
varNomeVariavel      → variáveis de valor único (string, integer, float)
arrNomeArray         → variáveis de array/coleção
strHtmlEmail         → string HTML do e-mail
intAtingimento       → número inteiro
fltAtingimentoPct    → float / percentual
strAssunto           → assunto do e-mail
```

### Padrão de e-mail

Todos os e-mails seguem o template de `templates/email_html_base.html`:
- Header com título e período de referência
- Corpo com tabela de dados do SQL
- Footer com link para o dashboard e nota de rodapé
- Cores semafóricas: verde (>= 100%), amarelo (90–99%), vermelho (< 90%)

### Tratamento de erro

Todos os fluxos têm um bloco `Scope` com configuração `Configure run after → has failed`:
- Envia e-mail de erro para Igor com o nome do fluxo e a etapa que falhou
- Inclui o output da ação que gerou erro (para diagnóstico)

---

## Checklist de configuração — todos os fluxos

- [ ] Conexão SQL Server criada com usuário `powerautomate_reader`
- [ ] Fluxo 1 habilitado e testado com dados reais
- [ ] Fluxo 2 habilitado e testado com dados reais
- [ ] Fluxo 3 habilitado e testado com dados reais
- [ ] Fluxo 4 conectado ao alerta correto no Power BI Dataset
- [ ] Fluxo 5 conectado ao dataset correto no Power BI Service
- [ ] E-mails de destinatários atualizados (substitua os placeholders)
- [ ] E-mail de erro configurado para o responsável técnico

---

*Arquivo gerado como parte do Commercial Planning Control Tower.*

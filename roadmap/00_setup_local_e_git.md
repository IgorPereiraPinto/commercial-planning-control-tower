# 00 — Setup Local e Git

## Objetivo
Preparar o ambiente de desenvolvimento antes de rodar qualquer código.

---

## O que fazer nesta etapa

1. Clonar o repositório ou criar a pasta local
2. Criar e ativar o ambiente virtual Python
3. Instalar dependências
4. Configurar o arquivo `.env`
5. Verificar estrutura de pastas

---

## Comandos

```bash
git clone https://github.com/IgorPereiraPinto/planejamento-comercial.git
cd planejamento-comercial

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
pip install -r requirements-dev.txt

copy .env.example .env
```

---

## Por que começar aqui

- isola dependências do projeto
- garante reprodutibilidade entre máquinas
- prepara rastreabilidade via Git desde o início

---

## Próximo passo

[01_visao_geral_do_projeto.md](01_visao_geral_do_projeto.md)

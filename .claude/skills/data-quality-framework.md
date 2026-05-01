---
name: data-quality-framework
description: >
  Especialista em qualidade de dados como entregável formal. Cobre as seis dimensões de
  qualidade: estrutural, domínio, unicidade, regras de negócio, reconciliação e auditoria.
  Gera relatórios de qualidade, define SLAs de dado, implementa validações automatizadas
  em Python e SQL, e apoia governança de dados. Baseado na arquitetura do projeto eabrasil.
  Use sempre que o usuário pedir framework de qualidade de dados, validação de dataset,
  relatório de qualidade, SLA de dado, governança, DQ checks, testes de dados, ou qualquer
  processo formal de validação e monitoramento da qualidade dos dados.
  Trigger para: "framework de qualidade de dados", "valida esses dados", "relatório de
  qualidade", "SLA de dado", "DQ check", "testa esse dataset", "governa esses dados".
---

# Data Quality Framework — Qualidade de Dados como Entregável

## Identidade

Especialista em Qualidade e Governança de Dados. Implementa validações formais, gera
relatórios de qualidade e define SLAs de dado. Trata qualidade como entregável de produto,
não como checagem pontual.

---

## As 6 Dimensões de Qualidade

```
1. ESTRUTURAL     → Colunas existem? Tipos corretos? Schema válido?
2. DOMÍNIO        → Valores estão dentro dos domínios permitidos?
3. UNICIDADE      → Existem duplicatas indevidas?
4. REGRAS NEGÓCIO → Lógicas de negócio estão satisfeitas?
5. RECONCILIAÇÃO  → Totais batem entre fontes?
6. AUDITORIA      → Rastreabilidade e metadados de carga presentes?
```

---

## 1. Engine de Validação

```python
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Callable, List, Any
from datetime import datetime

@dataclass
class RegraQualidade:
    nome: str
    dimensao: str          # estrutural, dominio, unicidade, negocio, reconciliacao, auditoria
    coluna: str = None
    critica: bool = True   # se True, falha bloqueia carga
    descricao: str = ""
    funcao: Callable = None
    resultado: dict = field(default_factory=dict)

    def executar(self, df: pd.DataFrame) -> bool:
        try:
            passou, detalhe = self.funcao(df)
            self.resultado = {
                'status': 'PASSOU' if passou else 'FALHOU',
                'detalhe': detalhe,
                'timestamp': datetime.now().isoformat(),
            }
            return passou
        except Exception as e:
            self.resultado = {'status': 'ERRO', 'detalhe': str(e)}
            return False


class DQChecker:
    """Motor de validação de qualidade de dados."""

    def __init__(self, nome_dataset: str):
        self.nome = nome_dataset
        self.regras: List[RegraQualidade] = []
        self.resultados = []

    def adicionar(self, regra: RegraQualidade):
        self.regras.append(regra)

    # ── Helpers para criar regras comuns ─────────────────────────────
    def coluna_existe(self, coluna: str) -> 'DQChecker':
        def fn(df): return coluna in df.columns, f"Coluna '{coluna}'"
        self.adicionar(RegraQualidade(
            nome=f"coluna_existe_{coluna}", dimensao='estrutural',
            coluna=coluna, funcao=fn,
            descricao=f"Coluna '{coluna}' deve existir"))
        return self

    def sem_nulos(self, coluna: str, max_pct: float = 0.0) -> 'DQChecker':
        def fn(df):
            pct = df[coluna].isna().mean() * 100 if coluna in df.columns else 100
            return pct <= max_pct * 100, f"{pct:.2f}% nulos (limite: {max_pct*100:.1f}%)"
        self.adicionar(RegraQualidade(
            nome=f"sem_nulos_{coluna}", dimensao='dominio',
            coluna=coluna, funcao=fn,
            descricao=f"'{coluna}' sem nulos acima de {max_pct*100:.0f}%"))
        return self

    def valores_validos(self, coluna: str, valores: list) -> 'DQChecker':
        def fn(df):
            if coluna not in df.columns: return False, "Coluna ausente"
            invalidos = ~df[coluna].isin(valores)
            n = invalidos.sum()
            exemplos = df.loc[invalidos, coluna].unique()[:5].tolist()
            return n == 0, f"{n} valores inválidos: {exemplos}"
        self.adicionar(RegraQualidade(
            nome=f"valores_validos_{coluna}", dimensao='dominio',
            coluna=coluna, funcao=fn,
            descricao=f"'{coluna}' só pode ter: {valores}"))
        return self

    def sem_duplicatas(self, subset: list) -> 'DQChecker':
        def fn(df):
            dups = df.duplicated(subset=subset).sum()
            return dups == 0, f"{dups:,} duplicatas por {subset}"
        self.adicionar(RegraQualidade(
            nome=f"sem_dups_{'_'.join(subset)}", dimensao='unicidade',
            funcao=fn, descricao=f"Sem duplicatas por {subset}"))
        return self

    def valor_positivo(self, coluna: str) -> 'DQChecker':
        def fn(df):
            if coluna not in df.columns: return False, "Coluna ausente"
            n = (df[coluna] <= 0).sum()
            return n == 0, f"{n:,} valores <= 0"
        self.adicionar(RegraQualidade(
            nome=f"positivo_{coluna}", dimensao='negocio',
            coluna=coluna, funcao=fn,
            descricao=f"'{coluna}' deve ser positivo"))
        return self

    def total_bate_fonte(self, coluna: str, total_esperado: float,
                          tolerancia_pct: float = 0.01) -> 'DQChecker':
        def fn(df):
            total_real = df[coluna].sum() if coluna in df.columns else 0
            delta_pct = abs(total_real - total_esperado) / total_esperado if total_esperado else 1
            return delta_pct <= tolerancia_pct, (
                f"Real: {total_real:,.2f} | Esperado: {total_esperado:,.2f} | "
                f"Delta: {delta_pct*100:.3f}% (limite: {tolerancia_pct*100:.1f}%)"
            )
        self.adicionar(RegraQualidade(
            nome=f"reconcilia_{coluna}", dimensao='reconciliacao',
            coluna=coluna, funcao=fn,
            descricao=f"Total de '{coluna}' reconciliado com fonte"))
        return self

    def metadados_presentes(self, colunas: list = None) -> 'DQChecker':
        cols = colunas or ['_etl_source', '_etl_loaded_at', '_etl_run_id']
        def fn(df):
            ausentes = [c for c in cols if c not in df.columns]
            return len(ausentes) == 0, f"Ausentes: {ausentes}"
        self.adicionar(RegraQualidade(
            nome="metadados_etl", dimensao='auditoria',
            funcao=fn, descricao="Metadados ETL presentes"))
        return self

    # ── Execução e Relatório ─────────────────────────────────────────
    def executar(self, df: pd.DataFrame) -> pd.DataFrame:
        resultados = []
        criticas_falhadas = 0

        for regra in self.regras:
            passou = regra.executar(df)
            if not passou and regra.critica:
                criticas_falhadas += 1
            resultados.append({
                'dataset':   self.nome,
                'regra':     regra.nome,
                'dimensao':  regra.dimensao,
                'critica':   regra.critica,
                'status':    regra.resultado.get('status'),
                'detalhe':   regra.resultado.get('detalhe'),
                'timestamp': regra.resultado.get('timestamp'),
            })

        df_result = pd.DataFrame(resultados)
        total = len(df_result)
        passou = (df_result['status'] == 'PASSOU').sum()
        falhou = (df_result['status'] == 'FALHOU').sum()

        print(f"\n{'='*60}")
        print(f"DQ REPORT — {self.nome}")
        print(f"{'='*60}")
        print(f"Total: {total} | ✅ {passou} | ❌ {falhou} | Críticas falhas: {criticas_falhadas}")
        if falhou > 0:
            print("\nFalhas:")
            for _, r in df_result[df_result['status']=='FALHOU'].iterrows():
                critica_tag = ' [CRÍTICA]' if r['critica'] else ''
                print(f"  ❌ [{r['dimensao']}]{critica_tag} {r['regra']}: {r['detalhe']}")

        df_result['aprovado'] = criticas_falhadas == 0
        return df_result
```

---

## 2. Uso — Exemplo Completo

```python
# Validação de tabela de vendas
checker = (DQChecker("fVendas")
    # Estrutural
    .coluna_existe('id_venda')
    .coluna_existe('valor_liquido')
    .coluna_existe('data_venda')
    # Domínio
    .sem_nulos('id_venda')
    .sem_nulos('valor_liquido')
    .valores_validos('status', ['APROVADO', 'PENDENTE', 'CANCELADO'])
    # Unicidade
    .sem_duplicatas(['id_venda'])
    # Regras de negócio
    .valor_positivo('valor_liquido')
    # Reconciliação com total da fonte
    .total_bate_fonte('valor_liquido', total_esperado=1_250_000.00, tolerancia_pct=0.005)
    # Auditoria
    .metadados_presentes()
)

df_resultado = checker.executar(df_vendas)

# Bloquear carga se há falhas críticas
if not df_resultado['aprovado'].iloc[0]:
    raise ValueError("❌ DQ crítico falhou — carga bloqueada.")
```

---

## 3. SQL — Checks de Qualidade em Banco

```sql
-- Relatório de qualidade para tabela de vendas (SQL Server)
SELECT 'NULOS id_venda'       AS check_nome,
       SUM(CASE WHEN id_venda IS NULL THEN 1 ELSE 0 END) AS falhas,
       COUNT(*)                                           AS total
FROM dbo.fVendas
UNION ALL
SELECT 'NULOS valor_liquido',
       SUM(CASE WHEN valor_liquido IS NULL THEN 1 ELSE 0 END), COUNT(*)
FROM dbo.fVendas
UNION ALL
SELECT 'VALOR NEGATIVO',
       SUM(CASE WHEN valor_liquido <= 0 THEN 1 ELSE 0 END), COUNT(*)
FROM dbo.fVendas
UNION ALL
SELECT 'STATUS INVALIDO',
       SUM(CASE WHEN status NOT IN ('APROVADO','PENDENTE','CANCELADO') THEN 1 ELSE 0 END),
       COUNT(*)
FROM dbo.fVendas
UNION ALL
SELECT 'DUPLICATAS id_venda',
       COUNT(*) - COUNT(DISTINCT id_venda), COUNT(*)
FROM dbo.fVendas;
```

---

## Regras de Qualidade

- Regras críticas bloqueiam carga — nunca deixar dado ruim chegar à camada Gold
- SLA de dado: definir qual % mínimo de registros válidos por dimensão (ex: 99.5% sem nulos na PK)
- Reconciliação: sempre validar totais com a fonte de origem (ERP, extrato bancário)
- Auditoria: metadados ETL não são opcionais — `_etl_loaded_at` e `_etl_source` obrigatórios
- Rodar DQ checks ANTES da carga Silver e ANTES da carga Gold
- Salvar o relatório de DQ com o run_id para auditoria futura

## Observações

Baseado na arquitetura do projeto eabrasil (danos, nps, manifestacoes).
Skill irmã: `etl-data-lake` para a pipeline de carga.
Skill irmã: `dbt-analytics` para testes de qualidade em dbt.

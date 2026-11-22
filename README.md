# Tech Challenge — Fase 5 | Datathon Passos Mágicos

Projeto de Engenharia de Dados e Analytics para investigar o desenvolvimento educacional dos estudantes da **Associação Passos Mágicos**, com processamento no **Databricks**, visualização em **AI/BI Dashboard** e exploração em linguagem natural usando **Databricks Genie**.

> **Status:** fundação de dados (Marco 1) documentada; pipeline Databricks ainda não implementado.
> Os achados iniciais e as regras de tratamento são **propostas em validação**, não indicadores oficiais da associação.

## Fonte de dados

Uma única planilha original — `BASE DE DADOS PEDE 2024 - DATATHON.xlsx` — contém três abas:

| Aba | Registros | INDE numérico |
|---|---:|---:|
| `PEDE2022` | 860 | 860 |
| `PEDE2023` | 1.014 | 931 |
| `PEDE2024` | 1.156 | 1.054 |

Há **468 RAs presentes nas três abas**, permitindo investigar trajetórias longitudinais **após as verificações de consistência**. Os relatórios PEDE e os relatórios de atividades de 2020–2023 são referências metodológicas e de contexto, não outras bases de registros individuais.

**Privacidade:** os dados individuais da planilha não são versionados neste repositório público. A pasta `data/raw/` é ignorada pelo Git. As análises divulgadas devem usar dados agregados, sem identificar estudantes.

## Arquitetura prevista

```text
Excel (PEDE2022, PEDE2023, PEDE2024)
        │
        ▼
Databricks Bronze — fonte preservada + rastreabilidade
        │
        ▼
Databricks Silver — padronização, qualidade e grão aluno-ano
        │
        ▼
Databricks Gold — métricas e visões analíticas verificadas
        ├──► AI/BI Dashboard
        └──► Genie + perguntas e benchmarks SQL
```

**Grão da tabela Silver:** um registro por `(ra, ano)`. Valores ausentes, marcadores (p. ex. `75` e `INCLUIR`) e divergências históricas serão tratados com regras documentadas e flags auditáveis.

## Estrutura do repositório

```text
.
├── docs/
│   ├── marco1/           # Contrato e diagnóstico de dados
│   ├── arquitetura.md
│   └── decisoes.md
├── data/                 # Instruções (dados brutos fora do Git)
├── scripts/              # Exportação e preparação para ingestão
├── notebooks/            # Databricks: Bronze, Silver e Gold
├── sql/                  # Consultas de referência e views Gold
├── tests/                # Qualidade, consistência e benchmarks
├── genie/                # Semântica, instruções e validações
├── dashboard/            # Especificação e evidências do AI/BI
└── apresentacao/         # Roteiro e artefatos de entrega
```

## Documentos do Marco 1

- [Especificação e regras de negócio](docs/marco1/MARCO1_FUNDACAO_DADOS.md)
- [Dicionário dos 140 campos de origem](docs/marco1/dicionario_campos.csv)
- [Contrato de dados v0.1](docs/marco1/contrato_dados.json)
- [Diagnóstico de qualidade](docs/marco1/resumo_qualidade.json)
- [Arquitetura proposta](docs/arquitetura.md)
- [Decisões e pendências](docs/decisoes.md)

## Roadmap

- [x] **Marco 1 —** Diagnóstico inicial e contrato de dados preliminar
- [ ] **Marco 2 —** Preparação da planilha e ingestão Bronze
- [ ] **Marco 3 —** Tratamento Silver e testes automatizados
- [ ] **Marco 4 —** Consultas analíticas e visões Gold
- [ ] **Marco 5 —** AI/BI Dashboard
- [ ] **Marco 6 —** Genie e validação de perguntas contra SQL
- [ ] **Marco 7 —** Storytelling, apresentação e entrega

## Como iniciar

1. Obtenha a planilha original pelos materiais autorizados do desafio; **não faça commit dela**.
2. Consulte o [contrato de dados](docs/marco1/contrato_dados.json) e as [regras de negócio](docs/marco1/MARCO1_FUNDACAO_DADOS.md).
3. Prepare um workspace Databricks e os arquivos de ingestão locais (procedimento a implementar em `scripts/`).
4. Execute os notebooks na ordem Bronze → Silver → Gold, quando disponibilizados.

> **Nota metodológica:** diferenças entre anos podem refletir mudanças de população ou na definição dos indicadores. Resultados de associação não demonstram, por si só, causalidade.

---
Trabalho acadêmico desenvolvido no contexto do Tech Challenge — Datathon, Fase 5.

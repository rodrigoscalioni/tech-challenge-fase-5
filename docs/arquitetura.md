# Arquitetura proposta (em elaboração)

## Fontes e camadas

- **Fonte única:** `BASE DE DADOS PEDE 2024 - DATATHON.xlsx`, com as abas `PEDE2022`, `PEDE2023` e `PEDE2024`.
- **Bronze:** preservação dos dados originais por aba, incluindo cabeçalhos repetidos e metadados de origem (arquivo, aba, linha, processamento).
- **Silver:** tabela `silver_aluno_ano`, com grão `(ra, ano)`, regras de normalização por ano, flags de qualidade e tratamento explícito de ausências.
- **Gold:** visões agregadas de INDE, IAN, IDA, engajamento, coortes e transições, com denominadores válidos documentados.
- **Consumo:** Databricks AI/BI Dashboard e Genie com instruções de negócio e validações comparadas a SQL de referência.

## Dependências

```text
Planilha Excel -> exportação local sem perda -> Bronze -> Silver -> Gold
                                                           |-> Dashboard
                                                           |-> Genie / SQL referência
```

## Restrições

1. Dados originais de alunos permanecem em armazenamento restrito, fora do GitHub público.
2. A associação entre anos usa o RA como hipótese de identidade; inconsistências devem ser auditadas.
3. Dados de texto livre sobre estudantes, aspectos psicológicos individuais ou escolas específicas não devem ficar disponíveis no Genie gerencial.
4. Antes de comparar indicadores entre anos, verificar diferenças metodológicas e de população.
5. Dados ausentes, erros Excel e códigos sentinela não devem ser convertidos em zero.

Consulte [Marco 1](marco1/MARCO1_FUNDACAO_DADOS.md) para valores de referência, regras e pendências.

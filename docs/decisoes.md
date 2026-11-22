# Registro de decisões e pendências técnicas

| ID | Decisão / questão | Situação | Evidência / encaminhamento |
|---|---|---|---|
| D01 | Uma única planilha com três abas por ano | Confirmada | PEDE2022, PEDE2023, PEDE2024 |
| D02 | Grão principal `RA + ano` | Proposta | Conferir unicidade e variações de atributos |
| D03 | Preservar Bronze sem descartes | Proposta | 3.030 linhas esperadas |
| D04 | Marcadores (`75`, `INCLUIR`, `#N/A`, `#DIV/0!`) não são notas | Proposta | Contrato v0.1, requer tratamento campo a campo |
| D05 | Não reinterpretar código de fase 9 | Pendente | Confirmar regra de 2024 |
| D06 | `Atingiu PV` ausente em 2023 e 2024 | Confirmada na planilha | Não inferir a partir de IPV |
| D07 | Campos históricos replicados não substituem fonte do ano original | Proposta | Validar divergências e cobertura |
| D08 | Ano de ingresso divergente entre observações | Pendente | Investigar 199 RAs entre 2023/2024 |
| D09 | Não publicar Excel bruto no repositório público | Adotada | Dados individuais de estudantes |
| D10 | Benchmark do Genie com consultas SQL | Planejada | Pelo menos cinco perguntas validadas |
| D11 | Revisão editorial do repositório após conclusão de todos os marcos | Planejada | Apresentação end-to-end, não por etapas; preservar histórico técnico de commits |

**Próxima revisão:** implementar exportação local e testes de contagem/colunas e atualizar o contrato a partir dos resultados.

# Marco 2 — Exportação e ingestão Bronze

## Objetivo

Consumir a **única fonte de registros individuais** recebida para o Datathon: `BASE DE DADOS PEDE 2024 - DATATHON.xlsx`. O arquivo contém as abas PEDE2022, PEDE2023 e PEDE2024.

**Observação:** os relatórios de atividades e PEDE são documentação de contexto, não novas planilhas de alunos.

## Por que exportar o Excel primeiro?

As abas contêm cabeçalhos duplicados, tipos mistos, números armazenados como texto e erros Excel (`#N/A`, `#DIV/0!`). A ingestão usa a representação XML do Excel para capturar valores textuais da origem sem avaliar fórmulas nem perder colunas com mesmo nome.

Não estamos criando uma Silver nesta etapa: **`75`, `INCLUIR` e erros permanecem como texto bruto**. Regras de validade serão aplicadas na etapa 3.

## Executar localmente

Pré-requisito: Python 3.10+ (somente biblioteca padrão para exportar; pytest para testes).

```bash
python scripts/exportar_excel.py \
  --input "data/raw/BASE DE DADOS PEDE 2024 - DATATHON.xlsx" \
  --output "data/raw/export"

python -m pytest -q tests/test_exportar_excel.py
```

Outputs locais restritos:

```
data/raw/export/
  pede2022.csv
  pede2023.csv
  pede2024.csv
  manifest.json
```

Cada CSV utiliza cabeçalhos não ambíguos (`c001`, `c002`, etc.) e três colunas técnicas:
- `_source_row`: posição da linha no Excel original;
- `_raw_type_signature`: tipo de cada célula em ordem (`S` texto, `N` número, `E` erro, `B` booleano, `_` vazia);
- `_row_sha256`: hash da posição, sequência de tipos e valores exportados (integridade de registro, não identidade do aluno).

O `manifest.json` (local) contém o SHA-256 do arquivo Excel, metadados das abas, mapeamento de nomes originais por posição, quantidades de linhas, contagens de erros e checksums dos CSVs. O manifest e os CSVs gerados são dados **restritos e não devem ser publicados**.

A exportação textual não converte o número do Excel para float nem arredonda valores: a camada Bronze mantém os textos de origem, e a interpretação semântica só ocorre na Silver. Células vazias são distinguidas de texto vazio pela assinatura de tipos. **Não use os CSVs gerados como base de planilha para edição; são artefatos de ingestão.**

## Upload no Databricks

1. No workspace Databricks com Unity Catalog, crie ou selecione catálogo e schema autorizados.
2. Crie um Volume gerenciado (por exemplo, `pede_raw`) e envie os 4 arquivos do diretório `data/raw/export/` ao **diretório raiz desse Volume** usando a interface da plataforma.
3. Importe o notebook `notebooks/01_ingestao_bronze.py` como Databricks notebook.
4. Preencha os parâmetros `catalog`, `schema`, `volume` e execute.
5. O notebook valida SHA dos CSVs, quantidade de colunas, contagem de linhas, unicidade de `_source_row` e escreve três tabelas Delta `bronze_pede_2022`, `bronze_pede_2023`, `bronze_pede_2024`.
6. Examine os totais agregados no fim do notebook; **não publique previews com registros individuais**.

O notebook exige acesso a `/Volumes/<catalog>/<schema>/<volume>/...`. Caso a configuração de Volume seja indisponível no workspace, é necessário adaptar o caminho após verificar as permissões efetivas, sem embutir credenciais no código.

## Critérios de aceite

- [x] Script de exportação preparado e testado com arquivo sintético.
- [x] Comparação local de linhas, colunas e valores de controle com a planilha recebida.
- [ ] Upload dos quatro arquivos no Volume do Databricks realizado.
- [ ] Notebook executado sem erros no workspace de destino.
- [ ] Três tabelas Delta criadas e contagens reconciliadas.

Contagens de controle esperadas (não são novos resultados analíticos):

| Ano | Linhas | Colunas originais |
|---|---:|---:|
| 2022 | 860 | 42 |
| 2023 | 1.014 | 48 |
| 2024 | 1.156 | 50 |

## Privacidade e limitações

- Não publicar dados individuais, CSVs, manifest gerado ou imagens com informações identificáveis.
- Preserve a planilha original em armazenamento controlado.
- A Bronze captura valores exportados **como texto** com metadados de tipo e proveniência, mas não substitui o XLSX em fórmulas, formatação, comentários ou macros; o XLSX segue sendo a fonte primária.
- A correspondência longitudinal por RA e a interpretação dos campos devem ser testadas na Silver.
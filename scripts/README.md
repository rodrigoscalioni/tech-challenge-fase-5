# Scripts de preparação

O script [`exportar_excel.py`](exportar_excel.py) exporta as três abas do Excel original para CSVs na pasta restrita `data/raw/export/`, preservando tipos textuais de origem, erros Excel e cabeçalhos duplicados com mapeamento posicional.

```bash
python scripts/exportar_excel.py --input "data/raw/BASE DE DADOS PEDE 2024 - DATATHON.xlsx" --output data/raw/export
```

Os CSVs e o manifest são **restritos** e não devem ser publicados. Consulte [o guia de ingestão](../docs/MARCO2_INGESTAO_BRONZE.md).

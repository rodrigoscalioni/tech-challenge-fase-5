# Testes e validações

[`test_exportar_excel.py`](test_exportar_excel.py) utiliza planilha XLSX sintética criada em memória, sem dados de alunos, para verificar cabeçalhos repetidos, erros Excel, números como texto, CSV multilinha e rejeição de fórmulas.

```bash
python -m pytest -q tests/test_exportar_excel.py
```

**Teste local executado:** 4 testes passaram. Os controles do Excel real (860 / 1.014 / 1.156 linhas e 42 / 48 / 50 colunas) foram reconciliados na exportação local. A validação das tabelas Delta no Databricks ainda depende da execução do notebook.

Na Silver/Gold acrescentaremos regras de unicidade `(RA, ano)`, valores inválidos, normalização, reconciliação de métricas e benchmarks SQL do Genie.

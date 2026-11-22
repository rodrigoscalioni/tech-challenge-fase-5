# Scripts de preparação

Nesta pasta ficarão os scripts locais para leitura e exportação da única planilha Excel, preservação dos dados e verificação dos controles de ingestão.

**Planejado:** `exportar_excel.py` com nomes de colunas duplicados preservados por posição, fonte/aba/linha e tratamento das células de erro. Não utilizar `pandas.read_excel` sem tratamento explícito de cabeçalhos duplicados.

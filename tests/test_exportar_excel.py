"""Testes offline com planilha OOXML sintética, sem dados de alunos."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from exportar_excel import SHEETS, excel_column_index, excel_column_name, export_workbook  # noqa: E402


def create_fixture(path: Path, *, with_formula=False):
    workbook = ('<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                + ''.join(f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"/>' for i, name in enumerate(SHEETS, 1))
                + '</sheets></workbook>')
    rel = ('<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
           + ''.join(f'<Relationship Id="rId{i}" Target="worksheets/sheet{i}.xml"/>' for i in range(1, 4))
           + '</Relationships>')
    shared = ('<?xml version="1.0"?><sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
              '<si><t>RA</t></si><si><t>Nota</t></si><si><t>Teste</t></si><si><t>RA-1</t></si>'
              '<si><t>comentário com vírgula, aspas " e nova linha\npróxima</t></si></sst>')
    rows = ('<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c>'
            '<c r="C1" t="s"><v>1</v></c><c r="D1" t="s"><v>2</v></c></row>'
            '<row r="2"><c r="A2" t="s"><v>3</v></c><c r="B2"><v>8.25</v></c>'
            '<c r="C2" t="e"><v>#DIV/0!</v></c><c r="D2" t="s"><v>4</v></c></row>'
            '<row r="3"><c r="A3" t="s"><v>3</v></c><c r="B3"><v>75</v></c>'
            + ('<c r="C3"><f>1+1</f><v>2</v></c>' if with_formula else '<c r="C3" t="s"><v>3</v></c>')
            + '<c r="D3" t="inlineStr"><is><t>INCLUIR</t></is></c></row>')
    with ZipFile(path, 'w') as archive:
        archive.writestr('xl/workbook.xml', workbook)
        archive.writestr('xl/_rels/workbook.xml.rels', rel)
        archive.writestr('xl/sharedStrings.xml', shared)
        for i in range(1, 4):
            archive.writestr(f'xl/worksheets/sheet{i}.xml',
                             f'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{rows}</sheetData></worksheet>')


def test_column_index_round_trip():
    for number in (0, 1, 25, 26, 49, 701):
        assert excel_column_index(f'{excel_column_name(number)}42') == number


def test_exports_preserving_duplicates_errors_and_multiline(tmp_path):
    source = tmp_path / 'fixture.xlsx'
    create_fixture(source)
    manifest = export_workbook(source, tmp_path / 'export')
    for name in SHEETS:
        info = manifest['sheets'][name]
        assert info['row_count'] == 2
        assert info['column_count'] == 4
        assert info['excel_error_cells'] == 1
        assert info['repeated_headers'] == ['Nota']
        assert info['columns'][1]['original_header'] == info['columns'][2]['original_header'] == 'Nota'
        with (tmp_path / 'export' / info['csv_filename']).open(encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2
        assert rows[0]['_source_row'] == '2'
        assert rows[0]['c002'] == '8.25'
        assert rows[0]['c003'] == '#DIV/0!'
        assert rows[0]['c004'] == 'comentário com vírgula, aspas " e nova linha\npróxima'
        assert rows[0]['_raw_type_signature'] == 'SNES'
        assert rows[1]['c002'] == '75'
        assert rows[1]['c004'] == 'INCLUIR'
        assert len(rows[0]['_row_sha256']) == 64
    assert (tmp_path / 'export' / 'manifest.json').is_file()
    assert json.loads((tmp_path / 'export' / 'manifest.json').read_text(encoding='utf-8'))['source_sha256']


def test_rejects_uncalculated_or_cached_formulas(tmp_path):
    source = tmp_path / 'formula.xlsx'
    create_fixture(source, with_formula=True)
    with pytest.raises(ValueError, match='Fórmula encontrada'):
        export_workbook(source, tmp_path / 'export')


def test_missing_source(tmp_path):
    with pytest.raises(FileNotFoundError):
        export_workbook(tmp_path / 'nao_existe.xlsx', tmp_path / 'saida')
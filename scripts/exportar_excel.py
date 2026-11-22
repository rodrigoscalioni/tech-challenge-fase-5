#!/usr/bin/env python3
"""Exporta as abas PEDE para CSVs de ingestão Bronze sem publicar os dados.

Usa somente a biblioteca padrão e lê o OOXML diretamente: preserva cabeçalhos
repetidos por posição, erros do Excel e a representação textual de números.
Não avalia fórmulas e não altera a planilha original.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import posixpath
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

SHEETS = ("PEDE2022", "PEDE2023", "PEDE2024")
MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_OFFICE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_PACKAGE = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"m": MAIN, "r": REL_OFFICE}
CELL_REF = re.compile(r"^([A-Z]+)([1-9][0-9]*)$")
TYPE_CODE = {"s": "S", "str": "S", "inlineStr": "S", "n": "N", "b": "B", "e": "E"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def excel_column_index(reference: str) -> int:
    match = CELL_REF.match(reference)
    if not match:
        raise ValueError(f"Referência de célula inválida: {reference!r}")
    number = 0
    for letter in match.group(1):
        number = number * 26 + ord(letter) - ord("A") + 1
    return number - 1


def excel_column_name(index: int) -> str:
    index += 1
    result = ""
    while index:
        index, rem = divmod(index - 1, 26)
        result = chr(ord("A") + rem) + result
    return result


def read_shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    values = []
    for item in root.findall("m:si", NS):
        # Evita incluir elementos de pronúncia (rPh) no texto da célula.
        parts = [node.text or "" for node in item.findall("m:t", NS)]
        for run in item.findall("m:r", NS):
            parts.extend(node.text or "" for node in run.findall("m:t", NS))
        values.append("".join(parts))
    return values


def sheet_paths(archive: ZipFile) -> dict[str, str]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {
        item.attrib["Id"]: item.attrib["Target"]
        for item in relationships.findall(f"{{{REL_PACKAGE}}}Relationship")
    }
    result = {}
    for item in workbook.findall("m:sheets/m:sheet", NS):
        rid = item.attrib[f"{{{REL_OFFICE}}}id"]
        target = targets[rid]
        location = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("xl", target))
        if location not in archive.namelist():
            raise ValueError(f"Planilha interna não encontrada: {location}")
        result[item.attrib["name"]] = location
    return result


def parse_cell(cell: ET.Element, strings: list[str]) -> tuple[str, str]:
    raw_type = cell.get("t", "n")
    if cell.find("m:f", NS) is not None:
        raise ValueError(f"Fórmula encontrada em {cell.get('r')}; exportação não calcula fórmulas")
    raw = cell.findtext("m:v", default=None, namespaces=NS)
    if raw_type == "s":
        value = strings[int(raw)] if raw is not None else ""
    elif raw_type == "inlineStr":
        inline = cell.find("m:is", NS)
        value = "" if inline is None else "".join(t.text or "" for t in inline.findall(".//m:t", NS))
    else:
        value = "" if raw is None else raw
    code = "_" if raw is None and raw_type not in ("inlineStr",) else TYPE_CODE.get(raw_type, "?")
    return value, code


def read_rows(archive: ZipFile, path: str, strings: list[str]):
    root = ET.fromstring(archive.read(path))
    for row in root.findall("m:sheetData/m:row", NS):
        number = int(row.attrib["r"])
        cells = {}
        for cell in row.findall("m:c", NS):
            idx = excel_column_index(cell.attrib["r"])
            cells[idx] = parse_cell(cell, strings)
        yield number, cells


def export_workbook(source: Path, destination: Path) -> dict:
    if not source.is_file():
        raise FileNotFoundError(f"Planilha não encontrada: {source}")
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {
        "format_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_filename": source.name,
        "source_sha256": sha256_file(source),
        "note": "Arquivos CSV e valores individuais devem ficar fora do GitHub público.",
        "sheets": {},
    }
    with ZipFile(source) as archive:
        shared_strings = read_shared_strings(archive)
        paths = sheet_paths(archive)
        missing = set(SHEETS) - paths.keys()
        if missing:
            raise ValueError(f"Abas obrigatórias ausentes: {sorted(missing)}")
        for sheet in SHEETS:
            iterator = iter(read_rows(archive, paths[sheet], shared_strings))
            try:
                header_row, headers = next(iterator)
            except StopIteration as error:
                raise ValueError(f"Aba vazia: {sheet}") from error
            if header_row != 1:
                raise ValueError(f"Cabeçalho deve estar na linha 1: {sheet}")
            ncols = max(headers, default=-1) + 1
            if ncols == 0:
                raise ValueError(f"Cabeçalho ausente: {sheet}")
            original_headers = [headers.get(i, ("", "_"))[0] for i in range(ncols)]
            if any(not value.strip() for value in original_headers):
                raise ValueError(f"Cabeçalho em branco na aba {sheet}")
            cols = [f"c{i + 1:03d}" for i in range(ncols)]
            path = destination / f"{sheet.lower()}.csv"
            counts = Counter()
            error_cells = 0
            blank_cells = 0
            rows_written = 0
            last_row = header_row
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream, quoting=csv.QUOTE_ALL, lineterminator="\n")
                writer.writerow(["_source_row", "_raw_type_signature", "_row_sha256", *cols])
                for number, cells in iterator:
                    if number <= last_row:
                        raise ValueError(f"Linhas fora de ordem em {sheet}")
                    last_row = number
                    if any(i >= ncols for i in cells):
                        raise ValueError(f"Linha {number} em {sheet} possui colunas além do cabeçalho")
                    values = []
                    codes = []
                    for idx in range(ncols):
                        value, code = cells.get(idx, ("", "_"))
                        values.append(value)
                        codes.append(code)
                        counts[code] += 1
                    if all(code == "_" for code in codes):
                        continue  # Não gerar linhas apenas de formatação.
                    error_cells += codes.count("E")
                    blank_cells += codes.count("_")
                    signature = "".join(codes)
                    digest_input = json.dumps([number, signature, values], ensure_ascii=False, separators=(",", ":"))
                    row_digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()
                    writer.writerow([number, signature, row_digest, *values])
                    rows_written += 1
            duplicates = sorted([name for name, freq in Counter(original_headers).items() if freq > 1])
            manifest["sheets"][sheet] = {
                "year": int(sheet[-4:]),
                "csv_filename": path.name,
                "csv_sha256": sha256_file(path),
                "source_header_row": header_row,
                "row_count": rows_written,
                "column_count": ncols,
                "columns": [
                    {"position": i + 1, "excel_column": excel_column_name(i), "csv_name": cols[i], "original_header": original_headers[i]}
                    for i in range(ncols)
                ],
                "repeated_headers": duplicates,
                "raw_type_counts": dict(counts),
                "excel_error_cells": error_cells,
                "blank_cells": blank_cells,
            }
    with (destination / "manifest.json").open("w", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Caminho do Excel PEDE original")
    parser.add_argument("--output", type=Path, default=Path("data/raw/export"), help="Destino restrito para CSVs e manifest")
    args = parser.parse_args()
    result = export_workbook(args.input, args.output)
    for name, info in result["sheets"].items():
        print(f"{name}: {info['row_count']} registros, {info['column_count']} colunas, {info['excel_error_cells']} erros Excel")
    print("Manifest criado; não publique arquivos CSV contendo registros de alunos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# Databricks notebook source
# MAGIC %md
# MAGIC # Fase 5 — Marco 2: Ingestão Bronze PEDE
# MAGIC Fonte: uma planilha Excel, três abas convertidas em CSVs **restritos**.
# MAGIC Não apresentar dados individuais em `display()` ou logs públicos.
# MAGIC Pré-requisito: upload dos três CSVs + `manifest.json` na raiz de um Volume do Unity Catalog.

# COMMAND ----------

import hashlib
import json
import re
from pathlib import Path

from pyspark.sql import functions as F

# COMMAND ----------

# Parâmetros: se o catálogo ficar em branco, usa o catálogo atual da sessão.
dbutils.widgets.text("catalog", "", "Catálogo (em branco = atual)")
dbutils.widgets.text("schema", "default", "Schema")
dbutils.widgets.text("volume", "pede_raw", "Volume com os arquivos exportados")

VALID_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def valid_identifier(value: str) -> str:
    if not VALID_NAME.fullmatch(value):
        raise ValueError(f"Identificador inválido de catálogo/schema/volume: {value!r}")
    return value


catalog = dbutils.widgets.get("catalog").strip() or spark.sql("SELECT current_catalog()").first()[0]
catalog = valid_identifier(catalog)
schema = valid_identifier(dbutils.widgets.get("schema").strip())
volume = valid_identifier(dbutils.widgets.get("volume").strip())
volume_root = Path(f"/Volumes/{catalog}/{schema}/{volume}")
manifest_path = volume_root / "manifest.json"

if not manifest_path.is_file():
    raise FileNotFoundError(f"Manifest não localizado no Volume: {manifest_path}")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
if manifest.get("format_version") != 1:
    raise ValueError("Versão de manifest não suportada")

# Controles definidos no Marco 1. Não devem ser alterados para 'fazer o teste passar'.
EXPECTED = {
    "PEDE2022": {"rows": 860, "columns": 42},
    "PEDE2023": {"rows": 1014, "columns": 48},
    "PEDE2024": {"rows": 1156, "columns": 50},
}


# COMMAND ----------


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validated_csv(sheet_name: str, config: dict):
    sheet = manifest.get("sheets", {}).get(sheet_name)
    if not sheet:
        raise ValueError(f"Aba ausente no manifest: {sheet_name}")
    csv_name = f"{sheet_name.lower()}.csv"
    if sheet.get("csv_filename") != csv_name:
        raise ValueError(f"Nome do CSV inesperado para {sheet_name}")
    ncols = config["columns"]
    if sheet.get("row_count") != config["rows"] or sheet.get("column_count") != ncols:
        raise ValueError(f"Manifest incompatível com as contagens oficiais de {sheet_name}")
    if len(sheet.get("columns", [])) != ncols:
        raise ValueError(f"Mapeamento incompleto de cabeçalhos: {sheet_name}")
    column_names = [f"c{i:03d}" for i in range(1, ncols + 1)]
    if [c["csv_name"] for c in sheet["columns"]] != column_names:
        raise ValueError(f"Colunas sem correspondência por posição em {sheet_name}")

    path = volume_root / csv_name
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo CSV não localizado: {path}")
    if file_sha256(path) != sheet["csv_sha256"]:
        raise ValueError(f"SHA-256 divergente: {sheet_name}; reenvie o arquivo correto")

    reader = (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "false")
        .option("multiLine", "true")
        .option("quote", '"')
        .option("escape", '"')
        .option("encoding", "UTF-8")
        .option("mode", "FAILFAST")
    )
    df = reader.load(str(path))
    required = ["_source_row", "_raw_type_signature", "_row_sha256", *column_names]
    if df.columns != required:
        raise ValueError(f"Cabeçalhos CSV inesperados para {sheet_name}: confira o exportador")

    total = df.count()
    if total != config["rows"]:
        raise ValueError(f"Contagem inesperada de {sheet_name}: {total}; esperado {config['rows']}")
    if df.filter(F.col("_source_row").isNull()).limit(1).count():
        raise ValueError(f"Linhas sem origem em {sheet_name}")
    if df.select("_source_row").distinct().count() != total:
        raise ValueError(f"Linhas de origem repetidas em {sheet_name}")
    if df.filter(F.length("_raw_type_signature") != ncols).limit(1).count():
        raise ValueError(f"Assinatura de tipos inválida em {sheet_name}")
    if df.filter(F.length("_row_sha256") != 64).limit(1).count():
        raise ValueError(f"Hash de linha inválido em {sheet_name}")

    # Dados brutos ficam como texto. Nenhuma regra de saneamento da Silver é aplicada aqui.
    return (
        df.withColumn("_source_sheet", F.lit(sheet_name))
        .withColumn("_source_year", F.lit(sheet["year"]).cast("int"))
        .withColumn("_source_file_sha256", F.lit(manifest["source_sha256"]))
        .withColumn("_ingested_at_utc", F.current_timestamp())
    )


# COMMAND ----------

summary = []
for sheet_name, config in EXPECTED.items():
    dataframe = validated_csv(sheet_name, config)
    table_name = f"bronze_pede_{sheet_name[-4:]}"
    full_table = f"`{catalog}`.`{schema}`.`{table_name}`"
    (
        dataframe.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(full_table)
    )
    loaded = spark.table(full_table).count()
    if loaded != config["rows"]:
        raise AssertionError(f"Ingestão Delta não reconciliada: {full_table}")
    summary.append({"table": full_table, "rows": loaded, "source_columns": config["columns"]})

# Imprimir APENAS agregados para evitar expor RAs e informações de alunos.
for item in summary:
    print(f"OK: {item['table']} — {item['rows']} registros; {item['source_columns']} colunas de origem")
print("Marco 2 — carga Bronze concluída. Iniciar Silver somente após revisão das regras do contrato.")
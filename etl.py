"""
ETL simple para e-commerce usando archivos Excel como fuente y SQLite como destino.

Estructura de carpetas esperada:

ecommerce_etl/
├── data/
│   ├── clientes.xlsx
│   ├── productos.xlsx
│   ├── ventas.xlsx
│   └── detalle_ventas.xlsx
├── database/
│   └── (se creará ecommerce.db)
└── etl.py   <- este archivo

Requisitos (instalar con pip):
- pandas
- sqlalchemy
- openpyxl

Ejemplo instalación:
    pip install pandas sqlalchemy openpyxl

Uso (desde la raíz del proyecto):
    python etl.py --step extract
    python etl.py --step transform
    python etl.py --step load
    python etl.py --step all

El script está diseñado para ejecutarse "punto a punto". Cada paso escribe artefactos intermedios en memoria y muestra reportes básicos.

"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import Dict, Tuple
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# Configuración
DATA_DIR = Path("data")
DB_DIR = Path("database")
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "ecommerce.db"
SQLITE_CONN_STR = f"sqlite:///{DB_PATH.as_posix()}"

# Nombres de archivos por defecto
FILES = {
    "clientes": DATA_DIR / "clientes.xlsx",
    "productos": DATA_DIR / "productos.xlsx",
    "ventas": DATA_DIR / "ventas.xlsx",
    "detalle_ventas": DATA_DIR / "detalle_ventas.xlsx",
}

# Lectura / Extracción


def extract(files: Dict[str, Path]) -> Dict[str, pd.DataFrame]:
    """Lee los archivos Excel y devuelve un dict de DataFrames.

    Devuelve también un resumen con filas y columnas leídas.
    """
    loaded = {}
    for key, path in files.items():
        if not path.exists():
            print(f"[ERROR] Archivo no encontrado: {path}")
            sys.exit(1)
        df = pd.read_excel(path, engine="openpyxl")
        print(
            f"[EXTRACT] {key}: {path} -> {df.shape[0]} filas x {df.shape[1]} columnas")
        loaded[key] = df
    return loaded

# Transformaciones / Validaciones


def validate_and_transform(dfs: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, object]]:
    """Aplica validaciones y transformaciones básicas.

    - Normaliza nombres de columnas (lowercase, sin espacios)
    - Valida claves foráneas y reporta inconsistencias
    - Calcula importe en detalle_ventas si falta
    - Convierte tipos: fechas, numericos
    """
    report = {}
    # Normalizar nombres de columnas
    for key, df in dfs.items():
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        dfs[key] = df

    # Tipos y conversiones básicas
    # clientes.fecha_alta -> datetime
    if "clientes" in dfs:
        if "fecha_alta" in dfs["clientes"].columns:
            dfs["clientes"]["fecha_alta"] = pd.to_datetime(
                dfs["clientes"]["fecha_alta"], errors="coerce")

    # ventas.fecha -> datetime
    if "ventas" in dfs:
        if "fecha" in dfs["ventas"].columns:
            dfs["ventas"]["fecha"] = pd.to_datetime(
                dfs["ventas"]["fecha"], errors="coerce")

    # productos.precio_unitario -> numeric
    if "productos" in dfs:
        if "precio_unitario" in dfs["productos"].columns:
            dfs["productos"]["precio_unitario"] = pd.to_numeric(
                dfs["productos"]["precio_unitario"], errors="coerce")

    # detalle_ventas: calcular importe si no existe o está mal
    if "detalle_ventas" in dfs:
        dv = dfs["detalle_ventas"]
        if "cantidad" in dv.columns:
            dv["cantidad"] = pd.to_numeric(
                dv["cantidad"], errors="coerce").fillna(0).astype(int)
        if "precio_unitario" in dv.columns:
            dv["precio_unitario"] = pd.to_numeric(
                dv["precio_unitario"], errors="coerce")
        # crear importe si no existe
        if "importe" not in dv.columns or dv["importe"].isnull().all():
            dv["importe"] = dv["cantidad"] * dv["precio_unitario"]
        else:
            # corregir valores nulos puntuales
            dv.loc[dv["importe"].isnull(), "importe"] = dv["cantidad"] * \
                dv["precio_unitario"]
        dfs["detalle_ventas"] = dv

    # Validar FK: ventas.id_cliente -> clientes.id_cliente
    fk_issues = {}
    if "ventas" in dfs and "clientes" in dfs:
        ventas = dfs["ventas"]
        clientes = dfs["clientes"]
        if "id_cliente" in ventas.columns and "id_cliente" in clientes.columns:
            ventas_ids = set(
                ventas["id_cliente"].dropna().astype(int).unique())
            clientes_ids = set(
                clientes["id_cliente"].dropna().astype(int).unique())
            missing_clients = sorted(list(ventas_ids - clientes_ids))
            fk_issues["ventas.id_cliente_missing_in_clientes"] = missing_clients
            if missing_clients:
                print(
                    f"[WARN] {len(missing_clients)} id_cliente en ventas no existen en clientes. Ej: {missing_clients[:5]}")

    # Validar FK: detalle_ventas.id_venta -> ventas.id_venta
    if "detalle_ventas" in dfs and "ventas" in dfs:
        dv = dfs["detalle_ventas"]
        ventas = dfs["ventas"]
        if "id_venta" in dv.columns and "id_venta" in ventas.columns:
            dv_ids = set(dv["id_venta"].dropna().astype(int).unique())
            ventas_ids = set(ventas["id_venta"].dropna().astype(int).unique())
            missing_ventas = sorted(list(dv_ids - ventas_ids))
            fk_issues["detalle_ventas.id_venta_missing_in_ventas"] = missing_ventas
            if missing_ventas:
                print(
                    f"[WARN] {len(missing_ventas)} id_venta en detalle_ventas no existen en ventas. Ej: {missing_ventas[:5]}")

    # Validar FK: detalle_ventas.id_producto -> productos.id_producto
    if "detalle_ventas" in dfs and "productos" in dfs:
        dv = dfs["detalle_ventas"]
        productos = dfs["productos"]
        if "id_producto" in dv.columns and "id_producto" in productos.columns:
            dv_prod_ids = set(dv["id_producto"].dropna().astype(int).unique())
            prod_ids = set(
                productos["id_producto"].dropna().astype(int).unique())
            missing_prod = sorted(list(dv_prod_ids - prod_ids))
            fk_issues["detalle_ventas.id_producto_missing_in_productos"] = missing_prod
            if missing_prod:
                print(
                    f"[WARN] {len(missing_prod)} id_producto en detalle_ventas no existen en productos. Ej: {missing_prod[:5]}")

    report["fk_issues"] = fk_issues
    return dfs, report

# Carga a DB


def load_to_sqlite(dfs: Dict[str, pd.DataFrame], conn_str: str = SQLITE_CONN_STR):
    """Carga los DataFrames a SQLite. Reemplaza tablas si ya existen.

    Mapea tipos mínimos para mantener compatibilidad.
    """
    engine = create_engine(conn_str, echo=False)

    # Mapeo simple de dtypes para to_sql
    dtype_map = {
        # sqlalchemy types can be specified if needed; pandas infers decent defaults for SQLite
    }

    # Orden de carga: productos, clientes, ventas, detalle_ventas
    order = ["productos", "clientes", "ventas", "detalle_ventas"]
    for name in order:
        if name in dfs:
            df = dfs[name]
            # normalizar columnas a snake_case ya hecho antes
            print(
                f"[LOAD] Cargando tabla {name} -> {DB_PATH} ({df.shape[0]} filas)")
            df.to_sql(name, con=engine, if_exists="replace", index=False)

    print("[LOAD] Carga finalizada.")

# Funciones auxiliares


def save_report(report: dict, path: Path = Path("etl_report.txt")):
    with open(path, "w", encoding="utf-8") as f:
        f.write("ETL REPORT\n")
        import json
        f.write(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"[REPORT] Guardado en {path}")

# Orquestador simple


def main(step: str):
    print(f"Iniciando ETL - paso: {step}")

    if step == "extract":
        dfs = extract(FILES)
        # Guardar snapshots intermedios opcionalmente
        for k, df in dfs.items():
            out = DATA_DIR / f"{k}_snapshot.csv"
            df.to_csv(out, index=False)
            print(f"[EXTRACT] Snapshot guardado: {out}")
        return

    if step == "transform":
        dfs = extract(FILES)
        dfs, report = validate_and_transform(dfs)
        save_report(report, Path("etl_report_transform.json"))
        # Guardar dataframes transformados para inspección
        for k, df in dfs.items():
            out = DATA_DIR / f"{k}_transformed.csv"
            df.to_csv(out, index=False)
            print(f"[TRANSFORM] Guardado: {out}")
        return

    if step == "load":
        dfs = extract(FILES)
        dfs, report = validate_and_transform(dfs)
        load_to_sqlite(dfs)
        save_report(report, Path("etl_report_load.json"))
        return

    if step == "all":
        dfs = extract(FILES)
        dfs, report = validate_and_transform(dfs)
        load_to_sqlite(dfs)
        save_report(report, Path("etl_report_all.json"))
        return

    print(f"Paso desconocido: {step}. Use extract|transform|load|all")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ETL simple desde Excel a SQLite")
    parser.add_argument("--step", type=str, required=True,
                        help="Paso a ejecutar: extract|transform|load|all")
    args = parser.parse_args()
    main(args.step)

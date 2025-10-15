from pathlib import Path
from typing import Dict
import sys
import pandas as pd

DATA_DIR = Path("data")
FILES = {
    "clientes": DATA_DIR / "clientes.xlsx",
    "productos": DATA_DIR / "productos.xlsx",
    "ventas": DATA_DIR / "ventas.xlsx",
    "detalle_ventas": DATA_DIR / "detalle_ventas.xlsx",
}


def extract(files: Dict[str, Path]) -> Dict[str, pd.DataFrame]:
    """Lee los archivos Excel y devuelve un dict de DataFrames."""
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

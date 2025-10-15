from typing import Dict
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

DB_DIR = Path("database")
DB_PATH = DB_DIR / "ecommerce.db"
SQLITE_CONN_STR = f"sqlite:///{DB_PATH.as_posix()}"


def load_to_sqlite(dfs: Dict[str, pd.DataFrame], conn_str: str = SQLITE_CONN_STR):
    """Carga los DataFrames a SQLite. Reemplaza tablas si ya existen."""
    engine = create_engine(conn_str, echo=False)
    order = ["productos", "clientes", "ventas", "detalle_ventas"]
    for name in order:
        if name in dfs:
            df = dfs[name]
            print(
                f"[LOAD] Cargando tabla {name} -> {DB_PATH} ({df.shape[0]} filas)")
            df.to_sql(name, con=engine, if_exists="replace", index=False)
    print("[LOAD] Carga finalizada.")

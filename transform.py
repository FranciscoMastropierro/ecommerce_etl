from typing import Dict, Tuple
import pandas as pd
from pathlib import Path


def validate_and_transform(dfs: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, object]]:
    """Aplica validaciones y transformaciones básicas."""
    report = {}
    # Normalizar nombres de columnas
    for key, df in dfs.items():
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        dfs[key] = df

    # Tipos y conversiones básicas
    if "clientes" in dfs:
        if "fecha_alta" in dfs["clientes"].columns:
            dfs["clientes"]["fecha_alta"] = pd.to_datetime(
                dfs["clientes"]["fecha_alta"], errors="coerce")
    if "ventas" in dfs:
        if "fecha" in dfs["ventas"].columns:
            dfs["ventas"]["fecha"] = pd.to_datetime(
                dfs["ventas"]["fecha"], errors="coerce")
    if "productos" in dfs:
        if "precio_unitario" in dfs["productos"].columns:
            dfs["productos"]["precio_unitario"] = pd.to_numeric(
                dfs["productos"]["precio_unitario"], errors="coerce")
    if "detalle_ventas" in dfs:
        dv = dfs["detalle_ventas"]
        if "cantidad" in dv.columns:
            dv["cantidad"] = pd.to_numeric(
                dv["cantidad"], errors="coerce").fillna(0).astype(int)
        if "importe" not in dv.columns or dv["importe"].isnull().all():
            dv["importe"] = dv["cantidad"] * dv["precio_unitario"]
        dfs["detalle_ventas"] = dv

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

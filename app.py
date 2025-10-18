# app.py
import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Aurelion Dashboard", layout="wide")

# --- CONEXIÓN A LA BASE ---


@st.cache_data
def get_data():
    import os

    db_path = "database/ecommerce.db"

    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        ventas = pd.read_sql_query("SELECT * FROM ventas", conn)
        clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
        detalle = pd.read_sql_query("SELECT * FROM detalle_ventas", conn)
        productos = pd.read_sql_query("SELECT * FROM productos", conn)
        conn.close()
    else:
        # Carga desde los Excel si la base no está disponible
        ventas = pd.read_excel("data/ventas.xlsx")
        clientes = pd.read_excel("data/clientes.xlsx")
        detalle = pd.read_excel("data/detalle_ventas.xlsx")
        productos = pd.read_excel("data/productos.xlsx")

    return ventas, clientes, detalle, productos


ventas, clientes, detalle, productos = get_data()

# --- TRANSFORMACIÓN / UNIÓN ---
df = (
    ventas
    .merge(clientes, on="id_cliente", suffixes=("", "_cliente"))
    .merge(detalle, on="id_venta")
    .merge(productos, on="id_producto", suffixes=("", "_producto"))
)

# Cálculo adicional si falta
if "importe" not in df.columns or df["importe"].isnull().any():
    df["importe"] = df["cantidad"] * df["precio_unitario"]

# --- Normalización de fecha ---
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

# --- Filtros ---
st.sidebar.header("Filtros")

filtro_ciudad = st.sidebar.multiselect(
    "Ciudad del cliente:",
    options=df["ciudad"].dropna().unique(),
)

filtro_categoria = st.sidebar.multiselect(
    "Categoría del producto:",
    options=df["categoria"].dropna().unique(),
)

# Se trata de fijar
min_fecha = df["fecha"].min()
max_fecha = df["fecha"].max()

filtro_fecha = st.sidebar.date_input(
    "Rango de fechas:",
    value=(min_fecha, max_fecha),
    min_value=min_fecha,
    max_value=max_fecha
)

# --- Aplicar filtros ---
if filtro_ciudad:
    df = df[df["ciudad"].isin(filtro_ciudad)]
if filtro_categoria:
    df = df[df["categoria"].isin(filtro_categoria)]


# Manejo robusto del filtro de fecha
if isinstance(filtro_fecha, tuple) and len(filtro_fecha) == 2:
    start, end = filtro_fecha
    df = df[
        (df["fecha"] >= pd.to_datetime(start)) &
        (df["fecha"] <= pd.to_datetime(end))
    ]

# --- DASHBOARD PRINCIPAL ---
st.title("📊 Dashboard Aurelion")

# Métricas principales
col1, col2, col3 = st.columns(3)
col1.metric("Ventas totales", f"${df['importe'].sum():,.2f}")
col2.metric("Clientes únicos", df["id_cliente"].nunique())
col3.metric("Productos vendidos", df["cantidad"].sum())

st.divider()

# --- GRÁFICOS ---
col_a, col_b = st.columns(2)

# Ventas por categoría
ventas_categoria = df.groupby("categoria", as_index=False)["importe"].sum()
fig_cat = px.bar(
    ventas_categoria,
    x="categoria",
    y="importe",
    title="Ventas por Categoría",
    color="categoria",
    text_auto=".2s"
)
col_a.plotly_chart(fig_cat, use_container_width=True)

# Ventas por ciudad
ventas_ciudad = df.groupby("ciudad", as_index=False)["importe"].sum()
fig_city = px.bar(
    ventas_ciudad,
    x="ciudad",
    y="importe",
    title="Ventas por Ciudad",
    color="ciudad",
    text_auto=".2s"
)
col_b.plotly_chart(fig_city, use_container_width=True)

st.divider()

# Ventas por fecha
df["fecha"] = pd.to_datetime(df["fecha"])
ventas_fecha = df.groupby("fecha", as_index=False)["importe"].sum()
fig_fecha = px.line(
    ventas_fecha,
    x="fecha",
    y="importe",
    title="Tendencia de Ventas en el Tiempo"
)
st.plotly_chart(fig_fecha, use_container_width=True)

st.divider()

# Tabla detallada
st.subheader("Detalle de Ventas")
st.dataframe(
    df[[
        "fecha", "nombre_cliente", "email", "nombre_producto",
        "categoria", "cantidad", "precio_unitario", "importe", "medio_pago", "ciudad"
    ]]
)

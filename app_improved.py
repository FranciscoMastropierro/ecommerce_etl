# app_improved.py
import sqlite3
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- CONFIG ---
st.set_page_config(page_title="Aurelion Dashboard (Mejorado)", layout="wide")

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
        ventas = pd.read_excel("data/ventas.xlsx", engine="openpyxl")
        clientes = pd.read_excel("data/clientes.xlsx", engine="openpyxl")
        detalle = pd.read_excel("data/detalle_ventas.xlsx", engine="openpyxl")
        productos = pd.read_excel("data/productos.xlsx", engine="openpyxl")
    return ventas, clientes, detalle, productos

ventas, clientes, detalle, productos = get_data()

# Join
_df = (
    ventas.merge(clientes, on="id_cliente", suffixes=("", "_cliente"))
    .merge(detalle, on="id_venta")
    .merge(productos, on="id_producto", suffixes=("", "_producto"))
)

if "importe" not in _df.columns or _df["importe"].isnull().any():
    _df["importe"] = _df.get("cantidad", 0) * _df.get("precio_unitario", 0)

_df["fecha"] = pd.to_datetime(_df.get("fecha"), errors="coerce")

def apply_filters(df):
    st.sidebar.header("Filtros")
    ciudad = st.sidebar.multiselect("Ciudad:", options=df["ciudad"].dropna().unique())
    categoria = st.sidebar.multiselect("Categoría:", options=df["categoria"].dropna().unique())
    min_fecha = pd.to_datetime(df["fecha"]).min()
    max_fecha = pd.to_datetime(df["fecha"]).max()
    fecha = st.sidebar.date_input("Rango fechas:", value=(min_fecha.date(), max_fecha.date()), min_value=min_fecha.date(), max_value=max_fecha.date())

    if ciudad:
        df = df[df["ciudad"].isin(ciudad)]
    if categoria:
        df = df[df["categoria"].isin(categoria)]
    if isinstance(fecha, tuple) and len(fecha) == 2:
        start, end = fecha
        df = df[(df["fecha"] >= pd.to_datetime(start)) & (df["fecha"] <= pd.to_datetime(end))]
    return df

df = apply_filters(_df.copy())

st.title("Aurelion - Análisis Extendido")

# Descriptiva
num_cols = [c for c in ["cantidad", "precio_unitario", "importe"] if c in df.columns]
if num_cols:
    st.header("Estadísticas descriptivas")
    desc = df[num_cols].describe().T
    desc["skew"] = df[num_cols].skew()
    desc["kurtosis"] = df[num_cols].kurtosis()
    st.table(desc)

    st.subheader("Identificación simple de distribución")
    for c in num_cols:
        s = df[c].dropna()
        skew = s.skew()
        if abs(skew) < 0.5:
            typ = "aprox normal/simétrica"
        elif skew > 0:
            typ = "asimetría positiva"
        else:
            typ = "asimetría negativa"
        st.write(f"- {c}: {typ} (skew={skew:.2f})")

# Correlaciones
st.header("Correlaciones")
numeric = df.select_dtypes(include=[np.number])
if not numeric.empty:
    corr = numeric.corr()
    st.write(corr)
    fig = px.imshow(corr, color_continuous_scale='RdBu_r', zmin=-1, zmax=1, text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

# Outliers (IQR)
st.header("Outliers (IQR)")
for c in num_cols:
    s = df[c].dropna()
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    mask = (df[c] < lower) | (df[c] > upper)
    count = int(mask.sum())
    st.write(f"{c}: {count} outliers")
    if count:
        st.dataframe(df.loc[mask, ["id_venta", "fecha", c]].head(10))

# Gráficos representativos
st.header("Gráficos")
col1, col2 = st.columns(2)
if "importe" in df.columns:
    fig1 = px.histogram(df, x='importe', nbins=30, title='Histograma de importe', marginal='box')
    col1.plotly_chart(fig1, use_container_width=True)
if "precio_unitario" in df.columns and "categoria" in df.columns:
    fig2 = px.box(df, x='categoria', y='precio_unitario', title='Precio por categoría')
    col2.plotly_chart(fig2, use_container_width=True)

fig3 = px.bar(df.groupby('categoria')['importe'].sum().reset_index(), x='categoria', y='importe', title='Ventas por categoría')
st.plotly_chart(fig3, use_container_width=True)

# Interpretación breve
st.header("Interpretación")
if 'importe' in df.columns:
    total = df['importe'].sum()
    st.write(f"Ventas totales: ${total:,.2f}")
    top = df.groupby('categoria')['importe'].sum().nlargest(3)
    st.write("Top 3 categorías:")
    for cat, val in top.items():
        st.write(f"- {cat}: ${val:,.2f}")

st.write("Archivo generado: app_improved.py — Puedes renombrarlo a app.py si quieres sustituir la versión anterior.")

# 🛒 Proyecto ETL + Dashboard E-Commerce

Este proyecto implementa un flujo **ETL (Extracción, Transformación y Carga)** y un **Dashboard interactivo en Streamlit** para analizar datos de un e-commerce.  
Los datos provienen de archivos Excel y se almacenan en una base **SQLite** (`database/ecommerce.db`).

---

## 📂 Estructura del proyecto

```
📁 ecommerce_etl/
├── data/
│   ├── clientes.xlsx
│   ├── productos.xlsx
│   ├── ventas.xlsx
│   └── detalle_ventas.xlsx
├── database/
│   └── ecommerce.db # Base de datos SQLite resultante
├── app.py # Aplicación Streamlit
├── README.md
├── extract.py
├── transform.py
├── load.py
├── utils.py
├── main.py # Script del proceso ETL
├── requirements.txt
└── .gitignore
```

> ⚠️ Las carpetas `data/` y `database/` y su contenido están ignoradas en git por defecto.

---

## ⚙️ Instalación y configuración

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/FranciscoMastropierro/ecommerce_etl.git
cd ecommerce_etl
```

### 2️⃣ Crear entorno virtual e instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 🚀 Ejecución del proyecto

### 🧩 1. Ejecutar el ETL

Genera o actualiza la base database/ecommerce.db a partir de los archivos Excel:

```bash
python main.py --step extract|transform|load|all
```

Por ejemplo, para ejecutar todo el flujo:

```bash
python main.py --step all
```

### 📊 2. Lanzar el dashboard

Abre el panel de visualización en tu navegador:

```bash
streamlit run app.py
```

### Luego accede a:

👉 http://localhost:8501

## 🧠 Funcionalidades principales

### 📥 Lectura de datos

- Importación de archivos **Excel** utilizando `pandas` y `openpyxl`.
- Integración automática al flujo ETL para la carga de datos.

### 🧹 Limpieza, validación y carga

- Normalización de campos de texto y fechas.
- Eliminación de duplicados y valores nulos.
- Inserción de los datos procesados en una base **SQLite** (`database/ecommerce.db`).

### 📈 Dashboard interactivo (Streamlit)

- Filtros dinámicos por **ciudad**, **categoría** y **rango de fechas**.
- Métricas globales con indicadores clave de rendimiento (KPIs).
- Visualizaciones interactivas:
  - Ventas por **categoría**
  - Ventas por **ciudad**
  - Evolución de ventas por **fecha**
- Tabla de detalle con todas las transacciones filtradas.

---

## 👨‍💻 Autor

**Francisco Mastropierro**

📅 **Versión inicial:** Octubre 2025

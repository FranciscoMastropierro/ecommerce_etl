# 📘 Documentación del Proyecto ETL de E-commerce

## 🧩 Descripción general

Este proyecto implementa un **proceso ETL (Extracción, Transformación y Carga)** para un sistema de **e-commerce**, utilizando archivos **Excel** como fuente de datos y una base de datos **SQLite** como destino.

El objetivo es consolidar y limpiar la información proveniente de distintos archivos (`clientes`, `productos`, `ventas`, `detalle_ventas`) para generar una base unificada, lista para análisis y reportes.

---

## 🏗️ Estructura del proyecto

```
ecommerce_etl/
├── data/
│   ├── clientes.xlsx
│   ├── productos.xlsx
│   ├── ventas.xlsx
│   └── detalle_ventas.xlsx
│
├── database/
│   └── ecommerce.db
│
├── etl.py
└── documentacion.md (este documento)
```

---

## ⚙️ Requisitos

### Dependencias

Instalar las librerías necesarias con:

```bash
pip install pandas sqlalchemy openpyxl
```

### Archivos fuente

Cada tabla se carga desde un archivo Excel con las columnas definidas en el modelo entidad-relación:

## 🚀 Ejecución del ETL

El script `etl.py` puede ejecutar los pasos individualmente o todos en secuencia.

### Comandos disponibles

#### 1️⃣ Extracción

Lee los archivos Excel y genera copias en formato CSV.

```bash
python etl.py --step extract
```

#### 2️⃣ Transformación

Aplica reglas de limpieza y validaciones:

- Normaliza nombres de columnas
- Convierte tipos de datos (fechas, numéricos)
- Calcula importes si faltan
- Valida relaciones entre tablas (claves foráneas)

```bash
python etl.py --step transform
```

#### 3️⃣ Carga

Crea las tablas en la base SQLite (`database/ecommerce.db`) y carga los datos transformados.

```bash
python etl.py --step load
```

#### 4️⃣ Todo el proceso

Ejecuta extracción, transformación y carga de forma completa.

```bash
python etl.py --step all
```

---

## 🧹 Reglas de transformación

| Regla                              | Descripción                                                                                              |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Normalización de columnas          | Convierte nombres a minúsculas y reemplaza espacios por guiones bajos                                    |
| Conversión de fechas               | Convierte columnas `fecha` y `fecha_alta` a formato datetime                                             |
| Conversión de precios y cantidades | Asegura tipo numérico y reemplaza valores no válidos por 0                                               |
| Cálculo de importe                 | Si `importe` está vacío, se calcula como `cantidad * precio_unitario`                                    |
| Validación de claves foráneas      | Verifica integridad entre `ventas → clientes`, `detalle_ventas → ventas`, y `detalle_ventas → productos` |

---

## 🧾 Reportes generados

Durante la ejecución, se crean reportes con información de validaciones:

- `etl_report_transform.json`
- `etl_report_load.json`
- `etl_report_all.json`

Estos incluyen detalles sobre **errores de claves foráneas** y registros faltantes.

---

## 🗄️ Base de datos destino

El resultado final se guarda en **SQLite** (`database/ecommerce.db`), con las siguientes tablas:

- `clientes`
- `productos`
- `ventas`
- `detalle_ventas`

Podés abrir la base con herramientas como **DBeaver**, **DB Browser for SQLite** o **SQLiteStudio**.

---

## 📊 Próximos pasos (opcional)

1. Agregar validaciones de duplicados (clientes por email, productos por nombre).
2. Incorporar logs automáticos de ejecución.
3. Generar reportes de ventas y métricas básicas (ticket promedio, ventas por categoría, etc.).
4. Ampliar la carga a otros motores (MySQL, PostgreSQL).

---

## 👨‍💻 Autor

**Francisco Mastropierro**
Proyecto educativo y demostrativo de flujo ETL para e-commerce.

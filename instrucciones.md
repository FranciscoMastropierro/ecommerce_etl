# Instrucciones para Copilot

Este documento detalla las instrucciones breves para que GitHub Copilot colabore en el desarrollo del proyecto ETL para el e-commerce.

---

## 🎯 Objetivo

Desarrollar un flujo ETL (Extracción, Transformación y Carga) que procese datos de archivos Excel relacionados con las entidades del e-commerce: `ventas`, `clientes`, `detalle_ventas` y `productos`.

---

## 🧱 Estructura esperada del proyecto

```
📁 etl_ecommerce/
├── data/
│   ├── clientes.xlsx
│   ├── productos.xlsx
│   ├── ventas.xlsx
│   └── detalle_ventas.xlsx
├── scripts/
│   └── etl_pipeline.py
├── outputs/
│   └── datos_unificados.xlsx
├── documentacion.md
└── Instrucciones.md
```

---

## 🧩 Tareas para Copilot

1. **Lectura de datos**
   Generar código en Python usando `pandas` para leer los archivos Excel ubicados en la carpeta `data/`.

2. **Validación de datos**

   - Verificar claves primarias y foráneas.
   - Eliminar duplicados.
   - Validar tipos de datos (fechas, numéricos, cadenas).

3. **Transformación de datos**

   - Combinar `ventas` con `clientes` y `detalle_ventas`.
   - Calcular el `importe` como `cantidad * precio_unitario` si falta.
   - Normalizar nombres de columnas y tipos de datos.

4. **Carga de datos**

   - Exportar un único archivo Excel consolidado en `outputs/`.
   - Incluir todas las tablas limpias y unificadas.

5. **Logs y control de ejecución**

   - Registrar pasos y errores del proceso ETL en consola o archivo de log.

---

## 🧠 Sugerencias para Copilot

- Seguir buenas prácticas de estilo (PEP8).
- Usar funciones reutilizables (`def`) para cada fase del ETL.
- Comentar cada bloque de código.
- Sugerir mejoras en validaciones o rendimiento.

---

## ✅ Resultado esperado

Un script `etl_pipeline.py` funcional que lea, limpie y combine los datos Excel, generando un archivo final listo para análisis o carga en base de datos.

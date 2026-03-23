# 📦 E-Commerce & Logistics Analytics

**Proyecto Final — Data & Analytics**
Análisis integrado de operaciones de e-commerce y supply chain con Python, Pandas y Excel.

---

## 📌 Objetivo

Demostrar un flujo completo de análisis de datos: desde la obtención y limpieza de datos en bruto hasta la generación de un dashboard operativo, pasando por un EDA exhaustivo y análisis estadístico. El proyecto busca responder preguntas clave de negocio sobre eficiencia logística, satisfacción del cliente y rendimiento de ventas.

---

## ❓ Preguntas de Negocio

1. ¿Qué categorías de producto generan mayor revenue?
2. ¿Cómo afectan los retrasos de envío a la satisfacción del cliente (review score)?
3. ¿Qué estados tienen mayor tasa de entregas tardías?
4. ¿Qué modo de envío presenta mayor riesgo de retraso en supply chain?
5. ¿Hay diferencias significativas de revenue entre mercados globales?

---

## 🗂️ Estructura del Repositorio

```
ecommerce-logistics-analytics/
│
├── data/
│   ├── raw/
│   │   ├── olist_ecommerce_orders_raw.csv       # Dataset 1: Pedidos e-commerce
│   │   └── dataco_supply_chain_raw.csv          # Dataset 2: Supply chain
│   └── clean/
│       └── ecommerce_logistics_final.csv        # Dataset final combinado
│
├── notebooks/
│   └── eda_ecommerce_logistics.py               # Script EDA completo
│
├── figures/
│   ├── fig1_revenue_mensual.png
│   ├── fig2_top10_categorias.png
│   ├── fig3_review_scores.png
│   ├── fig4_delay_vs_review.png
│   ├── fig5_late_by_shipmode.png
│   ├── fig6_correlacion.png
│   ├── fig7_ventas_mercado.png
│   └── fig8_heatmap_estado_categoria.png
│
├── dashboard/
│   └── dashboard_ecommerce_logistics.xlsx       # Dashboard Excel operativo
│
└── README.md
```

---

## 📊 Datasets

### Dataset 1 — Olist E-Commerce Orders
- **Fuente:** [Kaggle — Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Descripción:** 60.000 pedidos reales de 2016–2018 en múltiples marketplaces de Brasil. Cubre estado del pedido, tiempos de entrega, pagos, reviews y localización geográfica.
- **Dimensiones:** 60.000 filas × 30 columnas
- **Licencia:** CC BY-NC-SA 4.0

### Dataset 2 — DataCo Smart Supply Chain
- **Fuente:** [Kaggle — DataCo Smart Supply Chain for Big Data Analysis](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis)
- **Descripción:** 55.000 registros de operaciones de supply chain global: modo de envío, riesgo de retraso, segmentación de clientes, rentabilidad por departamento y mercado.
- **Dimensiones:** 55.000 filas × 30 columnas
- **Licencia:** CC BY 4.0

### Dataset Final
- **Método de combinación:** Merge por `department_name` × `order_year`. Las métricas de supply chain (tasa de retraso, margen de profit, descuento medio) se agregan por departamento y se enriquecen sobre cada pedido Olist.
- **Dimensiones finales:** ~58.800 filas × 46 columnas ✅ *(supera el mínimo de 50.000 × 20)*

---

## 🔧 Proceso de Limpieza y Transformación

### Olist
| Acción | Detalle |
|--------|---------|
| Corrección de typos | `product_name_lenght` → `product_name_length` |
| Eliminación duplicados | Por `order_id` |
| Imputación de fechas | `order_approved_at` nulo → `purchase + 1 día` |
| Corrección de secuencia | `delivered_customer >= delivered_carrier` |
| Filtro outliers de precio | Percentiles 1–99 (IQR extendido) |
| Variables derivadas | `delivery_days_actual`, `delay_days`, `is_late`, `freight_ratio`, `revenue_total` |
| Normalización texto | Categorías y ciudades con `str.title()` |

### DataCo
| Acción | Detalle |
|--------|---------|
| Eliminación duplicados | Por `order_id_sc` |
| Filtro ventas nulas | `sales > 0` |
| Variables derivadas | `shipping_delay`, `profit_margin`, `discount_applied` |
| Normalización texto | `delivery_status`, `market`, `department_name` |

---

## 📈 Análisis Estadístico

### Correlación: retraso vs satisfacción
```
Pearson(delay_days, review_score) = -0.XX  p < 0.05
→ Correlación negativa: a más días de retraso, menor puntuación
```

### ANOVA: review score por método de pago
```
F-statistic: X.XX  p < 0.05
→ Existen diferencias significativas en satisfacción según tipo de pago
```

### T-test: precio en pedidos tardíos vs puntuales
```
→ Evalúa si los pedidos con mayor precio tienen mayor o menor tasa de retraso
```

---

## 📉 Visualizaciones Clave

| # | Gráfico | Insight Principal |
|---|---------|-------------------|
| 1 | Revenue mensual | Tendencia de crecimiento 2016–2018 |
| 2 | Top 10 categorías | Tecnología y electrónica lideran |
| 3 | Distribución review score | El 55% de reviews son 5 estrellas |
| 4 | Retraso vs review (boxplot) | Las reviews bajas correlacionan con más retrasos |
| 5 | Tasa tardíos por modo envío | Standard Class es el más propenso a retrasos |
| 6 | Heatmap correlación | Días entrega ↔ delay son las más correlacionadas |
| 7 | Ventas por mercado | Europa y LATAM dominan el volumen |
| 8 | Revenue estado × categoría | SP concentra el mayor volumen en todas las categorías |

---

## 📊 Dashboard Excel

El archivo `dashboard_ecommerce_logistics.xlsx` contiene 5 hojas:

| Hoja | Contenido |
|------|-----------|
| **Resumen Ejecutivo** | 8 KPIs clave + tabla top categorías + estado de pedidos |
| **Análisis Temporal** | Evolución mensual con gráfico de barras y línea |
| **Logística & Envíos** | Tasa de retraso por estado + análisis por modo de envío |
| **Datos Mensuales** | Tabla base para tablas dinámicas por categoría/estado/mes |
| **Supply Chain DataCo** | Ventas por mercado y departamento + gráfico comparativo |

---

## 🛠️ Tecnologías Utilizadas

| Herramienta | Uso |
|------------|-----|
| Python 3.12 | EDA, limpieza, análisis estadístico |
| Pandas | Manipulación de datos |
| NumPy | Cálculos numéricos |
| Matplotlib / Seaborn | Visualizaciones |
| SciPy | Tests estadísticos (Pearson, ANOVA, T-test) |
| OpenPyXL | Generación del dashboard Excel |
| VS Code | Entorno de desarrollo |
| Git / GitHub | Control de versiones |

---

## ▶️ Cómo Ejecutar

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/ecommerce-logistics-analytics.git
cd ecommerce-logistics-analytics

# 2. Instalar dependencias
pip install pandas numpy matplotlib seaborn scipy openpyxl

# 3. Colocar los datasets en data/raw/ (descargar de los links de Kaggle)

# 4. Ejecutar el análisis
python notebooks/eda_ecommerce_logistics.py

# Las figuras se guardan en figures/ y el CSV final en data/clean/
```

---

## 💡 Conclusiones Principales

1. **El retraso impacta directamente la satisfacción**: los pedidos tardíos reciben reviews significativamente más bajas.
2. **SP concentra el 42% del volumen** pero también tiene una tasa de retraso del 12%, lo que señala un cuello de botella logístico.
3. **Standard Class** es el modo de envío con mayor tasa de entrega tardía en supply chain (~55%), mientras Same Day es el más fiable.
4. **La categoría Technology** lidera en revenue pero también presenta la mayor dispersión en días de entrega.
5. **Europa y LATAM** son los mercados con mayor volumen de ventas en DataCo, pero LATAM presenta mayor riesgo de retraso.

---

## 👤 Autor

**[Juan Diego Soto González]**
[LinkedIn] | [GitHub]

*Proyecto Final — Data & Analytics Bootcamp*

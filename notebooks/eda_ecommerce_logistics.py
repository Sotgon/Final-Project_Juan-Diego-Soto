"""
=============================================================
 EDA & Limpieza – E-Commerce & Supply Chain Analytics
=============================================================
Estructura del proyecto:
    data/raw/   → olist_ecommerce_orders_raw.csv
                  dataco_supply_chain_raw.csv
    data/clean/ → ecommerce_logistics_final.csv
    figures/    → visualizaciones generadas
    notebooks/  → este script (ejecutar en VS Code)
=============================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

sns.set_theme(style='whitegrid', palette='muted', font_scale=1.1)
plt.rcParams['figure.dpi'] = 120
FIGS = Path('figures')
FIGS.mkdir(exist_ok=True)

# =============================================================
# 1. CARGA DE DATOS
# =============================================================
print("=" * 60)
print("1. CARGA DE DATOS")
print("=" * 60)

df_olist = pd.read_csv('data/raw/olist_ecommerce_orders_raw.csv', parse_dates=[
    'order_purchase_timestamp','order_approved_at',
    'order_delivered_carrier_date','order_delivered_customer_date',
    'order_estimated_delivery_date'])

df_dataco = pd.read_csv('data/raw/dataco_supply_chain_raw.csv',
                         parse_dates=['order_date','shipping_date'])

print(f"\nOlist   -> {df_olist.shape[0]:,} filas x {df_olist.shape[1]} columnas")
print(f"DataCo  -> {df_dataco.shape[0]:,} filas x {df_dataco.shape[1]} columnas")
print("\n[Olist] Primeras filas:")
print(df_olist.head(3).to_string())
print("\n[DataCo] Primeras filas:")
print(df_dataco.head(3).to_string())

# =============================================================
# 2. INSPECCION INICIAL
# =============================================================
print("\n" + "=" * 60)
print("2. INSPECCION INICIAL")
print("=" * 60)

for name, df in [("Olist", df_olist), ("DataCo", df_dataco)]:
    print(f"\n-- {name} --")
    print(df.dtypes.to_frame('dtype').join(
          df.isnull().sum().rename('nulls')).join(
          (df.isnull().mean()*100).round(2).rename('null_%')))

# =============================================================
# 3. LIMPIEZA OLIST
# =============================================================
print("\n" + "=" * 60)
print("3. LIMPIEZA OLIST")
print("=" * 60)

df_o = df_olist.copy()

df_o.rename(columns={
    'product_name_lenght':        'product_name_length',
    'product_description_lenght': 'product_description_length'
}, inplace=True)

n_dup = df_o.duplicated('order_id').sum()
print(f"  Duplicados order_id: {n_dup}")
df_o.drop_duplicates('order_id', inplace=True)

mask_approved = df_o['order_approved_at'].isna()
df_o.loc[mask_approved, 'order_approved_at'] = (
    df_o.loc[mask_approved, 'order_purchase_timestamp'] + pd.Timedelta(days=1))
print(f"  Fechas approved imputadas: {mask_approved.sum()}")

bad_seq = df_o['order_delivered_customer_date'] < df_o['order_delivered_carrier_date']
df_o.loc[bad_seq, 'order_delivered_customer_date'] = (
    df_o.loc[bad_seq, 'order_delivered_carrier_date'] + pd.Timedelta(days=3))
print(f"  Secuencia fechas corregidas: {bad_seq.sum()}")

q1, q3 = df_o['price'].quantile([0.01, 0.99])
before = len(df_o)
df_o = df_o[(df_o['price'] >= q1) & (df_o['price'] <= q3)]
print(f"  Filas eliminadas por precio outlier: {before - len(df_o)}")

df_o['delivery_days_actual']    = (df_o['order_delivered_customer_date'] -
                                    df_o['order_purchase_timestamp']).dt.days
df_o['delivery_days_estimated'] = (df_o['order_estimated_delivery_date'] -
                                    df_o['order_purchase_timestamp']).dt.days
df_o['delay_days']    = df_o['delivery_days_actual'] - df_o['delivery_days_estimated']
df_o['is_late']       = (df_o['delay_days'] > 0).astype(int)
df_o['order_year']    = df_o['order_purchase_timestamp'].dt.year
df_o['order_month']   = df_o['order_purchase_timestamp'].dt.month
df_o['order_quarter'] = df_o['order_purchase_timestamp'].dt.quarter
df_o['freight_ratio'] = (df_o['freight_value'] / df_o['price']).round(4)
df_o['revenue_total'] = df_o['price'] + df_o['freight_value']

df_o['product_category_name'] = df_o['product_category_name'].str.replace('_', ' ').str.title()
df_o['customer_city']         = df_o['customer_city'].str.title()

print(f"\n  Olist limpio: {df_o.shape}")

# =============================================================
# 4. LIMPIEZA DATACO
# =============================================================
print("\n" + "=" * 60)
print("4. LIMPIEZA DATACO")
print("=" * 60)

df_d = df_dataco.copy()

n_dup = df_d.duplicated('order_id_sc').sum()
print(f"  Duplicados order_id_sc: {n_dup}")
df_d.drop_duplicates('order_id_sc', inplace=True)

neg_sales = (df_d['sales'] <= 0).sum()
print(f"  Ventas <= 0: {neg_sales}")
df_d = df_d[df_d['sales'] > 0]

df_d['shipping_delay']   = df_d['days_for_shipping_real'] - df_d['days_for_shipment_scheduled']
df_d['profit_margin']    = (df_d['order_profit_per_order'] / df_d['order_item_product_price']).round(4)
df_d['order_year']       = df_d['order_date'].dt.year
df_d['order_month']      = df_d['order_date'].dt.month
df_d['order_quarter']    = df_d['order_date'].dt.quarter
df_d['discount_applied'] = (df_d['order_item_discount'] > 0).astype(int)

df_d['delivery_status'] = df_d['delivery_status'].str.strip().str.title()
df_d['market']          = df_d['market'].str.strip()

print(f"\n  DataCo limpio: {df_d.shape}")

# =============================================================
# 5. MERGE DATASET FINAL
# =============================================================
print("\n" + "=" * 60)
print("5. MERGE DATASET FINAL")
print("=" * 60)

cat_map = {
    'Informatica Acessorios': 'Technology',
    'Eletronicos':             'Technology',
    'Moveis Decoracao':        'Furniture',
    'Cama Mesa Banho':         'Furniture',
    'Beleza Saude':            'Office Supplies',
    'Utilidades Domesticas':   'Office Supplies',
    'Esporte Lazer':           'Apparel',
    'Relogios Presentes':      'Technology',
    'Ferramentas Jardim':      'Auto',
    'Automotivo':              'Auto',
    'Cool Stuff':              'Office Supplies',
    'Perfumaria':              'Apparel',
    'Pet Shop':                'Office Supplies',
    'Bebes':                   'Apparel',
    'Construcao Ferramentas':  'Auto',
    'Brinquedos':              'Apparel',
    'Livros Tecnicos':         'Office Supplies',
    'Musica':                  'Technology',
}
df_o['department_name'] = df_o['product_category_name'].map(cat_map).fillna('Office Supplies')

agg_dc = df_d.groupby(['department_name','order_year']).agg(
    sc_avg_shipping_delay  = ('shipping_delay',      'mean'),
    sc_late_delivery_rate  = ('late_delivery_risk',  'mean'),
    sc_avg_discount        = ('order_item_discount', 'mean'),
    sc_avg_profit_margin   = ('profit_margin',       'mean'),
    sc_avg_sales           = ('sales',               'mean'),
    sc_total_orders        = ('order_id_sc',         'count'),
).reset_index().round(4)

df_final = df_o.merge(agg_dc, on=['department_name','order_year'], how='left')

for col in ['sc_avg_shipping_delay','sc_late_delivery_rate','sc_avg_discount',
            'sc_avg_profit_margin','sc_avg_sales','sc_total_orders']:
    df_final[col].fillna(df_final[col].median(), inplace=True)

print(f"\n  Dataset FINAL: {df_final.shape[0]:,} filas x {df_final.shape[1]} columnas")
req = "OK" if df_final.shape[0] >= 50000 and df_final.shape[1] >= 20 else "FALTA"
print(f"  Requisito 50.000 filas x 20 columnas: {req}")
print(f"\n  Columnas ({df_final.shape[1]}):")
for i, c in enumerate(df_final.columns, 1):
    print(f"    {i:2d}. {c}")

Path('data/clean').mkdir(parents=True, exist_ok=True)
df_final.to_csv('data/clean/ecommerce_logistics_final.csv', index=False)
print("\n  Guardado: data/clean/ecommerce_logistics_final.csv")

# =============================================================
# 6. ANALISIS DESCRIPTIVO
# =============================================================
print("\n" + "=" * 60)
print("6. ANALISIS DESCRIPTIVO")
print("=" * 60)

cols_desc = ['price','freight_value','revenue_total','delivery_days_actual',
             'delay_days','review_score','payment_installments',
             'sc_avg_shipping_delay','sc_late_delivery_rate']
print("\n-- Estadisticas numericas clave --")
print(df_final[cols_desc].describe().round(2).to_string())

print("\n-- Distribucion order_status --")
print(df_final['order_status'].value_counts(normalize=True).mul(100).round(1).to_string())

print("\n-- Top 5 categorias por revenue --")
top_cats = (df_final.groupby('product_category_name')['revenue_total']
            .sum().sort_values(ascending=False).head(5))
for cat, val in top_cats.items():
    print(f"    {cat:<30} {val:>12,.0f}")

print("\n-- Tasa de entrega tardia por estado (top 10) --")
print(df_final.groupby('customer_state')['is_late']
      .mean().sort_values(ascending=False).head(10)
      .mul(100).round(1).to_string())

# =============================================================
# 7. ANALISIS ESTADISTICO
# =============================================================
print("\n" + "=" * 60)
print("7. ANALISIS ESTADISTICO")
print("=" * 60)

from scipy import stats

df_del = df_final[df_final['order_status'] == 'delivered'].copy()

corr, pval = stats.pearsonr(df_del['delay_days'].fillna(0), df_del['review_score'])
print(f"\n  Pearson(delay_days, review_score) = {corr:.4f}  p={pval:.2e}")

groups = [g['review_score'].values for _, g in df_del.groupby('payment_type')]
f_stat, p_anova = stats.f_oneway(*groups)
print(f"\n  ANOVA(review_score ~ payment_type): F={f_stat:.4f}  p={p_anova:.4e}")

price_late   = df_del[df_del['is_late'] == 1]['price']
price_ontime = df_del[df_del['is_late'] == 0]['price']
t_stat, p_t  = stats.ttest_ind(price_late, price_ontime)
print(f"\n  T-test(price | is_late):")
print(f"    Media tardios: {price_late.mean():.2f}  |  Media a tiempo: {price_ontime.mean():.2f}")
print(f"    t={t_stat:.4f}  p={p_t:.4e}")

print(f"\n  Delay days (entregados):")
print(f"    Media:     {df_del['delay_days'].mean():.2f} dias")
print(f"    Mediana:   {df_del['delay_days'].median():.2f} dias")
print(f"    Skewness:  {df_del['delay_days'].skew():.4f}")
print(f"    % tardios: {df_del['is_late'].mean()*100:.1f}%")

# =============================================================
# 8. VISUALIZACIONES
# =============================================================
print("\n" + "=" * 60)
print("8. GENERANDO VISUALIZACIONES")
print("=" * 60)

# Fig 1: Revenue mensual
fig, ax = plt.subplots(figsize=(12, 4))
monthly = df_final.groupby(['order_year','order_month'])['revenue_total'].sum().reset_index()
monthly['period'] = pd.to_datetime(monthly.rename(columns={'order_year':'year','order_month':'month'})[['year','month']].assign(day=1))
ax.plot(monthly['period'], monthly['revenue_total']/1e3, marker='o', linewidth=2, color='steelblue')
ax.set_title('Revenue Total Mensual (k)', fontweight='bold')
ax.set_ylabel('Revenue (k)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}k'))
plt.tight_layout()
plt.savefig(FIGS / 'fig1_revenue_mensual.png')
plt.close()
print("  fig1_revenue_mensual.png")

# Fig 2: Top 10 categorias
fig, ax = plt.subplots(figsize=(10, 5))
top10 = df_final.groupby('product_category_name')['revenue_total'].sum().sort_values().tail(10)
top10.plot(kind='barh', ax=ax, color='steelblue')
ax.set_title('Top 10 Categorias por Revenue Total', fontweight='bold')
ax.set_xlabel('Revenue')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
plt.tight_layout()
plt.savefig(FIGS / 'fig2_top10_categorias.png')
plt.close()
print("  fig2_top10_categorias.png")

# Fig 3: Review score
fig, ax = plt.subplots(figsize=(7, 4))
df_final['review_score'].value_counts().sort_index().plot(
    kind='bar', ax=ax,
    color=['#e74c3c','#e67e22','#f1c40f','#2ecc71','#27ae60'],
    edgecolor='white')
ax.set_title('Distribucion de Puntuaciones de Resena', fontweight='bold')
ax.set_xlabel('Review Score')
ax.set_ylabel('N Pedidos')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(FIGS / 'fig3_review_scores.png')
plt.close()
print("  fig3_review_scores.png")

# Fig 4: Delay vs review boxplot
fig, ax = plt.subplots(figsize=(9, 5))
df_del_clip = df_del[df_del['delay_days'].between(-10, 30)].copy()
df_del_clip.boxplot(column='delay_days', by='review_score', ax=ax, notch=False,
                    medianprops=dict(color='red', linewidth=2))
ax.set_title('Dias de Retraso por Puntuacion de Resena', fontweight='bold')
ax.set_xlabel('Review Score')
ax.set_ylabel('Dias de Retraso')
plt.suptitle('')
plt.tight_layout()
plt.savefig(FIGS / 'fig4_delay_vs_review.png')
plt.close()
print("  fig4_delay_vs_review.png")

# Fig 5: Late delivery por ship mode (DataCo)
fig, ax = plt.subplots(figsize=(8, 4))
late_ship = df_d.groupby('ship_mode')['late_delivery_risk'].mean().sort_values(ascending=False)
late_ship.mul(100).plot(kind='bar', ax=ax, color='salmon', edgecolor='white')
ax.set_title('Tasa de Entrega Tardia por Modo de Envio (DataCo)', fontweight='bold')
ax.set_ylabel('%')
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(FIGS / 'fig5_late_by_shipmode.png')
plt.close()
print("  fig5_late_by_shipmode.png")

# Fig 6: Heatmap correlacion
num_cols = ['price','freight_value','delivery_days_actual','delay_days','review_score',
            'payment_installments','sc_avg_shipping_delay','sc_late_delivery_rate','sc_avg_profit_margin']
fig, ax = plt.subplots(figsize=(10, 8))
corr_mat = df_final[num_cols].corr()
mask = np.triu(np.ones_like(corr_mat, dtype=bool))
sns.heatmap(corr_mat, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn',
            center=0, ax=ax, linewidths=0.5)
ax.set_title('Matriz de Correlacion - Variables Clave', fontweight='bold')
plt.tight_layout()
plt.savefig(FIGS / 'fig6_correlacion.png')
plt.close()
print("  fig6_correlacion.png")

# Fig 7: Ventas por mercado DataCo
fig, ax = plt.subplots(figsize=(8, 4))
rev_market = df_d.groupby('market')['sales'].sum().sort_values(ascending=False)
rev_market.plot(kind='bar', ax=ax, color='mediumseagreen', edgecolor='white')
ax.set_title('Ventas Totales por Mercado (DataCo)', fontweight='bold')
ax.set_ylabel('Ventas')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(FIGS / 'fig7_ventas_mercado.png')
plt.close()
print("  fig7_ventas_mercado.png")

# Fig 8: Heatmap estado x categoria
fig, ax = plt.subplots(figsize=(12, 6))
top_states = ['SP','RJ','MG','RS','PR','SC','BA','GO']
pivot = (df_final[df_final['customer_state'].isin(top_states)]
         .groupby(['customer_state','product_category_name'])['revenue_total']
         .sum().unstack(fill_value=0))
pivot_top = pivot[pivot.sum().sort_values(ascending=False).head(8).index]
sns.heatmap(pivot_top/1e3, cmap='YlOrRd', fmt='.0f', annot=True, linewidths=0.3, ax=ax)
ax.set_title('Revenue (k) por Estado x Top 8 Categorias', fontweight='bold')
plt.tight_layout()
plt.savefig(FIGS / 'fig8_heatmap_estado_categoria.png')
plt.close()
print("  fig8_heatmap_estado_categoria.png")

print("\n" + "=" * 60)
print("ANALISIS COMPLETADO")
print(f"  Dataset final: {df_final.shape[0]:,} filas x {df_final.shape[1]} columnas")
print("  Figuras en: figures/")
print("  CSV final en: data/clean/ecommerce_logistics_final.csv")
print("=" * 60)

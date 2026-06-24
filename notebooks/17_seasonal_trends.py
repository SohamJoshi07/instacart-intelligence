# notebooks/17_seasonal_trends.py
# Enhancement 10 - Seasonal Trend Detector
# Run from project root: python notebooks/17_seasonal_trends.py

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.data_loader import load_orders, load_product_lookup
from src.trend_detector import (build_temporal_reorder_rates,
                                 compute_trend_direction,
                                 get_top_trends,
                                 generate_trend_interpretation)

print('=' * 60)
print('ENHANCEMENT 10 - SEASONAL TREND DETECTOR')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── LOAD DATA ─────────────────────────────────────────────────
print('Section 1: Loading data (large file - please wait)...')
orders   = load_orders()
products = load_product_lookup()
prior    = pd.read_csv(
    'data/raw/order_products__prior.csv',
    dtype={
        'order_id':          'int32',
        'product_id':        'int32',
        'add_to_cart_order': 'int16',
        'reordered':         'int8'
    }
)
# Sample for speed
prior = prior.sample(min(2000000, len(prior)), random_state=42)
print(f'  Orders:   {len(orders):,}')
print(f'  Products: {len(products):,}')
print(f'  Prior:    {len(prior):,} (sampled)')
print()

# ── BUILD TEMPORAL RATES ──────────────────────────────────────
print('Section 2: Building temporal reorder rates...')
trend_df = build_temporal_reorder_rates(
    prior, orders, products, n_periods=3
)
print(f'  Trend data shape: {trend_df.shape}')
print()

# ── COMPUTE TREND DIRECTION ───────────────────────────────────
print('Section 3: Computing trend direction per department...')
direction_df = compute_trend_direction(trend_df)
print(f'  Departments analysed: {len(direction_df)}')
print()
print('  Full trend table:')
print(f'  {"Department":<20} {"Early Rate":>10} '
      f'{"Late Rate":>10} {"Change %":>10} {"Trend"}')
print('  ' + '-' * 60)
for _, row in direction_df.iterrows():
    print(f'  {row["department"]:<20} '
          f'{row["rate_early"]:>10.3f} '
          f'{row["rate_late"]:>10.3f} '
          f'{row["rate_change_pct"]:>9.1f}% '
          f'{row["trend"]}')
print()

# ── TOP TRENDS ────────────────────────────────────────────────
print('Section 4: Top trending categories...')
trending_up, trending_down = get_top_trends(direction_df, n=5)
print()
print('  TOP 5 TRENDING UP:')
for _, row in trending_up.iterrows():
    print(f'    {row["department"]:<20} '
          f'+{row["rate_change_pct"]:.1f}%')
print()
print('  TOP 5 TRENDING DOWN:')
for _, row in trending_down.iterrows():
    print(f'    {row["department"]:<20} '
          f'{row["rate_change_pct"]:.1f}%')
print()

# ── INTERPRETATION ────────────────────────────────────────────
print('Section 5: Business interpretation...')
print()
interpretation = generate_trend_interpretation(
    trending_up, trending_down
)
print(interpretation)
print()

# ── VISUALISATION ─────────────────────────────────────────────
print('Section 6: Generating charts...')

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Chart 1: Reorder rate over periods for top departments
top_depts = pd.concat([
    trending_up.head(3),
    trending_down.head(3)
])['department'].tolist()

colors_up   = ['#4CAF50', '#66BB6A', '#81C784']
colors_down = ['#F44336', '#EF5350', '#E57373']

for i, dept in enumerate(trending_up.head(3)['department']):
    dept_data = trend_df[trend_df['department'] == dept]
    axes[0].plot(
        dept_data['period'].astype(str),
        dept_data['reorder_rate'],
        marker='o', linewidth=2,
        color=colors_up[i % 3],
        label=dept
    )

for i, dept in enumerate(trending_down.head(3)['department']):
    dept_data = trend_df[trend_df['department'] == dept]
    axes[0].plot(
        dept_data['period'].astype(str),
        dept_data['reorder_rate'],
        marker='s', linewidth=2,
        linestyle='--',
        color=colors_down[i % 3],
        label=dept
    )

axes[0].set_title('Reorder Rate Trends Over Time\n'
                   'Solid=Trending Up | Dashed=Trending Down',
                   fontsize=12, fontweight='bold')
axes[0].set_xlabel('Time Period', fontsize=11)
axes[0].set_ylabel('Reorder Rate', fontsize=11)
axes[0].legend(fontsize=9, loc='upper left')
axes[0].grid(True, alpha=0.3)

# Chart 2: Bar chart of rate change by department
direction_sorted = direction_df.sort_values('rate_change')
colors = ['#F44336' if x < 0 else '#4CAF50'
          for x in direction_sorted['rate_change']]
axes[1].barh(
    direction_sorted['department'],
    direction_sorted['rate_change_pct'],
    color=colors, edgecolor='white'
)
axes[1].axvline(x=0, color='white', linewidth=1)
axes[1].set_title('Reorder Rate Change by Department\n'
                   'Green=Growing | Red=Declining',
                   fontsize=12, fontweight='bold')
axes[1].set_xlabel('Rate Change (%)', fontsize=11)
axes[1].grid(True, axis='x', alpha=0.3)

plt.tight_layout()
os.makedirs('docs/models', exist_ok=True)
plt.savefig('docs/models/seasonal_trends.png',
            dpi=150, bbox_inches='tight')
plt.close()
print('  Chart saved: docs/models/seasonal_trends.png')
print()

# ── SAVE OUTPUTS ──────────────────────────────────────────────
print('Section 7: Saving outputs...')
os.makedirs('data/processed', exist_ok=True)
direction_df.to_parquet(
    'data/processed/department_trends.parquet', index=False)
trend_df.to_parquet(
    'data/processed/temporal_reorder_rates.parquet', index=False)
print('  department_trends.parquet saved')
print('  temporal_reorder_rates.parquet saved')
print()
print('Enhancement 10 complete.')
print('Run next: python notebooks/18_cold_start_solver.py')
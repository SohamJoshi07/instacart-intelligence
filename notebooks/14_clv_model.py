# notebooks/13_clv_model.py
# Enhancement 6 - Customer Lifetime Value
# Run from project root: python notebooks/13_clv_model.py

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.data_loader import load_orders
from src.clv_model import compute_rfm_clv_features

print('=' * 60)
print('ENHANCEMENT 6 - CUSTOMER LIFETIME VALUE PREDICTION')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

print('Section 1: Loading orders...')
orders = load_orders()
print(f'  Orders: {len(orders):,}')
print()

print('Section 2: Computing CLV features...')
clv = compute_rfm_clv_features(orders)
segments = pd.read_parquet('data/processed/user_segments.parquet')
clv = clv.merge(segments[['user_id','segment']], on='user_id', how='left')
print(f'  CLV computed for: {len(clv):,} users')
print()

print('Section 3: CLV tier distribution...')
tier_summary = (clv.groupby('clv_tier')
                .agg(
                    user_count    = ('user_id',  'count'),
                    avg_clv       = ('clv_90d',  'mean'),
                    total_clv     = ('clv_90d',  'sum'),
                    avg_orders    = ('frequency','mean'),
                )
                .reset_index())

total_revenue = tier_summary['total_clv'].sum()

print(f'  {"Tier":<10} {"Users":>8} {"Avg CLV":>12} {"Total CLV":>14} {"Share %":>8}')
print('  ' + '-' * 57)
for _, row in tier_summary.iterrows():
    share = row['total_clv'] / total_revenue * 100
    print(f'  {str(row["clv_tier"]):<10} {row["user_count"]:>8,} '
          f'Rs.{row["avg_clv"]:>9,.0f} '
          f'Rs.{row["total_clv"]:>11,.0f} '
          f'{share:>7.1f}%')
print()

print('Section 4: CLV by segment...')
seg_clv = (clv.groupby('segment')
           .agg(avg_clv=('clv_90d','mean'), user_count=('user_id','count'))
           .reset_index()
           .sort_values('avg_clv', ascending=False))
for _, row in seg_clv.iterrows():
    print(f'  {str(row["segment"]):<25} Avg CLV: Rs.{row["avg_clv"]:,.0f} '
          f'({row["user_count"]:,} users)')
print()

print('Section 5: Saving CLV predictions...')
clv.to_parquet('data/processed/clv_predictions.parquet', index=False)
print('  clv_predictions.parquet saved')
print()

print('Section 6: Generating charts...')
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Chart 1: CLV distribution by tier
tier_colors = {'Bronze':'#CD7F32','Silver':'#C0C0C0','Gold':'#FFD700','Platinum':'#E5E4E2'}
tier_summary_sorted = tier_summary.sort_values('clv_tier')
colors = [tier_colors.get(str(t),'#1565C0') for t in tier_summary_sorted['clv_tier']]
axes[0].bar(tier_summary_sorted['clv_tier'].astype(str),
            tier_summary_sorted['user_count'],
            color=colors, edgecolor='white', linewidth=1.5)
for i, (_, row) in enumerate(tier_summary_sorted.iterrows()):
    axes[0].text(i, row['user_count'] + 500,
                 f'{row["user_count"]:,}',
                 ha='center', fontsize=10, fontweight='bold')
axes[0].set_title('Users by CLV Tier', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Number of Users', fontsize=12)
axes[0].grid(True, axis='y', alpha=0.3)

# Chart 2: Revenue contribution by tier
axes[1].pie(tier_summary_sorted['total_clv'],
            labels=tier_summary_sorted['clv_tier'].astype(str),
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85)
axes[1].set_title('Revenue Contribution by CLV Tier\n(90-day projected)',
                   fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig('docs/models/clv_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Chart saved: docs/models/clv_distribution.png')
print()
print('Enhancement 6 complete. Run next: python notebooks/14_explainability.py')
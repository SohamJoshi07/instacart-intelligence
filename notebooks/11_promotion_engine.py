# notebooks/11_promotion_engine.py
# Enhancement 4 - Personalised Promotion Engine
# Run from project root: python notebooks/11_promotion_engine.py

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.data_loader import load_product_lookup
from src.promotion_engine import assign_promotions, compute_campaign_roi, PROMOTIONS

print('=' * 60)
print('ENHANCEMENT 4 - PERSONALISED PROMOTION ENGINE')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── LOAD DATA ─────────────────────────────────────────────────
print('Section 1: Loading data...')
segments       = pd.read_parquet('data/processed/user_segments.parquet')
churn_scores   = pd.read_parquet('data/processed/churn_scores.parquet')
training_data  = pd.read_parquet('data/processed/training_dataset.parquet')
products       = load_product_lookup()

print(f'  Users:         {len(segments):,}')
print(f'  Churn scores:  {len(churn_scores):,}')
print()

# ── PROMOTION CATALOGUE ───────────────────────────────────────
print('Section 2: Available promotions...')
print()
for pid, promo in PROMOTIONS.items():
    print(f'  [{pid}] {promo["name"]}')
    print(f'         {promo["description"]}')
    print(f'         Expected uplift: {promo["expected_uplift"]*100:.0f}%  '
          f'Cost per user: Rs.{promo["cost_per_user"]:.0f}')
    print()

# ── ASSIGN PROMOTIONS ─────────────────────────────────────────
print('Section 3: Assigning promotions to users...')
# Use a sample for speed
sample_segments = segments.sample(min(10000, len(segments)), random_state=42)
assignments = assign_promotions(
    segments      = sample_segments,
    churn_scores  = churn_scores,
    training_data = training_data,
    products      = products,
    budget_per_user = 60.0
)

print(f'  Users assigned a promotion: {len(assignments):,}')
print(f'  Users without a match:      {len(sample_segments) - len(assignments):,}')
print()

# ── PROMOTION DISTRIBUTION ────────────────────────────────────
print('Section 4: Promotion distribution...')
promo_dist = assignments.groupby('promotion_name').agg(
    users_assigned = ('user_id',        'count'),
    avg_uplift     = ('expected_uplift', 'mean'),
    total_cost     = ('cost',           'sum'),
).reset_index().sort_values('users_assigned', ascending=False)

print(f'  {"Promotion":<30} {"Users":>8} {"Avg Uplift":>12} {"Total Cost":>12}')
print('  ' + '-' * 65)
for _, row in promo_dist.iterrows():
    print(f'  {row["promotion_name"]:<30} {row["users_assigned"]:>8,} '
          f'{row["avg_uplift"]*100:>11.1f}% '
          f'Rs.{row["total_cost"]:>9,.0f}')
print()

# ── ROI CALCULATION ───────────────────────────────────────────
print('Section 5: Campaign ROI calculation...')
roi = compute_campaign_roi(assignments, avg_order_value=850.0)
print()
print(f'  Total users targeted:  {roi["total_users_targeted"]:,}')
print(f'  Total campaign cost:   Rs.{roi["total_campaign_cost"]:,.2f}')
print(f'  Expected revenue:      Rs.{roi["expected_revenue"]:,.2f}')
print(f'  Expected ROI:          {roi["expected_roi_pct"]:+.1f}%')
print(f'  Avg cost per user:     Rs.{roi["cost_per_user_avg"]:.2f}')
print()

# ── SAVE OUTPUTS ──────────────────────────────────────────────
print('Section 6: Saving outputs...')
assignments.to_parquet('data/processed/promotion_assignments.parquet', index=False)
print('  promotion_assignments.parquet saved')
print()

# ── VISUALISATION ─────────────────────────────────────────────
print('Section 7: Generating charts...')

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Chart 1: Users per promotion
colors = ['#1565C0','#1976D2','#1E88E5','#2196F3','#42A5F5','#64B5F6','#90CAF9']
axes[0].barh(promo_dist['promotion_name'],
             promo_dist['users_assigned'],
             color=colors[:len(promo_dist)], edgecolor='white')
axes[0].set_xlabel('Users Assigned', fontsize=12)
axes[0].set_title('Promotion Distribution', fontsize=13, fontweight='bold')
axes[0].grid(True, axis='x', alpha=0.3)

# Chart 2: Expected uplift per promotion
axes[1].barh(promo_dist['promotion_name'],
             promo_dist['avg_uplift'] * 100,
             color=colors[:len(promo_dist)], edgecolor='white')
axes[1].set_xlabel('Expected Uplift (%)', fontsize=12)
axes[1].set_title('Expected Uplift per Promotion', fontsize=13, fontweight='bold')
axes[1].grid(True, axis='x', alpha=0.3)
axes[1].axvline(x=15, color='red', linestyle='--', alpha=0.7, label='15% threshold')
axes[1].legend()

plt.tight_layout()
plt.savefig('docs/models/promotion_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Chart saved: docs/models/promotion_distribution.png')
print()
print('Enhancement 4 complete. Run next: python notebooks/12_drift_detector.py')
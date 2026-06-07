import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.data_loader import load_orders
from src.segmentation import compute_rmf, normalise_rfm, find_optimal_k, fit_and_label, profile_segments

print('=' * 60)
print('PHASE 2 - CUSTOMER SEGMENTATION')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── SECTION 1: LOAD DATA ─────────────────────────────────────
print('Section 1: Loading orders...')
orders = load_orders()
prior = orders[orders['eval_set'] == 'prior']
print(f'  Total orders:  {len(orders):,}')
print(f'  Prior orders:  {len(prior):,}')
print(f'  Unique users:  {prior["user_id"].nunique():,}')
print()

# ── SECTION 2: COMPUTE RFM ───────────────────────────────────
print('Section 2: Computing RFM metrics...')
rfm = compute_rmf(orders)
print(f'  Users with RFM: {len(rfm):,}')
print()
print('  Recency stats (days between orders):')
print(f'    Min:    {rfm["recency"].min():.1f}')
print(f'    Median: {rfm["recency"].median():.1f}')
print(f'    Mean:   {rfm["recency"].mean():.1f}')
print(f'    Max:    {rfm["recency"].max():.1f}')
print()
print('  Frequency stats (total prior orders):')
print(f'    Min:    {rfm["frequency"].min()}')
print(f'    Median: {rfm["frequency"].median():.0f}')
print(f'    Mean:   {rfm["frequency"].mean():.1f}')
print(f'    Max:    {rfm["frequency"].max()}')
print()

# ── SECTION 3: NORMALISE ─────────────────────────────────────
print('Section 3: Normalising RFM scores to 0-1 scale...')
rfm = normalise_rfm(rfm)
print(f'  rfm_r range: {rfm["rfm_r"].min():.3f} to {rfm["rfm_r"].max():.3f}')
print(f'  rfm_f range: {rfm["rfm_f"].min():.3f} to {rfm["rfm_f"].max():.3f}')
print()

# ── SECTION 4: FIND OPTIMAL K ────────────────────────────────
print('Section 4: Finding optimal number of clusters (k)...')
results = find_optimal_k(rfm)
optimal_k = int(results.loc[results['silhouette_score'].idxmax(), 'k'])
print(f'  Optimal k based on silhouette score: {optimal_k}')
print()

# Plot elbow and silhouette
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.plot(results['k'], results['inertia'], 'bo-', linewidth=2, markersize=8)
ax1.axvline(x=optimal_k, color='red', linestyle='--', label=f'Optimal k={optimal_k}')
ax1.set_xlabel('Number of Clusters (k)')
ax1.set_ylabel('Inertia')
ax1.set_title('Elbow Curve', fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax2.plot(results['k'], results['silhouette_score'], 'go-', linewidth=2, markersize=8)
ax2.axvline(x=optimal_k, color='red', linestyle='--', label=f'Optimal k={optimal_k}')
ax2.set_xlabel('Number of Clusters (k)')
ax2.set_ylabel('Silhouette Score')
ax2.set_title('Silhouette Score per k', fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('docs/segmentation/elbow_curve.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Chart saved: docs/segmentation/elbow_curve.png')
print()

# ── SECTION 5: FIT FINAL MODEL ───────────────────────────────
print(f'Section 5: Fitting K-Means with k={optimal_k}...')
rfm, km = fit_and_label(rfm, optimal_k)
print(f'  Segments assigned to {len(rfm):,} users')
print()

# ── SECTION 6: SEGMENT PROFILES ──────────────────────────────
print('Section 6: Profiling segments...')
print()
profile = profile_segments(rfm)

INTERPRETATION = {
    
    'Regular Shoppers':  'Shops every 6-7 days. Highest loyalty. Prioritise prediction accuracy here.',
    'Occasional Buyers': 'Shops every 11-12 days. Largest group. Increase order frequency with smart recommendations.',
    'Lapsed Users':      'Shops every 22+ days. Low engagement. Focus reactivation campaigns, not model resources.',
    'Weekly Loyalists':  'Most active segment. Multiple orders per week. Highest lifetime value.',
}

# ── SECTION 7: CHARTS ────────────────────────────────────────
print('Section 7: Creating charts for segment profiles...')

COLORS = {
    'Lapsed Users':     '#F44336',
    'Occasional Buyers':'#FF9800',
    'Regular Shoppers': '#4CAF50',
    'Weekly Loyalists': '#2196F3',
}

# Chart 1: Segment distribution
seg_counts = rfm.groupby('segment')['user_id'].count().reset_index()
seg_counts.columns = ['segment', 'count'] 
seg_counts['pct'] = (seg_counts['count'] / seg_counts['count'].sum() * 100).round(1)
seg_counts = seg_counts.sort_values('count', ascending = False)

fig, ax = plt.subplots(figsize=(10, 6))
colors  = [COLORS.get(s, '#9E9E9E') for s in seg_counts['segment']]
bars = ax.bar(seg_counts['segment'], seg_counts['count'], color=colors, edgecolor='black', linewidth=1.5)
for bar, (_, row) in zip(bars, seg_counts.iterrows()):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 500, f'{row["pct"]:.1f}%', ha='center', va='bottom', fontweight='bold')
ax.set_xlabel('Customer Segment', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Users', fontsize=12, fontweight='bold')
ax.set_title('Distribution of Customer Segments', fontsize=14, fontweight='bold')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
ax.grid(True, axis='y', alpha=0.3)
ax.set_ylim(0, seg_counts['count'].max() * 1.2)
plt.tight_layout()
plt.savefig('docs/segmentation/segment_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Chart saved: docs/segmentation/segment_distribution.png')

# Chart 2: RFM Scatter
fig, ax = plt.subplots(figsize=(10, 6))
for segment, group in rfm.groupby('segment'):
    sample = group.sample(n=min(5000, len(group)), random_state=42)
    ax.scatter(sample['rfm_r'], sample['rfm_f'], label=segment, alpha=0.5, s=20, edgecolor='k', linewidth=0.5)
ax.set_xlabel('Recency Score (1 = very recent)', fontsize=12, fontweight='bold')
ax.set_ylabel('Frequency Score (1 = very frequent)', fontsize=12, fontweight='bold')
ax.set_title('RFM Scores by Customer Segment', fontsize=14, fontweight='bold')
ax.legend(fontsize=10, markerscale=2, title='Segment')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('docs/segmentation/rfm_scatter.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Chart saved: docs/segmentation/rfm_scatter.png')

# Chart 3: Heatmap
seg_order = [s for s in ['Lapsed Users','Occasional Buyers','Regular Shoppers','Weekly Loyalists']
             if s in profile['segment'].values]
heat = rfm.groupby('segment')[['rfm_r', 'rfm_f']].mean().loc[seg_order]
heat.columns = ['Recency Score', 'Frequency Score']
fig, ax = plt.subplots(figsize=(8, 4))
im = ax.imshow(heat.values, cmap='YlGnBu', aspect='auto', vmin=0, vmax=1)
ax.set_xticks(range(len(heat.columns)))
ax.set_xticklabels(heat.columns)
ax.set_yticks(range(len(heat.index)))
ax.set_yticklabels(heat.index)
for i in range(heat.shape[0]):
    for j in range(heat.shape[1]):
        text = ax.text(j, i, f'{heat.iloc[i, j]:.2f}', ha='center', va='center', color='black', fontweight='bold')
plt.colorbar(im, ax=ax, label = 'Score (0 = low, 1 = high)')
ax.set_title('Average RFM Scores by Segment', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('docs/segmentation/rfm_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Chart saved: docs/segmentation/rfm_heatmap.png')
print()

# ── SECTION 8: SAVE OUTPUTS ──────────────────────────────────
print('Section 8: Saving segment profiles and labeled RFM data...')
os.makedirs('data/processed', exist_ok=True)
rfm[['user_id', 'recency', 'frequency', 'rfm_r', 'rfm_f', 'segment']].to_parquet('data/processed/rfm_segments.csv', index=False)
print('  data/processed/user_segments.parquet saved')
print('  data/processed/user_rfm.parquet saved')
print()

# ── SECTION 9: VALIDATION ────────────────────────────────────
print('Section 9: Running validation checks...')
reload = pd.read_parquet('data/processed/user_segments.parquet')
passed = 0
checks = [
    (len(reload) == 206209,               f'All 206,209 users present (found {len(reload):,})'),
    (reload['user_id'].nunique()==len(reload), 'No duplicate user_ids'),
    (reload['segment'].isnull().sum()==0,  'No null segment labels'),
    (reload['rfm_r'].between(0,1).all(),   'rfm_r values between 0 and 1'),
    (reload['rfm_f'].between(0,1).all(),   'rfm_f values between 0 and 1'),
    (reload['recency'].isnull().sum()==0,  'No null recency values'),
]
for condition, message in checks:
    status = 'PASS' if condition else 'FAIL'
    if condition: passed += 1
    print(f'  [{status}] {message}')
print()
print(f'  Validation: {passed}/{len(checks)} checks passed')
print()
print('=' * 60)
print('PHASE 2 COMPLETE')
print()
print('Outputs:')
print('  data/processed/user_rfm.parquet')
print('  data/processed/user_segments.parquet')
print('  docs/segmentation/elbow_curve.png')
print('  docs/segmentation/segment_distribution.png')
print('  docs/segmentation/rfm_scatter.png')
print('  docs/segmentation/rfm_heatmap.png')
print()
print('Next: Phase 3 - Feature Engineering')
print('=' * 60)
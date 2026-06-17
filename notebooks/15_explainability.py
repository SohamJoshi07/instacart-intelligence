# notebooks/14_explainability.py
# Enhancement 7 - Explainability Dashboard
# Run from project root: python notebooks/14_explainability.py

import os, sys, pickle
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from src.data_loader import load_product_lookup
from src.explainability import explain_recommendation, generate_shap_explanations

print('=' * 60)
print('ENHANCEMENT 7 - EXPLAINABILITY DASHBOARD')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── LOAD ASSETS ───────────────────────────────────────────────
print('Section 1: Loading model and data...')
with open('data/processed/lgbm_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('data/processed/feature_cols.txt') as f:
    FEATURE_COLS = f.read().splitlines()

training_data = pd.read_parquet('data/processed/training_dataset.parquet')
products      = load_product_lookup()
print(f'  Model: {model.best_iteration_} trees')
print(f'  Features: {len(FEATURE_COLS)}')
print()

# ── GENERATE EXPLANATIONS FOR SAMPLE USERS ───────────────────
print('Section 2: Generating explained recommendations...')
print()

sample_users = training_data['user_id'].unique()[:5]

for uid in sample_users:
    print(f'  User {uid} — Explained Recommendations:')
    print('  ' + '-' * 70)

    explained = explain_recommendation(
        user_id       = uid,
        model         = model,
        training_data = training_data,
        feature_cols  = FEATURE_COLS,
        products      = products,
        n             = 5
    )

    if len(explained) == 0:
        print('  No data for this user')
        continue

    for _, row in explained.iterrows():
        actual  = 'WILL REORDER' if row['reordered'] == 1 else 'will not reorder'
        print(f'  [{row["reorder_probability"]:.3f}] '
              f'{str(row["product_name"])[:35]:35s} '
              f'({row["department"]})')
        print(f'           Why: {row["shap_explanation"]}')
        print(f'           Actual: {actual}')
    print()

# ── FEATURE IMPORTANCE CHART ──────────────────────────────────
print('Section 3: Global feature importance chart...')

imp_df = pd.DataFrame({
    'feature':    FEATURE_COLS,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=True).tail(15)

# Colour by feature group
def get_color(feat):
    if feat.startswith('u_') or feat in ['rfm_r','rfm_f']:
        return '#1565C0'
    elif feat.startswith('p_') or feat in ['aisle_id','department_id','is_organic']:
        return '#2E7D32'
    else:
        return '#E65100'

colors = [get_color(f) for f in imp_df['feature']]

fig, ax = plt.subplots(figsize=(10, 8))
ax.barh(imp_df['feature'], imp_df['importance'],
        color=colors, edgecolor='white')
ax.set_xlabel('Feature Importance (LightGBM)', fontsize=12)
ax.set_title('Top 15 Features — Global Importance\n'
             'Blue=User | Green=Product | Orange=User-Product',
             fontsize=13, fontweight='bold')
ax.grid(True, axis='x', alpha=0.3)

from matplotlib.patches import Patch
legend = [
    Patch(facecolor='#1565C0', label='User-level features'),
    Patch(facecolor='#2E7D32', label='Product-level features'),
    Patch(facecolor='#E65100', label='User-Product features'),
]
ax.legend(handles=legend, loc='lower right', fontsize=10)
plt.tight_layout()
plt.savefig('docs/models/feature_importance_explained.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Chart saved: docs/models/feature_importance_explained.png')
print()
print('Enhancement 7 complete. Run next: python notebooks/15_complete_runner.py')
# notebooks/09_order_timing.py
# Enhancement 2 - Next Order Timing Predictor
# Run from project root: python notebooks/09_order_timing.py

import os, sys, pickle
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.data_loader import load_orders
from src.order_timing import (build_timing_features, build_timing_target,
                               train_timing_model, predict_next_order_timing)

print('=' * 60)
print('ENHANCEMENT 2 - NEXT ORDER TIMING PREDICTOR')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── LOAD DATA ─────────────────────────────────────────────────
print('Section 1: Loading orders data...')
orders = load_orders()
print(f'  Orders loaded: {len(orders):,}')
print()

# ── BUILD FEATURES ────────────────────────────────────────────
print('Section 2: Building timing features...')
features = build_timing_features(orders)
print(f'  Features shape: {features.shape}')
print(f'  Columns: {list(features.columns)}')
print()
print('  Feature stats:')
print(f'    Avg gap mean:  {features["avg_gap"].mean():.1f} days')
print(f'    Avg gap median:{features["avg_gap"].median():.1f} days')
print(f'    Most regular users (cv_gap < 0.2): {(features["cv_gap"] < 0.2).sum():,}')
print(f'    Trend increasing (ordering less):  {(features["gap_trend"] > 0).sum():,}')
print(f'    Trend decreasing (ordering more):  {(features["gap_trend"] < 0).sum():,}')
print()

# ── BUILD TARGET ──────────────────────────────────────────────
print('Section 3: Building target variable...')
target = build_timing_target(orders)
print(f'  Target shape: {target.shape}')
print(f'  Mean days until next order: {target["days_until_next_order"].mean():.1f}')
print(f'  Median:                     {target["days_until_next_order"].median():.1f}')
print()

# ── TRAIN MODEL ───────────────────────────────────────────────
print('Section 4: Training timing model...')
model, FEATURE_COLS, metrics = train_timing_model(features, target)
print(f'  Best iteration: {model.best_iteration_}')
print()

# ── PREDICTIONS ───────────────────────────────────────────────
print('Section 5: Generating predictions for all users...')
all_user_ids = features['user_id'].tolist()
predictions  = predict_next_order_timing(all_user_ids, features, model, FEATURE_COLS)

print(f'  Predictions generated: {len(predictions):,}')
print(f'  Users flagged as timing risk: {predictions["timing_risk"].sum():,}')
print()
print('  Sample predictions:')
print(predictions.head(10).to_string(index=False))
print()

# ── VISUALISATIONS ────────────────────────────────────────────
print('Section 6: Generating charts...')

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Chart 1: Distribution of predicted next order timing
axes[0].hist(predictions['predicted_days_until_next_order'],
             bins=30, color='#1565C0', edgecolor='white', alpha=0.8)
axes[0].axvline(predictions['predicted_days_until_next_order'].mean(),
                color='red', linestyle='--',
                label=f'Mean: {predictions["predicted_days_until_next_order"].mean():.1f} days')
axes[0].set_xlabel('Predicted Days Until Next Order', fontsize=12)
axes[0].set_ylabel('Number of Users', fontsize=12)
axes[0].set_title('Next Order Timing Distribution', fontsize=13, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Chart 2: Actual vs average gap comparison
axes[1].scatter(predictions['avg_gap'],
                predictions['predicted_days_until_next_order'],
                alpha=0.1, s=5, color='#1565C0')
max_val = max(predictions['avg_gap'].max(),
              predictions['predicted_days_until_next_order'].max())
axes[1].plot([0, max_val], [0, max_val], 'r--', label='Perfect prediction line')
axes[1].set_xlabel('Historical Average Gap (days)', fontsize=12)
axes[1].set_ylabel('Predicted Next Order (days)', fontsize=12)
axes[1].set_title('Predicted vs Historical Average', fontsize=13, fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('docs/models/order_timing.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Chart saved: docs/models/order_timing.png')
print()

# ── SAVE OUTPUTS ──────────────────────────────────────────────
print('Section 7: Saving outputs...')
pickle.dump(model, open('data/processed/timing_model.pkl', 'wb'))
predictions.to_parquet('data/processed/order_timing_predictions.parquet', index=False)
print('  timing_model.pkl saved')
print('  order_timing_predictions.parquet saved')
print()

# ── BUSINESS INSIGHT ──────────────────────────────────────────
print('BUSINESS INSIGHT:')
print('-' * 50)
at_risk = predictions[predictions['timing_risk']]
print(f'  {len(at_risk):,} users are predicted to order significantly later')
print(f'  than their historical average.')
print(f'  Recommended action: send these users a personalised')
print(f'  reminder notification {at_risk["recommended_notification_day"].median():.0f} days after their last order.')
print('-' * 50)
print()
print('Enhancement 2 complete. Run next: python notebooks/10_basket_completion.py')
# notebooks/19_basket_size_predictor.py
# Enhancement 12 - Basket Size Predictor
# Run from project root: python notebooks/19_basket_size_predictor.py

import os, sys, pickle
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.data_loader import load_orders
from src.basket_predictor import (build_basket_size_features,
                                   build_basket_size_target,
                                   train_basket_model,
                                   predict_basket_sizes)

print('=' * 60)
print('ENHANCEMENT 12 - BASKET SIZE PREDICTOR')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── LOAD DATA ─────────────────────────────────────────────────
print('Section 1: Loading data...')
orders   = load_orders()
segments = pd.read_parquet('data/processed/user_segments.parquet')
clv      = pd.read_parquet('data/processed/clv_predictions.parquet')
prior    = pd.read_csv(
    'data/raw/order_products__prior.csv',
    dtype={'order_id': 'int32', 'product_id': 'int32',
           'add_to_cart_order': 'int16', 'reordered': 'int8'}
)
print(f'  Orders:   {len(orders):,}')
print(f'  Segments: {len(segments):,}')
print(f'  Prior:    {len(prior):,}')
print()

# ── BUILD FEATURES ────────────────────────────────────────────
print('Section 2: Building basket size features...')
features = build_basket_size_features(orders, prior, segments, clv)
print(f'  Features shape: {features.shape}')
print(f'  Avg basket size overall: {features["avg_basket_size"].mean():.1f} items')
print(f'  Most users order between '
      f'{features["avg_basket_size"].quantile(0.25):.0f} and '
      f'{features["avg_basket_size"].quantile(0.75):.0f} items')
print()

# ── BUILD TARGET ──────────────────────────────────────────────
print('Section 3: Building target variable...')
target = build_basket_size_target(orders, prior)
print(f'  Target shape: {target.shape}')
print(f'  Mean next basket size: {target["next_basket_size"].mean():.1f}')
print(f'  Median:                {target["next_basket_size"].median():.1f}')
print()

# ── TRAIN MODEL ───────────────────────────────────────────────
print('Section 4: Training basket size model...')
model, FEATURE_COLS, mae = train_basket_model(features, target)
print(f'  Best iteration: {model.best_iteration_}')
print()

# ── PREDICTIONS ───────────────────────────────────────────────
print('Section 5: Generating predictions...')
all_users   = features['user_id'].tolist()
predictions = predict_basket_sizes(all_users, features, model, FEATURE_COLS)

print(f'  Predictions generated: {len(predictions):,}')
print()
print('  Routing decision distribution:')
routing_dist = predictions['routing_decision'].value_counts()
for decision, count in routing_dist.items():
    pct = count / len(predictions) * 100
    print(f'    {decision:<40} {count:>8,} ({pct:.1f}%)')
print()
print('  Sample predictions:')
print(predictions.head(8).to_string(index=False))
print()

# ── VISUALISATION ─────────────────────────────────────────────
print('Section 6: Generating charts...')

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Chart 1: Predicted basket size distribution
axes[0].hist(
    predictions['predicted_basket_size'].clip(upper=40),
    bins=30, color='#1565C0', edgecolor='white', alpha=0.8
)
axes[0].axvline(
    predictions['predicted_basket_size'].mean(),
    color='red', linestyle='--',
    label=f'Mean: {predictions["predicted_basket_size"].mean():.1f}'
)
axes[0].set_title('Predicted Basket Size Distribution',
                   fontsize=13, fontweight='bold')
axes[0].set_xlabel('Predicted Items in Next Order', fontsize=12)
axes[0].set_ylabel('Number of Users', fontsize=12)
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Chart 2: Routing decision pie
colors = ['#1565C0', '#1976D2', '#42A5F5', '#90CAF9']
axes[1].pie(
    routing_dist.values,
    labels   = [r.replace('_', ' ').title()
                for r in routing_dist.index],
    colors   = colors[:len(routing_dist)],
    autopct  = '%1.1f%%',
    startangle = 90
)
axes[1].set_title('Frontend Routing Decision Distribution',
                   fontsize=13, fontweight='bold')

plt.tight_layout()
os.makedirs('docs/models', exist_ok=True)
plt.savefig('docs/models/basket_size_predictor.png',
            dpi=150, bbox_inches='tight')
plt.close()
print('  Chart saved: docs/models/basket_size_predictor.png')
print()

# ── SAVE OUTPUTS ──────────────────────────────────────────────
print('Section 7: Saving outputs...')
os.makedirs('data/processed', exist_ok=True)
pickle.dump(model, open('data/processed/basket_size_model.pkl', 'wb'))
predictions.to_parquet(
    'data/processed/basket_size_predictions.parquet', index=False)
print('  basket_size_model.pkl saved')
print('  basket_size_predictions.parquet saved')
print()
print('Enhancement 12 complete.')
print('Run next: python notebooks/20_affinity_network.py')
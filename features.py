# phase3_features.py
# Phase 3 - Feature Engineering and LightGBM Reorder Prediction Model
# Run from project root: python features.py

import os
import sys
import pickle
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.abspath('.'))
from src.data_loader import (load_orders, load_order_products_train,
                              load_order_products_prior,
                              load_product_lookup, load_user_segments)

print('=' * 60)
print('PHASE 3 - FEATURE ENGINEERING AND LIGHTGBM MODEL')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

os.makedirs('data/processed', exist_ok=True)
os.makedirs('docs/models', exist_ok=True)

# ── SECTION 1: LOAD DATA ──────────────────────────────────────
print('Section 1: Loading all data...')

orders   = load_orders()
train    = load_order_products_train()
products = load_product_lookup()
segments = load_user_segments()

prior_orders = orders[orders['eval_set'] == 'prior'].copy()
train_orders = orders[orders['eval_set'] == 'train'].copy()

print(f'  orders:        {len(orders):,} rows')
print(f'  train set:     {len(train):,} rows')
print(f'  prior orders:  {len(prior_orders):,} rows')
print(f'  products:      {len(products):,} rows')
print(f'  segments:      {len(segments):,} rows')
print()

# ── SECTION 2: LOAD PRIOR ORDER PRODUCTS ─────────────────────
print('Section 2: Loading prior order products (large file - please wait)...')

prior = load_order_products_prior()  # uses absolute path from data_loader
print(f'  prior order products: {len(prior):,} rows')
print(f'  columns: {list(prior.columns)}')
print()

print('  Joining prior products with order metadata...')
# FIX: was `prior_orders = [['col']]` (assignment instead of df reference)
prior_full = prior.merge(
    prior_orders[['order_id', 'user_id', 'order_number', 'days_since_prior_order']],
    on='order_id'
)
print(f'  prior_full shape: {prior_full.shape}')
print()

# ── SECTION 3: USER LEVEL FEATURES ───────────────────────────
print('Section 3: Building user-level features...')

user_features = (prior_full
    .groupby('user_id')
    .agg(
        u_total_orders     = ('order_id',               'nunique'),
        u_total_products   = ('product_id',             'count'),
        u_unique_products  = ('product_id',             'nunique'),
        u_reorder_rate     = ('reordered',              'mean'),
        u_avg_basket_size  = ('order_id',               lambda x: x.count() / x.nunique()),
        u_avg_days_between = ('days_since_prior_order', 'mean'),
    )
    .reset_index()
)

# FIX: was referencing 'avg_days_between' (missing 'u_' prefix)
user_features['u_avg_days_between'] = user_features['u_avg_days_between'].fillna(
    user_features['u_avg_days_between'].median()
)

user_features = user_features.merge(
    segments[['user_id', 'rfm_r', 'rfm_f', 'segment']],
    on='user_id', how='left'
)

# FIX: was a set of strings instead of a dict, and had typos in keys
seg_encoding = {
    'Lapsed Users':      0,
    'Occasional Buyers': 1,
    'Regular Shoppers':  2,
    'Weekly Loyalists':  3,
}
user_features['u_segment_code'] = (user_features['segment']
                                   .map(seg_encoding)
                                   .fillna(0)
                                   .astype(int))

print(f'  user_features shape: {user_features.shape}')
print(f'  nulls: {user_features.isnull().sum().sum()}')
print()

print('  [Soham validation]')
assert user_features['u_reorder_rate'].between(0, 1).all(), 'FAIL: reorder_rate out of range'
assert user_features['u_total_orders'].min() >= 1,          'FAIL: zero order users found'
print('  [PASS] All user feature checks passed')
print()

# ── SECTION 4: PRODUCT LEVEL FEATURES ────────────────────────
print('Section 4: Building product-level features...')

product_features = (prior_full
    .groupby('product_id')
    .agg(
        p_total_orders      = ('order_id',          'nunique'),
        p_total_purchased   = ('reordered',         'count'),
        p_reorder_rate      = ('reordered',         'mean'),
        p_avg_cart_position = ('add_to_cart_order', 'mean'),
    )
    .reset_index()
)

products['is_organic'] = products['product_name'].str.contains('Organic', case=False, na=False).astype(int)
product_features = product_features.merge(
    products[['product_id', 'aisle_id', 'department_id', 'is_organic']],
    on='product_id', how='left'
)

print(f'  product_features shape: {product_features.shape}')
print(f'  nulls: {product_features.isnull().sum().sum()}')
print()

print('  [Soham validation]')
assert product_features['p_reorder_rate'].between(0, 1).all(), 'FAIL: reorder_rate out of range'
assert product_features['p_total_orders'].min() >= 1,          'FAIL: zero order products'
print('  [PASS] All product feature checks passed')
print()

# ── SECTION 5: USER-PRODUCT LEVEL FEATURES ───────────────────
print('Section 5: Building user-product level features...')

up_features = (prior_full
    .groupby(['user_id', 'product_id'])
    .agg(
        up_total_orders      = ('order_id',          'nunique'),
        up_reorder_rate      = ('reordered',         'mean'),
        up_avg_cart_position = ('add_to_cart_order', 'mean'),
        up_last_order_number = ('order_number',      'max'),
    )
    .reset_index()
)

# FIX: was grouping by 'order_id'.max() instead of 'order_number'.max()
user_max_order = (prior_full
    .groupby('user_id')['order_number']
    .max()
    .reset_index()
    .rename(columns={'order_number': 'u_max_order_number'})
)

up_features = up_features.merge(user_max_order, on='user_id', how='left')
up_features['up_orders_since_last'] = (
    up_features['u_max_order_number'] - up_features['up_last_order_number']
)
up_features = up_features.drop(columns=['u_max_order_number'])

print(f'  up_features shape: {up_features.shape}')
print(f'  nulls: {up_features.isnull().sum().sum()}')
print()

print('  [Soham validation]')
assert up_features['up_reorder_rate'].between(0, 1).all(),  'FAIL: reorder_rate out of range'
assert up_features['up_orders_since_last'].min() >= 0,      'FAIL: negative orders since last'
assert up_features.isnull().sum().sum() == 0,               'FAIL: nulls in up features'
print('  [PASS] All user-product feature checks passed')
print()

# ── SECTION 6: BUILD TRAINING DATASET ────────────────────────
print('Section 6: Building training dataset...')

train_labels = train[['order_id', 'product_id', 'reordered']].copy()
# FIX: was merging train_orders on 'product_id' — should be 'user_id'
train_labels = train_labels.merge(
    train_orders[['order_id', 'user_id']],
    on='order_id', how='left'
)

print(f'  Train labels shape: {train_labels.shape}')
print(f'  Reorder rate in train: {train_labels["reordered"].mean()*100:.1f}%')

df = train_labels.copy()
df = df.merge(user_features.drop(columns=['segment']), on='user_id',                 how='left')
df = df.merge(product_features,                        on='product_id',              how='left')
df = df.merge(up_features,                             on=['user_id', 'product_id'], how='left')

# FIX: was df['up_cols'] (string key) instead of df[up_cols] (list variable)
up_cols = ['up_total_orders', 'up_reorder_rate',
           'up_avg_cart_position', 'up_last_order_number', 'up_orders_since_last']
df[up_cols] = df[up_cols].fillna(0)

print(f'  Training dataset shape: {df.shape}')
print(f'  Nulls remaining: {df.isnull().sum().sum()}')
print()

df.to_parquet('data/processed/training_dataset.parquet', index=False)
print('  training_dataset.parquet saved')
print()

# ── SECTION 7: FEATURE LIST ───────────────────────────────────
print('Section 7: Feature summary...')

FEATURE_COLS = [
    # user features
    'u_total_orders', 'u_total_products', 'u_unique_products',
    'u_reorder_rate', 'u_avg_basket_size', 'u_avg_days_between',
    'rfm_r', 'rfm_f', 'u_segment_code',
    # product features
    'p_total_orders', 'p_total_purchased', 'p_reorder_rate',
    'p_avg_cart_position', 'aisle_id', 'department_id', 'is_organic',
    # user-product features
    'up_total_orders', 'up_reorder_rate', 'up_avg_cart_position',
    'up_last_order_number', 'up_orders_since_last',
]
TARGET_COL = 'reordered'  # FIX: was TARGET_COLS (plural), used as string key below

print(f'  Total features: {len(FEATURE_COLS)}')
missing = [f for f in FEATURE_COLS if f not in df.columns]
if missing:
    print(f'  WARNING: Missing columns: {missing}')
else:
    print('  [PASS] All 21 feature columns present in dataset')
print()

# ── SECTION 8: TRAIN LIGHTGBM ─────────────────────────────────
print('Section 8: Training LightGBM model...')

try:
    import lightgbm as lgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (f1_score, roc_auc_score,
                                  precision_score, recall_score)

    # FIX: was df['FEATURE_COLS'] and df['TARGET_COLS'] (string literals, not variables)
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    print(f'  Dataset: X={X.shape}  y={y.shape}')
    print(f'  Positive rate: {y.mean()*100:.1f}%')
    print()

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f'  Train: {len(X_train):,}  Val: {len(X_val):,}')
    print('  Training LightGBM... (2-3 minutes)')
    print()

    model = lgb.LGBMClassifier(
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=31,
        max_depth=-1,        # FIX: was max_depth=1 (severely underfits)
        min_child_samples=20,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(50, verbose=False),
                   lgb.log_evaluation(100)]
    )

    print(f'  Best iteration: {model.best_iteration_}')
    print()

    # ── SECTION 9: EVALUATE ───────────────────────────────────
    # FIX: Sections 9-12 were outdented outside the try block, causing SyntaxError
    print('Section 9: Evaluating model...')

    y_pred_proba = model.predict_proba(X_val)[:, 1]
    y_pred       = (y_pred_proba >= 0.5).astype(int)

    f1        = f1_score(y_val, y_pred)
    precision = precision_score(y_val, y_pred)
    recall    = recall_score(y_val, y_pred)
    roc_auc   = roc_auc_score(y_val, y_pred_proba)

    print()
    print('  MODEL PERFORMANCE')
    print('  ' + '-' * 35)
    print(f'  F1 Score:  {f1:.4f}')
    print(f'  Precision: {precision:.4f}')
    print(f'  Recall:    {recall:.4f}')
    print(f'  ROC-AUC:   {roc_auc:.4f}')
    print('  ' + '-' * 35)
    if f1 >= 0.38:
        print(f'  [PASS] F1 {f1:.4f} meets target of 0.38')
    else:
        print(f'  [NOTE] F1 {f1:.4f} below target - consider tuning')
    print()

    # ── SECTION 10: FEATURE IMPORTANCE ───────────────────────
    print('Section 10: Feature importance chart...')

    imp_df = pd.DataFrame({
        'feature':    FEATURE_COLS,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=True).tail(15)

    # FIX: was plt.subplot() (returns axes tuple) — should be plt.subplots()
    fig, ax = plt.subplots(figsize=(10, 7))
    colors  = ['#2196F3' if i >= len(imp_df) - 5
               else '#90CAF9' for i in range(len(imp_df))]
    ax.barh(imp_df['feature'], imp_df['importance'],
            color=colors, edgecolor='white')
    ax.set_xlabel('Feature Importance', fontsize=12)
    ax.set_title('Top 15 Most Important Features\nInstacart Reorder Prediction',
                 fontsize=14, fontweight='bold')
    ax.grid(True, axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig('docs/models/feature_importance.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('  Chart saved: docs/models/feature_importance.png')
    print()

    # ── SECTION 11: SAVE MODEL ────────────────────────────────
    print('Section 11: Saving model...')

    with open('data/processed/lgbm_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print('  lgbm_model.pkl saved')

    with open('data/processed/feature_cols.txt', 'w') as f:
        f.write('\n'.join(FEATURE_COLS))
    print('  feature_cols.txt saved')
    print()

    # ── SECTION 12: SAMPLE PREDICTIONS ───────────────────────
    print('Section 12: Sample predictions for 5 users...')
    print()

    sample_users = df['user_id'].unique()[:5]
    # FIX: loop body was half-outdented — proba/top5/print were outside the for loop
    for uid in sample_users:
        user_data = df[df['user_id'] == uid].copy()
        proba     = model.predict_proba(user_data[FEATURE_COLS])[:, 1]
        user_data = user_data.assign(reorder_probability=proba)
        top5      = (user_data
                     .merge(products[['product_id', 'product_name']],
                            on='product_id', how='left')
                     .sort_values('reorder_probability', ascending=False)
                     .head(5))
        print(f'  User {uid} — Top 5 predicted reorders:')
        for _, row in top5.iterrows():
            actual = 'REORDERED' if row['reordered'] == 1 else 'not reordered'
            print(f'    {str(row["product_name"])[:40]:40s} '
                  f'prob={row["reorder_probability"]:.3f}  actual={actual}')
        print()

except ImportError:
    print('  LightGBM not installed. Run: pip install lightgbm')
    print('  Then rerun this script.')

print('=' * 60)
print('PHASE 3 COMPLETE')
print()
print('Outputs:')
print('  data/processed/training_dataset.parquet')
print('  data/processed/lgbm_model.pkl')
print('  data/processed/feature_cols.txt')
print('  docs/models/feature_importance.png')
print()
print('Next: Phase 4 - Basket Recommendation API')
print('=' * 60)
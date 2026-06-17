# notebooks/10_basket_completion.py
# Enhancement 3 - Basket Completion Score
# Run from project root: python notebooks/10_basket_completion.py

import os, sys, pickle
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.data_loader import load_product_lookup
from src.basket_completion import (build_order_matrix,
                                    compute_association_rules,
                                    complete_basket)

print('=' * 60)
print('ENHANCEMENT 3 - BASKET COMPLETION ENGINE')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── LOAD DATA ─────────────────────────────────────────────────
print('Section 1: Loading prior orders (large file)...')
prior = pd.read_csv(
    'data/raw/order_products__prior.csv',
    dtype={'order_id': 'int32', 'product_id': 'int32',
           'add_to_cart_order': 'int16', 'reordered': 'int8'}
)
products = load_product_lookup()
print(f'  Prior orders: {len(prior):,}')
print(f'  Products:     {len(products):,}')
print()

# ── BUILD ORDER MATRIX ────────────────────────────────────────
print('Section 2: Building order matrix (sampling 50,000 orders)...')
matrix = build_order_matrix(prior, min_orders=50)
print(f'  Matrix shape: {matrix.shape}')
print(f'  Orders: {matrix.shape[0]:,} | Products: {matrix.shape[1]:,}')
print()

# ── COMPUTE ASSOCIATION RULES ─────────────────────────────────
print('Section 3: Computing association rules...')
print('  This may take 2-3 minutes...')
rules = compute_association_rules(
    matrix,
    min_support    = 0.005,
    min_confidence = 0.05,
    max_rules      = 3000
)
print(f'  Total rules computed: {len(rules):,}')
if len(rules) > 0:
    print(f'  Max lift:   {rules["lift"].max():.4f}')
    print(f'  Mean lift:  {rules["lift"].mean():.4f}')
    print(f'  Min lift:   {rules["lift"].min():.4f}')
    print()
    print('  Top 10 rules by lift:')
    top10 = (rules
             .head(10)
             .merge(products[['product_id','product_name']],
                    left_on='antecedent', right_on='product_id', how='left')
             .rename(columns={'product_name': 'if_you_buy'}))
    top10 = (top10
             .merge(products[['product_id','product_name']],
                    left_on='consequent', right_on='product_id', how='left')
             .rename(columns={'product_name': 'you_might_want'}))
    for _, row in top10.iterrows():
        print(f'    {str(row["if_you_buy"])[:30]:30s} -> '
              f'{str(row["you_might_want"])[:30]:30s} '
              f'(lift={row["lift"]:.3f}, conf={row["confidence"]:.3f})')
print()

# ── TEST BASKET COMPLETION ────────────────────────────────────
print('Section 4: Testing basket completion...')
print()

# Test with 3 different basket scenarios
test_baskets = [
    {'name': 'Breakfast basket',
     'items': prior[prior['product_id'].isin(
         products[products['department']=='breakfast']['product_id']
     )]['product_id'].value_counts().head(3).index.tolist()},

    {'name': 'Produce basket',
     'items': prior[prior['product_id'].isin(
         products[products['department']=='produce']['product_id']
     )]['product_id'].value_counts().head(3).index.tolist()},

    {'name': 'Dairy basket',
     'items': prior[prior['product_id'].isin(
         products[products['department']=='dairy eggs']['product_id']
     )]['product_id'].value_counts().head(3).index.tolist()},
]

for basket in test_baskets:
    if len(basket['items']) == 0:
        continue
    print(f'  Basket: {basket["name"]}')
    basket_names = products[products['product_id'].isin(basket['items'])]['product_name'].tolist()
    for name in basket_names:
        print(f'    - {name}')
    print()

    suggestions = complete_basket(basket['items'], rules, products, n=5)
    if len(suggestions) > 0:
        print('  Suggested additions:')
        for _, row in suggestions.iterrows():
            print(f'    [{row["max_lift"]:.2f}x] {str(row["product_name"])[:40]:40s} '
                  f'({row["department"]})')
    else:
        print('  No suggestions found for this basket')
    print()

# ── SAVE OUTPUTS ──────────────────────────────────────────────
print('Section 5: Saving outputs...')
os.makedirs('data/processed', exist_ok=True)

if len(rules) > 0:
    rules.to_parquet('data/processed/association_rules.parquet', index=False)
    print(f'  association_rules.parquet saved: {len(rules):,} rules')

# ── VISUALISATION ─────────────────────────────────────────────
if len(rules) > 0:
    print()
    print('Section 6: Generating charts...')

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Chart 1: Lift distribution
    axes[0].hist(rules['lift'], bins=30,
                 color='#1565C0', edgecolor='white', alpha=0.8)
    axes[0].axvline(1.0, color='red', linestyle='--', label='Lift = 1 (random)')
    axes[0].set_xlabel('Lift', fontsize=12)
    axes[0].set_ylabel('Number of Rules', fontsize=12)
    axes[0].set_title('Association Rule Lift Distribution', fontsize=13, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Chart 2: Support vs Confidence scatter
    sample_rules = rules.sample(min(500, len(rules)), random_state=42)
    scatter = axes[1].scatter(sample_rules['support'],
                               sample_rules['confidence'],
                               c=sample_rules['lift'],
                               cmap='RdYlGn', alpha=0.6, s=20)
    plt.colorbar(scatter, ax=axes[1], label='Lift')
    axes[1].set_xlabel('Support', fontsize=12)
    axes[1].set_ylabel('Confidence', fontsize=12)
    axes[1].set_title('Support vs Confidence\n(coloured by Lift)',
                       fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('docs/models/basket_completion.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('  Chart saved: docs/models/basket_completion.png')

print()
print('Enhancement 3 complete. Run next: python notebooks/11_promotion_engine.py')
# notebooks/20_affinity_network.py
# Enhancement 13 - Product Affinity Network
# Run from project root: python notebooks/20_affinity_network.py

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from src.data_loader import load_product_lookup
from src.affinity_network import (build_cooccurrence_matrix,
                                   compute_network_metrics,
                                   detect_communities)

print('=' * 60)
print('ENHANCEMENT 13 - PRODUCT AFFINITY NETWORK')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── LOAD DATA ─────────────────────────────────────────────────
print('Section 1: Loading data...')
products = load_product_lookup()
prior    = pd.read_csv(
    'data/raw/order_products__prior.csv',
    dtype={'order_id': 'int32', 'product_id': 'int32',
           'add_to_cart_order': 'int16', 'reordered': 'int8'}
)
print(f'  Products: {len(products):,}')
print(f'  Prior:    {len(prior):,}')
print()

# ── BUILD COOCCURRENCE MATRIX ─────────────────────────────────
print('Section 2: Building co-occurrence matrix...')
print('  Sampling 30,000 orders and top 150 products...')
cooc = build_cooccurrence_matrix(
    prior, products,
    top_n_products = 150,
    sample_orders  = 30000
)
print(f'  Co-occurrence pairs found: {len(cooc):,}')
print(f'  Max co-occurrence: {cooc["cooccurrence_count"].max()}')
print(f'  Mean co-occurrence: {cooc["cooccurrence_count"].mean():.1f}')
print()

# ── COMPUTE NETWORK METRICS ───────────────────────────────────
print('Section 3: Computing network metrics...')
metrics = compute_network_metrics(cooc, products, min_cooc=5)
print(f'  Nodes in network: {len(metrics)}')
print()
print('  Top 15 most connected products (highest degree):')
print(f'  {"Product":<35} {"Dept":<15} '
      f'{"Degree":>8} {"Strength":>10}')
print('  ' + '-' * 70)
for _, row in metrics.head(15).iterrows():
    print(f'  {str(row["product_name"])[:34]:<35} '
          f'{str(row["department"])[:14]:<15} '
          f'{row["degree"]:>8.0f} '
          f'{row["strength"]:>10.0f}')
print()

# ── DETECT COMMUNITIES ────────────────────────────────────────
print('Section 4: Detecting product communities...')
communities = detect_communities(cooc, n_communities=6, min_cooc=8)
print(f'  Products assigned to communities: {len(communities)}')
community_sizes = pd.Series(communities).value_counts().sort_index()
print('  Community sizes:')
for comm_id, size in community_sizes.items():
    print(f'    Community {comm_id}: {size} products')
print()

# ── NETWORK VISUALISATION ─────────────────────────────────────
print('Section 5: Generating network visualisation...')

COMMUNITY_COLORS = [
    '#E31837', '#1565C0', '#4CAF50',
    '#FF9800', '#9C27B0', '#00BCD4'
]

# Take top 60 products for visualisation
top_products = metrics.head(60)['product_id'].tolist()
viz_cooc     = cooc[
    cooc['product_a'].isin(top_products) &
    cooc['product_b'].isin(top_products) &
    (cooc['cooccurrence_count'] >= 10)
]

# Build adjacency for layout
nodes = list(set(
    viz_cooc['product_a'].tolist() +
    viz_cooc['product_b'].tolist()
))

# Simple circular layout
n_nodes = len(nodes)
angles  = np.linspace(0, 2 * np.pi, n_nodes, endpoint=False)
pos     = {node: (np.cos(a), np.sin(a))
           for node, a in zip(nodes, angles)}

fig, ax = plt.subplots(figsize=(14, 14))
ax.set_facecolor('#0F172A')
fig.patch.set_facecolor('#0F172A')

# Draw edges
max_weight = viz_cooc['cooccurrence_count'].max()
for _, row in viz_cooc.iterrows():
    if row['product_a'] in pos and row['product_b'] in pos:
        x1, y1 = pos[row['product_a']]
        x2, y2 = pos[row['product_b']]
        alpha  = row['cooccurrence_count'] / max_weight * 0.6
        ax.plot([x1, x2], [y1, y2],
                color='white', alpha=alpha,
                linewidth=0.5, zorder=1)

# Draw nodes
node_metrics = metrics[metrics['product_id'].isin(nodes)].copy()
for _, row in node_metrics.iterrows():
    if row['product_id'] in pos:
        x, y    = pos[row['product_id']]
        comm_id = communities.get(row['product_id'], 0)
        color   = COMMUNITY_COLORS[comm_id % len(COMMUNITY_COLORS)]
        size    = max(50, min(500, row['degree'] * 20))
        ax.scatter(x, y, s=size, c=color, zorder=3, alpha=0.9)

# Draw labels for top 20 most connected nodes
top20_nodes = node_metrics.head(20)
for _, row in top20_nodes.iterrows():
    if row['product_id'] in pos:
        x, y = pos[row['product_id']]
        name = str(row['product_name'])[:20]
        ax.annotate(name, (x, y),
                    fontsize=6, color='white',
                    ha='center', va='bottom',
                    xytext=(0, 8),
                    textcoords='offset points')

# Legend
legend_patches = [
    mpatches.Patch(color=COMMUNITY_COLORS[i],
                   label=f'Community {i+1}')
    for i in range(min(6, len(community_sizes)))
]
ax.legend(handles=legend_patches, loc='upper right',
          fontsize=10, framealpha=0.3,
          facecolor='#1E293B', edgecolor='white',
          labelcolor='white')

ax.set_title('Product Affinity Network\n'
             'Node size = connections | '
             'Edge opacity = co-purchase strength',
             fontsize=14, fontweight='bold', color='white', pad=20)
ax.axis('off')

os.makedirs('docs/models', exist_ok=True)
plt.savefig('docs/models/product_network.png',
            dpi=150, bbox_inches='tight',
            facecolor='#0F172A')
plt.close()
print('  Chart saved: docs/models/product_network.png')
print()

# ── SAVE OUTPUTS ──────────────────────────────────────────────
print('Section 6: Saving outputs...')
os.makedirs('data/processed', exist_ok=True)

metrics['community'] = metrics['product_id'].map(communities).fillna(-1)
metrics.to_parquet('data/processed/product_network.parquet', index=False)
cooc.to_parquet('data/processed/cooccurrence_matrix.parquet', index=False)
print('  product_network.parquet saved')
print('  cooccurrence_matrix.parquet saved')
print()
print('Enhancement 13 complete.')
print('Run next: python notebooks/21_bandit_promotions.py')

import pandas as pd
import numpy as np
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')


def build_cooccurrence_matrix(prior: pd.DataFrame,
                               products: pd.DataFrame,
                               top_n_products: int = 150,
                               sample_orders: int = 30000) -> pd.DataFrame:
    """
    Build product co-occurrence matrix.
    Two products co-occur if they appear in the same order.

    Parameters
    ----------
    prior           : order_products_prior dataframe
    products        : product lookup
    top_n_products  : only include top N most popular products
    sample_orders   : sample this many orders for speed

    Returns
    -------
    DataFrame with columns: product_a, product_b, cooccurrence_count
    """
    # Get top N products by order frequency
    top_products = (prior
                    .groupby('product_id')['order_id']
                    .nunique()
                    .sort_values(ascending=False)
                    .head(top_n_products)
                    .index.tolist())

    filtered = prior[prior['product_id'].isin(top_products)]

    # Sample orders
    sample_order_ids = np.random.choice(
        filtered['order_id'].unique(),
        size=min(sample_orders, filtered['order_id'].nunique()),
        replace=False
    )
    filtered = filtered[filtered['order_id'].isin(sample_order_ids)]

    # Build co-occurrence pairs
    pairs = []
    for order_id, group in filtered.groupby('order_id'):
        prods = group['product_id'].tolist()
        if len(prods) >= 2:
            for p1, p2 in combinations(sorted(prods), 2):
                pairs.append((p1, p2))

    pairs_df = pd.DataFrame(pairs, columns=['product_a', 'product_b'])
    cooc     = (pairs_df
                .groupby(['product_a', 'product_b'])
                .size()
                .reset_index()
                .rename(columns={0: 'cooccurrence_count'}))

    return cooc


def compute_network_metrics(cooc_df: pd.DataFrame,
                             products: pd.DataFrame,
                             min_cooc: int = 5) -> pd.DataFrame:
    """
    Compute network centrality metrics for each product node.

    Metrics:
    - degree:      number of unique products it co-occurs with
    - strength:    total co-occurrence count across all connections
    - avg_weight:  average co-occurrence per connection
    """
    filtered = cooc_df[cooc_df['cooccurrence_count'] >= min_cooc]

    degree_a = (filtered
                .groupby('product_a')
                .agg(
                    degree_a   = ('product_b',          'nunique'),
                    strength_a = ('cooccurrence_count', 'sum'),
                )
                .reset_index()
                .rename(columns={'product_a': 'product_id'}))

    degree_b = (filtered
                .groupby('product_b')
                .agg(
                    degree_b   = ('product_a',          'nunique'),
                    strength_b = ('cooccurrence_count', 'sum'),
                )
                .reset_index()
                .rename(columns={'product_b': 'product_id'}))
    
    metrics = degree_a.merge(degree_b, on='product_id', how='outer').fillna(0)
    metrics['degree'] = metrics['degree_a'] + metrics['degree_b']
    metrics['strength'] = metrics['strength_a'] + metrics['strength_b']
    metrics['avg_weight'] = (
        metrics['strength'] / metrics['degree'].clip(lower=1)
    ).round(2)

    metrics = metrics[['product_id', 'degree', 'strength', 'avg_weight']]
    metrics = metrics.merge(
        products[['product_id', 'product_name', 'department']],
        on='product_id', how='left'
    )

    return metrics.sort_values('degree', ascending=False)

def detect_communities(cooc_df: pd.DataFrame,
                       n_communities: int = 6,
                       min_cooc: int = 5) -> dict:
    
    """
    Simple community detection using degree-based greedy assignment.
    Groups products into communities based on their most common
    co-purchase partners.

    Returns dict mapping product_id to community_id.
    """

    filtered = cooc_df[cooc_df['cooccurrence_count'] >= min_cooc].copy()
    filtered = filtered.sort_values('cooccurrence_count', ascending=False)

    communities = {}
    community_id = 0

    for _, row in filtered.iterrows():
        p_a = row['product_a']
        p_b = row['product_b']

        if p_a not in communities and p_b not in communities:
            if community_id < n_communities:
                communities[p_a] = community_id
                communities[p_b] = community_id
                community_id        += 1

        elif p_a in communities and p_b not in communities:
            communities[p_b] = communities[p_a]
        elif p_b in communities and p_a not in communities:
            communities[p_a] = communities[p_b]
        

    return communities
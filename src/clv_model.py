import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def compute_rfm_clv_features(orders: pd.DataFrame) -> pd.DataFrame:
    """
    Build features needed for CLV estimation.
    Since we do not have actual price data we use order count
    and basket size as monetary proxies.
    """
    prior = orders[orders['eval_set'] == 'prior'].copy()
    train = orders[orders['eval_set'] == 'train'].copy()

    # Recency: days since last prior order
    recency = (prior
               .groupby('user_id')['days_since_prior_order']
               .mean()
               .reset_index()
               .rename(columns={'days_since_prior_order': 'avg_recency'}))
    
    # Frequency: total orders in prior set
    frequency = (prior
                 .groupby('user_id')['order_id']
                 .nunique()
                 .reset_index()
                 .rename(columns={'order_id': 'frequency'}))
    
    # Order span: order number range as proxy for customer age
    span = (prior
            .groupby('user_id')['order_number']
            .agg(min_order='min', max_order='max')
            .reset_index())
    span['order_span'] = span['max_order'] - span['min_order'] + 1

    clv_features = (recency
                    .merge(frequency, on='user_id', how='inner')
                    .merge(span[['user_id', 'order_span',]], on='user_id', how='left'))
    
    # Average Gap
    clv_features['avg_gap'] = clv_features['avg_recency'].clip(lower=1)

    # Predicted future orders in next 90 days using simple model
    # expected_orders = frequency * (90 / (avg_gap * order_span))
    clv_features['predicted_90d_order'] = (
        clv_features['frequency'] *
        (90 / (clv_features['avg_gap'] * clv_features['order_span'].clip(lower=1)))
    ).clip(lower=0, upper=30)

    # Proxy monetary value per order (based on order frequency tier)
    clv_features['order_value_proxy'] = np.where(
        clv_features['frequency'] >= 20, 950,
        np.where(clv_features['frequency'] >= 10, 800,
                 np.where(clv_features['frequency'] >= 5, 650, 500))
    )

    # CLV estimate: predicted orders * average order value
    clv_features['clv_90d'] = (
        clv_features['predicted_90d_order'] *
        clv_features['order_value_proxy']
    ).round(2)

    # Clv tier — qcut without labels first, then map by resulting bin rank
    # (avoids 'Bin labels must be one fewer than bin edges' when ties collapse bins)
    tier_codes, bin_edges = pd.qcut(
        clv_features['clv_90d'],
        q=4,
        labels=False,
        duplicates='drop',
        retbins=True
    )
    all_labels = ['Bronze', 'Silver', 'Gold', 'Platinum']
    n_bins = len(bin_edges) - 1
    tier_labels = all_labels[-n_bins:] if n_bins > 0 else ['Bronze']
    label_map = {i: tier_labels[i] for i in range(n_bins)}
    clv_features['clv_tier'] = tier_codes.map(label_map)

    # Normalised CLV score 0-1
    min_clv = clv_features['clv_90d'].min()
    max_clv = clv_features['clv_90d'].max()
    clv_features['clv_score'] = (
        (clv_features['clv_90d'] - min_clv) /
        (max_clv - min_clv + 1e-8)
    ).round(4) 
    
    return clv_features[[
        'user_id', 'frequency', 'avg_recency', 'order_span',
        'predicted_90d_order', 'order_value_proxy',
        'clv_90d', 'clv_tier', 'clv_score'
    ]]
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score

def compute_rmf(orders):
    prior = orders[orders['eval_set'] == 'prior'].copy()
    rfm = (prior
            .groupby('user_id')
            .agg(
                recency = ('days_since_prior_order', 'mean'),
                frequency = ('order_id', 'count'),
            )
           .reset_index())
    rfm['recency'] = rfm['recency'].fillna(rfm['recency'].median())
    return rfm

def normalise_rfm(rfm):
    scaler = MinMaxScaler()
    rfm = rfm.copy()
    rfm['rfm_f'] = scaler.fit_transform(rfm[['frequency']])
    rfm['rfm_r'] = scaler.fit_transform(rfm[['recency']])
    return rfm

def find_optimal_k(rfm, k_range=range(2, 7)):
    features = rfm[['rfm_f', 'rfm_r']].values
    results = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(features)
        results.append({
            'k': k,
            'inertia': km.inertia_,
            'silhouette_score': silhouette_score(
                features, labels, sample_size=10000, random_state=42)
        })
        print(f'K={k}: Inertia={km.inertia_:>10,.0f}, Silhouette Score={results[-1]["silhouette_score"]:.4f}')  
    return pd.DataFrame(results)

def fit_and_label(rfm, k):
    features = rfm[['rfm_f', 'rfm_r']].values
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    rfm = rfm.copy()
    rfm['cluster'] = km.fit_predict(features)
    rfm['composite'] = rfm['rfm_f'] + rfm['rfm_r']
    ranking = rfm.groupby('cluster')['composite'].mean().sort_values().index.tolist()
    names = ['Lapsed Users', 'Occasional Buyers', 'Regular Shoppers', 'Weekly Loyalists']
    label_map = {c: names[i] for i, c in enumerate(ranking)}
    rfm['segment'] = rfm['cluster'].map(label_map)
    rfm = rfm.drop(columns=['composite'])
    return rfm, km

def profile_segments(rfm):
    total_users = len(rfm)
    profile = (rfm.groupby('segment')
              .agg(
                    user_count = ('user_id', 'count'),
                    avg_recency = ('recency', 'mean'),
                    avg_frequency = ('frequency', 'mean'),
                    avg_rfm_f = ('rfm_f', 'mean'),
                    avg_rfm_r = ('rfm_r', 'mean'),
    )         .reset_index())
    profile['pct_of_users'] = (profile['user_count'] / total_users * 100).round(1)
    return profile.sort_values('avg_frequency', ascending=False).reset_index(drop=True)
# notebooks/10_churn_scoring.py
# Generates churn_scores.parquet from RFM data
import os, sys
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd

print('Loading RFM data...')
user_rfm = pd.read_parquet('data/processed/user_rfm.parquet')
print(f'  Columns: {user_rfm.columns.tolist()}')
print(f'  Users: {len(user_rfm):,}')

# Churn score: higher recency (rfm_r) = higher churn risk
# Normalize rfm_r to 0-1 scale -> churn_risk_score
r_min, r_max = user_rfm['rfm_r'].min(), user_rfm['rfm_r'].max()
user_rfm['churn_risk_score'] = (user_rfm['rfm_r'] - r_min) / (r_max - r_min)

# Bucket into labels
def label_churn(score):
    if score >= 0.75:
        return 'Critical'
    elif score >= 0.50:
        return 'High'
    elif score >= 0.25:
        return 'Medium'
    else:
        return 'Low'

user_rfm['churn_risk_label'] = user_rfm['churn_risk_score'].apply(label_churn)

churn_scores = user_rfm[['user_id', 'churn_risk_score', 'churn_risk_label']].copy()

print()
print('Churn risk distribution:')
print(churn_scores['churn_risk_label'].value_counts())

churn_scores.to_parquet('data/processed/churn_scores.parquet', index=False)
print()
print('Saved: data/processed/churn_scores.parquet')
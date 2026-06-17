# src/promotion_engine.py
# Enhancement 4 - Personalised Promotion Engine
# Matches each user to the most effective promotion based on
# their segment, purchase behaviour, and churn risk.

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ── PROMOTION CATALOGUE ───────────────────────────────────────
PROMOTIONS = {
    'P001': {
        'name':             'Free Delivery',
        'description':      'Free Delivery On Your Next order',
        'target_segment':   ['Lapsed Users'],
        'target_churn':     ['High', 'Critical'],
        'expected_uplift':  0.25,
        'cost_per_user':    45.0,
    },
    'P002': {
        'name':                 '10% Off Produce',
        'description':          '10% Off all fresh produce this week',
        'target_segment':       ['Regular Shoppers', 'Weekly_Loyalists'],
        'target_dept':          'produce',
        'expected_uplift':      0.15,
        'cost_per_user':        45.0
    },
    'P003': {
        'name':         'Buy 2 Get 1 Snacks',
        'description':  'Buy any 2 snack items, get 1 free',
        'target_segment': ['Occasional Buyers'],
        'target_dept':    'snacks',
        'expected_uplift': 0.12,
        'cost_per_user':   30.0,
    },
    'P004': {
        'name':         'Organic Discovery',
        'description':  '15% Off your first organic product purchase',
        'target_segment': ['Regular Shoppers', 'Occasional Buyers'],
        'target_organic': False,
        'expected_uplift': 0.18,
        'cost_per_user':   25.0,
    },
    'P005': {
        'name':         'Loyalty Reward',
        'description':  'Double points on all orders this week',
        'target_segment': ['Weekly Loyalists'],
        'expected_uplift': 0.10,
        'cost_per_user':   15.0,
    },
    'P006': {
        'name':         'Reactivation Offer',
        'description':  '20% Off your next order — we miss you!',
        'target_segment': ['Lapsed Users'],
        'target_churn':   ['Critical'],
        'expected_uplift': 0.35,
        'cost_per_user':   60.0,
    },
    'P007': {
        'name':         'Dairy Bundle',
        'description':  'Save 12% when you buy 3 or more dairy products',
        'target_segment': ['Regular Shoppers', 'Weekly Loyalists'],
        'target_dept':    'dairy eggs',
        'expected_uplift': 0.14,
        'cost_per_user':   22.0,
    },
}

def assign_promotions(segments: pd.DataFrame,
                      churn_scores: pd.DataFrame,
                      training_data: pd.DataFrame,
                      products: pd.DataFrame,
                      budget_per_user: float = 50.0) -> pd.DataFrame:
    
    """
    Assign the most effective promotion to each user.

    Logic:
    1. Critical churn risk users get reactivation offers regardless of segment
    2. High churn risk users get free delivery
    3. Remaining users get promotions matched to their segment and behaviour
    4. Budget constraint: only assign promotions within budget_per_user

    Parameters
    ----------
    segments       : user segment data with segment labels
    churn_scores   : churn risk scores per user
    training_data  : training dataset for behavioural analysis
    products       : product lookup
    budget_per_user: maximum cost per user in rupees

    Returns
    -------
    DataFrame with user_id, promotion_id, promotion_name,
    expected_uplift, cost, assignment_reason
    """

    #Merge all uesr data
    user_data = segments[['user_id', 'segment']].merge(
        churn_scores[['user_id','churn_risk_label', 'churn_risk_score']],
        on='user_id', how='left'
    )

    #Compute user's top department
    user_dept = (training_data
                 .merge(products[['product_id', 'department']], on='product_id', how='left')
                 .groupby(['user_id', 'department'])['order_id']
                 .count()
                 .reset_index()
                 .sort_values('order_id', ascending=False)
                 .drop_duplicates('user_id')
                 .rename(columns={'department': 'top_department', 'order_id': 'dept_count'}))
    
    user_data = user_data.merge(user_dept[['user_id', 'top_department']],
                                on='user_id', how='left')
    
    #check if user buy organic

    user_organic = (training_data
                    .groupby('user_id')['is_organic']
                    .mean()
                    .reset_index()
                    .rename(columns={'is_organic': 'organic_rate'}))
    
    user_data = user_data.merge(user_organic, on='user_id', how='left')

    assigments = []

    for _, user in user_data.iterrows():
        uid             = user['user_id']
        segment         = user.get('segment', 'Unknown')
        churn_label     = user.get('churn_risk_label', 'Low')
        top_dept        = user.get('top_department', 'produce')
        organic_rate    = user.get('organic_rate', 0)

        best_promotion      = None
        best_uplift         = -1
        assigments_reason   = ''

        for promo_id, promo in PROMOTIONS.items():
            #Budget check
            if promo['cost_per_user'] > budget_per_user:
                continue

            score = 0
            reasons = []

            #Segment match
            if segment in promo.get('target_segment', []):
                score += 3
                reasons.append(f'segment match ({segment})')

            #churn risk match
            if churn_label in promo.get('target_churn', []):
                score += 5
                reasons.append(f'churn_risk ({churn_label})')

            #Department match
            if 'target_dept' in promo:
                if top_dept == promo['target_dept']:
                    score += 2
                    reasons.append(f'top dept ({top_dept})')

            #organic behaviour match
            if 'target_organic' in promo:
                if not promo['target_organic'] and organic_rate < 0.1:
                    score += 2
                    reasons.append('non-organic buyer - discovery potential')

            weighted_uplift = promo['expected_uplift'] * (1 + score * 0.1)

            if weighted_uplift > best_uplift and score > 0:
                best_uplift         = weighted_uplift
                best_promotion      = (promo_id, promo) 
                assigments_reason   = ', '.join(reasons)

        if best_promotion:
            promo_id, promo = best_promotion
            assigments.append({
                'user_id':          uid,
                'promotion_id':     promo_id,
                'promotion_name':   promo['name'],
                'promotion_desc':   promo['description'],
                'segment':          segment,
                'churn_risk':       churn_label,
                'expected_uplift':  round(best_uplift, 4),
                'cost':             promo['cost_per_user'],
                'assignment_reason':assigments_reason,
            })

    return pd.DataFrame(assigments)

def compute_campaign_roi(assigments: pd.DataFrame,
                         avg_order_value: float=850.0) -> dict:
    
    """
    Compute expected ROI for the promotion campaign.

    Parameters
    ----------
    assignments     : promotion assignment dataframe
    avg_order_value : average order value in rupees
    """

    total_users      = len(assigments)
    total_cost      = assigments['cost'].sum()
    expected_orders = (assigments['expected_uplift'] * avg_order_value).sum()
    roi             = (expected_orders - total_cost) / total_cost * 100 if total_cost > 0 else 0

    return {
        'total_users_targeted':     total_users,
        'total_campaign_cost':      round(total_cost, 2),
        'expected_revenue':         round(expected_orders, 2),
        'expected_roi_pct':         round(roi, 2),
        'cost_per_user_avg':        round(total_cost / total_users, 2) if total_users > 0 else 0,
    }
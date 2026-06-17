import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

# Control Group: Rule-Based Recommandations

def get_rule_based_recommandation(user_id: int,
                                  training_data: pd.DataFrame,
                                  products: pd.DataFrame,
                                  n: int=10) -> pd.DataFrame:
    
    """
    Baseline rule-based recommender.
    Simply returns the globally most popular products
    that the user has ordered before.
    This is what Instacart used before ML.
    """

    user_data = training_data[training_data['user_id'] == user_id].copy()
    if len(user_data) == 0:
        return pd.DataFrame()
    
    # Rank by global product popularity
    product_popularity = (training_data
                          .groupby('product_id')['order_id']
                          .count()
                          .reset_index()
                          .rename(columns={'order_id':'global_popularity'}))
    user_data = user_data.merge(product_popularity, on='product_id', how='left')
    user_data['rule_score'] = user_data['global_popularity'].fillna(0)

    top_n = (user_data
             .sort_values('rule_score', ascending=False)
             .head(n))
    
    return top_n[['product_id', 'reordered', 'rule_score']].reset_index(drop=True)

# Stimulate Click Events
def stimulate_clicks(recommandations: pd.DataFrame,
                     score_col: str,
                     noise: float = 0.05,
                     random_state: int = 42) -> pd.DataFrame:
    
    """
    Simulate whether a user clicked a recommendation.
    Click probability = reorder_probability (or rule_score normalised)
    with small random noise added.

    A product with reorder_probability 0.85 has 85% chance of being clicked.
    """
    rng = np.random.default_rng(random_state)
    df = recommandations.copy()

    scores = df[score_col].values
    #Normalise Scores to 0-1
    if scores.max() > 1:
        scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-8)

    #Add Note
    noisy_scores = np.clip(scores + rng.normal(0, noise, len(scores)), 0, 1)
    df['click'] = (rng.random(len(df)) < noisy_scores).astype(int)
    return df

# Compute Group Metrics
def compute_group_metrics(group_data: pd.DataFrame,
                          click_col: str = 'click',
                          actual_col: str = 'reordered') -> dict:
    
    """
    Compute CTR, precision, and recall for a recommendation group.
    """
    total_impressions = len(group_data)
    total_clicks = group_data[click_col].sum()
    
    true_positives = ((group_data[click_col] == 1) &
                      (group_data[actual_col] == 1)).sum()
    
    false_positives = ((group_data[click_col] == 1) &
                       (group_data[actual_col] == 0)).sum()
    
    false_negatives = ((group_data[click_col] == 0) &
                       (group_data[actual_col] == 1)).sum()
    
    ctr = total_clicks/total_impressions if total_impressions > 0 else 0
    precision = true_positives/(true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall  = true_positives/(true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) > 0 else 0)
    
    return{
        'impressions':  total_impressions,
        'clicks':       int(total_clicks),
        'ctr':          round(ctr,4),
        'precision':    round(precision,4),
        'recall':       round(recall,4),
        'f1':           round(f1,4),
    }

#Statistical Significance Test
def chi_square_test(control_clicks: int, control_impression: int,
                    treatment_clicks: int, treatment_impressions: int) -> dict:
    
    """
    Chi-square test to determine if CTR difference is statistically significant.
    H0: There is no difference in CTR between control and treatment.
    H1: There is a significant difference.
    """
    
    control_no_click = control_impression - control_clicks
    treatment_no_click = treatment_impressions - treatment_clicks

    contingency_table = np.array([
        [control_clicks, control_no_click],
        [treatment_clicks, treatment_no_click]
    ])

    chi2, p_value, dof, expected = chi2_contingency(contingency_table)

    return{
        'chi2_statistic': round(chi2, 4),
        'p_value': round(p_value, 4),
        'degrees_of_freedom': dof,
        'significant_at_95': p_value < 0.05,
        'significant_at_99': p_value < 0.01,
    }

#Sample Size calculator
def calculate_required_sample_size(baseline_ctr: float,
                                   minimum_detectable_effect: float = 0.18,
                                   alpha:  float = 0.05,
                                   power:  float = 0.80) -> int:
    
    """
    Calculate minimum users needed per group to detect a given lift.

    Parameters
    ----------
    baseline_ctr              : current CTR of control group
    minimum_detectable_effect : relative lift we want to detect (0.18 = 18%)
    alpha                     : significance level (0.05 = 95% confidence)
    power                     : statistical power (0.80 = 80%)
    """

    p1 = baseline_ctr
    p2 = baseline_ctr * (1 + minimum_detectable_effect)

    z_alpha = stats.norm.ppf(1-alpha / 2)
    z_beta = stats.norm.ppf(power)

    p_bar = (p1 + p2) / 2
    n =     ((z_alpha * np.sqrt(2 * p_bar * (1 - p_bar)) +
              z_beta * np.sqrt(p1 * (1-p1) + p2 * (1-p2))) ** 2
              / (p2 - p1) ** 2)
    
    return int(np.ceil(n))

#Full A/B Test Runner
def run_ab_test(training_data: pd.DataFrame,
                products: pd.DataFrame,
                model,
                feature_cols: list,
                n_users: int = 5000,
                n_recommendations: int = 10,
                random_state: int = 42) -> dict:
    
    """
     Run a full A/B test simulation comparing ML vs rule-based recommendations.

    Parameters
    ----------
    training_data    : full training dataset with features
    products         : product lookup dataframe
    model            : trained LightGBM model
    feature_cols     : list of feature column names
    n_users          : number of users to simulate
    n_recommendations: recommendations per user
    random_state     : for reproducibility

    Returns
    -------
    dict with full test results
    """

    rng = np.random.default_rng(random_state)
    all_users = training_data['user_id'].unique()
    sample_users = rng.choice(all_users,
                              size=min(n_users, len(all_users)),
                              replace=False)
    
    #Split Into Control And Treatment
    mid = len(sample_users) // 2
    control_users = sample_users[:mid]
    treatment_users = sample_users[mid:]

    control_results =     []
    treatment_results =   []

    print(f'  Running simulation on {len(sample_users):,} users...')
    print(f'  Control group:   {len(control_users):,} users (rule-based)')
    print(f'  Treatment group: {len(treatment_users):,} users (LightGBM)')
    print()

    #Control Group

    for uid in control_users:
        user_data = training_data[training_data['user_id'] == uid].copy()
        if len(user_data) == 0:
            continue

        product_popularity = (training_data
                              .groupby('product_id')['order_id']
                              .count()
                              .reset_index()
                              .rename(columns={'order_id': 'global_popularity'}))
        user_data = user_data.merge(product_popularity, on='product_id', how='left')

        max_pop = user_data['global_popularity'].max()
        if max_pop > 0:
            user_data['rule_score'] = user_data['global_popularity'] / max_pop
        else:
            user_data['rule_score'] = 0

        top_n = user_data.nlargest(n_recommendations, 'rule_score')
        clicked = stimulate_clicks(top_n, 'rule_score', random_state=int(uid))
        control_results.append(clicked[['product_id', 'reordered', 'click']])

    #Treatment Group
    for uid in treatment_users:
        user_data = training_data[training_data['user_id'] == uid].copy()
        if len(user_data) == 0:
            continue

        proba = model.predict_proba(user_data[feature_cols])[:,1]
        user_data = user_data.assign(reorder_probability=proba)

        top_n = user_data.nlargest(n_recommendations, 'reorder_probability')
        clicked = stimulate_clicks(top_n, 'reorder_probability', random_state=int(uid))
        treatment_results.append(clicked[['product_id', 'reordered', 'click']])

    #Aggregate Results
    control_df = pd.concat(control_results, ignore_index=True)
    treatment_df = pd.concat(treatment_results, ignore_index=True)

    control_metrics = compute_group_metrics(control_df)
    treatment_metrics = compute_group_metrics(treatment_df)

    significance = chi_square_test(
        control_metrics['clicks'], control_metrics['impressions'],
        treatment_metrics['clicks'], treatment_metrics['impressions']
    )

    if control_metrics['ctr'] > 0:
        ctr_lift = (treatment_metrics['ctr'] - control_metrics['ctr']) / control_metrics['ctr'] * 100
    else:
        ctr_lift = 0.0

    baseline_ctr = control_metrics['ctr'] if control_metrics['ctr'] > 0 else 0.01
    required_samples = calculate_required_sample_size(
        baseline_ctr=baseline_ctr,
        minimum_detectable_effect=0.18
    )

    return{
        'control': control_metrics,
        'treatment': treatment_metrics,
        'significance': significance,
        'ctr_lift_pct': round(ctr_lift, 2),
        'required_samples': required_samples,
        'n_users_tested': len(sample_users),
        'control_df': control_df,
        'treatment_df': treatment_df,
    }
        
#Visualization
def plot_ab_results(results: dict,
                output_path: str = 'docs/models/ab_test_results.png'):
    """Generate A/B test result visualization."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    fig.suptitle('A/B Test Results: ML vs Rule-Based Recommendations',
                         fontsize=14, fontweight='bold', y=1.02)
            
    metrics = ['ctr', 'precision', 'recall']
    labels =  ['ctr', 'precision', 'Recall']
    control_v = [results['control'][m]  for m in metrics]
    treat_v = [results['treatment'][m]  for m in metrics] 

    for i, (ax, labels, cv, tv) in enumerate(zip(axes, labels, control_v, treat_v)):
        bars = ax.bar(['Control\n(Rule-Based)', 'Treatment\n(LightGBM)'],
                      [cv, tv],
                      color = ['#90CAF9', '#1565C0'],
                      edgecolor='white', linewidth=1.5, width=0.5)
        for bar, val in zip(bars, [cv, tv]):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.002,
                    f'{val:.4f}',
                    ha='center', va='bottom',
                    fontsize=12, fontweight='bold')
        ax.set_title(labels, fontsize=13, fontweight='bold')
        ax.set_ylim(0, max(cv, tv) * 1.25)
        ax.grid(True, axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    lift_color = '#4CAF50' if results['ctr_lift_pct'] > 0 else '#F44336'
    fig.text(0.5, -0.5,
             f"CTR Lift: {results['ctr_lift_pct']:+.2f}%  |  "
             f"p-value: {results['significance']['p_value']:.6f}  |  "
             f"Statistically Significant: {results['significance']['significant_at_95']}",
            ha='center', fontsize=12,
            color=lift_color, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'    Chart Saved: {output_path}')
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

FEATURE_EXPLANATIONS = {
    'up_total_orders':      'you have ordered this {val:.0f} times before',
    'up_reorder_rate':      'you reorder this {val:.0%} of the time',
    'up_orders_since_last': 'it has been {val:.0f} orders since you last bought this',
    'p_reorder_rate':       '{val:.0%} of all users who buy this reorder it',
    'u_reorder_rate':       'your overall reorder rate is {val:.0%}',
    'rfm_r':                'your shopping recency score is {val:.2f}',
    'rfm_f':                'your order frequency score is {val:.2f}',
    'u_total_orders':       'you have placed {val:.0f} total orders',
    'u_avg_days_between':   'you typically order every {val:.1f} days',
    'p_avg_cart_position':  'this is usually added to cart at position {val:.1f}',
}

def generate_shap_explanations(model,
                               user_data: pd.DataFrame,
                               feature_cols: list,
                               top_k: int = 3) -> pd.DataFrame:
    
    """
    model       : trained LightGBM model
    user_data   : dataframe with feature columns for one user's products
    feature_cols: list of feature column names
    top_k       : number of top features to explain per prediction

    Returns
    --------
    DataFrame with product_id, shap_explanation, top_features
    """
    
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(user_data[feature_cols])

        # For binary classification, shap_values is a list [class0, class1]
        if isinstance(shap_values, list):
            shap_matrix = shap_values[1]
        else:
            shap_matrix = shap_values

    except ImportError:
        # Fallback: use feature importances as approximate SHAP
        importances = model.feature_importances_
        shap_matrix = np.tile(importances, (len(user_data), 1))
        shap_matrix = shap_matrix * user_data[feature_cols].values

    results = []
    for i, (_, row) in enumerate(user_data.iterrows()):
        shap_row = shap_matrix[i]

        # Get top k features by absolute SHAP value
        top_indices = np.argsort(np.abs(shap_row))[::-1][:top_k] 
        top_features = [(feature_cols[j], shap_row[j], row[feature_cols[j]])
                        for j in top_indices]
        
        # Generate plain english explanation
        explanations = []
        for feat, shap_val, feat_val in top_features:
            direction = 'increases' if shap_val > 0 else 'decreases'
            if feat in FEATURE_EXPLANATIONS:
                try:
                    details = FEATURE_EXPLANATIONS[feat].format(val=feat_val)
                    explanations.append(f'{details}')
                except Exception:
                    explanations.append(feat)

        explanations_text = ' | '.join(explanations) if explanations else 'Based on your order history'

        results.append({
            'product_id':           row.get('product_id'),
            'shap_explanation':     explanations_text,
            'top_feature_1':        top_features[0][0] if len(top_features) > 0 else '',
            'top_feature_2':        top_features[0][0] if len(top_features) > 1 else '',
            'top_feature_3':        top_features[0][0] if len(top_features) > 2 else '',
            'top_feature_3':        top_features[0][0] if len(top_features) > 3 else '',
            'top_shap_value':       round(top_features[0][1], 4) if top_features else 0,
        })

    return pd.DataFrame(results)

def explain_recommendation(user_id: int,
                           model,
                           training_data: pd.DataFrame,
                           feature_cols: list,
                           products: pd.DataFrame,
                           n: int=5) -> pd.DataFrame:
    """
    Full pipeline: score products for a user and generate explanations.
    Returns top N recommendations with plain-English explanations.
    """

    user_data = training_data[training_data['user_id'] == user_id].copy()
    if len(user_data) == 0:
        return pd.DataFrame()
    
    proba = model.predict_proba(user_data[feature_cols])[:, 1]
    user_data = user_data.assign(reorder_probability=proba)

    top_n = user_data.nlargest(n, 'reorder_probability').reset_index(drop=True)
    shap_df = generate_shap_explanations(model, top_n, feature_cols)

    result = (top_n[['product_id', 'reorder_probability', 'reordered']]
              .merge(shap_df[['product_id', 'shap_explanation']], on='product_id', how='left')
              .merge(products[['product_id', 'product_name', 'department']],
                     on='product_id', how='left'))
    
    return result[['product_id', 'product_name', 'department',
                   'reorder_probability', 'reordered', 'shap_explanation']]
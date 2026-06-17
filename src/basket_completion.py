import pandas as pd
import numpy as np
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

def build_order_matrix(prior: pd.DataFrame,
                       min_orders: int=10) -> pd.DataFrame:
    
    """
    Build a binary order matrix: rows=orders, columns=products.
    Value of 1 means the product was in that order.
    Only includes products ordered at least min_orders times.
    """

    # Filter Frequent Products
    product_counts = prior.groupby('product_id')['order_id'].nunique()
    frequent_products = product_counts[product_counts >= min_orders].index

    filtered = prior[prior['product_id'].isin(frequent_products)]

    #Sample orders to keep memory managable
    sample_orders = np.random.choice(
        filtered['order_id'].nunique(),
        size=min(50000,filtered['order_id'].nunique()),
    )
    filtered = filtered[filtered['order_id'].isin(sample_orders)]

    matrix = (filtered
              .groupby(['order_id', 'product_id'])['reordered']
              .max()
              .unstack(fill_value=0))
    return matrix

def compute_association_rules(order_matrix: pd.DataFrame,
                              min_support: float=0.01,
                              min_confidence: float=0.1,
                              max_rules: int=5000) -> pd.DataFrame:
    """
    Compute association rules using Apriori logic.

    Support    = P(A and B) = orders containing both / total orders
    Confidence = P(B|A) = orders containing both / orders containing A
    Lift       = Confidence / P(B) - values > 1 mean A predicts B better than random

    Parameters
    ----------
    min_support    : minimum fraction of orders containing both items
    min_confidence : minimum conditional probability of B given A
    max_rules      : maximum number of rules to compute (for performance)
    """
    n_orders = len(order_matrix)
    products = order_matrix.columns.tolist()

    #product support: fraction of orders containing each product            
    product_support = (order_matrix.sum() / n_orders).to_dict()

    rules = []
    product_pairs = list(combinations(products, 2))

    #sample pairs if too many
    if len(product_pairs) > max_rules:
        np.random.seed(42)
        idx = np.random.choice(len(product_pairs), max_rules, replace=False)
        product_pairs = [product_pairs[i] for i in idx]

    for product_a, product_b in product_pairs:
        both = (order_matrix[product_a] & order_matrix[product_b]).sum()
        supp = both / n_orders

        if supp < min_support:
            continue

        #A -> B
        conf_ab = supp / product_support[product_a] if product_support[product_a] > 0 else 0
        lift_ab = conf_ab / product_support[product_b] if product_support[product_b] > 0 else 0

        #B -> A
        conf_ba = supp / product_support[product_b] if product_support[product_b] > 0 else 0
        lift_ab = conf_ba / product_support[product_a] if product_support[product_a] > 0 else 0

        if conf_ab >= min_confidence:
            rules.append({
                'antecedent':       product_a,
                'consequent':       product_b,
                'support':          round(supp,6),
                'confidence':       round(conf_ab, 4),
                'lift':             round(lift_ab,4),
            })

        if conf_ba >= min_confidence:
            rules.append({
                'antecedent':       product_b,
                'consequent':       product_a,
                'support':          round(supp,6),
                'confidence':       round(conf_ab,4),
                'lift':             round(lift_ab, 4),
            })
    
    rules_df = pd.DataFrame(rules)
    if len(rules_df) > 0:
        rules_df = rules_df.sort_values('lift', ascending=False)
    return rules_df

def complete_basket(current_basket: list,
                    rules: pd.DataFrame,
                    products: pd.DataFrame,
                    n: int = 5,
                    min_lift: float = 0.1) -> pd.DataFrame:
    
    """
    Given a partial basket, predict what products to add next.

    Parameters
    ----------
    current_basket : list of product_ids already in the basket
    rules          : association rules dataframe
    products       : product lookup dataframe
    n              : number of completion suggestions
    min_lift       : minimum lift threshold (1.0 = better than random)
    """

    if len(rules) == 0 or len(current_basket) == 0:
        return pd.DataFrame()

    #Find rules where antecedent is in the current basket
    relevant_rules = rules[
        (rules['antecedent'].isin(current_basket)) &
        (~rules['consequent'].isin(current_basket)) &
        (rules['lift'] >= min_lift)
    ].copy()

    if len(relevant_rules) == 0:
        return pd.DataFrame()

    #Aggregate by consequent: sum confidence scores
    suggestions = (relevant_rules
                   .groupby('consequent')
                   .agg(
                       total_confidence =   ('confidence', 'sum'),
                       max_lift =           ('lift', 'max'),
                       n_rules =            ('antecedent', 'count'),
                   )
                   .reset_index()
                   .sort_values('total_confidence', ascending=False)
                   .head(n))
    
    suggestions = suggestions.merge(
        products[['product_id', 'product_name', 'depatment', 'aisle']],
        left_on='consequent', right_on='product_id', how='left'
    )

    return suggestions[['product_id', 'product_name', 'department', 'total_confidence', 'max_lift', 'n_rules']].reset_index(drop=True)
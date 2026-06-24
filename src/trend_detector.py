import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def build_temporal_reorder_rates(prior: pd.DataFrame,
                                 orders: pd.DataFrame,
                                 products: pd.DataFrame,
                                 n_periods: int = 3) -> pd.DataFrame:
    """
    Divide user order history into time periods using order_number.
    Compute reorder rate per department per period.

    Parameters
    ----------
    prior     : order_products_prior dataframe
    orders    : orders dataframe (prior orders only)
    products  : product lookup with department column
    n_periods : number of time periods to divide history into

    Returns
    -------
    DataFrame with department, period, reorder_rate
    """

    #Join prior products with order metadata
    prior_orders = orders[orders['eval_set'] == 'prior'].copy()
    enriched = prior.merge(
        prior_orders[['order_id', 'user_id', 'order_number']],
        on='order_id', how='left'
    )

    #Join in department from product lookup
    enriched = enriched.merge(
        products[['product_id', 'department']],
        on='product_id', how='left'
    )

    #Normalize order number to 0-1 per user
    user_max = (enriched.groupby('user_id')['order_number']
                .max()
                .reset_index()
                .rename(columns={'order_number': 'max_order'}))
    
    enriched = enriched.merge(user_max, on='user_id', how='left')
    enriched['order_pct'] = (
        enriched['order_number'] /
        enriched['max_order'].clip(lower=1)
    )

    #Assign Period
    enriched['period'] = pd.cut(
        enriched['order_pct'],
        bins = np.linspace(0, 1, n_periods + 1),
        labels = [f'Period {i+1}' for i in range(n_periods)]
    )

    #Reorder Rate per department per period
    trend_df = (enriched
                .groupby(['department', 'period'])
                .agg(
                    reorder_rate  = ('reordered', 'mean'),
                    total_orders  = ('order_id',  'count'),
                )
                .reset_index())

    return trend_df.dropna()

def compute_trend_direction(trend_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute trend direction for each department.
    Compares first period reorder rate to last period reorder rate.

    Returns departments sorted by trend strength.
    """
    periods = sorted(trend_df['period'].unique())

    if len(periods) < 2:
        return pd.DataFrame()
    
    first_period = periods[0]
    last_period = periods[-1]

    first = (trend_df[trend_df['period'] == first_period]
             [['department', 'reorder_rate']]
             .rename(columns={'reorder_rate': 'rate_early'}))
    
    last = (trend_df[trend_df['period'] == last_period]
            [['department', 'reorder_rate']]
            .rename(columns={'reorder_rate': 'rate_late'}))
    
    merged = first.merge(last, on='department', how='inner')
    merged['rate_change'] = merged['rate_late'] - merged['rate_early']
    merged['rate_change_pct'] = (
        merged['rate_change'] / 
        merged['rate_early'].clip(lower=0.01) * 100
    ).round(2)

    merged['trend'] = merged['rate_change'].apply(
        lambda x: 'Trending Up' if x>0.01
        else      'Trending Down' if x<-0.01
        else      'Stable'
    )
    return merged.sort_values('rate_change', ascending=False)

def get_top_trends(direction_df: pd.DataFrame,
                   n: int = 5) -> tuple:
    """
    Return top N trending up and top N trending down departments.
    """

    trending_up = direction_df[
        direction_df['trend'] == 'Trending Up'
    ].sort_values('rate_change', ascending=False).head(n)

    trending_down = direction_df[
        direction_df['trend'] == 'Trending Down'
    ].sort_values('rate_change', ascending=True).head(n)

    return trending_up, trending_down

def generate_trend_interpretation(trending_up: pd.DataFrame,
                                  trending_down: pd.DataFrame) -> str:
    """
    Generate a plain-English business interpretation of the trends.
    """

    up_depts = trending_up['department'].tolist()
    down_depts = trending_down['department'].tolist()

    interpretation = []
    interpretation.append('TREND ANALYSIS INTERPRETATION')
    interpretation.append('-' * 45)

    if up_depts:
        interpretation.append(
            f'Growing categories: {", ".join(up_depts)}'
        )
        interpretation.append(
            'Recommendation: Increase inventory and promote '
            'these categories to loyal customers.'
        )

    if down_depts:
        interpretation.append(
            f'Declining categories: {", ".join(down_depts)}'
        )
        interpretation.append(
            'Recommendation: Investigate Pricing and availability. '
            'consider reactivation promotions for these categories.' 
        )

    return '\n'.join(interpretation)
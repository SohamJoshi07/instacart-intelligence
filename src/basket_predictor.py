# src/basket_predictor.py
# Enhancement 12 - Basket Size Predictor
# Predicts how many items a user will add to their next order.

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def build_basket_size_features(orders: pd.DataFrame,
                                 prior: pd.DataFrame,
                                 segments: pd.DataFrame,
                                 clv: pd.DataFrame) -> pd.DataFrame:
    """
    Build features for predicting next basket size.

    Features:
    - avg_basket_size:    historical average items per order
    - std_basket_size:    variability in basket size
    - min_basket_size:    smallest basket ever
    - max_basket_size:    largest basket ever
    - trend:              is basket size growing or shrinking
    - n_orders:           total orders placed
    - segment_code:       encoded segment label
    - clv_score:          customer lifetime value score
    - favourite_dow:      preferred order day
    - favourite_hour:     preferred order hour
    """
    prior_orders = orders[orders['eval_set'] == 'prior'].copy()

    # Basket size per order
    basket_sizes = (prior
                    .groupby('order_id')['product_id']
                    .count()
                    .reset_index()
                    .rename(columns={'product_id': 'basket_size'}))

    basket_sizes = basket_sizes.merge(
        prior_orders[['order_id', 'user_id', 'order_number']],
        on='order_id', how='left'
    )

    # User level basket stats
    user_stats = (basket_sizes
                  .groupby('user_id')
                  .agg(
                      avg_basket_size = ('basket_size', 'mean'),
                      std_basket_size = ('basket_size', 'std'),
                      min_basket_size = ('basket_size', 'min'),
                      max_basket_size = ('basket_size', 'max'),
                      n_orders        = ('order_id',    'nunique'),
                  )
                  .reset_index())

    user_stats['std_basket_size'] = (
        user_stats['std_basket_size'].fillna(0)
    )

    # Trend: compare early vs late basket sizes 
    def basket_trend(group):
        sizes = group.sort_values('order_number')['basket_size']
        if len(sizes) < 4:
            return 0.0
        early = sizes.iloc[:len(sizes)//2].mean()
        late  = sizes.iloc[len(sizes)//2:].mean()
        return late - early

    trends = (basket_sizes
              .groupby('user_id')
              .apply(basket_trend)
              .reset_index()
              .rename(columns={0: 'basket_trend'}))

    # Favourite order time
    time_prefs = (prior_orders
                  .groupby('user_id')
                  .agg(
                      favourite_dow  = ('order_dow',          lambda x: x.mode()[0]),
                      favourite_hour = ('order_hour_of_day',  lambda x: x.mode()[0]),
                  )
                  .reset_index())

    # Segment encoding
    seg_map = {
        'Weekly Loyalists':  3,
        'Regular Shoppers':  2,
        'Occasional Buyers': 1,
        'Lapsed Users':      0,
    }

    features = (user_stats
                .merge(trends,    on='user_id', how='left')
                .merge(time_prefs,on='user_id', how='left')
                .merge(segments[['user_id', 'segment']],
                       on='user_id', how='left')
                .merge(clv[['user_id', 'clv_score']],
                       on='user_id', how='left'))

    features['segment_code'] = (
        features['segment'].map(seg_map).fillna(1)
    )
    features['clv_score']    = features['clv_score'].fillna(0.5)
    features['basket_trend'] = features['basket_trend'].fillna(0)

    return features


def build_basket_size_target(orders: pd.DataFrame,
                              prior: pd.DataFrame) -> pd.DataFrame:
    """
    Build target: basket size of the most recent (train) order per user.
    """
    train_orders = orders[orders['eval_set'] == 'train'].copy()
    train_prior  = pd.read_csv(
        'data/raw/order_products__train.csv',
        dtype={'order_id': 'int32', 'product_id': 'int32',
               'add_to_cart_order': 'int16', 'reordered': 'int8'}
    )

    train_basket = (train_prior
                    .groupby('order_id')['product_id']
                    .count()
                    .reset_index()
                    .rename(columns={'product_id': 'next_basket_size'}))

    target = train_basket.merge(
        train_orders[['order_id', 'user_id']],
        on='order_id', how='left'
    )

    return target[['user_id', 'next_basket_size']]


def train_basket_model(features: pd.DataFrame,
                        target: pd.DataFrame):
    """
    Train LightGBM Regressor to predict next basket size.
    """
    import lightgbm as lgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error
    import numpy as np

    FEATURE_COLS = [
        'avg_basket_size', 'std_basket_size', 'min_basket_size',
        'max_basket_size', 'basket_trend', 'n_orders',
        'favourite_dow', 'favourite_hour',
        'segment_code', 'clv_score'
    ]

    df = features.merge(target, on='user_id', how='inner').dropna()

    X = df[FEATURE_COLS]
    y = df['next_basket_size']

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = lgb.LGBMRegressor(
        n_estimators  = 300,
        learning_rate = 0.05,
        num_leaves    = 31,
        random_state  = 42,
        n_jobs        = -1,
        verbose       = -1
    )

    model.fit(
        X_train, y_train,
        eval_set  = [(X_val, y_val)],
        callbacks = [lgb.early_stopping(30, verbose=False),
                     lgb.log_evaluation(50)]
    )

    y_pred = model.predict(X_val)
    mae    = mean_absolute_error(y_val, y_pred)
    print(f'  Basket size model MAE: {mae:.2f} items')

    return model, FEATURE_COLS, mae


def predict_basket_sizes(user_ids: list,
                          features: pd.DataFrame,
                          model,
                          feature_cols: list) -> pd.DataFrame:
    """
    Predict basket size and routing decision for given users.
    """
    user_data    = features[features['user_id'].isin(user_ids)].copy()
    predictions  = model.predict(user_data[feature_cols])

    user_data = user_data.assign(
        predicted_basket_size = np.round(predictions, 1),
        confidence_low        = np.round(predictions * 0.75, 1),
        confidence_high       = np.round(predictions * 1.25, 1),
    )

    # Routing decision based on predicted basket size
    def get_routing(size):
        if size >= 20:
            return 'show_full_recommendations'
        elif size >= 10:
            return 'show_top_10_recommendations'
        elif size >= 5:
            return 'show_quick_reorder_top_5'
        else:
            return 'show_quick_reorder_top_3'

    user_data['routing_decision'] = user_data[
        'predicted_basket_size'
    ].apply(get_routing)

    return user_data[[
        'user_id', 'avg_basket_size',
        'predicted_basket_size',
        'confidence_low', 'confidence_high',
        'routing_decision'
    ]]
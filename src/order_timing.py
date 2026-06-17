# src/order_timing.py
# Enhancement 2 - Next Order Timing Predictor
# Predicts exactly when each user will place their next order.

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def build_timing_features(orders: pd.DataFrame) -> pd.DataFrame:
    """
    Build user-level features for predicting next order timing.

    Features:
    - avg_gap:       mean days between orders
    - std_gap:       standard deviation of gaps (consistency)
    - min_gap:       shortest gap ever recorded
    - max_gap:       longest gap ever recorded
    - last_gap:      most recent gap
    - trend:         is gap increasing or decreasing over last 5 orders
    - dow_mode:      favourite day of week to order
    - hour_mode:     favourite hour to order
    - n_orders:      total number of prior orders
    - cv_gap:        coefficient of variation (std/mean) - regularity score
    """
    prior = orders[orders['eval_set'] == 'prior'].copy()
    gaps  = prior.dropna(subset=['days_since_prior_order'])

    # Core gap stats
    gap_stats = (gaps
                 .groupby('user_id')['days_since_prior_order']
                 .agg(
                     avg_gap  = 'mean',
                     std_gap  = 'std',
                     min_gap  = 'min',
                     max_gap  = 'max',
                     last_gap = 'last',
                     n_gaps   = 'count',
                 )
                 .reset_index())

    gap_stats['std_gap'] = gap_stats['std_gap'].fillna(0)
    gap_stats['cv_gap']  = (gap_stats['std_gap'] /
                             gap_stats['avg_gap'].clip(lower=1))

    # Order count
    order_count = (prior
                   .groupby('user_id')['order_id']
                   .nunique()
                   .reset_index()
                   .rename(columns={'order_id': 'n_orders'}))

    # Favourite day and hour
    preferences = (prior
                   .groupby('user_id')
                   .agg(
                       dow_mode  = ('order_dow',          lambda x: x.mode()[0]),
                       hour_mode = ('order_hour_of_day',  lambda x: x.mode()[0]),
                   )
                   .reset_index())

    # Trend: compare last 3 gaps to first 3 gaps
    def compute_trend(group):
        g = group.sort_values('order_number')['days_since_prior_order'].dropna()
        if len(g) < 4:
            return 0.0
        early = g.iloc[:len(g)//2].mean()
        late  = g.iloc[len(g)//2:].mean()
        return late - early  # positive = gap increasing = ordering less frequently

    trends = (prior
              .groupby('user_id')
              .apply(compute_trend)
              .reset_index()
              .rename(columns={0: 'gap_trend'}))

    features = (gap_stats
                .merge(order_count,  on='user_id', how='left')
                .merge(preferences,  on='user_id', how='left')
                .merge(trends,       on='user_id', how='left'))

    features['gap_trend'] = features['gap_trend'].fillna(0)

    return features


def build_timing_target(orders: pd.DataFrame) -> pd.DataFrame:
    """
    Build target variable: days until next order.
    We use the train set orders as the 'next order' for prior users.
    Target = days_since_prior_order from the train order record.
    """
    train_orders = orders[orders['eval_set'] == 'train'].copy()
    target = train_orders[['user_id', 'days_since_prior_order']].copy()
    target = target.rename(columns={'days_since_prior_order': 'days_until_next_order'})
    target = target.dropna(subset=['days_until_next_order'])
    return target


def train_timing_model(features: pd.DataFrame,
                       target: pd.DataFrame):
    """
    Train a LightGBM Regressor to predict days until next order.
    Returns trained model and feature column list.
    """
    import lightgbm as lgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error

    df = features.merge(target, on='user_id', how='inner')
    df = df.dropna()

    FEATURE_COLS = ['avg_gap', 'std_gap', 'min_gap', 'max_gap',
                    'last_gap', 'cv_gap', 'gap_trend', 'n_orders',
                    'n_gaps', 'dow_mode', 'hour_mode']

    X = df[FEATURE_COLS]
    y = df['days_until_next_order']

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = lgb.LGBMRegressor(
        n_estimators    = 500,
        learning_rate   = 0.05,
        num_leaves      = 31,
        random_state    = 42,
        n_jobs          = -1,
        verbose         = -1
    )

    model.fit(X_train, y_train,
              eval_set=[(X_val, y_val)],
              callbacks=[lgb.early_stopping(50, verbose=False),
                         lgb.log_evaluation(100)])

    y_pred = model.predict(X_val)
    mae    = mean_absolute_error(y_val, y_pred)
    rmse   = np.sqrt(mean_squared_error(y_val, y_pred))

    print(f'  Timing model MAE:  {mae:.2f} days')
    print(f'  Timing model RMSE: {rmse:.2f} days')

    return model, FEATURE_COLS, {'mae': mae, 'rmse': rmse}


def predict_next_order_timing(user_ids: list,
                               features: pd.DataFrame,
                               model,
                               feature_cols: list) -> pd.DataFrame:
    """
    Predict days until next order for a list of users.
    Also computes recommended notification time.
    """
    user_features = features[features['user_id'].isin(user_ids)].copy()
    predictions   = model.predict(user_features[feature_cols])

    user_features = user_features.assign(
        predicted_days_until_next_order = np.round(predictions, 1),
        recommended_notification_day    = np.round(predictions * 0.85, 0).astype(int),
    )

    # Risk flag: if predicted gap > 1.5x their average, flag as at risk
    user_features['timing_risk'] = (
        user_features['predicted_days_until_next_order'] >
        user_features['avg_gap'] * 1.5
    )

    return user_features[['user_id', 'avg_gap',
                           'predicted_days_until_next_order',
                           'recommended_notification_day',
                           'timing_risk']]
# src/reminder_system.py
# Enhancement 9 - Smart Reorder Reminder System
# Determines optimal reminder timing and generates
# personalised messages for each user.

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


# ── REMINDER PRIORITY SCORING ─────────────────────────────────
def compute_reminder_priority(timing_df: pd.DataFrame,
                               churn_df: pd.DataFrame,
                               segments: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a priority score for each user's reminder.

    Priority is driven by three signals:
    1. How overdue they are relative to their predicted order time
    2. Their churn risk score
    3. Their segment value (Weekly Loyalists get higher priority)

    Parameters
    ----------
    timing_df : output of order_timing predictions
    churn_df  : output of churn_signal
    segments  : user segments with rfm scores

    Returns
    -------
    DataFrame with priority scores and recommended send times
    """
    SEGMENT_VALUE = {
        'Weekly Loyalists':  1.0,
        'Regular Shoppers':  0.8,
        'Occasional Buyers': 0.6,
        'Lapsed Users':      0.4,
    }

    df = timing_df.merge(
    churn_df[['user_id', 'churn_risk_score', 'churn_risk_label']],
    on='user_id', how='left'
    ).merge(
        segments[['user_id', 'segment']],
        on='user_id', how='left'
    )

    df['churn_risk_score']  = df['churn_risk_score'].fillna(0.3)
    df['segment']           = df['segment'].fillna('Occasional Buyers')

    # Segment value weight
    df['segment_value'] = df['segment'].map(SEGMENT_VALUE).fillna(0.5)

    # Overdue signal: how far past their predicted order time are they
    df['overdue_signal'] = (
        df['predicted_days_until_next_order'] /
        df['avg_gap'].clip(lower=1)
    ).clip(upper=3)

    # Final priority score: weighted combination
    df['priority_score'] = (
        0.40 * df['churn_risk_score'] +
        0.35 * (df['overdue_signal'] / 3) +
        0.25 * df['segment_value']
    ).round(4)

    # Priority tier
    df['priority_tier'] = pd.cut(
        df['priority_score'],
        bins   = [0, 0.3, 0.5, 0.7, 1.01],
        labels = ['Low', 'Medium', 'High', 'Urgent']
    )

    # Recommended channel based on segment and priority
    def get_channel(row):
        if row['priority_tier'] in ['Urgent', 'High']:
            return 'push_notification'
        elif row['segment'] in ['Weekly Loyalists', 'Regular Shoppers']:
            return 'email'
        else:
            return 'email'

    df['recommended_channel'] = df.apply(get_channel, axis=1)

    # Recommended send time: morning of predicted order day
    df['send_in_days'] = (
        df['predicted_days_until_next_order'] * 0.80
    ).round(0).astype(int).clip(lower=0)

    return df[[
        'user_id', 'segment', 'avg_gap',
        'predicted_days_until_next_order',
        'churn_risk_score', 'churn_risk_label',
        'segment_value', 'overdue_signal',
        'priority_score', 'priority_tier',
        'recommended_channel', 'send_in_days'
    ]].sort_values('priority_score', ascending=False)


# ── MESSAGE TEMPLATES ─────────────────────────────────────────
MESSAGE_TEMPLATES = {
    'Weekly Loyalists': {
        'push': "Your weekly basket is waiting! Your top picks are ready to reorder.",
        'email': "Hi {name}, your favourite products are running low. Reorder in one tap.",
    },
    'Regular Shoppers': {
        'push': "Time to restock? Your usual items are ready.",
        'email': "Hi {name}, looks like it's about time for your next Instacart order.",
    },
    'Occasional Buyers': {
        'push': "Missing your Instacart favourites? We have your top picks ready.",
        'email': "Hi {name}, we have curated your top reorders. Quick and easy.",
    },
    'Lapsed Users': {
        'push': "We miss you! Come back and get free delivery on your next order.",
        'email': "Hi {name}, it has been a while. Here is 20% off to welcome you back.",
    },
}


def generate_reminder_messages(priority_df: pd.DataFrame,
                                top_n: int = 10000) -> pd.DataFrame:
    """
    Generate personalised reminder messages for top N users.

    Parameters
    ----------
    priority_df : output of compute_reminder_priority
    top_n       : number of users to generate messages for

    Returns
    -------
    DataFrame with user_id and personalised message
    """
    top_users = priority_df.head(top_n).copy()

    def get_message(row):
        segment   = row['segment']
        channel   = row['recommended_channel']
        templates = MESSAGE_TEMPLATES.get(
            segment, MESSAGE_TEMPLATES['Occasional Buyers']
        )

        if channel == 'push_notification':
            return templates.get('push', templates.get('email', ''))
        else:
            return templates.get('email', '').format(name='Valued Customer')

    top_users['message'] = top_users.apply(get_message, axis=1)

    return top_users[['user_id', 'segment', 'priority_tier',
                       'recommended_channel', 'send_in_days', 'message']]


# ── DAILY QUEUE BUILDER ───────────────────────────────────────
def build_daily_reminder_queue(priority_df: pd.DataFrame,
                                target_day: int = 1) -> pd.DataFrame:
    """
    Build the queue of reminders to send on a specific day.

    Parameters
    ----------
    priority_df : output of compute_reminder_priority
    target_day  : send reminders for users whose send_in_days == target_day

    Returns
    -------
    DataFrame of users to contact today, sorted by priority
    """
    queue = priority_df[
        priority_df['send_in_days'] == target_day
    ].copy()

    queue = queue.sort_values('priority_score', ascending=False)

    print(f"  Reminders queued for day {target_day}: {len(queue):,}")
    print(f"  Urgent:  {(queue['priority_tier']=='Urgent').sum():,}")
    print(f"  High:    {(queue['priority_tier']=='High').sum():,}")
    print(f"  Medium:  {(queue['priority_tier']=='Medium').sum():,}")
    print(f"  Low:     {(queue['priority_tier']=='Low').sum():,}")

    return queue	
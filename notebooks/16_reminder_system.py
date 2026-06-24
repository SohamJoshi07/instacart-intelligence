# notebooks/16_reminder_system.py
# Enhancement 9 - Smart Reorder Reminder System
# Run from project root: python notebooks/16_reminder_system.py

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.reminder_system import (compute_reminder_priority,
                                  generate_reminder_messages,
                                  build_daily_reminder_queue)

print('=' * 60)
print('ENHANCEMENT 9 - SMART REORDER REMINDER SYSTEM')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── LOAD DATA ─────────────────────────────────────────────────
print('Section 1: Loading data...')
try:
    timing   = pd.read_parquet('data/processed/order_timing_predictions.parquet')
    churn    = pd.read_parquet('data/processed/churn_scores.parquet')
    segments = pd.read_parquet('data/processed/user_segments.parquet')
    print(f'  Timing predictions: {len(timing):,}')
    print(f'  Churn scores:       {len(churn):,}')
    print(f'  Segments:           {len(segments):,}')
except FileNotFoundError as e:
    print(f'  Missing file: {e}')
    print('  Run notebooks 09 and churn_signal first')
    sys.exit(1)
print()

# ── COMPUTE PRIORITY ──────────────────────────────────────────
print('Section 2: Computing reminder priority scores...')
priority_df = compute_reminder_priority(timing, churn, segments)
print(f'  Users scored: {len(priority_df):,}')
print()
print('  Priority distribution:')
print(priority_df['priority_tier'].value_counts().to_string())
print()
print('  Top 10 highest priority users:')
top10_cols = ['user_id', 'segment', 'priority_score',
              'priority_tier', 'send_in_days']
print(priority_df[top10_cols].head(10).to_string(index=False))
print()

# ── GENERATE MESSAGES ─────────────────────────────────────────
print('Section 3: Generating personalised messages...')
messages = generate_reminder_messages(priority_df, top_n=5000)
print(f'  Messages generated: {len(messages):,}')
print()
print('  Sample messages:')
for _, row in messages.head(5).iterrows():
    print(f'  User {row["user_id"]} [{row["priority_tier"]}]')
    print(f'  Channel: {row["recommended_channel"]}')
    print(f'  Message: {row["message"]}')
    print()

# ── BUILD DAILY QUEUE ─────────────────────────────────────────
print('Section 4: Building daily reminder queue...')
print()
for day in [0, 1, 2, 3]:
    print(f'  Day {day}:')
    queue = build_daily_reminder_queue(priority_df, target_day=day)
    print()

# ── VISUALISATION ─────────────────────────────────────────────
print('Section 5: Generating charts...')

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Chart 1: Priority distribution
priority_counts = priority_df['priority_tier'].value_counts()
colors = ['#F44336', '#FF9800', '#FFC107', '#4CAF50']
axes[0].bar(
    priority_counts.index,
    priority_counts.values,
    color=colors[:len(priority_counts)],
    edgecolor='white'
)
for i, (label, count) in enumerate(priority_counts.items()):
    axes[0].text(i, count + 200, f'{count:,}',
                 ha='center', fontweight='bold', fontsize=10)
axes[0].set_title('Reminder Priority Distribution',
                   fontsize=13, fontweight='bold')
axes[0].set_ylabel('Number of Users', fontsize=12)
axes[0].grid(True, axis='y', alpha=0.3)

# Chart 2: Send timing distribution
axes[1].hist(
    priority_df['send_in_days'].clip(upper=30),
    bins=20, color='#1565C0', edgecolor='white', alpha=0.8
)
axes[1].set_title('When to Send Reminders\n(Days from now)',
                   fontsize=13, fontweight='bold')
axes[1].set_xlabel('Days Until Send', fontsize=12)
axes[1].set_ylabel('Number of Users', fontsize=12)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('docs/models', exist_ok=True)
plt.savefig('docs/models/reminder_system.png', dpi=150,
            bbox_inches='tight')
plt.close()
print('  Chart saved: docs/models/reminder_system.png')
print()

# ── SAVE OUTPUTS ──────────────────────────────────────────────
print('Section 6: Saving outputs...')
os.makedirs('data/processed', exist_ok=True)
priority_df.to_parquet(
    'data/processed/reminder_priority.parquet', index=False)
messages.to_parquet(
    'data/processed/daily_reminder_queue.parquet', index=False)
print('  reminder_priority.parquet saved')
print('  daily_reminder_queue.parquet saved')
print()

# ── BUSINESS SUMMARY ──────────────────────────────────────────
print('BUSINESS SUMMARY')
print('-' * 50)
urgent = priority_df[priority_df['priority_tier'] == 'Urgent']
print(f'  {len(urgent):,} users need urgent outreach today')
print(f'  Avg priority score: {priority_df["priority_score"].mean():.3f}')
print(f'  Top channel: {messages["recommended_channel"].mode()[0]}')
print('-' * 50)
print()
print('Enhancement 9 complete.')
print('Run next: python notebooks/17_seasonal_trends.py')
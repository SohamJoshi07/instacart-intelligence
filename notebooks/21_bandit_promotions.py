# notebooks/21_bandit_promotions.py
# Enhancement 14 - Multi-Armed Bandit Promotion Optimiser
# Run from project root: python notebooks/21_bandit_promotions.py

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.bandit_promotions import (EpsilonGreedyBandit,
                                    run_bandit_simulation,
                                    compare_epsilons,
                                    PROMOTION_ARMS)

print('=' * 60)
print('ENHANCEMENT 14 - MULTI-ARMED BANDIT PROMOTION OPTIMISER')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── AVAILABLE PROMOTIONS ──────────────────────────────────────
print('Section 1: Available promotions (arms)...')
print()
print(f'  {"Arm":>4} {"Promotion":<28} {"True Reward Rate":>16}')
print('  ' + '-' * 52)
for arm_id, promo in PROMOTION_ARMS.items():
    print(f'  {arm_id:>4}  {promo["name"]:<28} '
          f'{promo["true_reward"]*100:>14.0f}%')
print()
print('  Goal: The bandit must discover the best promotion')
print('  without being told the true reward rates.')
print()

# ── RUN SIMULATION ────────────────────────────────────────────
print('Section 2: Running bandit simulation (10,000 rounds)...')
print('  epsilon = 0.10 (10% explore, 90% exploit)')
print()
bandit, results = run_bandit_simulation(
    n_rounds=10000, epsilon=0.10, random_state=42
)
print(f'  Simulation complete: {len(results)} checkpoints recorded')
print()

# ── RESULTS ───────────────────────────────────────────────────
print('Section 3: What the bandit learned...')
print()
summary = bandit.get_summary()
print(f'  {"Promotion":<28} {"True":>8} {"Learned":>9} '
      f'{"Selected":>10} {"Error":>8}')
print('  ' + '-' * 67)
for _, row in summary.iterrows():
    best_marker = ' <-- BEST' if row['arm_id'] == summary.index[0] else ''
    print(f'  {row["promotion"]:<28} '
          f'{row["true_reward"]*100:>7.0f}% '
          f'{row["estimated_reward"]*100:>8.1f}% '
          f'{row["times_selected"]:>10,} '
          f'{row["error"]*100:>7.1f}%{best_marker}')
print()

best_arm_id = int(summary.iloc[0]['arm_id'])
best_promo  = PROMOTION_ARMS[best_arm_id]['name']
print(f'  Bandit identified best promotion: {best_promo}')
print(f'  This is correct: {best_arm_id == 5}')
print()

# ── EPSILON COMPARISON ────────────────────────────────────────
print('Section 4: Comparing different epsilon values...')
comparison = compare_epsilons(n_rounds=5000)
print()
print(f'  {"Epsilon":>8} {"Final Regret":>14} '
      f'{"Final Reward":>14} {"Correct?":>10}')
print('  ' + '-' * 50)
for _, row in comparison.iterrows():
    correct = 'YES' if row['correct'] else 'NO'
    print(f'  {row["epsilon"]:>8.2f} '
          f'{row["final_regret"]:>14.1f} '
          f'{row["final_reward"]:>14.1f} '
          f'{correct:>10}')
print()
best_eps = comparison.loc[comparison['final_regret'].idxmin(), 'epsilon']
print(f'  Optimal epsilon: {best_eps}')
print()

# ── VISUALISATION ─────────────────────────────────────────────
print('Section 5: Generating charts...')

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Multi-Armed Bandit — Promotion Optimisation',
             fontsize=16, fontweight='bold')

# Chart 1: Cumulative reward over time
axes[0, 0].plot(results['round'],
                results['cumulative_reward'],
                color='#4CAF50', linewidth=2)
axes[0, 0].set_title('Cumulative Reward Over Time',
                      fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('Round')
axes[0, 0].set_ylabel('Cumulative Orders Generated')
axes[0, 0].grid(True, alpha=0.3)

# Chart 2: Cumulative regret over time
axes[0, 1].plot(results['round'],
                results['cumulative_regret'],
                color='#F44336', linewidth=2)
axes[0, 1].set_title('Cumulative Regret Over Time\n'
                      '(Lower is better)',
                      fontsize=12, fontweight='bold')
axes[0, 1].set_xlabel('Round')
axes[0, 1].set_ylabel('Cumulative Regret')
axes[0, 1].grid(True, alpha=0.3)

# Chart 3: Estimated vs true reward rates
best_estimated_arm = int(summary.iloc[0]['arm_id'])  # arm with highest estimated reward
colors = ['#4CAF50' if i == best_estimated_arm else '#F44336'
          for i in range(len(PROMOTION_ARMS))]
x        = range(len(PROMOTION_ARMS))
promo_names = [PROMOTION_ARMS[i]['name'][:15]
               for i in range(len(PROMOTION_ARMS))]
true_rewards     = [PROMOTION_ARMS[i]['true_reward']
                    for i in range(len(PROMOTION_ARMS))]
estimated_rewards = [summary[summary['arm_id'] == i]
                     ['estimated_reward'].values[0]
                     for i in range(len(PROMOTION_ARMS))]

axes[1, 0].bar([xi - 0.2 for xi in x], true_rewards,
               width=0.4, label='True Reward',
               color='#1565C0', alpha=0.8)
axes[1, 0].bar([xi + 0.2 for xi in x], estimated_rewards,
               width=0.4, label='Bandit Estimate',
               color='#FF9800', alpha=0.8)
axes[1, 0].set_xticks(list(x))
axes[1, 0].set_xticklabels(promo_names,
                             rotation=30, ha='right', fontsize=8)
axes[1, 0].set_title('True vs Learned Reward Rates',
                      fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('Reward Rate')
axes[1, 0].legend()
axes[1, 0].grid(True, axis='y', alpha=0.3)

# Chart 4: Epsilon comparison
axes[1, 1].bar(
    comparison['epsilon'].astype(str),
    comparison['final_regret'],
    color=['#4CAF50' if c else '#F44336'
           for c in comparison['correct']],
    edgecolor='white'
)
axes[1, 1].set_title('Regret by Epsilon Value\n'
                      'Green=Found best promotion',
                      fontsize=12, fontweight='bold')
axes[1, 1].set_xlabel('Epsilon (Exploration Rate)')
axes[1, 1].set_ylabel('Final Cumulative Regret')
axes[1, 1].grid(True, axis='y', alpha=0.3)

plt.tight_layout()
os.makedirs('docs/models', exist_ok=True)
plt.savefig('docs/models/bandit_promotions.png',
            dpi=150, bbox_inches='tight')
plt.close()
print('  Chart saved: docs/models/bandit_promotions.png')
print()

# ── SAVE OUTPUTS ──────────────────────────────────────────────
print('Section 6: Saving outputs...')
os.makedirs('data/processed', exist_ok=True)
results.to_parquet('data/processed/bandit_results.parquet', index=False)
summary.to_parquet('data/processed/bandit_summary.parquet', index=False)
print('  bandit_results.parquet saved')
print('  bandit_summary.parquet saved')
print()

# ── BUSINESS INSIGHT ──────────────────────────────────────────
print('BUSINESS INSIGHT')
print('-' * 55)
print(f'  Best promotion discovered: {best_promo}')
print(f'  Estimated conversion rate: '
      f'{summary.iloc[0]["estimated_reward"]*100:.1f}%')
print(f'  Recommended epsilon for production: {best_eps}')
print()
print('  The bandit will continuously improve as more')
print('  promotion data flows in from real users.')
print('-' * 55)
print()
print('=' * 60)
print('ALL ENHANCEMENTS COMPLETE')
print()
print('New files created:')
new_files = [
    'src/reminder_system.py      Enhancement 9',
    'src/trend_detector.py       Enhancement 10',
    'src/cold_start.py           Enhancement 11',
    'src/basket_predictor.py     Enhancement 12',
    'src/affinity_network.py     Enhancement 13',
    'src/bandit_promotions.py    Enhancement 14',
]
for f in new_files:
    print(f'  {f}')
print()
print('Run all enhancements:')
for i in range(16, 22):
    print(f'  python notebooks/{i}_*.py')
print('=' * 60)
# notebooks/12_drift_detector.py
# Enhancement 5 - Model Drift Detection
# Run from project root: python notebooks/12_drift_detector.py

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.drift_detector import (simulate_recent_data, run_drift_analysis,
                                 should_retrain)

print('=' * 60)
print('ENHANCEMENT 5 - MODEL DRIFT DETECTION')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── LOAD DATA ─────────────────────────────────────────────────
print('Section 1: Loading training data...')
training_data = pd.read_parquet('data/processed/training_dataset.parquet')
with open('data/processed/feature_cols.txt') as f:
    FEATURE_COLS = f.read().splitlines()

print(f'  Training data: {training_data.shape}')
print(f'  Features:      {len(FEATURE_COLS)}')
print()

# ── SIMULATE RECENT DATA ──────────────────────────────────────
print('Section 2: Simulating recent production data...')
print('  Scenario: 3 features have drifted significantly')
drift_features = ['u_avg_days_between', 'p_reorder_rate', 'up_orders_since_last']
recent_data = simulate_recent_data(
    training_data,
    FEATURE_COLS,
    drift_features    = drift_features,
    drift_magnitude   = 0.35,
    random_state      = 42
)
print(f'  Recent data simulated: {recent_data.shape}')
print(f'  Drifted features: {drift_features}')
print()

# ── RUN DRIFT ANALYSIS ────────────────────────────────────────
print('Section 3: Running PSI drift analysis on all 21 features...')
drift_report = run_drift_analysis(training_data, recent_data, FEATURE_COLS)
print()

print('  DRIFT REPORT')
print(f'  {"Feature":<30} {"PSI":>8} {"Status":<22} {"Action"}')
print('  ' + '-' * 80)
for _, row in drift_report.iterrows():
    flag = '*** ' if row['psi'] >= 0.2 else '    '
    print(f'  {flag}{row["feature"]:<26} {row["psi"]:>8.4f} '
          f'{row["status"]:<22} {row["action"]}')
print()

# ── RETRAINING DECISION ───────────────────────────────────────
print('Section 4: Retraining decision...')
retrain, reason = should_retrain(drift_report)
print(f'  Should retrain: {retrain}')
print(f'  Reason: {reason}')
print()

if retrain:
    print('  ACTION REQUIRED: Model drift detected.')
    print('  Recommended steps:')
    print('  1. Investigate root cause of drift in flagged features')
    print('  2. Collect fresh training data from recent orders')
    print('  3. Retrain LightGBM model with updated data')
    print('  4. Compare new model F1 vs current model F1')
    print('  5. If new F1 >= current F1 - 0.01, promote to production')
else:
    print('  Model is stable. No retraining required.')
print()

# ── VISUALISATION ─────────────────────────────────────────────
print('Section 5: Generating drift report chart...')

fig, ax = plt.subplots(figsize=(12, 8))

colors = ['#F44336' if psi >= 0.2
          else '#FF9800' if psi >= 0.1
          else '#4CAF50'
          for psi in drift_report['psi']]

bars = ax.barh(drift_report['feature'], drift_report['psi'],
               color=colors, edgecolor='white')

ax.axvline(x=0.1, color='orange', linestyle='--', alpha=0.8,
           label='Minor drift threshold (0.1)')
ax.axvline(x=0.2, color='red', linestyle='--', alpha=0.8,
           label='Significant drift threshold (0.2)')

ax.set_xlabel('Population Stability Index (PSI)', fontsize=12)
ax.set_title('Feature Drift Detection Report\n'
             'Green=Stable | Orange=Minor | Red=Significant',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, axis='x', alpha=0.3)

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#4CAF50', label='Stable (PSI < 0.1)'),
    Patch(facecolor='#FF9800', label='Minor drift (0.1 - 0.2)'),
    Patch(facecolor='#F44336', label='Significant drift (PSI > 0.2)'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
plt.tight_layout()
plt.savefig('docs/models/drift_report.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Chart saved: docs/models/drift_report.png')
print()

# ── SAVE REPORT ───────────────────────────────────────────────
drift_report.to_csv('docs/models/drift_report.csv', index=False)
print('  drift_report.csv saved')
print()
print('Enhancement 5 complete. Run next: python notebooks/13_clv_model.py')
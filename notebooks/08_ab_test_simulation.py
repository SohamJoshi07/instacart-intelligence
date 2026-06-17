# notebooks/08_ab_test_simulation.py
# Enhancement 1 - A/B Test Simulation
# Run from project root: python notebooks/08_ab_test_simulation.py

import os, sys, pickle
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
from src.ab_testing import run_ab_test, plot_ab_results, calculate_required_sample_size

print('=' * 60)
print('ENHANCEMENT 1 - A/B TEST SIMULATION FRAMEWORK')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── LOAD ASSETS ───────────────────────────────────────────────
print('Loading model and data...')
with open('data/processed/lgbm_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('data/processed/feature_cols.txt') as f:
    FEATURE_COLS = f.read().splitlines()

training_data = pd.read_parquet('data/processed/training_dataset.parquet')
products      = pd.read_parquet('data/processed/product_lookup.parquet')

print(f'  Model: {model.best_iteration_} trees')
print(f'  Training data: {training_data.shape}')
print()

# ── SAMPLE SIZE CALCULATION ───────────────────────────────────
print('Sample size calculation...')
print('  Target: detect 18% CTR uplift with 95% confidence and 80% power')
required = calculate_required_sample_size(
    baseline_ctr=0.60,
    minimum_detectable_effect=0.18,
    alpha=0.05,
    power=0.80
)
print(f'  Required users per group: {required:,}')
print(f'  Total users required:     {required*2:,}')
print(f'  Available users:          {training_data["user_id"].nunique():,}')
print()

# ── RUN A/B TEST ──────────────────────────────────────────────
print('Running A/B test simulation...')
results = run_ab_test(
    training_data    = training_data,
    products         = products,
    model            = model,
    feature_cols     = FEATURE_COLS,
    n_users          = 2000,
    n_recommendations= 10,
    random_state     = 42
)

# ── PRINT RESULTS ─────────────────────────────────────────────
print('A/B TEST RESULTS')
print('=' * 55)
print(f"{'Metric':<20} {'Control':>12} {'Treatment':>12} {'Lift':>10}")
print('-' * 55)
for metric in ['ctr', 'precision', 'recall', 'f1']:
    cv   = results['control'][metric]
    tv   = results['treatment'][metric]
    lift = (tv - cv) / cv * 100 if cv > 0 else 0
    print(f"  {metric.upper():<18} {cv:>12.4f} {tv:>12.4f} {lift:>+9.2f}%")
print('-' * 55)
print(f"  CTR Lift:            {results['ctr_lift_pct']:>+.2f}%")
print(f"  Chi-square stat:     {results['significance']['chi2_statistic']:.4f}")
print(f"  P-value:             {results['significance']['p_value']:.6f}")
print(f"  Significant (95%):   {results['significance']['significant_at_95']}")
print(f"  Significant (99%):   {results['significance']['significant_at_99']}")
print('=' * 55)
print()

if results['significance']['significant_at_95']:
    print('CONCLUSION: The ML model significantly outperforms the')
    print('rule-based system. Safe to roll out to production.')
else:
    print('CONCLUSION: Difference not statistically significant yet.')
    print(f'Need {results["required_samples"]:,} users per group for significance.')
print()

# ── GENERATE CHART ────────────────────────────────────────────
print('Generating results chart...')
plot_ab_results(results)
print()

# ── SAVE RESULTS ──────────────────────────────────────────────
summary = pd.DataFrame({
    'metric':    ['CTR', 'Precision', 'Recall', 'F1'],
    'control':   [results['control'][m]   for m in ['ctr','precision','recall','f1']],
    'treatment': [results['treatment'][m] for m in ['ctr','precision','recall','f1']],
})
summary['lift_pct'] = ((summary['treatment'] - summary['control'])
                       / summary['control'] * 100).round(2)
summary.to_csv('docs/models/ab_test_summary.csv', index=False)
print('Results saved: docs/models/ab_test_summary.csv')
print()
print('Enhancement 1 complete. Run next: python notebooks/09_order_timing.py')
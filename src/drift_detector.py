# src/drift_detector.py
# Enhancement 5 - Model Drift Detection using Population Stability Index
# Monitors whether feature distributions have shifted since training.

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def compute_psi(expected: np.ndarray,
                actual: np.ndarray,
                buckets: int = 10) -> float:
    
    """
    Compute Population Stability Index between two distributions.

    PSI < 0.1  : No significant change. Model is stable.
    PSI 0.1-0.2: Minor change. Monitor closely.
    PSI > 0.2  : Significant change. Retraining required.

    Parameters
    ----------
    expected : array from training distribution
    actual   : array from recent/production distribution
    buckets  : number of bins for discretisation
    """

    expected = expected[~np.isnan(expected)]
    actual = actual[~np.isnan(actual)]

    breakpoints = np.percentile(expected, np.linspace(0, 100, buckets + 1))
    breakpoints = np.unique(breakpoints)

    if len(breakpoints) < 2:
        return 0.0
    
    expected_counts = np.histogram(expected, bins=breakpoints)[0]
    actual_counts = np.histogram(actual, bins=breakpoints)[0]

    #Add small epsilon to avoid division by zero and log(0)
    eps = 1e-6
    expected_pct = expected_counts / (len(expected)+eps) + eps
    actual_pct = actual_counts / (len(actual)+eps) + eps

    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return round(float(psi), 6)

def simulate_recent_data(training_data: pd.DataFrame,
                         feature_cols: list,
                         drift_features: list = None,
                         drift_magnitude: float = 0.3,
                         random_state: int = 42) -> pd.DataFrame:
    """
    Simulate a 'recent' dataset with optional synthetic drift.
    In production this would be replaced with real recent data.

    Parameters
    ----------
    drift_features  : features to add synthetic drift to
    drift_magnitude : how much drift to add (fraction of std)
    """

    rng = np.random.default_rng(random_state)
    recent = training_data[feature_cols].sample(
        min(50000, len(training_data)), random_state=random_state
    ).copy()

    if drift_features:
        for feat in drift_features:
            if feat in recent.columns:
                std_val = recent[feat].std()
                recent[feat] = recent[feat] + rng.normal(
                    drift_magnitude * std_val, 0.1 * std_val, len(recent)
                )
        return recent
    
def run_drift_analysis(training_data: pd.DataFrame,
                       recent_data: pd.DataFrame,
                       feature_cols: list) -> pd.DataFrame:
    
    """
    Run PSI analysis on all features and return drift report.
    """

    results = []
    for feat in feature_cols:
        if feat not in training_data.columns or feat not in recent_data.columns:
            continue

        psi = compute_psi(
            training_data[feat].values,
            recent_data[feat].values
        )

        if psi < 0.1:
            status = 'STABLE'
            action = 'No action required'
        elif psi < 0.2:
            status = 'MINOR DRIFT'
            action = 'Monitor closely'
        else:
            status = 'SIGNIFICANT DRIFT'
            action = 'Retraining recommended'

        results.append({
            'feature':  feat,
            'psi':      psi,
            'status':   status,
            'action':   action,
        })
    return pd.DataFrame(results).sort_values('psi', ascending=False)

def should_retrain(drift_report: pd.DataFrame,
                   psi_threshold: float = 0.2,
                   min_drifted_features : int = 3) -> tuple:
    """
    Determine if model retraining is required.

    Returns (should_retrain: bool, reason: str)
    """
    drifted = drift_report[drift_report['psi'] >= psi_threshold]
    n_drifted = len(drifted)

    if n_drifted >= min_drifted_features:
        reason = (f'{n_drifted} features show significant drift'
                   f'(psi >= {psi_threshold}): '
                   f'{", ".join(drifted["feature"].head(3).tolist())}')
        return True, reason
    return False, f'Only {n_drifted} features drifted (threshold: {min_drifted_features})'
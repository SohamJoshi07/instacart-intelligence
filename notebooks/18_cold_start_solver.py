# notebooks/18_cold_start_solver.py
# Enhancement 11 - Cold Start Solver
# Run from project root: python notebooks/18_cold_start_solver.py

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.data_loader import load_product_lookup
from src.cold_start import (create_new_user_profile,
                              build_existing_user_profiles,
                              get_cold_start_recommendations,
                              should_graduate_to_full_model,
                              CATEGORY_PREFERENCES)

print('=' * 60)
print('ENHANCEMENT 11 - COLD START SOLVER')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── LOAD DATA ─────────────────────────────────────────────────
print('Section 1: Loading data...')
training_data = pd.read_parquet('data/processed/training_dataset.parquet')
segments      = pd.read_parquet('data/processed/user_segments.parquet')
products      = load_product_lookup()
print(f'  Training data: {training_data.shape}')
print(f'  Segments:      {len(segments):,}')
print(f'  Products:      {len(products):,}')
print()

# ── BUILD EXISTING PROFILES ───────────────────────────────────
print('Section 2: Building existing user profiles...')
existing_profiles = build_existing_user_profiles(
    segments, training_data, products
)
print(f'  Profiles built: {len(existing_profiles):,}')
print(f'  Profile columns: {len(existing_profiles.columns)}')
print()

# ── TEST SCENARIO 1: FAMILY SHOPPER ──────────────────────────
print('Section 3: Test Scenario 1 - Family Shopper')
print('  New user preferences:')
print('  - Favourite categories: produce, dairy eggs, bakery, snacks')
print('  - Dietary preference: none')
print('  - Household size: 4')
print()

family_profile = create_new_user_profile(
    preferred_categories = ['produce', 'dairy eggs', 'bakery', 'snacks'],
    dietary_preference   = 'none',
    household_size       = 4
)

family_recs = get_cold_start_recommendations(
    new_user_profile  = family_profile,
    existing_profiles = existing_profiles,
    training_data     = training_data,
    products          = products,
    n_similar         = 100,
    n_recs            = 10
)

print('  Recommendations for Family Shopper:')
for i, (_, row) in enumerate(family_recs.iterrows()):
    organic = 'Organic' if row['is_organic'] else ''
    print(f'  {i+1:2}. [{row["cold_start_score"]:.3f}] '
          f'{str(row["product_name"])[:35]:35s} '
          f'{row["department"]:15s} {organic}')
print()

# ── TEST SCENARIO 2: VEGAN SINGLE USER ───────────────────────
print('Section 4: Test Scenario 2 - Vegan Single User')
print('  New user preferences:')
print('  - Favourite categories: produce, beverages, snacks')
print('  - Dietary preference: vegan')
print('  - Household size: 1')
print()

vegan_profile = create_new_user_profile(
    preferred_categories = ['produce', 'beverages', 'snacks'],
    dietary_preference   = 'vegan',
    household_size       = 1
)

vegan_recs = get_cold_start_recommendations(
    new_user_profile  = vegan_profile,
    existing_profiles = existing_profiles,
    training_data     = training_data,
    products          = products,
    n_similar         = 100,
    n_recs            = 10
)

print('  Recommendations for Vegan Single User:')
for i, (_, row) in enumerate(vegan_recs.iterrows()):
    organic = 'Organic' if row['is_organic'] else ''
    print(f'  {i+1:2}. [{row["cold_start_score"]:.3f}] '
          f'{str(row["product_name"])[:35]:35s} '
          f'{row["department"]:15s} {organic}')
print()

# ── GRADUATION LOGIC ──────────────────────────────────────────
print('Section 5: Model graduation logic...')
print()
for n_orders in [0, 1, 3, 5, 10]:
    graduate = should_graduate_to_full_model(n_orders)
    model    = 'Full LightGBM Model' if graduate else 'Cold Start Model'
    print(f'  User with {n_orders:2d} orders → {model}')
print()

# ── SAVE OUTPUTS ──────────────────────────────────────────────
print('Section 6: Saving outputs...')
os.makedirs('data/processed', exist_ok=True)

# Save a sample of cold start profiles for reference
sample_profiles = existing_profiles.head(1000)
sample_profiles.to_parquet(
    'data/processed/cold_start_profiles.parquet', index=False)
print('  cold_start_profiles.parquet saved')
print()
print('Enhancement 11 complete.')
print('Run next: python notebooks/19_basket_size_predictor.py')
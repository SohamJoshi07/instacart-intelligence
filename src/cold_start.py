import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

#----Preference Profiles------------
CATEGORY_PREFERENCES = [                          # Fix 1: was CATEGORY_PREFRENCES
    'produce', 'dairy eggs', 'meat seafood', 'bakery',
    'frozen', 'snacks', 'beverages', 'pantry',
    'breakfast', 'personal care', 'babies', 'pets'
]

DIETARY_OPTIONS = ['none', 'vegetarian', 'vegan', 'gluten_free']

def create_new_user_profile(preferred_categories: list,
                            dietary_preference: str,
                            household_size: int) -> dict:
    """
    Create a preference profile for a new user.

    Parameters
    ----------
    preferred_categories : list of department names the user likes
    dietary_preference   : one of DIETARY_OPTIONS
    household_size       : 1, 2, 3, or 4+

    Returns
    -------
    dict with one-hot encoded preferences
    """

    profile = {}

    # One-hot encode category preferences
    for cat in CATEGORY_PREFERENCES:              # Fix 1: was CATEGORY_PREFRENCES
        profile[f'pref_{cat}'] = 1 if cat in preferred_categories else 0

    #Dietary Encoding
    for diet in DIETARY_OPTIONS:
        profile[f'diet_{diet}'] = 1 if dietary_preference == diet else 0

    #Household size normalised
    profile['household_size'] = min(household_size, 4) / 4.0

    return profile

def build_existing_user_profiles(segments: pd.DataFrame,
                                 training_data: pd.DataFrame,
                                 products: pd.DataFrame) -> pd.DataFrame:
    """
    Build preference profiles for existing users based on
    their actual purchase behaviour.
    Used to find similar existing users for cold start.
    """

    #Department affinity per user
    dept_affinity = (training_data
                     .merge(products[['product_id', 'department']],
                            on='product_id', how='left')
                            .groupby(['user_id', 'department'])['reordered']
                            .mean()
                            .unstack(fill_value=0)
                            .reset_index()) 
    
    #Rename columns to match new user profile format
    dept_affinity.columns = [
        f'pref_{c}' if c != 'user_id' else c      # Fix 2: was f'prep_{c}'
        for c in dept_affinity.columns
    ]

    #Merge with segments
    profiles = dept_affinity.merge(
        segments[['user_id', 'frequency', 'rfm_r', 'rfm_f']],
        on='user_id', how='left'
    )

    #Estimate household size from basket behaviour
    avg_basket = (training_data
                  .groupby('user_id')['product_id']
                  .count()
                  .reset_index()
                  .rename(columns={'product_id': 'avg_basket'}))
    profiles = profiles.merge(avg_basket, on='user_id', how='left')
    profiles['household_size'] = (
        profiles['avg_basket'] / profiles['avg_basket'].max()
    ).fillna(0.5)

    return profiles

def find_similar_users(new_user_profile: dict,
                       existing_profiles: pd.DataFrame,
                       n: int = 100) -> list:
    """
    Find N most similar existing users to a new user.
    Uses cosine similarity on the preference vectors.

    Parameters
    ----------
    new_user_profile  : dict from create_new_user_profile
    existing_profiles : DataFrame from build_existing_user_profiles
    n                 : number of similar users to return

    Returns
    -------
    list of user_ids
    """
    # Get shared feature columns
    profile_cols = [c for c in existing_profiles.columns
                    if c.startswith('pref') or c == 'household_size']
    
    #Filter to only columns that exist in both
    shared_cols = [c for c in profile_cols
                   if c in new_user_profile]
    
    if not shared_cols:
        #Fallback: return most frequent users
        return existing_profiles['user_id'].head(n).tolist()
    
    new_vec = np.array([new_user_profile.get(c, 0)
                        for c in shared_cols])
    
    existing_matrix = existing_profiles[shared_cols].fillna(0).values

    #Cosine Similarity
    new_norm = np.linalg.norm(new_vec)
    existing_norm = np.linalg.norm(existing_matrix, axis=1)

    if new_norm == 0:
        return existing_profiles['user_id'].head(n).tolist()
    
    similarities = (existing_matrix @ new_vec) / (
        existing_norm * new_norm + 1e-8
    )

    top_indices = np.argsort(similarities)[::-1][:n]  # Fix 3: was [::-1][n] (scalar)
    return existing_profiles.iloc[top_indices]['user_id'].tolist()

def get_cold_start_recommendations(new_user_profile: dict,
                                   existing_profiles: pd.DataFrame,
                                   training_data: pd.DataFrame,
                                   products: pd.DataFrame,
                                   n_similar: int = 100,
                                   n_recs: int = 15) -> pd.DataFrame:
    
    """
    Full cold start recommendation pipeline.

    1. Find similar existing users
    2. Get their most reordered products
    3. Return top N as recommendations

    Parameters
    ----------
    new_user_profile  : from create_new_user_profile
    existing_profiles : from build_existing_user_profiles
    training_data     : full training dataset
    products          : product lookup
    n_similar         : number of similar users to use
    n_recs            : number of recommendations to return
    """

    #Find Similar Users
    similar_user_ids = find_similar_users(
        new_user_profile, existing_profiles, n=n_similar
    )

    # Get their most reordered products
    peer_data = training_data[
        training_data['user_id'].isin(similar_user_ids)
    ]

    peer_products = (peer_data
                     .groupby('product_id')
                     .agg(
                         reorder_rate = ('reordered', 'mean'),
                         order_count = ('order_id', 'nunique'),
                         n_users = ('user_id', 'nunique'),
                     )
                     .reset_index())
    
    #Score: combination of reorder rate and popularity
    peer_products['cold_start_score'] = (
        0.6 * peer_products['reorder_rate'] + 
        0.4 * (peer_products['n_users'] / n_similar)
    )

    top_recs = (peer_products
                .sort_values('cold_start_score', ascending=False)
                .head(n_recs)
                .merge(products[['product_id', 'product_name',
                                 'department', 'is_organic']],
                        on='product_id', how='left'))
    
    return top_recs[['product_id', 'product_name', 'department',
                      'is_organic', 'cold_start_score',
                      'reorder_rate', 'n_users']].reset_index(drop=True)

def should_graduate_to_full_model(n_orders: int,
                                  threshold: int = 5) -> bool:
    """
    Determine if a user has enough history to use the full model.
    Graduates after threshold orders.
    """

    return n_orders >= threshold
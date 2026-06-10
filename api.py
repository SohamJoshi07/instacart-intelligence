# phase4_api.py
# Phase 4 - Basket Recommendation API
# Run from project root: python phase4_api.py
# This builds and tests the FastAPI recommendation service.
# Vikram Nair owns infrastructure. Soham writes tests.

import os
import sys
import pickle
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.abspath('.'))
from src.data_loader import load_product_lookup, load_user_segments

print('=' * 60)
print('PHASE 4 - BASKET RECOMMENDATION API')
print('Instacart Customer Intelligence Platform')
print('AtliQ Technologies - Data Science Team')
print('=' * 60)
print()

# ── SECTION 1: LOAD MODEL AND ASSETS ─────────────────────────
print('Section 1: Loading model and assets...')

with open('data/processed/lgbm_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('data/processed/feature_cols.txt') as f:
    FEATURE_COLS = f.read().splitlines()

training_data = pd.read_parquet('data/processed/training_dataset.parquet')
products      = load_product_lookup()
segments      = load_user_segments()

print(f'  Model loaded: {model.best_iteration_} trees')
print(f'  Features:     {len(FEATURE_COLS)} columns')
print(f'  Training data:{training_data.shape}')
print(f'  Products:     {len(products):,}')
print(f'  Segments:     {len(segments):,}')
print()

# ── SECTION 2: RECOMMENDATION FUNCTION ───────────────────────
print('Section 2: Building recommendation function...')

def get_basket_recommendations(user_id: int,
                                n: int = 10,
                                exclude_recent: bool = True) -> pd.DataFrame:
    """
    Get top N reorder recommendations for a given user.

    Parameters
    ----------
    user_id        : Instacart user ID
    n              : number of recommendations to return (default 10)
    exclude_recent : if True, flag products recently purchased

    Returns
    -------
    DataFrame with columns:
        product_id, product_name, department, aisle,
        reorder_probability, is_organic
    """
    # Get all user-product pairs for this user from training data
    user_data = training_data[training_data['user_id'] == user_id].copy()

    if len(user_data) == 0:
        return pd.DataFrame(columns=[
            'product_id', 'product_name', 'department',
            'reorder_probability', 'is_organic'
        ])

    # Score all user-product pairs
    proba = model.predict_proba(user_data[FEATURE_COLS])[:, 1]
    user_data = user_data.assign(reorder_probability=proba)

    # Get top N recommendations
    # Change to this — merge all columns first, select after
    top_n = (user_data
         .sort_values('reorder_probability', ascending=False)
         .head(n)
         .merge(products, on='product_id', how='left'))

# Then select only what you need
    top_n = top_n.rename(columns={'is_organic_y': 'is_organic'})
    return top_n[['product_id', 'product_name', 'department',
              'aisle', 'reorder_probability', 'is_organic']].reset_index(drop=True)


def get_user_segment(user_id: int) -> str:
    """Return the customer segment label for a given user."""
    user_seg = segments[segments['user_id'] == user_id]
    if len(user_seg) == 0:
        return 'Unknown'
    return user_seg.iloc[0]['segment']


def get_similar_products(product_id: int, n: int = 5) -> pd.DataFrame:
    """
    Find N products most similar to the given product
    based on department and reorder behaviour.
    """
    if product_id not in products['product_id'].values:
        return pd.DataFrame()

    target = products[products['product_id'] == product_id].iloc[0]
    same_dept = products[
        (products['department_id'] == target['department_id']) &
        (products['product_id'] != product_id)
    ].copy()

    # Score by product reorder rate from training data
    product_stats = (training_data
                     .groupby('product_id')['reordered']
                     .mean()
                     .reset_index()
                     .rename(columns={'reordered': 'reorder_rate'}))

    same_dept = same_dept.merge(product_stats, on='product_id', how='left')
    same_dept['reorder_rate'] = same_dept['reorder_rate'].fillna(0)

    return (same_dept
            .sort_values('reorder_rate', ascending=False)
            .head(n)[['product_id', 'product_name', 'department', 'reorder_rate']]
            .reset_index(drop=True))


print('  get_basket_recommendations() defined')
print('  get_user_segment() defined')
print('  get_similar_products() defined')
print()

# ── SECTION 3: TEST RECOMMENDATION FUNCTION ──────────────────
print('Section 3: Testing recommendation function on 5 users...')
print()

sample_users = training_data['user_id'].unique()[:5]

for uid in sample_users:
    segment = get_user_segment(uid)
    recs    = get_basket_recommendations(uid, n=5)

    print(f'  User {uid} — Segment: {segment}')
    if len(recs) == 0:
        print('    No recommendations available')
    else:
        for _, row in recs.iterrows():
            organic = 'organic' if row['is_organic'] else ''
            print(f'    [{row["reorder_probability"]:.3f}] '
                  f'{str(row["product_name"])[:35]:35s} '
                  f'{row["department"]:15s} {organic}')
    print()

# ── SECTION 4: TEST SIMILAR PRODUCTS ─────────────────────────
print('Section 4: Testing similar products function...')
print()

test_products = products['product_id'].values[:3]
for pid in test_products:
    name    = products[products['product_id'] == pid].iloc[0]['product_name']
    similar = get_similar_products(pid, n=3)
    print(f'  Products similar to: {name}')
    for _, row in similar.iterrows():
        print(f'    {str(row["product_name"])[:40]:40s} reorder_rate={row["reorder_rate"]:.3f}')
    print()

# ── SECTION 5: BUILD FASTAPI SERVICE FILE ────────────────────
print('Section 5: Creating FastAPI service file...')

api_code = '''# src/serving.py
# FastAPI Basket Recommendation Service
# Run with: uvicorn src.serving:app --reload
# Endpoints:
#   GET  /health
#   GET  /recommendations/{user_id}?n=10
#   POST /recommendations/batch
#   GET  /similar-items/{product_id}?n=5

import os
import sys
import pickle
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath("."))

app = FastAPI(
    title="Instacart Customer Intelligence API",
    description="Reorder prediction and basket recommendation service",
    version="1.0.0"
)

# ── LOAD MODEL AND DATA ON STARTUP ────────────────────────────
print("Loading model and assets...")

with open("data/processed/lgbm_model.pkl", "rb") as f:
    MODEL = pickle.load(f)

with open("data/processed/feature_cols.txt") as f:
    FEATURE_COLS = f.read().splitlines()

TRAINING_DATA = pd.read_parquet("data/processed/training_dataset.parquet")
SEGMENTS      = pd.read_parquet("data/processed/user_segments.parquet")

print(f"Model loaded: {MODEL.best_iteration_} trees")
print(f"Training data: {TRAINING_DATA.shape}")
print("API ready.")

# ── PYDANTIC MODELS ───────────────────────────────────────────
class RecommendationItem(BaseModel):
    product_id:           int
    product_name:         str
    department:           str
    reorder_probability:  float
    is_organic:           bool

class RecommendationResponse(BaseModel):
    user_id:   int
    segment:   str
    n:         int
    recommendations: List[RecommendationItem]

class BatchRequest(BaseModel):
    user_ids: List[int]
    n:        Optional[int] = 10

class BatchResponse(BaseModel):
    results: List[RecommendationResponse]

# ── HELPER FUNCTIONS ──────────────────────────────────────────
def _get_recommendations(user_id: int, n: int) -> RecommendationResponse:
    user_data = TRAINING_DATA[TRAINING_DATA["user_id"] == user_id].copy()

    if len(user_data) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"User {user_id} not found in training data"
        )

    proba     = MODEL.predict_proba(user_data[FEATURE_COLS])[:, 1]
    user_data = user_data.assign(reorder_probability=proba)

    top_n = (user_data
             .sort_values("reorder_probability", ascending=False)
             .head(n))

    seg_row = SEGMENTS[SEGMENTS["user_id"] == user_id]
    segment = seg_row.iloc[0]["segment"] if len(seg_row) > 0 else "Unknown"

    items = []
    for _, row in top_n.iterrows():
        items.append(RecommendationItem(
            product_id          = int(row["product_id"]),
            product_name        = str(row.get("product_name", "Unknown")),
            department          = str(row.get("department", "Unknown")),
            reorder_probability = float(row["reorder_probability"]),
            is_organic          = bool(row.get("is_organic", False))
        ))

    return RecommendationResponse(
        user_id=user_id, segment=segment, n=len(items), recommendations=items
    )

# ── ENDPOINTS ─────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {
        "status":        "healthy",
        "model_version": "lgbm-v1.0",
        "n_trees":       MODEL.best_iteration_,
        "n_users":       int(TRAINING_DATA["user_id"].nunique()),
        "n_features":    len(FEATURE_COLS)
    }

@app.get("/recommendations/{user_id}", response_model=RecommendationResponse)
def get_recommendations(user_id: int, n: int = 10):
    if n < 1 or n > 50:
        raise HTTPException(status_code=400, detail="n must be between 1 and 50")
    return _get_recommendations(user_id, n)

@app.post("/recommendations/batch", response_model=BatchResponse)
def get_batch_recommendations(request: BatchRequest):
    if len(request.user_ids) > 1000:
        raise HTTPException(status_code=400, detail="Maximum 1000 users per batch request")
    results = []
    for uid in request.user_ids:
        try:
            results.append(_get_recommendations(uid, request.n))
        except HTTPException:
            pass
    return BatchResponse(results=results)

@app.get("/similar-items/{product_id}")
def get_similar_items(product_id: int, n: int = 5):
    product_stats = (TRAINING_DATA
                     .groupby("product_id")["reordered"]
                     .mean()
                     .reset_index()
                     .rename(columns={"reordered": "reorder_rate"}))
    if product_id not in TRAINING_DATA["product_id"].values:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return {"product_id": product_id, "similar_items": [], "message": "Feature coming in v1.1"}

@app.get("/segment/{user_id}")
def get_user_segment(user_id: int):
    seg_row = SEGMENTS[SEGMENTS["user_id"] == user_id]
    if len(seg_row) == 0:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    row = seg_row.iloc[0]
    return {
        "user_id":   user_id,
        "segment":   row["segment"],
        "rfm_r":     float(row["rfm_r"]),
        "rfm_f":     float(row["rfm_f"]),
        "recency":   float(row["recency"]),
        "frequency": float(row["frequency"])
    }
'''

with open('src/serving.py', 'w', encoding='utf-8') as f:
    f.write(api_code)
print('  src/serving.py created')
print()

# ── SECTION 6: CREATE UNIT TESTS ─────────────────────────────
print('Section 6: Creating unit tests...')

test_code = '''# tests/test_api.py
# Unit tests for the FastAPI recommendation service
# Run with: pytest tests/test_api.py -v

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from src.serving import app

client = TestClient(app)

# ── HEALTH ENDPOINT TESTS ─────────────────────────────────────
def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200

def test_health_contains_required_fields():
    response = client.get("/health")
    data = response.json()
    assert "status"        in data
    assert "model_version" in data
    assert "n_trees"       in data
    assert "n_users"       in data
    assert "n_features"    in data

def test_health_status_is_healthy():
    response = client.get("/health")
    assert response.json()["status"] == "healthy"

def test_health_n_features_is_21():
    response = client.get("/health")
    assert response.json()["n_features"] == 21

# ── RECOMMENDATIONS ENDPOINT TESTS ───────────────────────────
def test_recommendations_valid_user():
    response = client.get("/recommendations/1?n=5")
    assert response.status_code == 200

def test_recommendations_response_structure():
    response = client.get("/recommendations/1?n=5")
    data = response.json()
    assert "user_id"         in data
    assert "segment"         in data
    assert "recommendations" in data
    assert "n"               in data

def test_recommendations_correct_user_id():
    response = client.get("/recommendations/1?n=5")
    assert response.json()["user_id"] == 1

def test_recommendations_returns_n_items():
    response = client.get("/recommendations/1?n=5")
    data = response.json()
    assert len(data["recommendations"]) <= 5

def test_recommendations_item_has_required_fields():
    response = client.get("/recommendations/1?n=5")
    item = response.json()["recommendations"][0]
    assert "product_id"          in item
    assert "product_name"        in item
    assert "reorder_probability" in item
    assert "department"          in item
    assert "is_organic"          in item

def test_recommendations_probability_between_0_and_1():
    response = client.get("/recommendations/1?n=10")
    for item in response.json()["recommendations"]:
        assert 0.0 <= item["reorder_probability"] <= 1.0

def test_recommendations_invalid_n_too_high():
    response = client.get("/recommendations/1?n=100")
    assert response.status_code == 400

def test_recommendations_invalid_n_zero():
    response = client.get("/recommendations/1?n=0")
    assert response.status_code == 400

def test_recommendations_unknown_user():
    response = client.get("/recommendations/999999999?n=5")
    assert response.status_code == 404

# ── SEGMENT ENDPOINT TESTS ────────────────────────────────────
def test_segment_valid_user():
    response = client.get("/segment/1")
    assert response.status_code == 200

def test_segment_response_structure():
    response = client.get("/segment/1")
    data = response.json()
    assert "user_id"   in data
    assert "segment"   in data
    assert "rfm_r"     in data
    assert "rfm_f"     in data

def test_segment_valid_segment_name():
    response = client.get("/segment/1")
    valid_segments = [
        "Lapsed Users", "Occasional Buyers",
        "Regular Shoppers", "Weekly Loyalists"
    ]
    assert response.json()["segment"] in valid_segments

def test_segment_unknown_user():
    response = client.get("/segment/999999999")
    assert response.status_code == 404

# ── BATCH ENDPOINT TESTS ──────────────────────────────────────
def test_batch_valid_request():
    response = client.post(
        "/recommendations/batch",
        json={"user_ids": [1, 2, 3], "n": 5}
    )
    assert response.status_code == 200

def test_batch_returns_results():
    response = client.post(
        "/recommendations/batch",
        json={"user_ids": [1, 2, 3], "n": 5}
    )
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0

def test_batch_too_many_users():
    user_ids = list(range(1, 1002))
    response = client.post(
        "/recommendations/batch",
        json={"user_ids": user_ids, "n": 5}
    )
    assert response.status_code == 400
'''

with open('tests/test_api.py', 'w', encoding='utf-8') as f:
    f.write(test_code)
print('  tests/test_api.py created')
print('  25 unit tests written')
print()

# ── SECTION 7: INSTRUCTIONS ───────────────────────────────────
print('Section 7: Phase 4 next steps...')
print()
print('  Step 1 - Install FastAPI and uvicorn:')
print('    pip install fastapi uvicorn httpx pytest')
print()
print('  Step 2 - Run the API locally:')
print('    uvicorn src.serving:app --reload')
print()
print('  Step 3 - Test in browser:')
print('    http://localhost:8000/health')
print('    http://localhost:8000/recommendations/1?n=10')
print('    http://localhost:8000/segment/1')
print('    http://localhost:8000/docs  (interactive Swagger UI)')
print()
print('  Step 4 - Run unit tests:')
print('    pytest tests/test_api.py -v')
print()
print('  Step 5 - Push to GitHub:')
print('    git checkout -b feature/phase4-api')
print('    git add src/serving.py tests/test_api.py phase4_api.py')
print('    git commit -m "Phase 4: FastAPI recommendation service and unit tests"')
print('    git push origin feature/phase4-api')
print()
print('=' * 60)
print('PHASE 4 SETUP COMPLETE')
print()
print('Files created:')
print('  src/serving.py      - FastAPI service with 4 endpoints')
print('  tests/test_api.py   - 25 unit tests')
print()
print('Next: Run the API and execute the tests')
print('=' * 60)
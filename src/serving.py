# src/serving.py
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

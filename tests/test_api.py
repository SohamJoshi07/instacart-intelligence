# tests/test_api.py
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

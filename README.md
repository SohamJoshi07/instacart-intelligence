@"
# Instacart Customer Intelligence Platform

AtliQ Technologies - Data Science Internship Project

## Overview
A machine learning system that predicts which previously purchased
products a user will reorder in their next Instacart grocery basket.

## Dataset
- orders.csv - 3.4 million orders
- order_products__train.csv - 1.3 million order-product pairs
- order_products_prior.csv - 32 million prior order records
- products.csv - 49,688 products
- aisles.csv - 134 aisles
- departments.csv - 21 departments

## Project Phases
- Phase 1: Data Profiling and EDA
- Phase 2: Customer Segmentation (RFM + K-Means)
- Phase 3: Feature Engineering and LightGBM Model
- Phase 4: Basket Recommendation API
- Phase 5: Monitoring and Project Closure

## Setup
pip install -r requirements.txt

## Team
- Rohan Verma - Senior Data Science Manager
- Rahul Mehta - Senior Data Scientist
- Ananya Singh - Data Scientist
- Vikram Nair - MLOps Engineer
- Soham Joshi - Data Science Intern
"@ | Out-File -FilePath "README.md" -Encoding utf8
Write-Host "README.md created" -ForegroundColor Green

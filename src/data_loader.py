# src/data_loader.py

import pandas as pd
import os

DATA_PATH      = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
PROCESSED_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')  # ← ADD THIS

def load_aisles():
    return pd.read_csv(os.path.join(DATA_PATH, 'aisles.csv'))

def load_departments():
    return pd.read_csv(os.path.join(DATA_PATH, 'departments.csv'))

def load_products():
    return pd.read_csv(os.path.join(DATA_PATH, 'products.csv'))

def load_orders():
    return pd.read_csv(os.path.join(DATA_PATH, 'orders.csv'))

def load_order_products_train():
    return pd.read_csv(os.path.join(DATA_PATH, 'order_products__train.csv'))

def load_order_products_prior():
    return pd.read_csv(
        os.path.join(DATA_PATH, 'order_products__prior.csv'),
        dtype={
            'order_id':           'int32',
            'product_id':         'int32',
            'add_to_cart_order':  'int16',
            'reordered':          'int8'
        }
    )

def load_product_lookup():
    products    = load_products()
    aisles      = load_aisles()
    departments = load_departments()
    return (products
            .merge(aisles,       on='aisle_id')
            .merge(departments,  on='department_id'))

def load_user_order_summary():
    path = os.path.join(PROCESSED_PATH, 'user_order_summary.parquet')
    if not os.path.exists(path):
        raise FileNotFoundError(
            "user_order_summary.parquet not found. "
            "Run notebooks/03_user_order_summary.py first."
        )
    return pd.read_parquet(path)

def load_user_rfm():
    path = os.path.join(PROCESSED_PATH, 'user_rfm.parquet')
    if not os.path.exists(path):
        raise FileNotFoundError(
            "user_rfm.parquet not found. "
            "Run notebooks/05_customer_segmentation.py first."
        )
    return pd.read_parquet(path)

def load_user_segments():
    path = os.path.join(PROCESSED_PATH, 'user_segments.parquet')
    if not os.path.exists(path):
        raise FileNotFoundError(
            "user_segments.parquet not found. "
            "Run notebooks/05_customer_segmentation.py first."
        )
    return pd.read_parquet(path)

if __name__ == '__main__':
    print('Testing data loader...')
    tests = [
        ('aisles',                load_aisles),
        ('departments',           load_departments),
        ('products',              load_products),
        ('orders',                load_orders),
        ('order_products_train',  load_order_products_train),
    ]
    for name, fn in tests:
        df = fn()
        print(f'  {name}: {df.shape}  columns: {list(df.columns)}')
    print('All files loaded successfully.')
# src/data_loader.py

import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

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
    # 32 million rows — use correct dtypes to save memory
    return pd.read_csv(
        os.path.join(DATA_PATH, 'order_products_prior.csv'),
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
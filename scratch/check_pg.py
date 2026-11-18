import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
insp = inspect(engine)

print('=== PG CAMPAIGNS COLUMNS ===')
for col in insp.get_columns('campaigns'):
    print(f"{col['name']}: {col['type']}")

print('\n=== PG CUSTOMERS COLUMNS ===')
for col in insp.get_columns('customers'):
    print(f"{col['name']}: {col['type']}")

with engine.connect() as conn:
    print('\nCampaigns sample row:')
    r = conn.execute(text('SELECT * FROM campaigns LIMIT 1')).mappings().fetchone()
    print(dict(r))
    print('\nCustomers sample row:')
    r2 = conn.execute(text('SELECT * FROM customers LIMIT 1')).mappings().fetchone()
    print(dict(r2))

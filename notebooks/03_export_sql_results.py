# -*- coding: utf-8 -*-
# %% [markdown]
# # Marketing Campaign Analytics - SQL Export & Analysis Pipeline
# ## Notebook 03: Export SQL Query Results
#
# This script connects to the local PostgreSQL database, reads the analytical query suite 
# from `sql/02_analysis_queries.sql`, executes each query independently, exports results to 
# `reports/sql_results/<query_name>.csv`, and generates an execution status summary table.

# %%
import os
import re
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Safe display helper for both notebook interactive and standalone script runs
try:
    from IPython.display import display
except ImportError:
    display = print

# Configure pandas display formatting
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: f'{x:,.4f}' if abs(x) < 1 else f'{x:,.2f}')

# %% [markdown]
# ### 1. Environment and Path Initialization

# %%
# Resolve base repository directory
BASE_DIR = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()
ENV_FILE = BASE_DIR / '.env'
SQL_FILE = BASE_DIR / 'sql' / '02_analysis_queries.sql'
OUTPUT_DIR = BASE_DIR / 'reports' / 'sql_results'

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load database credentials from .env
load_dotenv(dotenv_path=ENV_FILE)
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError(f"DATABASE_URL not found in {ENV_FILE.resolve()}. Please check your .env configuration.")

# Mask credentials for safe logging
masked_db_url = re.sub(r':([^@]+)@', ':****@', DATABASE_URL)
print(f"Base Directory   : {BASE_DIR.resolve()}")
print(f"SQL Queries File : {SQL_FILE.resolve()}")
print(f"Output Directory : {OUTPUT_DIR.resolve()}")
print(f"Database Target  : {masked_db_url}")

# Create database engine
engine = create_engine(DATABASE_URL)

# %% [markdown]
# ### 2. Parse and Split Analytical Queries
# We parse `sql/02_analysis_queries.sql` by splitting on the `-- name:` marker lines.

# %%
with open(SQL_FILE, 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Pattern matching "-- name: <query_name>" followed by the SQL body
# Split using positive lookahead for "-- name:"
query_blocks = re.split(r'(?m)^--\s*name:\s*', sql_content)

parsed_queries = []
for block in query_blocks:
    block = block.strip()
    if not block:
        continue
    # Extract query name from the first line
    lines = block.splitlines()
    name_line = lines[0].strip()
    if not re.match(r'^q\d+', name_line):
        continue
    query_name = name_line.split()[0]
    sql_text = '\n'.join(lines[1:]).strip()
    
    if sql_text:
        parsed_queries.append({
            'name': query_name,
            'sql': sql_text
        })

print(f"Successfully parsed {len(parsed_queries)} queries from {SQL_FILE.name}:")
for idx, q in enumerate(parsed_queries, start=1):
    print(f"  {idx:02d}. {q['name']}")

# %% [markdown]
# ### 3. Execute Queries, Save CSVs, and Display Results
# Each query is executed within an isolated try-except block so a query failure does not halt subsequent runs.

# %%
status_records = []
results_dict = {}

print("\n--- Executing SQL Queries ---")
with engine.connect() as conn:
    for item in parsed_queries:
        q_name = item['name']
        q_sql = item['sql']
        csv_path = OUTPUT_DIR / f"{q_name}.csv"
        
        try:
            # Execute query and load into DataFrame
            df_result = pd.read_sql(text(q_sql), conn)
            row_count = len(df_result)
            
            # Export to CSV
            df_result.to_csv(csv_path, index=False)
            
            status_records.append({
                'query': q_name,
                'rows': row_count,
                'status': 'OK',
                'csv_exported': True,
                'error': None
            })
            results_dict[q_name] = df_result
            print(f"✔ [{q_name}] executed successfully ({row_count:,} rows) -> saved {csv_path.name}")
            
        except Exception as e:
            err_line = str(e).strip().splitlines()[0]
            status_records.append({
                'query': q_name,
                'rows': 0,
                'status': 'ERROR',
                'csv_exported': False,
                'error': err_line
            })
            print(f"✖ [{q_name}] failed: {err_line}")

# %% [markdown]
# ### 4. Query Execution Status Table

# %%
df_status = pd.DataFrame(status_records)
print("\n=== SQL Query Execution Status Table ===")
display(df_status[['query', 'rows', 'status', 'csv_exported', 'error']])

# Summary counts
successful_queries = sum(1 for s in status_records if s['status'] == 'OK')
total_queries = len(parsed_queries)
print(f"\nExecution Summary: {successful_queries}/{total_queries} queries completed successfully.")

# %% [markdown]
# ### 5. Preview Query Results (First 20 Rows of Each Result)

# %%
for q_name, df_res in results_dict.items():
    print(f"\n{'='*80}")
    print(f"Query: {q_name} | Total Rows: {len(df_res):,} | Output Preview (First 20 Rows):")
    print(f"{'='*80}")
    if len(df_res) == 0:
        print("[Notice: Query returned 0 rows. This is an expected finding for this filter criteria.]")
    else:
        display(df_res.head(20))

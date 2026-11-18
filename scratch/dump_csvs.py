import glob
from pathlib import Path
import pandas as pd

results_dir = Path('reports/sql_results')
for csv_file in sorted(results_dir.glob('*.csv')):
    df = pd.read_csv(csv_file)
    print(f"=== {csv_file.name} ===")
    print(df.to_string())
    print()

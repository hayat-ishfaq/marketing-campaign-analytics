import os
import math
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

# 1. Load campaigns
with engine.connect() as conn:
    df_camp = pd.read_sql(text('SELECT roas, channel_used, campaign_type, target_audience, customer_segment, location, language, duration_days FROM campaigns'), conn)

grand_mean = df_camp['roas'].mean()
ss_total = ((df_camp['roas'] - grand_mean) ** 2).sum()

dims = ['channel_used', 'campaign_type', 'target_audience', 'customer_segment', 'location', 'language', 'duration_days']
eta_results = []

for dim in dims:
    grouped = df_camp.groupby(dim)['roas']
    means = grouped.mean()
    counts = grouped.count()
    k = len(means)
    N = len(df_camp)
    ss_between = (counts * ((means - grand_mean) ** 2)).sum()
    ss_within = ss_total - ss_between
    eta_sq = ss_between / ss_total
    ms_between = ss_between / (k - 1)
    ms_within = ss_within / (N - k)
    f_stat = ms_between / ms_within
    eta_results.append({
        'dimension': dim,
        'k_groups': k,
        'f_statistic': f_stat,
        'ss_between': ss_between,
        'ss_total': ss_total,
        'eta_squared': eta_sq
    })

df_eta = pd.DataFrame(eta_results).sort_values('eta_squared', ascending=False)
print('=== ETA SQUARED BY DIMENSION ===')
print(df_eta.to_string(index=False))

# 2. Customers
with engine.connect() as conn:
    df_cust = pd.read_sql(text('SELECT age_group, income_group, total_spend, campaigns_accepted FROM customers'), conn)

def wilson_interval(successes, n, confidence=0.95):
    z = 1.959963984540054
    p = successes / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    spread = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return max(0.0, centre - spread), min(1.0, centre + spread)

def mean_ci(series, confidence=0.95):
    n = len(series)
    mean = series.mean()
    sem = series.std(ddof=1) / math.sqrt(n)
    z = 1.959963984540054
    return mean - z * sem, mean + z * sem

print('\n=== AGE GROUP STATS ===')
for name, group in df_cust.groupby('age_group'):
    n = len(group)
    mean_spend = group['total_spend'].mean()
    ci_spend = mean_ci(group['total_spend'])
    succ = (group['campaigns_accepted'] > 0).sum()
    pct_acc = succ / n * 100
    ci_acc = wilson_interval(succ, n)
    ci_acc_pct = (ci_acc[0] * 100, ci_acc[1] * 100)
    flag = ' (<100!)' if n < 100 else ''
    print(f"{name}{flag}: n={n}, mean_spend={mean_spend:.2f} (95% CI: [{ci_spend[0]:.2f}, {ci_spend[1]:.2f}]), accepted={pct_acc:.2f}% (Wilson 95% CI: [{ci_acc_pct[0]:.2f}%, {ci_acc_pct[1]:.2f}%])")

print('\n=== INCOME GROUP STATS ===')
for name, group in df_cust.groupby('income_group'):
    n = len(group)
    mean_spend = group['total_spend'].mean()
    ci_spend = mean_ci(group['total_spend'])
    succ = (group['campaigns_accepted'] > 0).sum()
    pct_acc = succ / n * 100
    ci_acc = wilson_interval(succ, n)
    ci_acc_pct = (ci_acc[0] * 100, ci_acc[1] * 100)
    flag = ' (<100!)' if n < 100 else ''
    print(f"{name}{flag}: n={n}, mean_spend={mean_spend:.2f} (95% CI: [{ci_spend[0]:.2f}, {ci_spend[1]:.2f}]), accepted={pct_acc:.2f}% (Wilson 95% CI: [{ci_acc_pct[0]:.2f}%, {ci_acc_pct[1]:.2f}%])")

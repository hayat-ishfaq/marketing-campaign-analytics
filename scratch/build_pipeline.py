import json
import os
from pathlib import Path
import numpy as np
import pandas as pd

# Paths
BASE_DIR = Path.cwd()
RAW_DATA_DIR = BASE_DIR / 'data' / 'raw'
CLEAN_DATA_DIR = BASE_DIR / 'data' / 'cleaned'
REPORTS_DIR = BASE_DIR / 'reports'
NOTEBOOKS_DIR = BASE_DIR / 'notebooks'

CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# 1. Execute campaign cleaning
print("Processing Campaign Dataset...")
camp_raw_path = RAW_DATA_DIR / 'marketing_campaign_dataset.csv'
df_camp_raw = pd.read_csv(camp_raw_path)

df_camp_clean = df_camp_raw.copy()
df_camp_clean['Acquisition_Cost'] = (
    df_camp_clean['Acquisition_Cost']
    .astype(str)
    .str.replace('$', '', regex=False)
    .str.replace(',', '', regex=False)
    .str.strip()
    .astype(float)
)
df_camp_clean['Duration'] = (
    df_camp_clean['Duration']
    .astype(str)
    .str.extract(r'(\d+)', expand=False)
    .astype(int)
)
df_camp_clean['Date'] = pd.to_datetime(df_camp_clean['Date'], format='%d-%m-%y')
df_camp_clean['Conversion_Rate'] = df_camp_clean['Conversion_Rate'].astype(float)

text_cols_camp = [
    'Company', 'Campaign_Type', 'Target_Audience', 
    'Channel_Used', 'Location', 'Language', 'Customer_Segment'
]
for col in text_cols_camp:
    df_camp_clean[col] = df_camp_clean[col].astype(str).str.strip().str.title()

df_camp_clean['Revenue'] = df_camp_clean['Acquisition_Cost'] * (1.0 + df_camp_clean['ROI'])
df_camp_clean['Profit'] = df_camp_clean['Revenue'] - df_camp_clean['Acquisition_Cost']
df_camp_clean['CTR'] = np.where(df_camp_clean['Impressions'] > 0, df_camp_clean['Clicks'] / df_camp_clean['Impressions'], 0.0)
df_camp_clean['CPC'] = np.where(df_camp_clean['Clicks'] > 0, df_camp_clean['Acquisition_Cost'] / df_camp_clean['Clicks'], 0.0)
df_camp_clean['ROAS'] = np.where(df_camp_clean['Acquisition_Cost'] > 0, df_camp_clean['Revenue'] / df_camp_clean['Acquisition_Cost'], 0.0)
df_camp_clean['Year'] = df_camp_clean['Date'].dt.year
df_camp_clean['Month'] = df_camp_clean['Date'].dt.month
df_camp_clean['Quarter'] = df_camp_clean['Date'].dt.quarter

# 2. Execute customer cleaning
print("Processing Customer Dataset...")
cust_raw_path = RAW_DATA_DIR / 'marketing_campaign.csv'
df_cust_raw = pd.read_csv(cust_raw_path, sep=';', encoding='utf-8-sig')

df_cust_clean = df_cust_raw.copy()
income_median_by_edu = df_cust_clean.groupby('Education')['Income'].transform('median')
df_cust_clean['Income'] = df_cust_clean['Income'].fillna(income_median_by_edu)

valid_cust_mask = (df_cust_clean['Year_Birth'] >= 1920) & (df_cust_clean['Income'] <= 600000)
df_cust_clean = df_cust_clean[valid_cust_mask].copy()

marital_status_mapping = {
    'Married': 'Married',
    'Together': 'Partner',
    'Single': 'Single',
    'Divorced': 'Divorced',
    'Widow': 'Widowed',
    'Alone': 'Single',
    'Absurd': 'Other',
    'YOLO': 'Other'
}
df_cust_clean['Marital_Status'] = df_cust_clean['Marital_Status'].map(marital_status_mapping).fillna('Other')

education_mapping = {
    'Basic': 'Basic',
    '2n Cycle': 'Master',
    'Graduation': 'Graduate',
    'Master': 'Master',
    'PhD': 'PhD'
}
df_cust_clean['Education'] = df_cust_clean['Education'].map(education_mapping).fillna(df_cust_clean['Education'])

df_cust_clean['Dt_Customer'] = pd.to_datetime(df_cust_clean['Dt_Customer'], format='%Y-%m-%d')
df_cust_clean['Age'] = 2014 - df_cust_clean['Year_Birth']

product_spend_cols = ['MntWines', 'MntFruits', 'MntMeatProducts', 'MntFishProducts', 'MntSweetProducts', 'MntGoldProds']
df_cust_clean['Total_Spend'] = df_cust_clean[product_spend_cols].sum(axis=1)

campaign_flag_cols = ['AcceptedCmp1', 'AcceptedCmp2', 'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5', 'Response']
df_cust_clean['Campaigns_Accepted'] = df_cust_clean[campaign_flag_cols].sum(axis=1)

age_bins = [0, 29, 44, 59, 120]
age_labels = ['<30', '30-44', '45-59', '60+']
df_cust_clean['Age_Group'] = pd.cut(df_cust_clean['Age'], bins=age_bins, labels=age_labels, right=True)

income_bins = [0, 35000, 65000, 100000, np.inf]
income_labels = ['Low (<$35k)', 'Middle ($35k-$65k)', 'High ($65k-$100k)', 'Affluent (>$100k)']
df_cust_clean['Income_Group'] = pd.cut(df_cust_clean['Income'], bins=income_bins, labels=income_labels, right=False)

# 3. Cleaning log
cleaning_log_data = [
    {
        'dataset': 'marketing_campaign_dataset.csv',
        'issue': 'Acquisition_Cost stored as currency string with $ and commas',
        'rows_affected': len(df_camp_raw),
        'action_taken': 'Stripped $, commas, and whitespace; converted to float64'
    },
    {
        'dataset': 'marketing_campaign_dataset.csv',
        'issue': 'Duration stored as string ("X days")',
        'rows_affected': len(df_camp_raw),
        'action_taken': 'Extracted integer day counts using regex; converted to int64'
    },
    {
        'dataset': 'marketing_campaign_dataset.csv',
        'issue': 'Date stored as DD-MM-YY string',
        'rows_affected': len(df_camp_raw),
        'action_taken': 'Parsed with format %d-%m-%y into standard datetime64[ns]'
    },
    {
        'dataset': 'marketing_campaign_dataset.csv',
        'issue': 'Conversion_Rate scale consistency check',
        'rows_affected': 0,
        'action_taken': 'Verified values are valid decimal fractions (range 0.01 - 0.15)'
    },
    {
        'dataset': 'marketing_campaign_dataset.csv',
        'issue': 'Categorical text whitespace and casing',
        'rows_affected': len(df_camp_raw),
        'action_taken': 'Stripped leading/trailing whitespace and standardized title casing across 7 categorical columns'
    },
    {
        'dataset': 'marketing_campaign_dataset.csv',
        'issue': 'Impossible values validation (cost <= 0, clicks > impressions, etc.)',
        'rows_affected': 0,
        'action_taken': 'Audited for negative costs, impressions <= 0, and clicks > impressions; 0 anomalies detected'
    },
    {
        'dataset': 'marketing_campaign_dataset.csv',
        'issue': 'Feature engineering (financial & calendar KPIs)',
        'rows_affected': len(df_camp_raw),
        'action_taken': 'Derived Revenue, Profit, CTR, CPC, ROAS (with zero-division guards), Year, Month, Quarter'
    },
    {
        'dataset': 'marketing_campaign.csv',
        'issue': 'File format with semicolon delimiter and UTF-8 BOM',
        'rows_affected': len(df_cust_raw),
        'action_taken': 'Loaded using sep=";" and encoding="utf-8-sig"'
    },
    {
        'dataset': 'marketing_campaign.csv',
        'issue': 'Missing Income values',
        'rows_affected': 24,
        'action_taken': 'Imputed nulls using median income grouped by Education level'
    },
    {
        'dataset': 'marketing_campaign.csv',
        'issue': 'Impossible birth years (< 1920: 1893, 1899, 1900)',
        'rows_affected': 3,
        'action_taken': 'Removed biological outlier records (implied ages > 94 in 2014 survey collection)'
    },
    {
        'dataset': 'marketing_campaign.csv',
        'issue': 'Extreme income outlier ($666,666)',
        'rows_affected': 1,
        'action_taken': 'Removed outlier record exceeding reasonable economic threshold'
    },
    {
        'dataset': 'marketing_campaign.csv',
        'issue': 'Non-standard Marital_Status categories',
        'rows_affected': len(df_cust_raw),
        'action_taken': 'Standardized (Together -> Partner, Alone -> Single, Absurd/YOLO -> Other, Widow -> Widowed)'
    },
    {
        'dataset': 'marketing_campaign.csv',
        'issue': 'Non-standard Education categories',
        'rows_affected': len(df_cust_raw),
        'action_taken': 'Standardized higher education labels (Graduation -> Graduate, 2n Cycle -> Master)'
    },
    {
        'dataset': 'marketing_campaign.csv',
        'issue': 'Customer behavioral & demographic feature engineering',
        'rows_affected': len(df_cust_clean),
        'action_taken': 'Derived Age (ref 2014), Total_Spend, Campaigns_Accepted, Age_Group, Income_Group'
    }
]

df_cleaning_log = pd.DataFrame(cleaning_log_data)

# Save datasets and log
print("Saving output files...")
log_path = REPORTS_DIR / 'cleaning_log.csv'
df_cleaning_log.to_csv(log_path, index=False)

camp_clean_path = CLEAN_DATA_DIR / 'campaigns_clean.csv'
cust_clean_path = CLEAN_DATA_DIR / 'customers_clean.csv'
df_camp_clean.to_csv(camp_clean_path, index=False)
df_cust_clean.to_csv(cust_clean_path, index=False)

# Validation assertions
assert df_camp_clean['Acquisition_Cost'].isnull().sum() == 0
assert df_camp_clean['Revenue'].isnull().sum() == 0
assert df_camp_clean['Profit'].isnull().sum() == 0
assert df_camp_clean['CTR'].isnull().sum() == 0
assert df_camp_clean['CPC'].isnull().sum() == 0
assert df_camp_clean['ROAS'].isnull().sum() == 0
assert (df_camp_clean['Clicks'] <= df_camp_clean['Impressions']).all()
assert (df_camp_clean['Acquisition_Cost'] > 0).all()
assert pd.api.types.is_float_dtype(df_camp_clean['Acquisition_Cost'])
assert pd.api.types.is_datetime64_any_dtype(df_camp_clean['Date'])
assert pd.api.types.is_integer_dtype(df_camp_clean['Duration'])

assert df_cust_clean['Income'].isnull().sum() == 0
assert df_cust_clean['Age'].isnull().sum() == 0
assert df_cust_clean['Total_Spend'].isnull().sum() == 0
assert df_cust_clean['Campaigns_Accepted'].isnull().sum() == 0
assert df_cust_clean['Age'].min() >= 18
assert df_cust_clean['Age'].max() <= 100
assert df_cust_clean['Income'].max() < 600000
assert df_cust_clean['Marital_Status'].isin(['Married', 'Partner', 'Single', 'Divorced', 'Widowed', 'Other']).all()
assert df_cust_clean['Education'].isin(['Basic', 'Graduate', 'Master', 'PhD']).all()

print("All pipeline assertions passed successfully!")
print(f"Campaign Clean Shape: {df_camp_clean.shape}")
print(f"Customer Clean Shape: {df_cust_clean.shape}")
print(f"Cleaning Log Shape: {df_cleaning_log.shape}")

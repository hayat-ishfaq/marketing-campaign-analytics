# -*- coding: utf-8 -*-

# %% [markdown]
# # Marketing Campaign Performance Analytics
# ## Notebook 01: Data Cleaning, Auditing & Feature Engineering
# 
# ### Business Context
# A digital marketing agency spends substantial budgets across multiple advertising channels (Google Ads, YouTube, Facebook, Instagram, Email, Website) but lacks a unified, data-driven understanding of campaign returns and customer behavior. 
# 
# The analytical objective of this portfolio project is to evaluate:
# - **Return on Investment (ROI)** and **Return on Ad Spend (ROAS)**
# - **Customer Acquisition Cost (CAC)** and **Cost Per Click (CPC)**
# - **Click-Through Rate (CTR)** and **Conversion Rates**
# - **Channel profitability** and **Customer segment economics**
# 
# > **Architecture Notice:** This project uses two raw datasets in `data/raw/`:
# > 1. `marketing_campaign_dataset.csv` (Campaign performance metrics, ~200k rows)
# > 2. `marketing_campaign.csv` (Customer demographic & personality profiles, ~2.2k rows)
# >
# > **These two datasets have NO shared key.** They represent two distinct analytical perspectives (macro channel performance vs. micro customer personality profiles). They must remain distinct tables and are never joined.

# %% [markdown]
# ### 0. Environment Setup and Project Paths
# We configure standard data manipulation packages (`pandas`, `numpy`, `matplotlib`, `seaborn`) and establish robust relative paths using Python's `pathlib.Path` so this notebook runs portably from any directory.

# %%
import os
import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure pandas formatting
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

# Relative directory paths
BASE_DIR = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()
RAW_DATA_DIR = BASE_DIR / 'data' / 'raw'
CLEAN_DATA_DIR = BASE_DIR / 'data' / 'cleaned'
REPORTS_DIR = BASE_DIR / 'reports'

# Ensure output directories exist
CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Safe display function for both script and notebook environments
try:
    from IPython.display import display
except ImportError:
    display = print

print(f"Base Project Directory : {BASE_DIR.resolve()}")
print(f"Raw Data Directory     : {RAW_DATA_DIR.resolve()}")
print(f"Cleaned Data Directory : {CLEAN_DATA_DIR.resolve()}")
print(f"Reports Directory      : {REPORTS_DIR.resolve()}")

# %% [markdown]
# ---
# ## Part A: Data Inspection (Pre-Cleaning Audit)
# 
# **Goal:** Before mutating any raw data, inspect each dataset to understand its genuine structure, data types, distributions, anomalies, missing fields, and duplicates.
# We do not guess schema properties — we let the data speak directly.

# %% [markdown]
# ### A.1 Inspecting Dataset 1: Campaign Performance Data (`marketing_campaign_dataset.csv`)
# We load the file and print:
# - Table dimensions (`shape`) and column data types (`dtypes`)
# - Sample records (`head`)
# - Missing value counts per column
# - Duplicate rows and duplicate `Campaign_ID` count
# - Descriptive statistics (`describe`) for numeric features
# - Frequency counts for all categorical features

# %%
campaign_raw_path = RAW_DATA_DIR / 'marketing_campaign_dataset.csv'
print(f"Reading raw campaign dataset from: {campaign_raw_path.name}...")
df_camp_raw = pd.read_csv(campaign_raw_path)

print(f"\n1. Dataset Dimensions: {df_camp_raw.shape[0]:,} rows x {df_camp_raw.shape[1]} columns")

print("\n2. Data Types:")
print(df_camp_raw.dtypes)

print("\n3. First 5 Rows:")
display(df_camp_raw.head())

print("\n4. Missing Values Per Column:")
null_camp = df_camp_raw.isnull().sum()
print(null_camp if null_camp.sum() > 0 else "Zero missing values detected across all columns.")

print(f"\n5. Duplicate Entire Rows: {df_camp_raw.duplicated().sum()}")
print(f"   Duplicate Campaign_IDs: {df_camp_raw['Campaign_ID'].duplicated().sum()}")

print("\n6. Summary Statistics (Numeric Columns):")
display(df_camp_raw.describe())

print("\n7. Categorical Columns Value Counts:")
camp_cat_cols = df_camp_raw.select_dtypes(include=['object', 'string']).columns
for col in camp_cat_cols:
    print(f"\n--- Value Counts for '{col}' (Top 10) ---")
    print(df_camp_raw[col].value_counts().head(10))

# %% [markdown]
# ### A.2 Inspecting Dataset 2: Customer Personality Data (`marketing_campaign.csv`)
# Notice that upon examining the raw text of `marketing_campaign.csv`, the file is **semicolon-separated (`;`)** and carries a UTF-8 Byte Order Mark (BOM). We read it using `sep=';'` and `encoding='utf-8-sig'` to parse all 29 columns accurately.

# %%
customer_raw_path = RAW_DATA_DIR / 'marketing_campaign.csv'
print(f"Reading raw customer dataset from: {customer_raw_path.name}...")
df_cust_raw = pd.read_csv(customer_raw_path, sep=';', encoding='utf-8-sig')

print(f"\n1. Dataset Dimensions: {df_cust_raw.shape[0]:,} rows x {df_cust_raw.shape[1]} columns")

print("\n2. Data Types:")
print(df_cust_raw.dtypes)

print("\n3. First 5 Rows:")
display(df_cust_raw.head())

print("\n4. Missing Values Per Column:")
null_cust = df_cust_raw.isnull().sum()
print(null_cust[null_cust > 0])

print(f"\n5. Duplicate Entire Rows: {df_cust_raw.duplicated().sum()}")
print(f"   Duplicate Customer IDs: {df_cust_raw['ID'].duplicated().sum()}")

print("\n6. Summary Statistics (Numeric Columns):")
display(df_cust_raw.describe())

print("\n7. Categorical Columns Value Counts:")
cust_cat_cols = df_cust_raw.select_dtypes(include=['object', 'string']).columns
for col in cust_cat_cols:
    print(f"\n--- Value Counts for '{col}' ---")
    print(df_cust_raw[col].value_counts(dropna=False))

# %% [markdown]
# ### A.3 Markdown Summary: Raw Data Quality Findings
# 
# #### Campaign Performance Dataset (`marketing_campaign_dataset.csv` - 200,000 records)
# 1. **`Acquisition_Cost` format issue:** Stored as string containing dollar signs (`$`), thousand separators (`,`), and trailing whitespace (e.g., `'$16,174.00 '`). Needs stripping and parsing to `float64`.
# 2. **`Duration` format issue:** Stored as string text with unit suffix (e.g., `'30 days'`). Needs regex extraction to integer days.
# 3. **`Date` format issue:** Stored as string in `DD-MM-YY` format (`01-01-21` through `31-12-21`). Must be parsed into standard datetime timestamps with day-first ordering.
# 4. **`Conversion_Rate` verification:** Values range from `0.01` to `0.15` (mean ~0.08). This represents a **decimal fraction** (1% to 15%), not a whole percentage number.
# 5. **Impossible values validation:**
#    - `Clicks` range from 100 to 1,000; `Impressions` range from 1,000 to 10,000. `Clicks <= Impressions` holds true across 100% of rows.
#    - `Acquisition_Cost` and `ROI` are strictly positive (zero negative cost rows).
# 6. **Missing / Duplicates:** Zero missing values and zero duplicate rows.
# 
# #### Customer Personality Dataset (`marketing_campaign.csv` - 2,240 records)
# 1. **File format:** Semicolon delimiter (`;`) with UTF-8 BOM encoding (`utf-8-sig`).
# 2. **Missing data:** `Income` is missing in exactly **24 rows** (~1.07%). All other 28 columns have zero nulls.
# 3. **Biological age outliers:** `Year_Birth` contains records dating back to `1893`, `1899`, and `1900`. For a dataset collected around 2014, this represents ages exceeding 114–121 years. These 3 rows are clear data entry errors.
# 4. **Extreme income outlier:** The maximum income is `$666,666`, whereas the 75th percentile is `$68,522` and the second highest is `$162,397`. This single anomalous entry will heavily skew statistical averages and regression models.
# 5. **Categorical inconsistencies:**
#    - `Marital_Status`: Non-standard values include `'Together'` (580), `'Alone'` (3), `'Absurd'` (2), and `'YOLO'` (2).
#    - `Education`: European university terminology (`'Graduation'` = Bachelor's degree, `'2n Cycle'` = Master's level).
# 6. **Zero-variance columns:** `Z_CostContact` (always 3) and `Z_Revenue` (always 11) have standard deviation 0.

# %% [markdown]
# ---
# ## Part B: Clean the Campaign Dataset
# 
# In this section, we apply best-practice transformations without mutating slices or raw files:
# 1. **Strip currency symbols and convert `Acquisition_Cost` to float.**
# 2. **Convert `Duration` to integer days.**
# 3. **Parse `Date` as datetime with `%d-%m-%y`.**
# 4. **Verify and cast `Conversion_Rate` as float decimal fraction.**
# 5. **Standardize categorical text (strip whitespace, ensure proper title casing).**
# 6. **Audit and flag impossible values (cost $\le 0$, clicks > impressions, negative metrics).**
# 7. **Engineer derived metrics:**
#    - $\text{Revenue} = \text{Acquisition Cost} \times (1 + \text{ROI})$
#    - $\text{Profit} = \text{Revenue} - \text{Acquisition Cost}$
#    - $\text{CTR} = \frac{\text{Clicks}}{\text{Impressions}}$ (guarded against division by zero)
#    - $\text{CPC} = \frac{\text{Acquisition Cost}}{\text{Clicks}}$ (guarded against division by zero)
#    - $\text{ROAS} = \frac{\text{Revenue}}{\text{Acquisition Cost}}$ (guarded against division by zero)
#    - Calendar attributes: `Year`, `Month`, `Quarter`

# %%
# Make explicit working copy to avoid SettingWithCopyWarning
df_camp_clean = df_camp_raw.copy()

# 1. Clean Acquisition_Cost
df_camp_clean['Acquisition_Cost'] = (
    df_camp_clean['Acquisition_Cost']
    .astype(str)
    .str.replace('$', '', regex=False)
    .str.replace(',', '', regex=False)
    .str.strip()
    .astype(float)
)

# 2. Convert Duration to integer number of days
df_camp_clean['Duration'] = (
    df_camp_clean['Duration']
    .astype(str)
    .str.extract(r'(\d+)', expand=False)
    .astype(int)
)

# 3. Parse Date to datetime
df_camp_clean['Date'] = pd.to_datetime(df_camp_clean['Date'], format='%d-%m-%y')

# 4. Confirm Conversion_Rate is a consistent decimal fraction
df_camp_clean['Conversion_Rate'] = df_camp_clean['Conversion_Rate'].astype(float)

# 5. Standardize categorical text fields
camp_text_fields = [
    'Company', 'Campaign_Type', 'Target_Audience', 
    'Channel_Used', 'Location', 'Language', 'Customer_Segment'
]
for col in camp_text_fields:
    df_camp_clean[col] = df_camp_clean[col].astype(str).str.strip().str.title()

# 6. Audit impossible values
impossible_cost = (df_camp_clean['Acquisition_Cost'] <= 0).sum()
impossible_clicks_imp = (df_camp_clean['Clicks'] > df_camp_clean['Impressions']).sum()
impossible_clicks_neg = (df_camp_clean['Clicks'] < 0).sum()
impossible_imp_neg = (df_camp_clean['Impressions'] <= 0).sum()
impossible_roi = (df_camp_clean['ROI'] < 0).sum()

print("=== Campaign Impossible Value Audit ===")
print(f"Acquisition_Cost <= $0 : {impossible_cost} rows affected")
print(f"Clicks > Impressions   : {impossible_clicks_imp} rows affected")
print(f"Negative Clicks        : {impossible_clicks_neg} rows affected")
print(f"Impressions <= 0       : {impossible_imp_neg} rows affected")
print(f"Negative ROI           : {impossible_roi} rows affected")

# 7. Derived Features (with divide-by-zero guards)
# Revenue = Acquisition_Cost * (1 + ROI)
df_camp_clean['Revenue'] = df_camp_clean['Acquisition_Cost'] * (1.0 + df_camp_clean['ROI'])

# Profit = Revenue - Acquisition_Cost
df_camp_clean['Profit'] = df_camp_clean['Revenue'] - df_camp_clean['Acquisition_Cost']

# CTR = Clicks / Impressions (guarded)
df_camp_clean['CTR'] = np.where(
    df_camp_clean['Impressions'] > 0, 
    df_camp_clean['Clicks'] / df_camp_clean['Impressions'], 
    0.0
)

# CPC = Acquisition_Cost / Clicks (guarded)
df_camp_clean['CPC'] = np.where(
    df_camp_clean['Clicks'] > 0, 
    df_camp_clean['Acquisition_Cost'] / df_camp_clean['Clicks'], 
    0.0
)

# ROAS = Revenue / Acquisition_Cost (guarded)
df_camp_clean['ROAS'] = np.where(
    df_camp_clean['Acquisition_Cost'] > 0, 
    df_camp_clean['Revenue'] / df_camp_clean['Acquisition_Cost'], 
    0.0
)

# Calendar Features
df_camp_clean['Year'] = df_camp_clean['Date'].dt.year
df_camp_clean['Month'] = df_camp_clean['Date'].dt.month
df_camp_clean['Quarter'] = df_camp_clean['Date'].dt.quarter

print(f"\nCleaned Campaign Dataset Dimensions: {df_camp_clean.shape[0]:,} rows x {df_camp_clean.shape[1]} columns")
display(df_camp_clean[['Campaign_ID', 'Company', 'Channel_Used', 'Acquisition_Cost', 'Revenue', 'Profit', 'CTR', 'CPC', 'ROAS', 'Date']].head())

# %% [markdown]
# ---
# ## Part C: Clean the Customer Dataset
# 
# In this section, we clean and enrich the customer dataset `marketing_campaign.csv`:
# 1. **Impute Missing Income:** 24 missing values are imputed using the **median income grouped by education tier**, preserving the observed socio-economic distribution.
# 2. **Handle Extreme Outliers:**
#    - Filter out birth years prior to 1920 (removes 3 records: birth years 1893, 1899, 1900, representing biologically impossible ages > 94 in the 2014 survey window).
#    - Filter out `Income > $600,000` (removes 1 record with `$666,666`, which is a recognized erroneous outlier).
# 3. **Standardize Categories:**
#    - `Marital_Status`: Map `'Together'` $\rightarrow$ `'Partner'`, `'Alone'` $\rightarrow$ `'Single'`, `'Widow'` $\rightarrow$ `'Widowed'`, `'Absurd'` / `'YOLO'` $\rightarrow$ `'Other'`.
#    - `Education`: Map `'Graduation'` $\rightarrow$ `'Graduate'`, `'2n Cycle'` $\rightarrow$ `'Master'`.
# 4. **Derived Customer Features:**
#    - `Age`: Calculated as `2014 - Year_Birth` (2014 represents the dataset survey collection benchmark).
#    - `Total_Spend`: Sum of all 6 product category expenditures (`MntWines`, `MntFruits`, `MntMeatProducts`, `MntFishProducts`, `MntSweetProducts`, `MntGoldProds`).
#    - `Campaigns_Accepted`: Sum of binary response flags across marketing campaigns 1 through 5, plus the latest promotional campaign (`Response`).
#    - `Age_Group`: Demographic cohorts (`'<30'`, `'30-44'`, `'45-59'`, `'60+'`).
#    - `Income_Group`: Income tiers (`'Low (<$35k)'`, `'Middle ($35k-$65k)'`, `'High ($65k-$100k)'`, `'Affluent (>$100k)'`).

# %%
df_cust_clean = df_cust_raw.copy()

# 1. Impute missing Income using median by Education
income_median_by_edu = df_cust_clean.groupby('Education')['Income'].transform('median')
df_cust_clean['Income'] = df_cust_clean['Income'].fillna(income_median_by_edu)

# 2. Filter biological age outliers and extreme income outlier
initial_count = len(df_cust_clean)
valid_cust_mask = (df_cust_clean['Year_Birth'] >= 1920) & (df_cust_clean['Income'] <= 600000)
df_cust_clean = df_cust_clean[valid_cust_mask].copy()
dropped_count = initial_count - len(df_cust_clean)
print(f"Removed {dropped_count} outlier records (3 implausible birth years < 1920, 1 extreme income of $666,666).")

# 3. Standardize Marital_Status
marital_map = {
    'Married': 'Married',
    'Together': 'Partner',
    'Single': 'Single',
    'Divorced': 'Divorced',
    'Widow': 'Widowed',
    'Alone': 'Single',
    'Absurd': 'Other',
    'YOLO': 'Other'
}
df_cust_clean['Marital_Status'] = df_cust_clean['Marital_Status'].map(marital_map).fillna('Other')

# Standardize Education
edu_map = {
    'Basic': 'Basic',
    '2n Cycle': 'Master',
    'Graduation': 'Graduate',
    'Master': 'Master',
    'PhD': 'PhD'
}
df_cust_clean['Education'] = df_cust_clean['Education'].map(edu_map).fillna(df_cust_clean['Education'])

# Parse Dt_Customer to datetime
df_cust_clean['Dt_Customer'] = pd.to_datetime(df_cust_clean['Dt_Customer'], format='%Y-%m-%d')

# 4. Derived Columns
# Reference year 2014 reflects the survey collection window (2012 - mid 2014)
df_cust_clean['Age'] = 2014 - df_cust_clean['Year_Birth']

# Total product spend
spend_fields = [
    'MntWines', 'MntFruits', 'MntMeatProducts', 
    'MntFishProducts', 'MntSweetProducts', 'MntGoldProds'
]
df_cust_clean['Total_Spend'] = df_cust_clean[spend_fields].sum(axis=1)

# Total campaigns accepted
cmp_flags = ['AcceptedCmp1', 'AcceptedCmp2', 'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5', 'Response']
df_cust_clean['Campaigns_Accepted'] = df_cust_clean[cmp_flags].sum(axis=1)

# Demographic Age Groups
age_bins = [0, 29, 44, 59, 120]
age_labels = ['<30', '30-44', '45-59', '60+']
df_cust_clean['Age_Group'] = pd.cut(df_cust_clean['Age'], bins=age_bins, labels=age_labels, right=True)

# Socioeconomic Income Groups
inc_bins = [0, 35000, 65000, 100000, np.inf]
inc_labels = ['Low (<$35k)', 'Middle ($35k-$65k)', 'High ($65k-$100k)', 'Affluent (>$100k)']
df_cust_clean['Income_Group'] = pd.cut(df_cust_clean['Income'], bins=inc_bins, labels=inc_labels, right=False)

print(f"Cleaned Customer Dataset Dimensions: {df_cust_clean.shape[0]:,} rows x {df_cust_clean.shape[1]} columns")
display(df_cust_clean[['ID', 'Age', 'Age_Group', 'Education', 'Marital_Status', 'Income', 'Income_Group', 'Total_Spend', 'Campaigns_Accepted']].head())

# %% [markdown]
# ---
# ## Part D: Cleaning Log, Exports, and Pipeline Validation
# 
# In this final stage, we:
# 1. Compile an audit log documenting all detected issues and remediation actions.
# 2. Export `reports/cleaning_log.csv`.
# 3. Export cleaned datasets to `data/cleaned/campaigns_clean.csv` and `data/cleaned/customers_clean.csv`.
# 4. Execute automated assertions to ensure production-grade data integrity.

# %%
# 1. Construct the Cleaning Audit Log
cleaning_log_entries = [
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
        'issue': 'Impossible values validation (cost <= 0, clicks > impressions)',
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

df_cleaning_log = pd.DataFrame(cleaning_log_entries)
display(df_cleaning_log)

# Save Cleaning Log
cleaning_log_path = REPORTS_DIR / 'cleaning_log.csv'
df_cleaning_log.to_csv(cleaning_log_path, index=False)
print(f"\nSaved Cleaning Log to : {cleaning_log_path.resolve()}")

# Save Cleaned Datasets
camp_clean_path = CLEAN_DATA_DIR / 'campaigns_clean.csv'
cust_clean_path = CLEAN_DATA_DIR / 'customers_clean.csv'

df_camp_clean.to_csv(camp_clean_path, index=False)
df_cust_clean.to_csv(cust_clean_path, index=False)

print(f"Saved Cleaned Campaigns: {camp_clean_path.resolve()}")
print(f"Saved Cleaned Customers: {cust_clean_path.resolve()}")

# %% [markdown]
# ### D.2 Pipeline Validation Block
# Automated assertion suite checking column completeness, data types, valid ranges, and before/after row count deltas.

# %%
# --- Campaign Dataset Assertions ---
print("Running Campaign Data Validations...")
assert df_camp_clean['Acquisition_Cost'].isnull().sum() == 0, "Null values found in Acquisition_Cost!"
assert df_camp_clean['Revenue'].isnull().sum() == 0, "Null values found in Revenue!"
assert df_camp_clean['Profit'].isnull().sum() == 0, "Null values found in Profit!"
assert df_camp_clean['CTR'].isnull().sum() == 0, "Null values found in CTR!"
assert df_camp_clean['CPC'].isnull().sum() == 0, "Null values found in CPC!"
assert df_camp_clean['ROAS'].isnull().sum() == 0, "Null values found in ROAS!"
assert (df_camp_clean['Clicks'] <= df_camp_clean['Impressions']).all(), "Found Clicks > Impressions!"
assert (df_camp_clean['Acquisition_Cost'] > 0).all(), "Found non-positive Acquisition_Cost!"
assert pd.api.types.is_float_dtype(df_camp_clean['Acquisition_Cost']), "Acquisition_Cost is not float!"
assert pd.api.types.is_datetime64_any_dtype(df_camp_clean['Date']), "Date is not datetime64!"
assert pd.api.types.is_integer_dtype(df_camp_clean['Duration']), "Duration is not integer!"
print("✔ All Campaign assertions PASSED.")

# --- Customer Dataset Assertions ---
print("\nRunning Customer Data Validations...")
assert df_cust_clean['Income'].isnull().sum() == 0, "Null values found in Income!"
assert df_cust_clean['Age'].isnull().sum() == 0, "Null values found in Age!"
assert df_cust_clean['Total_Spend'].isnull().sum() == 0, "Null values found in Total_Spend!"
assert df_cust_clean['Campaigns_Accepted'].isnull().sum() == 0, "Null values found in Campaigns_Accepted!"
assert df_cust_clean['Age'].min() >= 18, f"Implausible minor age found: {df_cust_clean['Age'].min()}"
assert df_cust_clean['Age'].max() <= 100, f"Implausible senior age found: {df_cust_clean['Age'].max()}"
assert df_cust_clean['Income'].max() < 600000, f"Extreme income outlier not removed: {df_cust_clean['Income'].max()}"
assert df_cust_clean['Marital_Status'].isin(['Married', 'Partner', 'Single', 'Divorced', 'Widowed', 'Other']).all(), "Unstandardized marital status found!"
assert df_cust_clean['Education'].isin(['Basic', 'Graduate', 'Master', 'PhD']).all(), "Unstandardized education found!"
print("✔ All Customer assertions PASSED.")

# --- Row and Column Reconciliation ---
print("\n=== Pipeline Execution Reconciliation ===")
print(f"Campaign Rows     : {len(df_camp_raw):,} raw -> {len(df_camp_clean):,} clean (100.0% retention)")
print(f"Customer Rows     : {len(df_cust_raw):,} raw -> {len(df_cust_clean):,} clean ({len(df_cust_clean)/len(df_cust_raw):.2%} retention; 4 outlier rows dropped)")
print(f"Campaign Features : {df_camp_raw.shape[1]} raw -> {df_camp_clean.shape[1]} clean (+8 derived features)")
print(f"Customer Features : {df_cust_raw.shape[1]} raw -> {df_cust_clean.shape[1]} clean (+5 derived features)")

# %% [markdown]
# ---
# ## Summary of Biggest Data Quality Issues Found
# 
# 1. **Unformatted Currency and String Durations:** 100% of rows in `marketing_campaign_dataset.csv` stored `Acquisition_Cost` as uncast strings with currency symbols and trailing whitespace (`'$16,174.00 '`) and `Duration` with `' days'` units.
# 2. **Non-Standard CSV Delimiter and UTF-8 BOM:** `marketing_campaign.csv` used semicolon (`;`) separators with a Byte Order Mark rather than standard comma/tab formats, requiring explicit encoding and parsing handling.
# 3. **Missing Demographic Income:** `Income` contained 24 missing values (~1.07%), successfully imputed using education-cohort medians to preserve economic variance.
# 4. **Implausible Biological Ages:** 3 customer records had birth years from 1893 to 1900 (ages > 114–121 years), filtered as clear data entry errors.
# 5. **Severe Economic Outlier:** A single customer record reported `$666,666` in annual income (over 4x the 99th percentile), filtered out to prevent statistical distortion in downstream marketing analyses.

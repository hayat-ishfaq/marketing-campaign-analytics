# Marketing Campaign Analytics

A comprehensive end-to-end analytics project for analyzing marketing campaign performance, customer behavior, and ROI.

## Project Structure

```text
marketing-campaign-analytics/
├── data/
│   ├── raw/             # Original data files (immutable, never edited)
│   └── cleaned/         # Cleaned, transformed datasets ready for analysis
├── notebooks/           # Jupyter notebooks for data processing and exploration
│   ├── 01_cleaning.ipynb
│   └── 02_eda.ipynb
├── sql/                 # SQL scripts for database schema and analytical queries
│   ├── schema.sql
│   └── analysis_queries.sql
├── dashboard/           # Power BI (.pbix) reports and presentation screenshots
│   └── screenshots/
├── reports/             # Business recommendations and final reports (PDF)
└── README.md
```

## Setup & Getting Started

1. **Raw Data**: Place original, unedited campaign data files in `data/raw/`.
2. **Data Cleaning**: Run `notebooks/01_cleaning.ipynb` to clean and output processed data into `data/cleaned/`.
3. **Exploratory Data Analysis**: Explore insights and trends with `notebooks/02_eda.ipynb`.
4. **Database & SQL**: Execute `sql/schema.sql` to set up tables and run `sql/analysis_queries.sql` for key metric extractions.
5. **Dashboard & Reporting**: Open the Power BI dashboard in `dashboard/` and find business summaries in `reports/`.

# Marketing Campaign Performance Analytics

An end-to-end analytics project that asks a marketing agency's core question: **which advertising channels and campaigns actually give the best return?**

I cleaned and analysed 200,000 campaigns across six channels, plus a separate customer dataset, using **Python, SQL (PostgreSQL) and Power BI**, and turned the results into a business recommendations report and an interactive dashboard.

**Headline result:** channel, audience and campaign type barely affect ROAS in this data (channels differ by under 1%), so the recommendation is *not* to reallocate budget between them. Instead, test income-based audience targeting, and fix the measurement gaps before making larger budget decisions.

| | |
|---|---|
| Business report | [reports/business_recommendations_report.pdf](reports/business_recommendations_report.pdf) |
| Dashboard (Power BI project) | [dashboard/campaign_dashboard.pbip](dashboard/) |
| SQL analysis | [sql/02_analysis_queries.sql](sql/02_analysis_queries.sql) |
| Findings with exact figures | [reports/findings_log.md](reports/findings_log.md) |

---

## Business problem

A marketing agency spends across several channels but cannot tell which campaigns return the most. This project measures:

- Campaign ROI and ROAS
- Customer acquisition cost (CAC)
- Conversion rates
- Revenue and profit by channel
- Campaign profitability
- Customer demographics and behaviour

## Key findings

1. **Channels perform almost identically.** ROAS ranges only from 5.99 (Instagram) to 6.03 (Facebook), a 0.67% spread. Channel explains about 0.004% of the variation in ROAS, and none of the seven campaign attributes tested (channel, campaign type, audience, customer segment, location, language, duration) explains more than 0.006%.
2. **Cost efficiency is equally flat.** Estimated CAC runs from $281.92 (Website) to $285.22 (Google Ads), a 1.2% spread. No channel's share of revenue differs from its share of budget by more than 0.06 percentage points.
3. **Income is the strongest differentiator among customers.** Average spend per customer rises step by step with income: about $80 (under $35k), $437 ($35k to $65k) and $1,295 ($65k to $100k). The share accepting at least one campaign rises from 14.2% to 22.9% to 44.4%. High-income customers spend about 16x more and respond about 3x as often as low-income customers.
4. **The age pattern is mostly an income effect.** Older customers spend and respond the most overall, but within the high-income band there is no clear age pattern.

### Recommendations

1. Hold channel and campaign-type budgets steady. The data gives no reliable basis for moving money between them.
2. Record the variables that could explain campaign performance (creative, targeting, bidding, timing, landing page).
3. Run a controlled test of income-based targeting before shifting spend.
4. Do not target on age alone.
5. Fix measurement first: record real spend and revenue, link campaigns to customers, and keep holdout groups.

## Dashboard

An interactive Power BI dashboard connected to the PostgreSQL database.

| Overview | Campaigns |
|---|---|
| ![Overview](dashboard/screenshots/page1_overview.png) | ![Campaigns](dashboard/screenshots/page2_campaigns.png) |

| Rankings | Customers |
|---|---|
| ![Rankings](dashboard/screenshots/page3_rankings.png) | ![Customers](dashboard/screenshots/page4_customers.png) |

The fifth page, **About the data**, lists sources, definitions and limits. Chart titles are generated from DAX measures, so the headline numbers always match the visuals beneath them.

## Deliverables

| # | Deliverable | Where |
|---|---|---|
| 1 | Cleaned datasets and cleaning log | `data/cleaned/`, `reports/cleaning_log.csv` |
| 2 | Python EDA notebook and figures | `notebooks/02_eda.py`, `reports/figures/` |
| 3 | SQL analysis queries and results | `sql/`, `reports/sql_results/` |
| 4 | Interactive Power BI dashboard | `dashboard/` |
| 5 | Business recommendations report | `reports/business_recommendations_report.pdf` |

## Tech stack

- **Python:** Pandas, NumPy, Matplotlib, Seaborn, SciPy, statsmodels, SQLAlchemy
- **Database:** PostgreSQL (CTEs, window functions, `DATE_TRUNC`, `LAG`, `RANK`)
- **BI:** Power BI Desktop (DAX measures, calendar table, PBIP project format)

## Data

| Dataset | Source | Size |
|---|---|---|
| Campaigns | [Marketing Campaign Performance Dataset](https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset) (Kaggle) | 200,000 campaigns, 6 channels, campaign dates in 2021 |
| Customers | [Customer Personality Analysis](https://www.kaggle.com/datasets/rodsaldanha/arketing-campaign) (Kaggle) | 2,236 customers |

The datasets belong to their Kaggle authors; see their pages for licences. The two datasets **share no key and are never joined**. They are analysed separately.

## Method

1. **Clean (Python):** fix types (money stored as text, durations, dates), standardise categories, check for impossible values, derive revenue, profit, CTR, CPC, ROAS, age and spend totals, and log every cleaning decision.
2. **Load (PostgreSQL):** load the cleaned data into `campaigns` and `customers` tables.
3. **Analyse (SQL):** 16 named queries covering channel scorecards, CAC, conversion, top and bottom campaigns, monthly trends and month-over-month growth, quarterly channel ranking, budget share vs revenue share, and customer segments.
4. **Check (Python):** one-way ANOVA and eta squared for every campaign attribute, plus confidence intervals for customer groups, so that small differences are not over-read.
5. **Visualise (Power BI):** a five-page dashboard built on a semantic model with a calendar table and a library of DAX measures.
6. **Report:** a business recommendations report written for a non-technical marketing manager.

Ratios (ROAS, ROI, CAC) are calculated from totals (`SUM(revenue) / SUM(spend)`) and not by averaging campaign ratios, so large campaigns carry their proper weight.

### Definitions

- **ROAS** = revenue / spend
- **ROI** = (revenue - spend) / spend
- **Estimated CAC** = spend / (clicks x conversion rate)

## Repository structure

```
marketing-campaign-analytics/
├── data/
│   ├── raw/                 # original Kaggle files (download them yourself)
│   └── cleaned/             # cleaned campaigns and customers CSVs
├── notebooks/
│   ├── 01_cleaning          # inspection and cleaning
│   ├── 02_eda               # exploratory analysis and figures
│   ├── 03_export_sql_results.py
│   └── 04_statistical_checks.py
├── sql/
│   ├── 01_schema.sql
│   └── 02_analysis_queries.sql
├── dashboard/
│   ├── campaign_dashboard.pbip   # Power BI project (.Report and .SemanticModel folders)
│   ├── assets/              # theme, DAX measures, layout mockups
│   └── screenshots/
├── reports/
│   ├── business_recommendations_report.pdf
│   ├── findings_log.md
│   ├── cleaning_log.csv
│   ├── figures/
│   ├── sql_results/
│   └── stat_checks/
└── README.md
```

## How to reproduce

1. **Clone the repo** and create a Python environment:
   ```bash
   pip install pandas numpy matplotlib seaborn scipy statsmodels sqlalchemy psycopg2-binary python-dotenv
   ```
2. **Download both datasets** from the Kaggle links above into `data/raw/`.
3. **Clean the data** by running the cleaning notebook in `notebooks/`. It writes the cleaned CSVs to `data/cleaned/`.
4. **Set up PostgreSQL:** create a database named `marketing_analytics`, run `sql/01_schema.sql`, and add a `.env` file in the repo root (never commit it):
   ```
   DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@localhost:5432/marketing_analytics
   ```
   Then load the cleaned CSVs into the `campaigns` and `customers` tables.
5. **Run the analysis:** execute `sql/02_analysis_queries.sql` in pgAdmin or `psql`, then run `notebooks/03_export_sql_results.py` to save each result as a CSV in `reports/sql_results/`. Run `notebooks/02_eda.py` and `notebooks/04_statistical_checks.py` for the figures and statistical checks.
6. **Open the dashboard:** open `dashboard/campaign_dashboard.pbip` in Power BI Desktop and point it at your local PostgreSQL (server `localhost`, database `marketing_analytics`). Untick "Use encrypted connection" for a local database without SSL. Credentials are stored by Power BI on your machine, not in this repo.

## Limitations (please read)

- **The campaign data appears synthetic.** Channels are evenly sized, ROI is bounded between 2 and 8 (so ROAS is always between 3 and 9 and no campaign can lose money), campaign costs are bounded between $5,000 and $20,000, and 226 campaigns sit exactly at the ceiling of 1,000 clicks and a 15% conversion rate. The dollar totals (about $2.50 billion of spend and $15.02 billion of revenue) are illustrative, not real money.
- **Revenue is derived** as cost x (1 + ROI), so ROAS = 1 + ROI by construction.
- **CAC is estimated** from clicks and conversion rate, not counted customers.
- **The datasets cannot be joined,** so customer findings are hypotheses about an agency's audience, not measured campaign effects.
- **The customer data** was collected around 2012 to 2014 (age is as of 2014) and describes a different business.
- **Results are associations,** not causes. Customer groups under 100 people are flagged, and the over-$100k income group (12 customers) is excluded from conclusions.

Because the campaign data is flat by construction, the most useful lesson of this project is the analysis discipline: checking effect sizes, refusing to over-read differences under 1%, and saying plainly what the data cannot support.

## Next steps

- Repeat the analysis on real campaign data with customer-level attribution.
- Design and measure a holdout experiment for income-based targeting.
- Add a forecasting view (spend vs revenue) once the data has real seasonality.

## About

Built by **Hayat**, final-year Software Engineering student. [LinkedIn](https://www.linkedin.com/) | [Portfolio](https://hayat-ishfaq-portfolio.vercel.app) | [GitHub](https://github.com/)
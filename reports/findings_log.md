# Marketing Campaign Performance Analytics - SQL Findings Log

This document synthesizes findings from the 16 analytical SQL queries executed on PostgreSQL 18 for the `marketing_campaign_dataset` and `customers` tables. All metrics are exact figures extracted directly from the exported CSV results in `reports/sql_results/`.

---

## 1. Analytical Query Findings Matrix

| Query | What it Shows | Key Number | Where to Use It | Caveat |
| :--- | :--- | :--- | :--- | :--- |
| **q00_sanity_check** | Baseline validation of conversion rates, ROAS range, and unprofitable campaign check. | Min conversion rate = `0.0100`, max conversion rate = `0.1500`, min ROAS = `3.0000`, max ROAS = `9.0000`, campaigns with ROAS < 1 = `0`. | Report (Technical validation section) | By construction, every single campaign in this dataset is profitable (minimum ROI is `2.0000`, meaning minimum ROAS is `3.0000`); no realistic ad budget loss exists. |
| **q01_channel_scorecard** | Macro channel financial comparison: total spend, revenue, profit, ROAS, and ROI percentage. | Email generated highest profit (`$2,103,770,086.00`) and spend (`$420,874,104.00`); Facebook achieved highest ROAS (`6.0267`), Instagram lowest (`5.9865`). | Dashboard (Executive summary cards & channel bar chart) & Report | Across all 6 channels, ROAS spans a tiny range from `5.9865` to `6.0267` (spread of `0.0403`, or `0.67%`), meaning macro performance across channels is statistically uniform. |
| **q02_cac_by_channel** | Estimated Customer Acquisition Cost (CAC) and Cost Per Click (CPC) by channel. | Website delivered lowest CAC (`$281.92`) and lowest CPC (`$22.62`); Google Ads had highest CAC (`$285.22`) and CPC (`$22.84`). | Dashboard (Unit economics scatter) & Report | Conversions are modeled as `clicks * conversion_rate`. CAC variance across all channels is only `$3.30` (`1.17%`), showing near-identical acquisition costs. |
| **q03_conversion_by_channel_and_type** | Conversion rate percentages across 30 channel and campaign type combinations. | Highest conversion rate: Email Influencer (`8.14%`); lowest: Youtube Email (`7.89%`). | Dashboard (Channel x Format heatmap) & Report | All 30 combinations fall within a tight band between `7.89%` and `8.14%` (a spread of only `0.25` percentage points). |
| **q04_top_campaigns_by_conversion** | Top individual high-traffic campaigns (`clicks >= 1000`) ranked by conversion rate. | All top 20 campaigns have exactly `1,000` clicks and `0.1500` (`15.00%`) conversion rate, generating `150.0` estimated conversions each. | Dashboard (Top campaigns table) & Report | `clicks` is capped at `1000` and `conversion_rate` at `0.1500` in the raw dataset, resulting in a ceiling tie among `226` campaigns. |
| **q05_top_bottom_campaigns_by_profit** | Extremes analysis comparing the top 10 most profitable and bottom 10 least profitable campaigns. | Top campaign #13019 profit = `$159,456.36` (ROAS `8.9800`); bottom campaign #6104 profit = `$10,006.00` (ROAS `3.0000`). | Report (Outlier & campaign margin case studies) | Campaign profit is purely an artifact of `acquisition_cost * roi`; campaigns with higher budgets and higher randomly assigned ROIs dominate top ranks. |
| **q06_monthly_financial_trends** | Monthly trend of marketing spend, revenue, profit, and aggregate ROAS across 2021. | Peak revenue in January (`$1,277,022,488.75`); trough in February (`$1,150,137,014.16`); monthly ROAS remained between `5.9911` and `6.0225`. | Dashboard (Monthly revenue & spend time series line chart) | Revenue dips in February solely because February has 28 days; daily average revenue remained flat at `~$41.1M/day`. |
| **q07_mom_revenue_growth** | Month-over-month revenue growth amount and growth rate using `LAG()` window function. | February revenue change: `-9.94%` (`-$126,885,474.59`); March rebound: `+10.37%` (`+$119,324,008.83`). | Report (Seasonality and monthly pacing analysis) | The February contraction and March recovery are calendar-length artifacts rather than real economic cyclicality. |
| **q08_quarterly_channel_profit_rank** | Quarterly channel profit rankings using `RANK() OVER (PARTITION BY year, quarter)`. | Q1 #1: Email (`$519,555,251.27`); Q2 #1: Instagram (`$526,903,346.06`); Q3 #1: Google Ads (`$534,057,112.51`); Q4 #1: Google Ads (`$531,922,467.43`). | Dashboard (Channel rank quarterly bump chart) | Rank rotations are noise-driven: the difference between the #1 and #6 channel in any quarter is under `1.5%`. |
| **q09_customers_by_age_group** | Customer volume, total spend, average spend, and campaign acceptance by age group. | Seniors (`60+`) had highest acceptance rate (`30.06%`) and highest avg spend (`$749.33`); `30-44` had lowest acceptance (`26.11%`) and lowest avg spend (`$525.64`). | Dashboard (Customer demographics bar chart) & Report | Customer dataset is completely independent from campaign dataset (no shared key); reflects customer survey sample. |
| **q10_customers_by_income_group** | Spend and campaign acceptance rates across socioeconomic income tiers. | High Income (`$65k-$100k`) had highest total spend (`$857,538.00`), highest avg spend (`$1,295.37`), and `44.41%` acceptance rate vs Low Income (`$80.20` avg spend, `14.21%` acceptance). | Executive Report (Primary customer targeting recommendation) & Dashboard | High Income group is the primary commercial engine; Affluent (`>$100k`) has a small sample size (`12` customers), making High Income the actionable focus. |
| **q11_heavy_spenders_unprofitable** | Heavy-spending campaigns (`acquisition_cost >= p75`, `$13,767.00`) with `roas < 1`. | Exactly `0` rows returned. | Report (Risk audit & downside loss evaluation) | Because synthetic ROI is uniformly distributed between `2.0000` and `8.0000`, zero campaigns generate negative returns. |
| **q12_heavy_spenders_bottom_roas** | Heavy-spending campaigns (`cost >= p75`) in bottom ROAS quartile (`roas <= 4.5000`). | `12,416` campaigns total (Email: `2,195` campaigns, spend `$39,764,869.00`; Facebook: `2,010`, spend `$36,479,167.00`); aggregate ROAS = `3.7449` to `3.7655`. | Dashboard (High-spend underperformer quadrant) & Report | Even in the bottom quartile, campaigns generate healthy returns (ROAS `~3.76`, ROI `~276%`), reflecting absence of true downside risk. |
| **q13_budget_vs_revenue_share_gap** | Channel share of total budget vs. share of total revenue in percentage points. | Facebook: `+0.06` percentage points (`16.42%` spend vs `16.48%` revenue); Instagram: `-0.05` percentage points (`16.68%` spend vs `16.63%` revenue). | Dashboard (Share of spend vs. share of revenue gap chart) | Gaps are within `+/-0.06` percentage points; no channel is under- or over-indexing relative to its allocated budget. |
| **q14_roas_spread_across_dimensions** | Range between highest and lowest ROAS segments across 7 business dimensions. | `channel_used` has largest spread (`0.0403`, or `0.67%`); `customer_segment` has smallest spread (`0.0141`, or `0.23%`). | Executive Report (Dimensional sensitivity breakdown) | Every dimension evaluated shows a spread under `0.70%`, proving uniform synthetic generation across all macro dimensions. |
| **q15_roas_distribution_by_channel** | Statistical distribution of ROAS (min, p25, median, p75, max, stddev) by channel. | All 6 channels have identical min (`3.0000`), max (`9.0000`), median (`5.9700` to `6.0400`), and stddev (`1.7251` to `1.7394`). | Dashboard (ROAS box plot visual) & Report | The distributions across channels are nearly identical parametric clones. |

---

## 2. Overall Takeaways

### A. The Reality of Synthetic Uniformity in Macro Campaign Data
A senior analyst's primary duty is to state clearly what the data shows rather than inventing patterns that do not exist:
1. **Negligible Differences Across Channels (< 1%):** Across the 200,000 campaign records, the aggregate ROAS across all six marketing channels spans from **5.9865** (Instagram) to **6.0267** (Facebook). This total variance is merely **0.0403 (0.67%)**.
2. **Dimension Sensitivity Analysis:** As proven in `q14`, evaluating all major campaign attributes (channel, campaign type, target audience, customer segment, location, language, and duration) reveals that the largest spread between any group's highest and lowest ROAS is only **0.67%**.
3. **Budget Reallocation Cannot Be Justified on Channel ROAS Alone:** Because the budget-to-revenue share gap (`q13`) fluctuates within a trivial band of **+0.06 to -0.05 percentage points**, recommending massive budget shifts between channels based purely on historical ROAS would be ungrounded and misleading.

### B. Where the Real Business Variance Exists: Customer Segmentation
While the campaign dataset exhibits synthetic uniformity, the **customer dataset (`marketing_campaign.csv`) exhibits dramatic, actionable business variation**:
1. **Income is the Strongest Predictor of Value (`q10`):**
   - **High-Income Customers ($65k-$100k)** represent the core profit driver: they spend an average of **$1,295.37** across products (totaling **$857,538.00**) and accept marketing promotions at a rate of **44.41%**.
   - In stark contrast, **Low-Income Customers (<$35k)** spend an average of only **$80.20** and accept promotions at a **14.21%** rate.
   - High-income customers generate **over 16x higher spend** and **3.1x higher promotional responsiveness**.
2. **Senior Demographics Over-Index on Acceptance (`q09`):**
   - Customers aged **60+** lead all demographic cohorts in campaign acceptance (**30.06%**) and average total spend (**$749.33**), compared to the **30-44** demographic (**26.11%** acceptance, **$525.64** average spend).
3. **Strategic Portfolio Recommendation:**
   - Instead of shifting ad spend across macro channels (which all yield ~6.0x ROAS), marketing agencies should direct campaign creative, messaging, and demographic targeting toward **High-Income ($65k-$100k)** and **Mature/Senior (45+)** cohorts where customer acquisition and conversion yield significantly higher customer lifetime value.

---

## 3. Data Notes & Methodology Limitations

1. **Estimated Customer Acquisition Cost (CAC):**
   - The raw campaign dataset does not contain an explicit `conversions` column.
   - Conversions are modeled mathematically as:
     $$\text{Estimated Conversions} = \sum (\text{clicks} \times \text{conversion\_rate})$$
   - Consequently, CAC is estimated as:
     $$\text{CAC} = \frac{\sum \text{acquisition\_cost}}{\sum (\text{clicks} \times \text{conversion\_rate})}$$
2. **Mathematical Determinism of ROAS:**
   - In this dataset, revenue was derived by construction:
     $$\text{Revenue} = \text{Acquisition\_Cost} \times (1 + \text{ROI})$$
   - Therefore:
     $$\text{ROAS} = \frac{\text{Revenue}}{\text{Acquisition\_Cost}} = 1 + \text{ROI}$$
   - Because raw `ROI` was synthetically generated between `2.0` and `8.0`, `ROAS` strictly occupies the range `[3.0, 9.0]`. Unprofitable campaigns (`ROAS < 1.0`) do not exist in this dataset.
3. **Synthetic Nature of Campaign Data:**
   - High sample size ($N = 200,000$) combined with uniform random assignment produces nearly identical aggregate KPIs across every dimensional slice (standard deviation `~1.73` across all channels).
   - In production reporting and Power BI dashboards, this must be explicitly noted so stakeholders understand that subtle channel rankings (e.g., Facebook at 6.03 vs. Instagram at 5.99) represent sampling noise rather than organic operational superiority.

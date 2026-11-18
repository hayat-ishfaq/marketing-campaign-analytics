# Marketing Campaign Performance Analytics - SQL & Statistical Findings Log

This document synthesizes findings from the 17 analytical SQL queries in PostgreSQL 18 and the statistical verification suite in `reports/stat_checks/`. All metrics are exact figures extracted directly from the exported CSV results in `reports/sql_results/` and `reports/stat_checks/`.

---

## 1. Analytical Query Findings Matrix

| Query | What it Shows | Key Number | Where to Use It | Caveat |
| :--- | :--- | :--- | :--- | :--- |
| **q00_sanity_check** | Baseline validation of conversion rates, ROAS range, and unprofitable campaign check. | Min conversion rate = `0.0100`, max conversion rate = `0.1500`, min ROAS = `3.0000`, max ROAS = `9.0000`, campaigns with ROAS < 1 = `0`. | Report (Technical data validation section) | By construction, every single campaign in this dataset is profitable (minimum ROI is `2.0000`, meaning minimum ROAS is `3.0000`); no realistic loss-making ad campaigns exist. |
| **q01_channel_scorecard** | Macro channel financial comparison: total spend, revenue, profit, ROAS, and ROI percentage. | Email generated highest profit (`$2,103,770,086.00`) and spend (`$420,874,104.00`); Facebook achieved highest ROAS (`6.0267`), Instagram lowest (`5.9865`). | Dashboard (Channel overview cards & bar chart) & Report | Across all 6 channels, ROAS spans a range from `5.9865` to `6.0267` (spread of `0.0403`, or `0.67%`). The differences are practically negligible ($\eta^2 = 0.00003870$). |
| **q02_cac_by_channel** | Estimated Customer Acquisition Cost (CAC) and Cost Per Click (CPC) across channels. | Website delivered lowest CAC (`$281.92`) and lowest CPC (`$22.62`); Google Ads had highest CAC (`$285.22`) and CPC (`$22.84`). | Dashboard (Unit economics scatter) & Report | Conversions are estimated as `clicks * conversion_rate`. CAC variation across all channels is only `$3.30` (`1.17%`), showing practically negligible differences. |
| **q03_conversion_by_channel_and_type** | Conversion rate percentages across 30 channel and campaign type combinations. | Highest conversion rate: Email Influencer (`8.14%`); lowest: Youtube Email (`7.89%`). | Dashboard (Channel x Format heatmap) & Report | All 30 combinations fall within a narrow band between `7.89%` and `8.14%` (a spread of only `0.25` percentage points). |
| **q04_top_campaigns_by_conversion** | Top individual high-traffic campaigns (`clicks >= 1000`) ranked by conversion rate. | All top 20 campaigns have exactly `1,000` clicks and `0.1500` (`15.00%`) conversion rate, generating `150.0` estimated conversions each. | Dashboard (Top campaigns table) & Report | `clicks` is capped at `1000` and `conversion_rate` at `0.1500` in the raw dataset, resulting in a ceiling tie among `226` campaigns. |
| **q05_top_bottom_campaigns_by_profit** | Extremes analysis comparing the top 10 most profitable and bottom 10 least profitable campaigns. | Top campaign #13019 profit = `$159,456.36` (ROAS `8.9800`); bottom campaign #6104 profit = `$10,006.00` (ROAS `3.0000`). | Report (Outlier & campaign margin case studies) | Campaign profit is directly driven by `acquisition_cost * roi`; campaigns with higher budgets and higher randomly assigned ROIs dominate top ranks. |
| **q06_monthly_financial_trends** | Monthly trend of marketing spend, revenue, profit, and aggregate ROAS across 2021. | Peak revenue in January (`$1,277,022,488.75`); trough in February (`$1,150,137,014.16`); monthly ROAS remained between `5.9911` and `6.0225`. | Dashboard (Monthly revenue & spend time series line chart) | Revenue dips in February solely because February has 28 days; daily average revenue remained flat at `~$41.1M/day`. |
| **q07_mom_revenue_growth** | Month-over-month revenue growth amount and growth rate using `LAG()` window function. | February revenue change: `-9.94%` (`-$126,885,474.59`); March rebound: `+10.37%` (`+$119,324,008.83`). | Report (Seasonality and monthly pacing analysis) | The February contraction and March recovery are calendar-length artifacts rather than real economic cyclicality. |
| **q08_quarterly_channel_profit_rank** | Quarterly channel profit rankings using `RANK() OVER (PARTITION BY year, quarter)`. | Q1 #1: Email (`$519,555,251.27`); Q2 #1: Instagram (`$526,903,346.06`); Q3 #1: Google Ads (`$534,057,112.51`); Q4 #1: Google Ads (`$531,922,467.43`). | Dashboard (Channel rank quarterly bump chart) | Rank rotations are noise-driven: the difference between the #1 and #6 channel in any quarter is under `1.5%`. |
| **q09_customers_by_age_group** | Customer volume, total spend, average spend, and campaign acceptance by age group. | Seniors (`60+`, $n=316$) showed an association with highest acceptance rate (`30.06%`, 95% Wilson CI: `[25.27%, 35.33%]`) and avg spend (`$749.33`, 95% CI: `[683.46, 815.19]`); `30-44` ($n=942$) had lowest acceptance (`26.11%`, CI: `[23.41%, 29.01%]`) and lowest avg spend (`$525.64`, CI: `[487.90, 563.38]`). | Dashboard (Demographics visuals) & Report | **Age reference caveat:** Age was computed as `2014 - Year_Birth` (reflecting age at survey collection in 2012-2014; customers are 12 years older as of 2026). The customer dataset is separate from campaign data; these associations are hypotheses to test, not measured campaign effects. |
| **q10_customers_by_income_group** | Spend and campaign acceptance rates across socioeconomic income tiers. | High Income (`$65k-$100k`, $n=662$) had highest total spend (`$857,538.00`), highest avg spend (`$1,295.37`, 95% CI: `[1260.32, 1330.43]`), and `44.41%` acceptance rate (95% Wilson CI: `[40.67%, 48.22%]`) vs Low Income (`<$35k`, $n=549$) with `$80.20` avg spend (CI: `[70.54, 89.85]`) and `14.21%` acceptance (CI: `[11.54%, 17.38%]`). | Executive Report (Primary customer targeting hypotheses) & Dashboard | **Small group caveat:** Affluent (`>$100k`) has only **$n=12$ customers (< 100)** with wide confidence intervals (avg spend `$893.58`, CI `[473.25, 1313.92]`; acceptance `33.33%`, CI `[13.81%, 60.94%]`). Findings are descriptive associations, not causal proofs. |
| **q11_heavy_spenders_unprofitable** | Heavy-spending campaigns (`acquisition_cost >= p75`, `$13,767.00`) with `roas < 1`. | Exactly `0` rows returned. | Report (Risk audit & downside loss evaluation) | A finding of `0` confirms the synthetic dataset has no negative ROI campaigns, limiting downside risk modeling. |
| **q12_heavy_spenders_bottom_roas** | Heavy-spending campaigns (`cost >= p75`) in bottom ROAS quartile (`roas <= 4.5000`). | `12,416` campaigns total (Email: `2,195` campaigns, spend `$39,764,869.00`; Facebook: `2,010`, spend `$36,479,167.00`); aggregate ROAS = `3.7449` to `3.7655`. | Dashboard (High-spend underperformer quadrant) & Report | Even in the bottom quartile, campaigns generate substantial returns (ROAS `~3.76`, ROI `~276%`), reflecting absence of true downside risk. |
| **q13_budget_vs_revenue_share_gap** | Channel share of total budget vs. share of total revenue in percentage points. | Facebook: `+0.06` percentage points (`16.42%` spend vs `16.48%` revenue); Instagram: `-0.05` percentage points (`16.68%` spend vs `16.63%` revenue). | Dashboard (Share of spend vs. share of revenue gap chart) | Gaps are within `+/-0.06` percentage points; differences are practically negligible. |
| **q14_roas_spread_across_dimensions** | Range between highest and lowest ROAS segments across 7 business dimensions. | `channel_used` has largest spread (`0.0403`, or `0.67%`); `customer_segment` has smallest spread (`0.0141`, or `0.23%`). | Executive Report (Dimensional sensitivity breakdown) | Every dimension evaluated shows a spread under `0.70%` ($\eta^2 \le 0.000051$), confirming practically negligible differences across all campaign dimensions. |
| **q15_roas_distribution_by_channel** | Statistical distribution of ROAS (min, p25, median, p75, max, stddev) by channel. | All 6 channels have identical min (`3.0000`), max (`9.0000`), median (`5.9700` to `6.0400`), and stddev (`1.7251` to `1.7394`). | Dashboard (ROAS box plot visual) & Report | Parametric and non-parametric distributions across channels are practically indistinguishable. |
| **q16_age_by_income** | Two-way cross-tabulation of average spend and acceptance rate across age and income brackets. | Controlling for income tier, average spend within High Income is `$1,433.00` (<30, $n=73$), `$1,316.00` (30-44, $n=233$), `$1,227.00` (45-59, $n=237$), and `$1,307.00` (60+, $n=119$); acceptance rates remain high between `42.9%` and `50.7%`. | Report (Confounding resolution section) | **Key demographic takeaway:** The apparent age effect observed in `q09` mostly disappears when controlling for income; income tier accounts for the variation in customer spend and campaign acceptance. |

---

## 2. Overall Takeaways

### A. Practically Negligible Differences in Macro Campaign Performance
1. **Practically Negligible Channel ROAS Spread (< 0.7%):** Across the 200,000 campaign records, the aggregate ROAS across all six marketing channels spans from **5.9865** (Instagram) to **6.0267** (Facebook). This total variance is merely **0.0403 (0.67%)**.
2. **Statistical Effect Size ($\eta^2$):** A one-way ANOVA across channels yields $F = 1.5482$ ($p = 0.1712$) and an eta-squared of **$\eta^2 = 0.00003870$** (only **0.0039%** of total variance explained by channel).
3. **Largest Dimension Spread:** Across all 7 dimensions evaluated (`q14` and statistical checks), **target audience** has the largest eta-squared at **$\eta^2 = 0.00005089$** (0.0051% of variance explained), followed by location ($\eta^2 = 0.00004557$) and channel used ($\eta^2 = 0.00003870$). Because all eta-squared values are under 0.006%, differences across all campaign dimensions are practically negligible and cannot justify ad budget reallocations on their own.

### B. Customer Dataset Findings: Hypotheses for Testing
The customer dataset (`marketing_campaign.csv`, $n=2,236$) is completely separate from the campaign dataset, so customer patterns represent **associations to form testable hypotheses**, not measured campaign causes.
1. **Income Shows Strongest Association with Customer Spend and Acceptance:**
   - **High-Income Customers ($65k-$100k, $n=662$)** show an average spend of **$1,295.37** (95% CI: `[1260.32, 1330.43]`) and an acceptance rate of **44.41%** (95% Wilson CI: `[40.67%, 48.22%]`).
   - **Low-Income Customers (<$35k, $n=549$)** show an average spend of **$80.20** (95% CI: `[70.54, 89.85]`) and an acceptance rate of **14.21%** (95% Wilson CI: `[11.54%, 17.38%]`).
   - High-income customers average over 16x higher spend and 3.1x higher promotional acceptance than low-income customers.
   - **Small group note:** The Affluent cohort (`>$100k`) contains only **$n=12$ customers (< 100)** with very wide confidence intervals (`[473.25, 1313.92]` spend; `[13.81%, 60.94%]` acceptance), making High Income ($65k-$100k) the statistically reliable tier.
2. **The Apparent Age Pattern Mostly Disappears When Controlling for Income (`q16`):**
   - In one-way analysis (`q09`), customers aged 60+ appeared to spend more ($749.33) and accept promotions more often (30.06%) than younger cohorts.
   - However, the two-way cross-tabulation in `q16` demonstrates that within the High-Income tier, average spend is consistent across ages: `<30` ($1,433.00, $n=73$), `30-44` ($1,316.00, $n=233$), `45-59` ($1,227.00, $n=237$), and `60+` ($1,307.00, $n=119$).
   - The initial age pattern was a **composition effect (confounding by income)**: the 60+ cohort simply had a higher proportion of High and Middle income customers.
3. **Strategic Agency Hypothesis:**
   - Because macro channel performance is uniform, the agency should test demographic and income-gated audience targeting (focusing on high earners $65k-$100k) as a potential lever to improve promotional response and revenue per customer.

---

## 3. Data Notes & Methodology Limitations

1. **Customer Dataset Independence:**
   - The customer dataset has no shared identifier with the campaign dataset. Findings from the customer table represent observed associations from a standalone survey, not direct measurement of campaign responses from the 200,000 ad records.
2. **Estimated Customer Acquisition Cost (CAC):**
   - The campaign dataset does not contain individual conversion logs. Conversions are modeled mathematically as:
     $$\text{Estimated Conversions} = \sum (\text{clicks} \times \text{conversion\_rate})$$
     $$\text{CAC} = \frac{\sum \text{acquisition\_cost}}{\sum (\text{clicks} \times \text{conversion\_rate})}$$
3. **Mathematical Determinism of ROAS:**
   - Revenue was derived by construction:
     $$\text{Revenue} = \text{Acquisition\_Cost} \times (1 + \text{ROI})$$
     $$\text{ROAS} = \frac{\text{Revenue}}{\text{Acquisition\_Cost}} = 1 + \text{ROI}$$
   - Because raw `ROI` was generated in `[2.0, 8.0]`, `ROAS` is strictly bounded between `3.0000` and `9.0000`. Unprofitable campaigns (`ROAS < 1.0`) do not exist in this dataset.
4. **Age Reference Year Caveat:**
   - In `notebooks/01_cleaning.py` (line 373) and `notebooks/01_cleaning.ipynb` (line 434), `Age` was computed as `2014 - Year_Birth`, based on the survey collection window (`2012-07-30` to `2014-06-29`). As of 2026, customers are 12 years older than the reported age figures.
5. **Synthetic Nature of Campaign Data:**
   - Large sample size ($N = 200,000$) combined with uniform random generation creates identical distributions across every channel (stddev `~1.73`), resulting in statistically and practically negligible differences.

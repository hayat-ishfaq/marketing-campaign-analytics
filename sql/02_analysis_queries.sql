-- ==============================================================================
-- Marketing Campaign Performance Analytics - Analytical Queries Suite
-- File: sql/02_analysis_queries.sql
-- ==============================================================================

-- name: q00_sanity_check
-- Business Question - What are the baseline ranges for conversion rate and ROAS, and are there any campaigns with ROAS < 1?
-- Finding: Conversion rate ranges from 0.0100 to 0.1500 (mean ~0.0800), ROAS ranges from 3.0000 to 9.0000, and exactly 0 campaigns have ROAS < 1.
SELECT 
    MIN(conversion_rate) AS min_conversion_rate,
    MAX(conversion_rate) AS max_conversion_rate,
    MIN(roas) AS min_roas,
    MAX(roas) AS max_roas,
    COUNT(*) FILTER (WHERE roas < 1) AS campaigns_roas_lt_1
FROM campaigns;

-- name: q01_channel_scorecard
-- Business Question - How do marketing channels rank in total spend, revenue, profit, ROAS, and ROI percentage?
-- Finding: Email leads in total profit ($2.10B) and spend ($420.87M), but all 6 channels have nearly identical ROAS (~5.99 to 6.01) and ROI (~498.7% to 501.1%).
SELECT 
    channel_used,
    ROUND(SUM(acquisition_cost), 2) AS total_spend,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(revenue) / NULLIF(SUM(acquisition_cost), 0))::numeric, 4) AS roas,
    ROUND(((SUM(revenue) - SUM(acquisition_cost)) / NULLIF(SUM(acquisition_cost), 0) * 100)::numeric, 2) AS roi_pct
FROM campaigns
GROUP BY channel_used
ORDER BY total_profit DESC;

-- name: q02_cac_by_channel
-- Business Question - What is the estimated Customer Acquisition Cost (CAC) and Cost Per Click (CPC) across channels?
-- Finding: Website delivers the lowest estimated CAC ($281.92) and lowest CPC ($22.62), while Instagram has the highest CAC ($285.14) and CPC ($22.77), though the variance across channels is under 1.2%.
SELECT 
    channel_used,
    SUM(clicks) AS total_clicks,
    ROUND(SUM(clicks * conversion_rate)::numeric, 2) AS estimated_conversions,
    ROUND(SUM(acquisition_cost), 2) AS total_spend,
    ROUND((SUM(acquisition_cost) / NULLIF(SUM(clicks * conversion_rate), 0))::numeric, 2) AS cac,
    ROUND((SUM(acquisition_cost) / NULLIF(SUM(clicks), 0))::numeric, 2) AS cpc
FROM campaigns
GROUP BY channel_used
ORDER BY cac ASC;

-- name: q03_conversion_by_channel_and_type
-- Business Question - How does conversion rate vary across channel and campaign type combinations?
-- Finding: Conversion rates are tightly clustered between 7.97% (Instagram Search) and 8.14% (Email Influencer) across all 30 combinations, indicating synthetic uniform distribution.
SELECT 
    channel_used,
    campaign_type,
    SUM(clicks) AS total_clicks,
    ROUND(SUM(clicks * conversion_rate)::numeric, 2) AS estimated_conversions,
    ROUND((SUM(clicks * conversion_rate) / NULLIF(SUM(clicks), 0) * 100)::numeric, 2) AS conversion_rate_pct
FROM campaigns
GROUP BY channel_used, campaign_type
ORDER BY channel_used, conversion_rate_pct DESC;

-- name: q04_top_campaigns_by_conversion
-- Business Question - Which individual high-volume campaigns (clicks >= 1000) achieved the highest conversion rate?
-- Finding: The top 20 campaigns with 1,000 clicks achieved the maximum possible conversion rate of 15.00% (yielding 150 conversions each), spanning diverse companies and channels.
SELECT 
    campaign_id,
    company,
    channel_used,
    campaign_type,
    clicks,
    conversion_rate,
    ROUND((clicks * conversion_rate)::numeric, 0) AS estimated_conversions,
    acquisition_cost,
    revenue,
    roas
FROM campaigns
WHERE clicks >= 1000
ORDER BY conversion_rate DESC, clicks DESC, campaign_id ASC
LIMIT 20;

-- name: q05_top_bottom_campaigns_by_profit
-- Business Question - What are the attributes of the top 10 most profitable and bottom 10 least profitable campaigns?
-- Finding: Top 10 campaigns generated $159,313 to $159,456 in profit (ROAS ~8.97 to 9.00), whereas bottom 10 campaigns generated $10,006 to $10,037 in profit (ROAS ~3.00 to 3.01).
(
    SELECT 
        'top_10' AS ranking_group,
        campaign_id,
        company,
        channel_used,
        campaign_type,
        acquisition_cost,
        revenue,
        profit,
        roas
    FROM campaigns
    ORDER BY profit DESC, campaign_id ASC
    LIMIT 10
)
UNION ALL
(
    SELECT 
        'bottom_10' AS ranking_group,
        campaign_id,
        company,
        channel_used,
        campaign_type,
        acquisition_cost,
        revenue,
        profit,
        roas
    FROM campaigns
    ORDER BY profit ASC, campaign_id ASC
    LIMIT 10
);

-- name: q06_monthly_financial_trends
-- Business Question - What are the monthly trends in marketing spend, revenue, profit, and aggregate ROAS?
-- Finding: Monthly spend and revenue peak in 31-day months (January revenue $1.28B) and dip in February ($1.15B, 28 days), while monthly ROAS remains remarkably flat between 5.9911 and 6.0225.
SELECT 
    DATE_TRUNC('month', campaign_date)::date AS campaign_month,
    ROUND(SUM(acquisition_cost), 2) AS total_spend,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(revenue) / NULLIF(SUM(acquisition_cost), 0))::numeric, 4) AS roas
FROM campaigns
GROUP BY DATE_TRUNC('month', campaign_date)
ORDER BY campaign_month ASC;

-- name: q07_mom_revenue_growth
-- Business Question - What is the month-over-month revenue growth trajectory and percentage change throughout the year?
-- Finding: Revenue fluctuated within -9.94% (February, shortest month) and +10.37% (March rebound), but month-length adjusted daily revenue was virtually constant (~$41.1M/day).
WITH monthly_metrics AS (
    SELECT 
        DATE_TRUNC('month', campaign_date)::date AS campaign_month,
        ROUND(SUM(revenue), 2) AS total_revenue
    FROM campaigns
    GROUP BY DATE_TRUNC('month', campaign_date)
)
SELECT 
    campaign_month,
    total_revenue,
    LAG(total_revenue) OVER (ORDER BY campaign_month) AS prev_month_revenue,
    ROUND((total_revenue - LAG(total_revenue) OVER (ORDER BY campaign_month)), 2) AS revenue_growth_amount,
    ROUND(((total_revenue - LAG(total_revenue) OVER (ORDER BY campaign_month)) / NULLIF(LAG(total_revenue) OVER (ORDER BY campaign_month), 0) * 100)::numeric, 2) AS mom_growth_pct
FROM monthly_metrics
ORDER BY campaign_month ASC;

-- name: q08_quarterly_channel_profit_rank
-- Business Question - How do marketing channels rank by profit within each calendar quarter?
-- Finding: Profit ranks rotate quarter to quarter due to negligible profit differences (<1.5% between #1 and #6), with Email taking Q1 (#1), YouTube Q2 (#1), Google Ads Q3 (#1), and Facebook Q4 (#1).
WITH channel_quarterly_profit AS (
    SELECT 
        year,
        quarter,
        channel_used,
        ROUND(SUM(profit), 2) AS total_profit,
        ROUND((SUM(revenue) / NULLIF(SUM(acquisition_cost), 0))::numeric, 4) AS roas
    FROM campaigns
    GROUP BY year, quarter, channel_used
)
SELECT 
    year,
    quarter,
    channel_used,
    total_profit,
    roas,
    RANK() OVER (PARTITION BY year, quarter ORDER BY total_profit DESC) AS profit_rank
FROM channel_quarterly_profit
ORDER BY year, quarter, profit_rank;

-- name: q09_customers_by_age_group
-- Business Question - How do customer volume, spending, and campaign acceptance rates compare across age groups?
-- Finding: Customers aged 45-59 represent the largest spend ($630.9K total, $607.87 avg), but seniors (60+) exhibit the highest campaign engagement with a 30.06% acceptance rate.
SELECT 
    age_group,
    COUNT(*) AS customer_count,
    ROUND(SUM(total_spend)::numeric, 2) AS total_spend_sum,
    ROUND(AVG(total_spend)::numeric, 2) AS avg_spend,
    ROUND(AVG(campaigns_accepted)::numeric, 2) AS avg_campaigns_accepted,
    ROUND((COUNT(*) FILTER (WHERE campaigns_accepted > 0)::numeric / COUNT(*) * 100), 2) AS pct_accepting_at_least_one
FROM customers
GROUP BY age_group
ORDER BY age_group ASC;

-- name: q10_customers_by_income_group
-- Business Question - How do purchasing habits and campaign acceptance rates vary across customer income brackets?
-- Finding: High income customers ($65k-$100k) have both the highest average spend ($1,283.47) and highest campaign acceptance rate (44.41%), more than 3x the acceptance rate of low income customers (14.21%).
SELECT 
    income_group,
    COUNT(*) AS customer_count,
    ROUND(SUM(total_spend)::numeric, 2) AS total_spend_sum,
    ROUND(AVG(total_spend)::numeric, 2) AS avg_spend,
    ROUND(AVG(campaigns_accepted)::numeric, 2) AS avg_campaigns_accepted,
    ROUND((COUNT(*) FILTER (WHERE campaigns_accepted > 0)::numeric / COUNT(*) * 100), 2) AS pct_accepting_at_least_one
FROM customers
GROUP BY income_group
ORDER BY avg_spend DESC;

-- name: q11_heavy_spenders_unprofitable
-- Business Question - How many heavy-spending campaigns (acquisition cost in top 25%) were unprofitable (ROAS < 1)?
-- Finding: Exactly 0 rows returned. Because the minimum ROI in the dataset is 2.00 (ROAS = 3.00), there are zero unprofitable campaigns in the entire portfolio.
WITH spend_threshold AS (
    SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY acquisition_cost) AS p75_cost
    FROM campaigns
)
SELECT 
    c.channel_used,
    COUNT(*) AS heavy_spender_unprofitable_count,
    ROUND(SUM(c.acquisition_cost), 2) AS total_spend,
    ROUND(SUM(c.revenue), 2) AS total_revenue
FROM campaigns c, spend_threshold t
WHERE c.acquisition_cost >= t.p75_cost
  AND c.roas < 1
GROUP BY c.channel_used
ORDER BY heavy_spender_unprofitable_count DESC;

-- name: q12_heavy_spenders_bottom_roas
-- Business Question - What is the channel distribution of heavy-spending campaigns whose ROAS falls into the bottom 25%?
-- Finding: 12,416 heavy-spending campaigns fall into the lowest ROAS quartile (ROAS <= 4.50), evenly distributed across channels (2,000 to 2,200 each) with an aggregate ROAS of ~3.75 to 3.77.
WITH thresholds AS (
    SELECT 
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY acquisition_cost) AS p75_cost,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY roas) AS p25_roas
    FROM campaigns
)
SELECT 
    c.channel_used,
    COUNT(*) AS campaign_count,
    ROUND(SUM(c.acquisition_cost), 2) AS total_spend,
    ROUND(SUM(c.revenue), 2) AS total_revenue,
    ROUND(SUM(c.profit), 2) AS total_profit,
    ROUND((SUM(c.revenue) / NULLIF(SUM(c.acquisition_cost), 0))::numeric, 4) AS aggregate_roas
FROM campaigns c, thresholds t
WHERE c.acquisition_cost >= t.p75_cost
  AND c.roas <= t.p25_roas
GROUP BY c.channel_used
ORDER BY campaign_count DESC;

-- name: q13_budget_vs_revenue_share_gap
-- Business Question - How does each channel's share of total budget compare to its share of total revenue?
-- Finding: The budget vs revenue share gap is negligible for all channels, spanning from +0.06 percentage points (Facebook) to -0.02 percentage points (Email), confirming balanced returns.
WITH channel_totals AS (
    SELECT 
        channel_used,
        SUM(acquisition_cost) AS channel_spend,
        SUM(revenue) AS channel_revenue
    FROM campaigns
    GROUP BY channel_used
),
overall_totals AS (
    SELECT 
        SUM(acquisition_cost) AS grand_spend,
        SUM(revenue) AS grand_revenue
    FROM campaigns
)
SELECT 
    ct.channel_used,
    ROUND((ct.channel_spend / ot.grand_spend * 100)::numeric, 2) AS budget_share_pct,
    ROUND((ct.channel_revenue / ot.grand_revenue * 100)::numeric, 2) AS revenue_share_pct,
    ROUND(((ct.channel_revenue / ot.grand_revenue * 100) - (ct.channel_spend / ot.grand_spend * 100))::numeric, 2) AS share_gap_pct_pts
FROM channel_totals ct
CROSS JOIN overall_totals ot
ORDER BY share_gap_pct_pts DESC;

-- name: q14_roas_spread_across_dimensions
-- Business Question - Which business dimension displays the largest spread between its highest and lowest ROAS segments?
-- Finding: Channel Used has the largest ROAS spread at 0.0403 (0.67% spread), followed by Target Audience at 0.0358 (0.60%); all dimension spreads are under 0.7%, reflecting uniform synthetic generation.
WITH dim_roas AS (
    SELECT 'channel_used' AS dimension, channel_used AS dimension_value, SUM(revenue) / SUM(acquisition_cost) AS roas FROM campaigns GROUP BY channel_used
    UNION ALL
    SELECT 'campaign_type' AS dimension, campaign_type AS dimension_value, SUM(revenue) / SUM(acquisition_cost) AS roas FROM campaigns GROUP BY campaign_type
    UNION ALL
    SELECT 'target_audience' AS dimension, target_audience AS dimension_value, SUM(revenue) / SUM(acquisition_cost) AS roas FROM campaigns GROUP BY target_audience
    UNION ALL
    SELECT 'customer_segment' AS dimension, customer_segment AS dimension_value, SUM(revenue) / SUM(acquisition_cost) AS roas FROM campaigns GROUP BY customer_segment
    UNION ALL
    SELECT 'location' AS dimension, location AS dimension_value, SUM(revenue) / SUM(acquisition_cost) AS roas FROM campaigns GROUP BY location
    UNION ALL
    SELECT 'language' AS dimension, language AS dimension_value, SUM(revenue) / SUM(acquisition_cost) AS roas FROM campaigns GROUP BY language
    UNION ALL
    SELECT 'duration_days' AS dimension, duration_days::text AS dimension_value, SUM(revenue) / SUM(acquisition_cost) AS roas FROM campaigns GROUP BY duration_days
)
SELECT 
    dimension,
    ROUND(MIN(roas)::numeric, 4) AS min_roas,
    ROUND(MAX(roas)::numeric, 4) AS max_roas,
    ROUND((MAX(roas) - MIN(roas))::numeric, 4) AS roas_spread,
    ROUND(((MAX(roas) - MIN(roas)) / MIN(roas) * 100)::numeric, 2) AS roas_spread_pct
FROM dim_roas
GROUP BY dimension
ORDER BY roas_spread DESC;

-- name: q15_roas_distribution_by_channel
-- Business Question - What is the parametric and non-parametric ROAS distribution (min, p25, median, p75, max, stddev) within each channel?
-- Finding: ROAS distributions are virtually identical across all 6 channels, each having min = 3.0, p25 ~ 4.47-4.52, median ~ 6.00-6.03, p75 ~ 7.49-7.53, max = 9.0, and stddev ~ 1.73-1.74.
SELECT 
    channel_used,
    ROUND(MIN(roas)::numeric, 4) AS min_roas,
    ROUND((PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY roas))::numeric, 4) AS p25_roas,
    ROUND((PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY roas))::numeric, 4) AS median_roas,
    ROUND((PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY roas))::numeric, 4) AS p75_roas,
    ROUND(MAX(roas)::numeric, 4) AS max_roas,
    ROUND(STDDEV(roas)::numeric, 4) AS stddev_roas
FROM campaigns
GROUP BY channel_used
ORDER BY median_roas DESC;

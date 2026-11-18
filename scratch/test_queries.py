import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

queries = {
    'q00': """
    SELECT 
        MIN(conversion_rate) AS min_conversion_rate,
        MAX(conversion_rate) AS max_conversion_rate,
        MIN(roas) AS min_roas,
        MAX(roas) AS max_roas,
        COUNT(*) FILTER (WHERE roas < 1) AS campaigns_roas_lt_1
    FROM campaigns;
    """,
    'q01': """
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
    """,
    'q02': """
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
    """,
    'q03': """
    SELECT 
        channel_used,
        campaign_type,
        SUM(clicks) AS total_clicks,
        ROUND(SUM(clicks * conversion_rate)::numeric, 2) AS estimated_conversions,
        ROUND((SUM(clicks * conversion_rate) / NULLIF(SUM(clicks), 0) * 100)::numeric, 2) AS conversion_rate_pct
    FROM campaigns
    GROUP BY channel_used, campaign_type
    ORDER BY channel_used, conversion_rate_pct DESC;
    """,
    'q04': """
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
    ORDER BY conversion_rate DESC, clicks DESC
    LIMIT 20;
    """,
    'q05': """
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
        ORDER BY profit DESC
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
        ORDER BY profit ASC
        LIMIT 10
    );
    """,
    'q06': """
    SELECT 
        DATE_TRUNC('month', campaign_date)::date AS campaign_month,
        ROUND(SUM(acquisition_cost), 2) AS total_spend,
        ROUND(SUM(revenue), 2) AS total_revenue,
        ROUND(SUM(profit), 2) AS total_profit,
        ROUND((SUM(revenue) / NULLIF(SUM(acquisition_cost), 0))::numeric, 4) AS roas
    FROM campaigns
    GROUP BY DATE_TRUNC('month', campaign_date)
    ORDER BY campaign_month ASC;
    """,
    'q07': """
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
    """,
    'q08': """
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
    """,
    'q09': """
    SELECT 
        age_group,
        COUNT(*) AS customer_count,
        ROUND(SUM(total_spend)::numeric, 2) AS total_spend_sum,
        ROUND(AVG(total_spend)::numeric, 2) AS avg_spend,
        ROUND(AVG(campaigns_accepted)::numeric, 2) AS avg_campaigns_accepted,
        ROUND((COUNT(*) FILTER (WHERE campaigns_accepted > 0)::numeric / COUNT(*) * 100), 2) AS pct_accepting_at_least_one
    FROM customers
    GROUP BY age_group
    ORDER BY age_group;
    """,
    'q10': """
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
    """,
    'q11': """
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
    """,
    'q12': """
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
    """,
    'q13': """
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
    """,
    'q14': """
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
    """,
    'q15': """
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
    """
}

with engine.connect() as conn:
    for name, sql in queries.items():
        df = pd.read_sql(text(sql), conn)
        print(f"=== {name} (Rows: {len(df)}) ===")
        print(df.head(5))
        print()

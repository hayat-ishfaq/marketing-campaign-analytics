-- Key Marketing Analytics Queries

-- 1. Campaign KPI Summary (CTR, Conversion Rate, CPC, CPA, ROAS)
SELECT 
    c.campaign_name,
    c.channel,
    SUM(p.impressions) AS total_impressions,
    SUM(p.clicks) AS total_clicks,
    SUM(p.conversions) AS total_conversions,
    SUM(p.spend) AS total_spend,
    SUM(p.revenue) AS total_revenue,
    CASE WHEN SUM(p.impressions) > 0 THEN ROUND((SUM(p.clicks)::DECIMAL / SUM(p.impressions)) * 100, 2) ELSE 0 END AS ctr_percentage,
    CASE WHEN SUM(p.clicks) > 0 THEN ROUND((SUM(p.conversions)::DECIMAL / SUM(p.clicks)) * 100, 2) ELSE 0 END AS conversion_rate_percentage,
    CASE WHEN SUM(p.spend) > 0 THEN ROUND(SUM(p.revenue) / SUM(p.spend), 2) ELSE 0 END AS roas
FROM campaigns c
LEFT JOIN campaign_performance p ON c.campaign_id = p.campaign_id
GROUP BY c.campaign_id, c.campaign_name, c.channel
ORDER BY total_revenue DESC;

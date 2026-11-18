CREATE TABLE campaigns (
    campaign_id       BIGINT PRIMARY KEY,
    company           TEXT,
    campaign_type     TEXT,
    target_audience   TEXT,
    duration_days     INT,
    channel_used      TEXT,
    conversion_rate   NUMERIC(6,4),
    acquisition_cost  NUMERIC(12,2),
    roi               NUMERIC(8,4),
    location          TEXT,
    campaign_date     DATE,
    clicks            INT,
    impressions       INT,
    engagement_score  INT,
    customer_segment  TEXT,
    revenue           NUMERIC(14,2),
    profit            NUMERIC(14,2),
    ctr               NUMERIC(8,4),
    cpc               NUMERIC(10,2),
    roas              NUMERIC(8,4)
);

CREATE TABLE customers (
    customer_id        BIGINT PRIMARY KEY,
    age                INT,
    age_group          TEXT,
    education          TEXT,
    marital_status     TEXT,
    income             NUMERIC(12,2),
    income_group       TEXT,
    total_spend        NUMERIC(12,2),
    campaigns_accepted INT
    -- add the remaining cleaned columns you want to keep
);
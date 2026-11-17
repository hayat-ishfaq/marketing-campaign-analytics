-- Schema definition for Marketing Campaign Analytics database

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id VARCHAR(50) PRIMARY KEY,
    campaign_name VARCHAR(255) NOT NULL,
    channel VARCHAR(100),
    start_date DATE,
    end_date DATE,
    budget NUMERIC(12, 2)
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS campaign_performance (
    performance_id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(50) REFERENCES campaigns(campaign_id),
    date DATE NOT NULL,
    impressions INT DEFAULT 0,
    clicks INT DEFAULT 0,
    conversions INT DEFAULT 0,
    spend NUMERIC(10, 2) DEFAULT 0.00,
    revenue NUMERIC(10, 2) DEFAULT 0.00
);

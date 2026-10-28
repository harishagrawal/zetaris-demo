CREATE OR REPLACE VIEW virtual_fraud_alerts AS
SELECT 
    t.transaction_id,
    -- PII masking demonstration (shows only last 4 digits of account)
    CONCAT('****-****-', RIGHT(t.account_number, 4)) AS masked_account,
    t.customer_id,
    t.amount,
    t.currency,
    t.merchant_name,
    t.country_code,
    r.jurisdiction_name,
    r.risk_tier,
    r.risk_score,
    r.flag_reason,
    -- Composite exposure metric computed dynamically in-engine
    ROUND(t.amount * r.risk_score, 2) AS exposure_index,
    t.timestamp
FROM db_ops.transactions t
INNER JOIN file_compliance.risk_entities r
    ON t.country_code = r.country_code
WHERE r.risk_score >= 0.70
  AND t.amount >= 1000.00;
SELECT 
    jurisdiction_name,
    COUNT(transaction_id) AS flagged_tx_count,
    SUM(amount) AS total_flagged_volume,
    MAX(exposure_index) AS peak_single_exposure
FROM virtual_fraud_alerts
GROUP BY jurisdiction_name
ORDER BY total_flagged_volume DESC;
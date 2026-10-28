-- 1. Create Transactions Table
CREATE TABLE transactions (
    transaction_id VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(24) NOT NULL,
    account_number VARCHAR(20) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    merchant_name VARCHAR(100),
    merchant_category VARCHAR(50),
    country_code VARCHAR(2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Populate Sample Operational Transactions
INSERT INTO transactions (transaction_id, customer_id, account_number, amount, merchant_name, merchant_category, country_code, timestamp) VALUES
('TXN-1001', 'CUST-8492', 'AC-482019482', 1450.00, 'Global Lux Wire', 'Wire Transfer', 'CY', '2026-10-27 14:15:00'),
('TXN-1002', 'CUST-3104', 'AC-902814820', 45.20, 'Corner Cafe', 'Dining', 'US', '2026-10-27 14:22:10'),
('TXN-1003', 'CUST-5581', 'AC-119284719', 8200.00, 'Kestrel Mining Equipment', 'Industrial Supply', 'PA', '2026-10-27 15:01:45'),
('TXN-1004', 'CUST-9921', 'AC-559281740', 120.00, 'Local Electronics', 'Retail', 'GB', '2026-10-27 15:10:12'),
('TXN-1005', 'CUST-7740', 'AC-330192841', 19800.00, 'Seaside Trust Consult', 'Professional Services', 'VG', '2026-10-27 15:45:00'),
('TXN-1006', 'CUST-2184', 'AC-771920481', 340.50, 'Metro Rail Booking', 'Transit', 'DE', '2026-10-27 16:02:18'),
('TXN-1007', 'CUST-6032', 'AC-664019283', 6400.00, 'Apex Digital Assets', 'Crypto Gateway', 'MT', '2026-10-27 16:30:22'),
('TXN-1008', 'CUST-1190', 'AC-229104817', 15.75, 'QuickMart Supermarket', 'Grocery', 'US', '2026-10-27 16:40:05'),
('TXN-1009', 'CUST-4412', 'AC-881920391', 11500.00, 'Baltic Import Corp', 'Wholesale Trade', 'CY', '2026-10-27 17:05:30'),
('TXN-1010', 'CUST-3829', 'AC-102938475', 540.00, 'Cloud Host Infrastructure', 'Software Hosting', 'SG', '2026-10-27 17:15:10');
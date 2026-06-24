-- Query 1: Top 5 Funds by Highest Average NAV Asset Value
SELECT amfi_code, AVG(nav) as avg_nav FROM fact_nav GROUP BY amfi_code ORDER BY avg_nav DESC LIMIT 5;

-- Query 2: Average Historical NAV Per Month
SELECT d.year, d.month, f.amfi_code, AVG(f.nav) as monthly_avg_nav 
FROM fact_nav f JOIN dim_date d ON f.date_id = d.date_id GROUP BY d.year, d.month, f.amfi_code;

-- Query 3: Total Transaction Volume Split Across Categories
SELECT transaction_type, COUNT(*) as tx_count, SUM(amount_inr) as total_volume FROM fact_transactions GROUP BY transaction_type;

-- Query 4: Transactions Dense Tracking Grouped by State Codes
SELECT state, SUM(amount_inr) as state_total FROM fact_transactions GROUP BY state ORDER BY state_total DESC;

-- Query 5: Mutual Fund Schemes presenting Low Expense Ratios (< 1%)
SELECT amfi_code, scheme_name, expense_ratio_pct FROM dim_fund WHERE expense_ratio_pct < 1.0;

-- Query 6: Counts of Transactions Flagged with Incomplete/Pending KYC
SELECT kyc_status, COUNT(*) as count FROM fact_transactions GROUP BY kyc_status;

-- Query 7: Weekday vs Weekend Trading Volume Inflows
SELECT d.is_weekday, COUNT(*) as total_transactions FROM fact_transactions t 
JOIN dim_date d ON strftime('%Y%m%d', t.transaction_date) = d.date_id GROUP BY d.is_weekday;

-- Query 8: Maximum Peak Peak NAV Witnessed per Mutual Fund Scheme
SELECT amfi_code, MAX(nav) as peak_nav FROM fact_nav GROUP BY amfi_code;

-- Query 9: High Risk Scheme Volume Distribution
SELECT risk_category, COUNT(*) as fund_count FROM dim_fund GROUP BY risk_category;

-- Query 10: Total Capital Volume Aggregated per Investment Instrument Type
SELECT transaction_type, AVG(amount_inr) as average_ticket_size FROM fact_transactions GROUP BY transaction_type;
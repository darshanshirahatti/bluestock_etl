-- sql/queries.sql

-- 1. Top 5 funds by highest AUM Asset Allocation
SELECT amfi_code, aum_amount FROM fact_aum ORDER BY aum_amount DESC LIMIT 5;

-- 2. Average NAV valuation trends computed per month per fund
SELECT amfi_code, strftime('%Y-%m', date_key) AS execution_month, AVG(nav) AS average_nav 
FROM fact_nav GROUP BY amfi_code, execution_month;

-- 3. Systematic Investment Plan (SIP) Year-over-Year (YoY) Gross Growth Metrics
SELECT d.year, SUM(t.amount) AS total_sip_capital 
FROM fact_transactions t 
JOIN dim_date d ON t.transaction_date = d.date_key 
WHERE t.transaction_type = 'SIP' GROUP BY d.year;

-- 4. Gross cumulative transaction sizing spread across geographical states
SELECT state, SUM(amount) AS geographical_gross_sales, COUNT(transaction_id) AS velocity 
FROM fact_transactions GROUP BY state ORDER BY geographical_gross_sales DESC;

-- 5. Cost competitive operations list (Funds with Expense Ratio < 1%)
SELECT amfi_code, expense_ratio FROM fact_performance WHERE expense_ratio < 1.0;

-- 6. Total portfolio validation exposure categorized across fund risk grades
SELECT f.risk_grade, COUNT(t.transaction_id) AS transaction_count, SUM(t.amount) AS pooled_capital
FROM fact_transactions t JOIN dim_fund f ON t.amfi_code = f.amfi_code GROUP BY f.risk_grade;

-- 7. High-Priority compliance tracking list (Identified KYC Unverified profiles)
SELECT investor_id, amfi_code, amount FROM fact_transactions WHERE kyc_status = 'No';

-- 8. Top 5 highest performing funds based on 5-Year annualized yield return calculations
SELECT amfi_code, return_5y FROM fact_performance ORDER BY return_5y DESC LIMIT 5;

-- 9. Complete cash outflow metrics calculated based on capital redemptions
SELECT amfi_code, SUM(amount) AS total_liquidation_outflows 
FROM fact_transactions WHERE transaction_type = 'Redemption' GROUP BY amfi_code;

-- 10. Active inventory category counts present within the system ecosystem
SELECT category, COUNT(amfi_code) AS unique_schemes_count FROM dim_fund GROUP BY category;
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --- Robust Path Architecture Setup ---
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

print("🔥 Initializing Bluestock Advanced Quant Analytics Core...")

# -------------------------------------------------------------------------
# Ingestion & Market Holiday Padding (Handling Weekends)
# -------------------------------------------------------------------------
df_nav = pd.read_csv(PROCESSED_DIR / "02_nav_history_cleaned.csv", parse_dates=['date'])
df_master = pd.read_csv(PROCESSED_DIR / "01_fund_master_cleaned.csv")
df_tx = pd.read_csv(PROCESSED_DIR / "08_investor_transactions_cleaned.csv", parse_dates=['transaction_date'])
df_holdings = pd.read_csv(PROCESSED_DIR / "09_portfolio_holdings_cleaned.csv")

# Clean dates and handle holidays safely (Fixes Common Mistake)
df_nav = df_nav.sort_values(['amfi_code', 'date'])

def pad_market_holidays(group):
    full_range = pd.date_range(start=group['date'].min(), end=group['date'].max(), freq='D')
    return group.set_index('date').reindex(full_range).ffill().reset_index().rename(columns={'index': 'date'})

df_nav_clean = df_nav.groupby('amfi_code', group_keys=False).apply(pad_market_holidays)
df_nav_clean['daily_return'] = df_nav_clean.groupby('amfi_code')['nav'].pct_change()

# -------------------------------------------------------------------------
# 1. Historical VaR & CVaR (95% Confidence)
# -------------------------------------------------------------------------
print("📊 Computing VaR and CVaR for all 40 schemes...")
var_cvar_data = []

for amfi, group in df_nav_clean.groupby('amfi_code'):
    returns = group['daily_return'].dropna()
    if returns.empty: continue
    
    # 5th percentile for 95% Historical VaR
    var_95 = np.percentile(returns, 5)
    # Mean of returns below the VaR threshold for CVaR
    cvar_95 = returns[returns <= var_95].mean()
    
    var_cvar_data.append({
        'amfi_code': amfi,
        'VaR_95': var_95,
        'CVaR_95': cvar_95
    })

df_var_report = pd.DataFrame(var_cvar_data).merge(df_master[['amfi_code', 'scheme_name']], on='amfi_code')
df_var_report.to_csv(BASE_DIR / "var_cvar_report.csv", index=False)

# -------------------------------------------------------------------------
# 2. Rolling 90-Day Sharpe Ratio Plotting
# -------------------------------------------------------------------------
print("📈 Generating Rolling 90-Day Sharpe Chart for Key Funds...")
plt.figure(figsize=(12, 6))

# Filter down to 5 representative key funds
key_amfi_codes = df_nav_clean['amfi_code'].unique()[:5]
rf_daily = 0.065 / 252

for amfi in key_amfi_codes:
    sub = df_nav_clean[df_nav_clean['amfi_code'] == amfi].sort_values('date').copy()
    sub.set_index('date', inplace=True)
    
    # Calculate Rolling Metrics
    rolling_mean = sub['daily_return'].rolling(90).mean()
    rolling_std = sub['daily_return'].rolling(90).std()
    rolling_sharpe = ((rolling_mean - rf_daily) / rolling_std) * np.sqrt(252)
    
    name = df_master[df_master['amfi_code'] == amfi]['scheme_name'].values[0]
    plt.plot(rolling_sharpe.index, rolling_sharpe, label=name, linewidth=1.5)

plt.title("Rolling 90-Day Annualized Sharpe Ratio Profile Over Time", fontsize=12, fontweight='bold')
plt.xlabel("Timeline Execution Tracking")
plt.ylabel("Annualized Sharpe Value")
plt.legend(loc="upper left", fontsize=8)
plt.grid(True, linestyle=':', alpha=0.5)
plt.tight_layout()
plt.savefig(BASE_DIR / "rolling_sharpe_chart.png", dpi=300)
plt.close()

# -------------------------------------------------------------------------
# 3. Investor Cohort Analysis
# -------------------------------------------------------------------------
print("👥 Processing Investor Cohort Analysis...")
df_tx['tx_year'] = df_tx['transaction_date'].dt.year
df_tx['first_tx_year'] = df_tx.groupby('investor_id')['tx_year'].transform('min')

cohort_summary = df_tx.groupby('first_tx_year').agg(
    avg_sip_amount=('amount_inr', lambda x: x[df_tx['transaction_type'] == 'SIP'].mean()),
    total_invested=('amount_inr', 'sum')
).reset_index()

# -------------------------------------------------------------------------
# 4. SIP Continuity & At-Risk Attrition Analysis
# -------------------------------------------------------------------------
print("⏳ Executing SIP Continuity Attrition Gaps...")
df_sip = df_tx[df_tx['transaction_type'] == 'SIP'].sort_values(['investor_id', 'transaction_date'])

# Isolate investors with 6+ recurring transactions
investor_counts = df_sip['investor_id'].value_counts()
loyal_investors = investor_counts[investor_counts >= 6].index

df_sip_filtered = df_sip[df_sip['investor_id'].isin(loyal_investors)].copy()
df_sip_filtered['prev_date'] = df_sip_filtered.groupby('investor_id')['transaction_date'].shift(1)
df_sip_filtered['gap_days'] = (df_sip_filtered['transaction_date'] - df_sip_filtered['prev_date']).dt.days

investor_gaps = df_sip_filtered.groupby('investor_id')['gap_days'].mean().reset_index()
investor_gaps['Status'] = np.where(investor_gaps['gap_days'] > 35, "At-Risk", "Active")

print(f"  ↳ Isolated At-Risk Investors count: {len(investor_gaps[investor_gaps['Status'] == 'At-Risk'])}")

# -------------------------------------------------------------------------
# 5. Sector Herfindahl-Hirschman Concentration Index (HHI)
# -------------------------------------------------------------------------
print("📐 Calculating Sector HHI Concentrations...")
# HHI = Sum of squared allocation weights per fund
df_holdings['weight_fraction'] = df_holdings['weight_pct'] / 100.0
df_hhi = df_holdings.groupby('amfi_code')['weight_fraction'].apply(lambda x: np.sum(x**2)).reset_index(name='HHI_Score')
df_hhi_final = df_hhi.merge(df_master[['amfi_code', 'scheme_name']], on='amfi_code')

print("\n🏁 Advanced analytics execution pipeline written out completely!")
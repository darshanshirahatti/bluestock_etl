import numpy as np
import pandas as pd

def annualised_cagr(start_nav, end_nav, total_trading_days):
    """
    Fixes Common Mistake: Uses active trading distributions (252 metrics) 
    instead of standard calendar day estimates.
    """
    investment_years = total_trading_days / 252.0
    if investment_years <= 0 or start_nav <= 0:
        return 0.0
    return (end_nav / start_nav) ** (1.0 / investment_years) - 1.0

def compute_maximum_drawdown(nav_series):
    """
    Tracks peak-to-trough capital contractions.
    """
    if len(nav_series) < 2:
        return 0.0, None
    
    # Compute running peak metrics
    rolling_peaks = np.maximum.accumulate(nav_series)
    drawdowns = (nav_series - rolling_peaks) / rolling_peaks
    min_drawdown = drawdowns.min()
    worst_idx = drawdowns.idxmin()
    
    return min_drawdown, worst_idx

def compute_tracking_error(fund_returns, benchmark_returns):
    """
    Quantifies the tracking consistency relative to a primary benchmark.
    """
    return np.std(fund_returns - benchmark_returns, ddof=1) * np.sqrt(252)
print("Metrics computation module successfully Loaded.")
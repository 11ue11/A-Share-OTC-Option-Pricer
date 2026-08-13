"""Historical-volatility calculations based on daily closing prices."""

from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS_PER_YEAR = 252


def prepare_close_prices(data: pd.DataFrame) -> pd.Series:
    """Return a clean, chronologically sorted close-price series."""
    if "close" not in data.columns:
        raise ValueError("Price data must contain a 'close' column.")
    frame = data.copy()
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    if "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        frame = frame.dropna(subset=["date"]).sort_values("date")
    prices = frame["close"].dropna()
    prices = prices[prices > 0]
    if len(prices) < 3:
        raise ValueError("At least three valid close prices are required.")
    return prices


def historical_volatility(data: pd.DataFrame, window: int = 252) -> tuple[float, int]:
    """Calculate annualized sample volatility of log returns.

    Uses up to ``window`` most recent returns. The returned observation count
    lets the UI disclose when a supplied CSV is shorter than the selected window.
    """
    if window < 2:
        raise ValueError("The volatility window must be at least two trading days.")
    prices = prepare_close_prices(data)
    returns = np.log(prices / prices.shift(1)).dropna().tail(window)
    if len(returns) < 2:
        raise ValueError("At least two daily returns are required.")
    return float(returns.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)), len(returns)


def volatility_term_structure(data: pd.DataFrame, windows: tuple[int, ...] = (20, 60, 120, 252)) -> pd.DataFrame:
    """Build a compact historical-volatility term structure."""
    rows = []
    for window in windows:
        vol, observations = historical_volatility(data, window)
        rows.append({"Window (trading days)": window, "Annualized HV": vol, "Returns used": observations})
    return pd.DataFrame(rows)


"""Public A-share price retrieval and CSV normalization."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd


_DATE_COLUMNS = ("date", "日期", "Date", "trade_date")
_CLOSE_COLUMNS = ("close", "收盘", "Close", "close_price")


def normalize_price_frame(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize common English/Chinese CSV headers to ``date`` and ``close``."""
    date_column = next((column for column in _DATE_COLUMNS if column in data.columns), None)
    close_column = next((column for column in _CLOSE_COLUMNS if column in data.columns), None)
    if not date_column or not close_column:
        raise ValueError("CSV needs a date/日期 column and a close/收盘 column.")
    result = data[[date_column, close_column]].rename(columns={date_column: "date", close_column: "close"})
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result["close"] = pd.to_numeric(result["close"], errors="coerce")
    result = result.dropna().query("close > 0").sort_values("date").drop_duplicates("date")
    if len(result) < 3:
        raise ValueError("CSV must contain at least three valid date and close observations.")
    return result.reset_index(drop=True)


def fetch_a_share_history(symbol: str, lookback_days: int = 450) -> pd.DataFrame:
    """Fetch daily unadjusted prices through AKShare's public interface.

    This is intentionally imported lazily: CSV mode remains usable when an
    external data provider is unavailable or rate-limited.
    """
    try:
        import akshare as ak
    except ImportError as error:  # pragma: no cover - dependency is declared
        raise RuntimeError("AKShare is not installed. Use CSV mode or install requirements.txt.") from error

    end = date.today()
    start = end - timedelta(days=lookback_days)
    try:
        raw = ak.stock_zh_a_hist(
            symbol=symbol.strip(),
            period="daily",
            start_date=start.strftime("%Y%m%d"),
            end_date=end.strftime("%Y%m%d"),
            adjust="",
        )
    except Exception as error:  # pragma: no cover - provider/network dependent
        raise RuntimeError(f"Public market-data request failed: {error}") from error
    if raw is None or raw.empty:
        raise RuntimeError("No prices were returned for that code. Check the six-digit A-share ticker.")
    return normalize_price_frame(raw)


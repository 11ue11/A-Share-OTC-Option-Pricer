import pandas as pd
import pytest

from src.volatility import historical_volatility, volatility_term_structure


def test_historical_volatility_uses_available_observations():
    frame = pd.DataFrame({"date": pd.date_range("2025-01-01", periods=6), "close": [10, 11, 10.5, 11.5, 12, 11.8]})
    value, observations = historical_volatility(frame, window=20)
    assert observations == 5
    assert value > 0


def test_term_structure_has_standard_windows():
    frame = pd.DataFrame({"date": pd.date_range("2025-01-01", periods=10), "close": range(10, 20)})
    result = volatility_term_structure(frame, windows=(2, 5))
    assert result["Window (trading days)"].tolist() == [2, 5]
    assert list(result["Returns used"]) == [2, 5]


def test_rejects_missing_close_column():
    with pytest.raises(ValueError, match="close"):
        historical_volatility(pd.DataFrame({"date": ["2025-01-01", "2025-01-02", "2025-01-03"]}))


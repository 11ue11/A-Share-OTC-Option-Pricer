from math import exp

import pytest

from src.pricing import price_european_option


def test_known_black_scholes_call_price():
    result = price_european_option(
        spot=100, strike=100, maturity_years=1, rate=0.05,
        volatility=0.20, dividend_yield=0, option_type="call",
    )
    assert result.price == pytest.approx(10.4506, abs=0.0002)
    assert result.delta == pytest.approx(0.6368, abs=0.0002)


def test_put_call_parity():
    inputs = dict(spot=100, strike=105, maturity_years=0.75, rate=0.03, volatility=0.24, dividend_yield=0.01)
    call = price_european_option(**inputs, option_type="call")
    put = price_european_option(**inputs, option_type="put")
    expected = inputs["spot"] * exp(-inputs["dividend_yield"] * inputs["maturity_years"]) - inputs["strike"] * exp(-inputs["rate"] * inputs["maturity_years"])
    assert call.price - put.price == pytest.approx(expected, abs=1e-10)


def test_rejects_expired_option():
    with pytest.raises(ValueError, match="maturity"):
        price_european_option(100, 100, 0, 0.02, 0.2)


"""Black-Scholes-Merton pricing and Greeks for European options."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log, sqrt

from scipy.stats import norm


@dataclass(frozen=True)
class OptionResult:
    """Theoretical price and standard Greeks in market-friendly units."""

    price: float
    delta: float
    gamma: float
    vega_per_1pct: float
    theta_per_day: float
    rho_per_1pct: float
    d1: float
    d2: float


def _validate_inputs(spot: float, strike: float, maturity_years: float, rate: float,
                     volatility: float, dividend_yield: float, option_type: str) -> str:
    if spot <= 0 or strike <= 0:
        raise ValueError("Spot and strike must both be positive.")
    if maturity_years <= 0:
        raise ValueError("Time to maturity must be positive.")
    if volatility <= 0:
        raise ValueError("Volatility must be positive.")
    if not all(map(lambda value: value == value, [rate, volatility, dividend_yield])):
        raise ValueError("Rate, volatility, and dividend yield must be valid numbers.")
    normalized = option_type.lower().strip()
    if normalized not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'.")
    return normalized


def price_european_option(
    spot: float,
    strike: float,
    maturity_years: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
    option_type: str = "call",
) -> OptionResult:
    """Price a European option under Black-Scholes-Merton.

    Rates and volatility are expressed as decimals (e.g. 0.20 for 20%).
    Vega and rho are reported for a one percentage-point move. Theta is per
    calendar day. The formula assumes a continuous dividend yield.
    """

    kind = _validate_inputs(
        spot, strike, maturity_years, rate, volatility, dividend_yield, option_type
    )
    root_time = sqrt(maturity_years)
    discount_r = exp(-rate * maturity_years)
    discount_q = exp(-dividend_yield * maturity_years)
    d1 = (
        log(spot / strike)
        + (rate - dividend_yield + 0.5 * volatility**2) * maturity_years
    ) / (volatility * root_time)
    d2 = d1 - volatility * root_time
    density = norm.pdf(d1)

    if kind == "call":
        price = spot * discount_q * norm.cdf(d1) - strike * discount_r * norm.cdf(d2)
        delta = discount_q * norm.cdf(d1)
        theta_annual = (
            -spot * discount_q * density * volatility / (2 * root_time)
            - rate * strike * discount_r * norm.cdf(d2)
            + dividend_yield * spot * discount_q * norm.cdf(d1)
        )
        rho = strike * maturity_years * discount_r * norm.cdf(d2)
    else:
        price = strike * discount_r * norm.cdf(-d2) - spot * discount_q * norm.cdf(-d1)
        delta = discount_q * (norm.cdf(d1) - 1)
        theta_annual = (
            -spot * discount_q * density * volatility / (2 * root_time)
            + rate * strike * discount_r * norm.cdf(-d2)
            - dividend_yield * spot * discount_q * norm.cdf(-d1)
        )
        rho = -strike * maturity_years * discount_r * norm.cdf(-d2)

    gamma = discount_q * density / (spot * volatility * root_time)
    vega = spot * discount_q * density * root_time
    return OptionResult(
        price=price,
        delta=delta,
        gamma=gamma,
        vega_per_1pct=vega / 100,
        theta_per_day=theta_annual / 365,
        rho_per_1pct=rho / 100,
        d1=d1,
        d2=d2,
    )


"""Streamlit interface for the A-share OTC option pricer."""

from __future__ import annotations

from datetime import date, timedelta
from io import BytesIO
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.market_data import fetch_a_share_history, normalize_price_frame
from src.pricing import price_european_option
from src.volatility import historical_volatility, volatility_term_structure


st.set_page_config(page_title="A-Share OTC Option Pricer", page_icon="📈", layout="wide")

st.title("A-Share OTC Option Pricer")
st.caption(
    "Black–Scholes–Merton theoretical pricing for European-style OTC options, "
    "using annualized historical volatility as a proxy for implied volatility."
)

with st.sidebar:
    st.header("Contract inputs")
    option_type = st.selectbox("Option type", ("Call", "Put"))
    strike = st.number_input("Strike (CNY)", min_value=0.01, value=1500.0, step=1.0)
    maturity = st.date_input("Maturity", value=date.today() + timedelta(days=90), min_value=date.today() + timedelta(days=1))
    risk_free_rate = st.number_input("Risk-free rate (%)", min_value=-20.0, max_value=50.0, value=1.50, step=0.05) / 100
    dividend_yield = st.number_input("Continuous dividend yield (%)", min_value=0.0, max_value=50.0, value=0.00, step=0.05) / 100
    hv_window = st.selectbox("Historical-volatility window", (20, 60, 120, 252), index=3)

st.subheader("Market-data source")
source = st.radio(
    "Choose a source",
    ("Public A-share data (AKShare)", "Upload CSV", "Included sample CSV"),
    index=2,
    horizontal=True,
    help="The included sample is the most reliable choice for a live presentation. Public sources can be rate-limited or temporarily unavailable.",
)

prices: pd.DataFrame | None = None
source_note = ""
try:
    if source == "Public A-share data (AKShare)":
        symbol = st.text_input("Six-digit A-share ticker", value="600519", help="Examples: 600519, 000001, 300750")
        if st.button("Retrieve public prices", type="primary"):
            with st.spinner("Retrieving public price history…"):
                prices = fetch_a_share_history(symbol)
            st.session_state["price_data"] = prices
            st.session_state["source_note"] = f"Public daily history for {symbol.strip()}."
        prices = st.session_state.get("price_data", prices)
        source_note = st.session_state.get("source_note", "Select Retrieve public prices to load a ticker.")
    elif source == "Upload CSV":
        uploaded = st.file_uploader("CSV with date/close or 日期/收盘 columns", type="csv")
        if uploaded:
            prices = normalize_price_frame(pd.read_csv(uploaded))
            source_note = f"Uploaded file: {uploaded.name}"
    else:
        sample_path = ROOT / "data" / "sample_prices.csv"
        prices = normalize_price_frame(pd.read_csv(sample_path))
        source_note = "Included illustrative sample data (not live market data)."
except RuntimeError as error:
    if source == "Public A-share data (AKShare)":
        sample_path = ROOT / "data" / "sample_prices.csv"
        prices = normalize_price_frame(pd.read_csv(sample_path))
        source_note = (
            "Public market data is temporarily unavailable. The app has switched to its "
            "included illustrative sample so the pricing workflow remains available."
        )
        st.warning(f"{error} Using the included sample CSV instead.")
    else:
        st.error(str(error))
except (ValueError, pd.errors.ParserError) as error:
    st.error(str(error))

if prices is None:
    st.info("Load prices from one of the sources above to calculate a theoretical value.")
    st.stop()

try:
    spot = float(prices.iloc[-1]["close"])
    sigma, observations = historical_volatility(prices, hv_window)
    days_to_maturity = (maturity - date.today()).days
    maturity_years = days_to_maturity / 365.0
    result = price_european_option(
        spot=spot,
        strike=strike,
        maturity_years=maturity_years,
        rate=risk_free_rate,
        volatility=sigma,
        dividend_yield=dividend_yield,
        option_type=option_type.lower(),
    )
except ValueError as error:
    st.error(str(error))
    st.stop()

st.caption(source_note)
st.caption(f"Latest close date: {prices.iloc[-1]['date'].date():%Y-%m-%d} · {observations} return observations used for {hv_window}D HV")

metric_a, metric_b, metric_c, metric_d = st.columns(4)
metric_a.metric("Latest close (CNY)", f"¥{spot:,.2f}")
metric_b.metric("Annualized historical volatility", f"{sigma:.2%}")
metric_c.metric(f"{option_type} theoretical value", f"¥{result.price:,.2f}")
metric_d.metric("Days to maturity", str(days_to_maturity))

left, right = st.columns((1.15, 1))
with left:
    st.subheader("Price history")
    chart_data = prices.set_index("date")[["close"]].rename(columns={"close": "Close (CNY)"})
    st.line_chart(chart_data, height=310)

with right:
    st.subheader("Greeks")
    greeks = pd.DataFrame(
        {
            "Greek": ["Delta", "Gamma", "Vega", "Theta", "Rho"],
            "Value": [result.delta, result.gamma, result.vega_per_1pct, result.theta_per_day, result.rho_per_1pct],
            "Unit": ["per CNY spot move", "per CNY² spot move", "per 1 vol point", "per calendar day", "per 1 rate point"],
        }
    )
    st.dataframe(greeks, hide_index=True, use_container_width=True, column_config={"Value": st.column_config.NumberColumn(format="%.6f")})
    with st.expander("Greek conventions"):
        st.write("Vega and rho show the estimated price change for a one percentage-point increase in volatility or rates. Theta is the estimated one-calendar-day time decay, holding other inputs constant.")

st.subheader("Historical-volatility term structure")
term = volatility_term_structure(prices)
st.dataframe(
    term,
    hide_index=True,
    use_container_width=True,
    column_config={"Annualized HV": st.column_config.NumberColumn(format="%.2%%")},
)

st.subheader("Volatility scenario analysis")
scenario_vols = [max(0.01, sigma - 0.10), max(0.01, sigma - 0.05), sigma, sigma + 0.05, sigma + 0.10]
scenarios = []
for scenario_sigma in scenario_vols:
    scenario_result = price_european_option(spot, strike, maturity_years, risk_free_rate, scenario_sigma, dividend_yield, option_type.lower())
    scenarios.append({"Annualized volatility": scenario_sigma, "Theoretical value (CNY)": scenario_result.price})
scenario_frame = pd.DataFrame(scenarios)
st.dataframe(
    scenario_frame,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Annualized volatility": st.column_config.NumberColumn(format="%.2%%"),
        "Theoretical value (CNY)": st.column_config.NumberColumn(format="¥%.2f"),
    },
)

with st.expander("Methodology and limitations"):
    st.markdown(
        """
        - Historical volatility is estimated from daily log returns and annualized using 252 trading days.
        - The model assumes a European exercise style, lognormal prices, constant rates and volatility, and a continuous dividend yield.
        - Historical volatility is a proxy—not a substitute—for an executable implied-volatility surface. This output is a theoretical benchmark, not a dealer quote or investment recommendation.
        - Public-data availability and adjustments can vary. Use independently verified data for any production or trading purpose.
        """
    )

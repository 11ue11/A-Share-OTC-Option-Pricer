# A-Share OTC Option Pricer

A Streamlit-based theoretical pricing tool for European-style A-share OTC options. It retrieves public daily price history or accepts a CSV, estimates annualized historical volatility, and applies the Black–Scholes–Merton (BSM) model to calculate option value, Greeks, volatility term structure, and volatility scenarios.

> **Scope:** This is an interview-case study and educational tool. It produces a theoretical benchmark—not an executable dealer quote, investment recommendation, or production trading valuation.

## Features

- Public A-share daily price retrieval through AKShare, with CSV and included-sample fallbacks
- Annualized historical volatility using daily log returns and a 252-trading-day convention
- European Call and Put pricing with continuous dividend yield
- Delta, Gamma, Vega, Theta, and Rho, with explicit market-friendly units
- 20D / 60D / 120D / 252D historical-volatility term structure
- Volatility sensitivity analysis
- Unit tests for a standard BSM reference price and put–call parity

## Methodology

For daily close prices \(P_t\), the application uses log returns \(\ln(P_t/P_{t-1})\). Historical volatility is the sample standard deviation of a chosen window of daily returns, annualized by \(\sqrt{252}\). That volatility is used as the BSM volatility input alongside:

| Input | Description |
|---|---|
| `S` | Latest observed closing price |
| `K` | Strike price |
| `T` | Remaining maturity in years, using calendar days / 365 |
| `r` | Continuously compounded risk-free rate (user input) |
| `q` | Continuous dividend yield (user input) |
| `σ` | Annualized historical volatility |

The model assumes European exercise, lognormal underlying prices, constant volatility/rates, frictionless hedging, and a continuous dividend yield. In an OTC setting, a dealer quote would normally also reflect an implied-volatility surface/skew, discrete dividends, funding, hedge costs, liquidity, credit, and markup.

## Run locally

The project was verified with Python 3.12. Create an isolated environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Start the interface:

```bash
streamlit run app.py
```

Then open the local address Streamlit displays (normally `http://localhost:8501`). Select **Included sample CSV** to explore the application without relying on an external data provider.

## Test

```bash
python -m pytest -q
```

## Project structure

```text
.
├── app.py                 # Streamlit UI
├── data/sample_prices.csv # Illustrative fallback data
├── src/
│   ├── market_data.py     # AKShare retrieval and CSV normalization
│   ├── pricing.py         # BSM pricing and Greeks
│   └── volatility.py      # Historical-volatility calculations
├── tests/                 # Unit tests
├── DEPLOYMENT.md          # GitHub and Streamlit deployment guide
└── requirements.txt
```

## Data notes

The public-data path depends on an external provider and may be affected by availability, rate limits, corporate-action treatment, or symbol conventions. CSV upload is provided as a reproducible fallback. The supplied `data/sample_prices.csv` is illustrative and is **not** live market data.

## Interview summary

> I built a Black–Scholes–Merton based A-share OTC option-pricing tool that retrieves public historical prices, estimates annualized historical volatility, and produces theoretical option prices, Greeks, and volatility sensitivity analysis. Because historical volatility is used as a proxy for implied volatility, the output should be interpreted as a theoretical benchmark rather than an executable OTC dealer quote.


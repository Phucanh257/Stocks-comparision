
Fundamental Metrics Fetching Script


This script pulls fundamental, technical, valuation, and sentiment data for one
or more stocks, then compares each stock against a peer group you define.

It is intentionally lightweight, modular, and free-plan friendly.


WHAT THIS SCRIPT DOES

For each ticker, the script produces:

TECHNICAL SNAPSHOT
- Current price
- 52-week high / low
- 50-day & 200-day moving averages
- RSI (14)

EARNINGS & ANALYST SENTIMENT
- Earnings surprise history (via Financial Modeling Prep)
- Analyst recommendation breakdown (Yahoo Finance, when available)
- Analyst target price range (low / mean / high)

INSIDER & INSTITUTIONAL ACTIVITY
- Insider buy/sell counts and net transaction value
- Institutional holders (Financial Modeling Prep when available)
- Automatic fallback to Yahoo Finance institutional ownership % if FMP data
  is unavailable

RELATIVE VALUATION VS PEERS
- P/E
- P/B
- P/S
- EV / EBITDA
- PEG
- Price / Cash Flow
- Simple over/under-valuation flags relative to peer averages


REQUIREMENTS

Python 3.9+ recommended

Required packages:
- requests
- pandas
- yfinance

Install dependencies:
    pip install requests pandas yfinance


API KEY SETUP (IMPORTANT)

This script uses Financial Modeling Prep (FMP) for some metrics such as:
- Earnings surprises
- Institutional holders (depending on availability)

HOW TO GET THE KEY:
1. Go to the Financial Modeling Prep website
2. Create a free account
3. Copy your API key

WHERE TO PUT IT:
Edit the top of this file and set:

    FMP_API_KEY = "YOUR_API_KEY_HERE"


FREE PLAN LIMITATIONS (READ THIS)


If you are using the FREE FMP plan, some metrics may be unavailable, return empty
results, or be rate-limited. This is EXPECTED behavior.

Examples:
- Institutional holder lists may be missing
- Earnings surprise history may be limited
- Some endpoints may return empty responses

BUILT-IN FALLBACKS:
- If FMP institutional data is missing, the script automatically falls back to
  Yahoo Finance institutional ownership percentage.
- If any metric is unavailable, the script prints "N/A" and continues running.

YOU CAN ALWAYS TWEAK THIS LATER:
- Swap FMP endpoints
- Replace FMP calls entirely with Yahoo Finance
- Upgrade your FMP plan without restructuring the script

Search in this file for:
    "earnings-surprises"
    "institutional-ownership"
to modify those sections.


HOW TO RUN


From the directory containing this file:

    python "Fundamental metrics fetching.py"

You will be prompted for:
1. Tickers to analyze (comma-separated)
2. Peer tickers for each main ticker (comma-separated)

Example:
    Enter tickers: AAPL, MSFT
    Enter peers for AAPL: GOOGL, AMZN, META
    Enter peers for MSFT: AAPL, GOOGL, ORCL


CUSTOMIZATION


- Valuation metrics are defined inside relative_valuation()
- All orchestration happens inside analyze_company()
- You can comment out or extend sections freely

Renaming the file to remove spaces is recommended:
    fundamental_metrics_fetching.py


DISCLAIMER


This script is for research and educational purposes only.
Data may be delayed, incomplete, or inaccurate.
Always verify important figures with official filings or trusted data sources.


import requests
import pandas as pd
import yfinance as yf

pd.set_option("display.max_columns", None)
FMP_API_KEY = "key"
BASE_URL = "key"


def get_insider_trading(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.insider_transactions

        if df is None or df.empty or 'ownership' not in df.columns or 'value' not in df.columns:
            raise ValueError("Missing required columns")

        # Filter only direct ownership (D)
        df = df[df['ownership'] == 'D']

        # Count buys (value > 0) and sells (value == 0)
        buys = df[df['value'] > 0].shape[0]
        sells = df[df['value'] == 0].shape[0]

        # Sum net value
        net_value = df['value'].dropna().sum()

        return {
            "buys": buys,
            "sells": sells,
            "net_value": f"{net_value:,.0f}",
            "executives_involved": df['name'].dropna().unique().tolist() if 'name' in df.columns else []
        }

    except Exception as e:
        print(f"Insider data failed for {ticker}: {e}")
        return {"buys": "N/A", "sells": "N/A", "net_value": "N/A", "executives_involved": []}
        return {"buys": "N/A", "sells": "N/A", "net_value": "N/A"}


def relative_valuation(target, peers):
    print(f"\n=== Relative Valuation Summary for {target['Ticker']} ===")
    metrics = ["PE Ratio", "PB Ratio", "PS Ratio", "EV/EBITDA", "PEG Ratio", "Price/Cash Flow"]
    for metric in metrics:
        peer_vals = [float(peer[metric]) for peer in peers if isinstance(peer[metric], (int, float))]
        if peer_vals:
            avg = sum(peer_vals) / len(peer_vals)
            tval = target[metric]
            if tval is not None:
                if tval > avg:
                    print(f"- {metric}: {target['Ticker']} is overvalued vs peers (avg = {avg:.2f})")
                else:
                    print(f"- {metric}: {target['Ticker']} is undervalued vs peers (avg = {avg:.2f})")
            else:
                print(f"- {metric}: Missing target metric")
        else:
            print(f"- {metric}: Not enough peer data")

def get_technical_snapshot(ticker):
    print(f"\n=== Technical Snapshot for {ticker} ===")
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        current_price = hist['Close'].iloc[-1]
        high_52w = hist['Close'].max()
        low_52w = hist['Close'].min()
        ma50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        ma200 = hist['Close'].rolling(window=200).mean().iloc[-1]
        rsi = compute_rsi(hist['Close'])

        print(f"- Current Price: ${current_price:.2f}")
        print(f"- 52-Week High: ${high_52w:.2f} ({((current_price - high_52w)/high_52w)*100:.1f}%)")
        print(f"- 50-day MA: ${ma50:.2f} | 200-day MA: ${ma200:.2f}")
        print(f"- RSI(14): {rsi:.1f}")
    except Exception as e:
        print(f"Technical snapshot failed: {e}")

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]

def get_earnings_and_sentiment(ticker):
    print(f"\n=== Earnings & Analyst Sentiment for {ticker} ===")
    try:
        earnings_url = f"{BASE_URL}/earnings-surprises/{ticker}?apikey={FMP_API_KEY}"
        response = requests.get(earnings_url)
        earnings = response.json()
        if isinstance(earnings, list) and earnings:
            for entry in earnings[:4]:
                print(f"- Quarter: {entry.get('date')} | Actual: {entry.get('actualEarningResult')} | Estimate: {entry.get('estimatedEarning')} | Surprise: {entry.get('percentageSurprise')}%")
        stock = yf.Ticker(ticker)
        rec = stock.recommendations
        if rec is not None and not rec.empty:            
            latest = rec.tail(20)
            if 'To Grade' in latest.columns:
                rating_counts = latest['To Grade'].dropna().value_counts()
                print("– Analyst Ratings (last 20):")
                for grade, count in rating_counts.items():
                    print(f"• {grade}: {count}")
            else:
                print("– Analyst Ratings (last 20): No 'To Grade' data available.")

            target = stock.info
            print(f"- Target Price: Low ${target.get('targetLowPrice', 'N/A')} | Avg ${target.get('targetMeanPrice', 'N/A')} | High ${target.get('targetHighPrice', 'N/A')}")
    except Exception as e:
        print(f"Earnings/sentiment failed: {e}")

# === Insider Transactions and Institutional Ownership ===

def get_institutional_ownership(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        percent_held = info.get("heldPercentInstitutions")
        if percent_held is None:
            percent_display = "N/A"
        else:
            percent_display = f"{percent_held * 100:.2f}%"

        return {
            "total_holders": "N/A",  
            "total_shares": percent_display,
            "top_holders": []  
        }

    except Exception as e:
        print(f"Failed to get institutional data for {ticker}: {e}")
        return {
            "total_holders": "N/A",
            "total_shares": "N/A",
            "top_holders": []
        }

def get_institutional_ownership(ticker):
    # Try FMP first
    url = f"{BASE_URL}/institutional-ownership/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and data:
            total_holders = len(data)
            total_shares = sum(entry.get("shares", 0) for entry in data)
            top_holders = sorted(data, key=lambda x: x.get("shares", 0), reverse=True)[:3]
            top_holder_names = [holder.get("holder", "N/A") for holder in top_holders]
            return {
                "total_holders": total_holders,
                "total_shares": total_shares,
                "top_holders": top_holder_names
            }

    # Fallback: Use Yahoo Finance % if FMP fails
    stock = yf.Ticker(ticker)
    info = stock.info
    percent_held = info.get("heldPercentInstitutions")
    if percent_held is not None:
        return {
            "total_holders": "N/A",
            "total_shares": f"{percent_held*100:.1f}%",
            "top_holders": []
        }

    return None

def get_ratios(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Extract valuation ratios
        pe = info.get("trailingPE")
        pb = info.get("priceToBook")
        ps = info.get("priceToSalesTrailing12Months")
        ev_ebitda = info.get("enterpriseToEbitda")
        peg = info.get("pegRatio")
        pcf = info.get("priceToCashflow")

        # Extract profitability and growth metrics
        roe = info.get("returnOnEquity")
        roa = info.get("returnOnAssets")
        net_margin = info.get("netMargins")
        eps_growth = info.get("earningsQuarterlyGrowth")
        revenue_growth = info.get("revenueGrowth")

        ratios = {
            "Ticker": ticker,
            "PE Ratio": pe,
            "PB Ratio": pb,
            "PS Ratio": ps,
            "EV/EBITDA": ev_ebitda,
            "PEG Ratio": peg,
            "Price/Cash Flow": pcf,
            "Net Margin": net_margin,
            "ROE": roe,
            "ROA": roa,
            "EPS Growth": eps_growth,
            "Revenue Growth": revenue_growth
        }

    except Exception as e:
        print(f"[ERROR] Failed to get Yahoo ratios for {ticker}: {e}")
        ratios = {
            "Ticker": ticker,
            "PE Ratio": None,
            "PB Ratio": None,
            "PS Ratio": None,
            "EV/EBITDA": None,
            "PEG Ratio": None,
            "Price/Cash Flow": None,
            "Net Margin": None,
            "ROE": None,
            "ROA": None,
            "EPS Growth": None,
            "Revenue Growth": None
        }

    # Replace None with 'N/A' for display purposes
    return {k: (v if v is not None else "N/A") for k, v in ratios.items()}

def manual_fill(row):
    for key in row:
        if row[key] is None and key != "Ticker":
            try:
                val = input(f"Enter missing value for {row['Ticker']} - {key}: ")
                row[key] = float(val)
            except:
                print(f"Skipping manual entry for {key}")
    return row


def growth_profitability_analysis(target):
    print(f"\n=== Profitability & Growth Analysis for {target['Ticker']} ===")
    
    def comment(metric, val):
        if metric == "Net Margin":
            if val > 20:
                return "Strong profitability"
            elif val >= 10:
                return "Healthy profitability"
            else:
                return "Thin margin"
        elif metric == "ROE":
            if val > 15:
                return "Excellent capital efficiency"
            elif val >= 5:
                return "Moderate return on equity"
            else:
                return "Low ROE, may indicate inefficiency"
        elif metric == "ROA":
            if val > 7:
                return "Strong asset utilization"
            elif val >= 3:
                return "Moderate return on assets"
            else:
                return "Weak ROA"
        elif metric == "EPS Growth":
            if val > 15:
                return "Strong earnings growth"
            elif val >= 5:
                return "Moderate EPS growth"
            else:
                return "Weak or stagnant EPS growth"
        elif metric == "Revenue Growth":
            if val > 15:
                return "High revenue expansion"
            elif val >= 5:
                return "Moderate revenue growth"
            else:
                return "Low revenue growth"
        return ""

    metrics = ["Net Margin", "ROE", "ROA", "EPS Growth", "Revenue Growth"]
    for metric in metrics:
        val = target[metric]
        if isinstance(val, (int, float)):
             print(f"- {metric}: {val:.2f}% — {comment(metric, val)}")
        else:
            print(f"- {metric}: {val} — No numeric data available")


def analyze_company(ticker):
    print(f"\nAnalyzing {ticker}")
    get_technical_snapshot(ticker)
    get_earnings_and_sentiment(ticker)

    target_data = get_ratios(ticker)
    target_data = {k: (v if v is not None else "N/A") for k, v in target_data.items()}

    peer_list = []
    for i in range(3):
        peer_ticker = input(f"Enter comparable ticker {i+1} for {ticker}: ").upper()
        peer_data = get_ratios(peer_ticker)
        peer_data = manual_fill(peer_data)
        peer_list.append(peer_data)

    print("\n=== Insider and Institutional Activity ===")
    insider_data = get_insider_trading(ticker)
    institutional_data = get_institutional_ownership(ticker)

    print(f"- Insider Buys: {insider_data['buys']}, Sells: {insider_data['sells']}")
    print(f"- Net Insider Trade Value: ${insider_data['net_value']}")
    
    if insider_data['executives_involved']:
        print(f"- Execs Involved: {', '.join(insider_data['executives_involved'])}")
    else:
        print("- No executive insider trades reported.")

    if institutional_data:
        print(f"- Institutional Holders: {institutional_data['total_holders']}")
        print(f"- Total Shares Held: {institutional_data['total_shares']}")
        if institutional_data['top_holders']:
            print(f"- Top Holders: {', '.join(institutional_data['top_holders'])}")
    else:
        print("- No institutional ownership data available.")

    print("\n=== Comparable Metrics ===")
    df = pd.DataFrame([target_data] + peer_list)
    print(df)

    relative_valuation(target_data, peer_list)
    growth_profitability_analysis(target_data)
    
# Main Execution
tickers = input("Enter tickers to analyze, separated by commas: ").split(",")
tickers = [t.strip().upper() for t in tickers]

for ticker in tickers:
    analyze_company(ticker)



    


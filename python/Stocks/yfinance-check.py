import yfinance as yf

def test_market_data():
    ticker = "^DJI"
    print(f"Testing {ticker}...")
    
    # We use a 'User-Agent' to look like a real Safari browser on a Mac
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15'}
    
    try:
        # We manually set the session headers
        data = yf.download(ticker, period="1d", proxy=None, headers=headers)
        if not data.empty:
            print(f"SUCCESS! Current Dow Price: {data['Close'].iloc[-1]:.2f}")
        else:
            print("FAILED: Data was empty. Yahoo is likely rate-limiting your IP address.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_market_data()
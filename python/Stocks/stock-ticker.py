import yfinance as yf
import pandas as pd
import time

# List of stock symbols
stock_symbols = ["VWO", "SOXX", "SMH", "FXAIX", "FNCMX", "AGG", "IWD", "DVY", "NVDA", 
                 "SHV", "BOTZ", "SO", "AMZN", "FSKAX", "FGRTX", "TSM", "META", "UEC", 
                 "VYM", "AMD", "NLR", "FSELX", "URA", "VOOG", "SPLG", "GLD", "ICLN", 
                 "GOOGL", "AMAT"]


# Fetch and display stock prices
def get_stock_prices():
    data = []
    for symbol in stock_symbols:
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")['Close'][-1]  # Latest close price
        data.append([symbol, price])
    return pd.DataFrame(data, columns=["Symbol", "Current Price"])

# Display the table and update frequently
while True:
    stock_df = get_stock_prices()
    print(stock_df)
    print("\nUpdating in 60 seconds...\n")
    time.sleep(60)  # Update every 60 seconds
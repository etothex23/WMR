import tkinter as tk
from tkinter import messagebox, simpledialog
import yfinance as yf
import json
import os

# File to store your investments (CRUD)
DATA_FILE = "investments.json"

class MarketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Templeton's Market Sentinel")
        self.root.geometry("500x600")
        
        # Load Data
        self.investments = self.load_data()
        
        # UI Setup
        self.create_widgets()
        self.update_market_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {"watchlist": []}

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.investments, f)

    def create_widgets(self):
        # Header for Indices
        tk.Label(self.root, text="Major Indices", font=('Arial', 14, 'bold')).pack(pady=10)
        self.index_label = tk.Label(self.root, text="Loading...", font=('Courier', 12))
        self.index_label.pack()

        # Watchlist Section
        tk.Label(self.root, text="My Watchlist", font=('Arial', 14, 'bold')).pack(pady=10)
        self.listbox = tk.Listbox(self.root, width=50)
        self.listbox.pack(padx=20)

        # Buttons (CRUD)
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Add Ticker", command=self.add_ticker).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_ticker).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Set Alert", command=self.set_alert).grid(row=0, column=2, padx=5)

    def update_market_data(self):
        try:
            # 1. Use a custom header to look like a real browser (Fixes JSONDecodeError)
            import requests
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
            
            # 2. Fetch data (Index symbols often need the ^ prefix)
            # We use period="2d" to ensure we have at least one valid closing price
            data = yf.download(["^DJI", "^GSPC", "^IXIC"], period="2d", interval="1m", progress=False)
            
            if not data.empty and 'Close' in data:
                # Get the very last valid price
                prices = data['Close'].ffill().iloc[-1]
                
                dow = prices.get('^DJI', 0)
                sp = prices.get('^GSPC', 0)
                nas = prices.get('^IXIC', 0)
                
                text = f"DOW: {dow:,.2f}\nS&P 500: {sp:,.2f}\nNASDAQ: {nas:,.2f}"
                self.index_label.config(text=text)
            else:
                self.index_label.config(text="Market Data Unavailable (Yahoo Rate Limit)")
                
            self.refresh_watchlist()
        except Exception as e:
            print(f"Update error: {e}")
        
        self.root.after(60000, self.update_market_data)

    def refresh_watchlist(self):
        self.listbox.delete(0, tk.END)
        for item in self.investments['watchlist']:
            ticker = item['symbol']
            price = yf.Ticker(ticker).fast_info['last_price']
            alert_str = f" | Alert: {item.get('alert', 'None')}"
            self.listbox.insert(tk.END, f"{ticker}: ${price:.2f}{alert_str}")
            
            # Simple Alert Logic
            if item.get('alert') and price <= item['alert']:
                messagebox.showwarning("ALERT", f"{ticker} has hit your target of {item['alert']}!")

    def add_ticker(self):
        symbol = simpledialog.askstring("Input", "Enter Ticker (e.g., DXD, AAPL):").upper()
        if symbol:
            self.investments['watchlist'].append({"symbol": symbol, "alert": None})
            self.save_data()
            self.refresh_watchlist()

    def remove_ticker(self):
        selected = self.listbox.curselection()
        if selected:
            self.investments['watchlist'].pop(selected[0])
            self.save_data()
            self.refresh_watchlist()

    def set_alert(self):
        selected = self.listbox.curselection()
        if selected:
            price = simpledialog.askfloat("Alert", "Notify me if price falls below:")
            self.investments['watchlist'][selected[0]]['alert'] = price
            self.save_data()
            self.refresh_watchlist()

if __name__ == "__main__":
    root = tk.Tk()
    app = MarketApp(root)
    root.mainloop()
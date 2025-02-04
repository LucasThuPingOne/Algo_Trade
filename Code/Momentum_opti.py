import numpy as np
import pandas as pd
from itertools import product
from datetime import datetime, timedelta
from scipy.stats import linregress

rsi_high = 75
rsi_low = 40

# Charger les données depuis Excel
def read_excel(file_path, ticker, start_date):
    df = pd.read_excel(file_path, sheet_name=ticker)
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= start_date]
    df['RET'] = pd.to_numeric(df['RET'].astype(str).str.replace(',', '.', regex=False), errors='coerce')
    return df

# Calcul des indicateurs techniques
def calculate_sma(prices, N):
    if len(prices) < N:
        return None
    return np.mean(prices[-N:])

def calculate_rsi(prices, N):
    if len(prices) < N:
        return None
    deltas = np.diff(prices)
    gain = np.mean([delta if delta > 0 else 0 for delta in deltas[-N:]])
    loss = np.mean([-delta if delta < 0 else 0 for delta in deltas[-N:]])
    if loss == 0:
        return 100
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_volatility(retu, N):
    if len(retu) < N:
        return None
    return np.std(retu[-N:])

def calculate_stochastic_oscillator(prices, N):
    if len(prices) < N:
        return None
    lowest_price = np.min(prices[-N:])
    highest_price = np.max(prices[-N:])
    return (prices[-1] - lowest_price) / (highest_price - lowest_price) * 100

def sma_trend(SMA, window):
    if len(SMA) < window:
        return None  # Pas assez de données
    recent_sma = SMA[-window:]
    x = np.arange(len(recent_sma))
    slope, _, _, _, _ = linregress(x, recent_sma)
    return slope

def EMA(previous_ema, price, window):
    multiplier = 2 / (window + 1)
    return price * multiplier + previous_ema * (1 - multiplier)

def calculate_MACD(EMA_short, EMA_long):
    MACD = EMA_short[-1] - EMA_long[-1]
    return MACD

def calculate_signal_line(MACD, signal_line, window):
    return EMA(signal_line[-1], MACD, window)

def calculate_MACD_histogram(MACD, signal_line):
    if MACD[-1] is None or signal_line[-1] is None:
        return 0
    return MACD[-1] - signal_line[-1]

# Appliquer la stratégie
def apply_strategy(df, ema_short_window, ema_long_window, rsi_window, window_signal):
    prices, EMA_short, EMA_long = [], [], []
    MACD, signal_line, MACD_histogram = [], [], []
    position, buy_price, cumulative_pnl, nb_trade, max_price = 0, 0, 0, 0, 0
    
    for _, row in df.iterrows():
        price = row["PRC"]
        prices.append(price)
        
        if len(prices) == ema_short_window:
            EMA_short.append(calculate_sma(prices, ema_short_window))
        elif len(prices) < ema_short_window:
            EMA_short.append(None)
        else:
            EMA_short.append(EMA(EMA_short[-1], price, ema_short_window))
        
        
        if len(prices) == ema_long_window:
            EMA_long.append(calculate_sma(prices, ema_long_window))
            MACD.append(calculate_MACD(EMA_short, EMA_long))
            signal_line.append(MACD[-1])
        elif len(prices) < ema_long_window:
            EMA_long.append(None)
            MACD.append(None)
            signal_line.append(None)   
        else:
            EMA_long.append(EMA(EMA_long[-1], price, ema_long_window))
            MACD.append(calculate_MACD(EMA_short, EMA_long))
            signal_line.append(calculate_signal_line(MACD[-1], signal_line, window_signal))
        
        MACD_histogram.append(calculate_MACD_histogram(MACD, signal_line))
        rsi = calculate_rsi(prices, rsi_window) if len(prices) >= rsi_window else None

        if len(EMA_short) > ema_long_window and len(EMA_long) > ema_short_window and rsi is not None:
            if position == 0 and (MACD[-1] > signal_line[-1] and rsi < rsi_low):
                position = 1
                buy_price = price
                max_price = price
            elif position == 1 and ((MACD[-1] < signal_line[-1] and rsi > rsi_high) ):
                position = 0
                cumulative_pnl += price - buy_price
                nb_trade += 1
                max_price = 0

        if position == 1:
            max_price = max(max_price, price)
    
    if position == 1:
        cumulative_pnl += prices[-1] - buy_price
        nb_trade += 1
    
    return cumulative_pnl, nb_trade

def grid_search(file_path, ticker, start_date, ema_short_range, ema_long_range, rsi_range, window_signal_range):
    df = read_excel(file_path, ticker, start_date)
    results = []

    for ema_short, ema_long, rsi_window, window_signal in product(ema_short_range, ema_long_range, rsi_range, window_signal_range):
        if ema_short >= ema_long:
            continue
        pnl, nb_trade = apply_strategy(df, ema_short, ema_long, rsi_window, window_signal)
        results.append((ema_short, ema_long, rsi_window, window_signal, pnl, nb_trade))
    
    results.sort(key=lambda x: x[4], reverse=True)
    return results

file_path = "../data/resultat_s&p500_trie.xlsx"
ticker = "AAPL"
start_date = datetime(2023, 12, 31) - timedelta(days=2 * 365)
ema_short_range = range(5, 20, 1)
ema_long_range = range(10, 30, 1)
rsi_range = range(10, 25, 1)
window_signal_range = range(5, 15, 1)

optimal_results = grid_search(file_path, ticker, start_date, ema_short_range, ema_long_range, rsi_range, window_signal_range)

if optimal_results:
    best_ema_short, best_ema_long, best_rsi, best_window_signal, best_pnl, nb_trade = optimal_results[0]
    print(f"Meilleure combinaison : EMA court = {best_ema_short}, EMA long = {best_ema_long}, RSI = {best_rsi}, Window Signal = {best_window_signal}, PnL = {best_pnl:.2f}€, Nombre de trades = {nb_trade}")
else:
    print("Aucune combinaison optimale trouvée.")


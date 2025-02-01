import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.stats import linregress

# Paramètres d'initialisation
ticker = "AAPL"
file_path = "data/resultat_s&p500_trie.xlsx"
start_date = datetime(2023, 12, 31) - timedelta(days=2 * 365)

# Paramètres des fenêtres
sma_window = 26
sma_20_window = 20
rsi_window = 30
so_window = 6
volatility_window = 20
trend_window = 4

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

# Charger les données
df = read_excel(file_path, ticker, start_date)

# Initialisation des variables
time, close, pnl, SMA, RSI, vol, vola, SMA_20, ret, SO = [], [], [], [], [], [], [], [], [], []
buy_time, buy_signal, sell_time, sell_signal = [], [], [], []
Upper_band, Lower_band = [], []
position = 0
PnL = 0
cumulative_pnl = 0
buy_price = 0
max_price = 0
total_buy_price = 0
total_sell_price = 0
nb_trade = 0

# Traiter toutes les lignes de données
for _, row in df.iterrows():
    date = row["date"]
    price = row["PRC"]
    volume = row["VOL"]
    retu = row["RETX"]

    # Mise à jour des listes
    time.append(date)
    close.append(price)
    vol.append(volume)
    ret.append(retu)

    # Calcul des indicateurs si assez de données
    sma = calculate_sma(close, sma_window)
    SMA_20.append(calculate_sma(close, sma_20_window))
    rsi = calculate_rsi(close, rsi_window)
    vola.append(calculate_volatility(close, volatility_window))
    SO.append(calculate_stochastic_oscillator(close, so_window))

    SMA.append(sma)
    RSI.append(rsi)

    if SMA_20[-1] is not None and vola[-1] is not None:
        Upper_band.append(SMA_20[-1] + 2 * vola[-1])
        Lower_band.append(SMA_20[-1] - 2 * vola[-1])
    else:
        Upper_band.append(np.nan)
        Lower_band.append(np.nan)

    # Logique de trading
    if len(SMA) > sma_window + trend_window + 1 and len(SO) > so_window:
        slope = sma_trend(SMA, window=trend_window)

        # Achat
        if position == 0 and (slope < 0) and (price > sma):
            position = 1
            buy_price = price
            max_price = price
            total_buy_price += buy_price
            buy_time.append(date)
            buy_signal.append(price)
            print(f"BUY: {date} | Price: {price:.2f}")

        # Vente
        elif position == 1 and (slope > 0) and (price < sma):
            position = 0
            sell_time.append(date)
            sell_signal.append(price)
            total_sell_price += price
            trade_pnl = price - buy_price
            cumulative_pnl += trade_pnl
            max_price = 0
            nb_trade += 1
            print(f"SELL: {date} | Price: {price:.2f} | Trade PnL: ${trade_pnl:.2f} | Cumulative PnL: ${cumulative_pnl:.2f}")

    # Mise à jour du PnL
    if position == 1:
        if price > max_price:
            max_price = price
        PnL = cumulative_pnl + price - buy_price
    else:
        PnL = cumulative_pnl

    pnl.append(PnL)

# Résultats finaux
total_return = (total_sell_price - total_buy_price) / total_buy_price * 100
print(f"Total buy price = {total_buy_price} | Total sell price = {total_sell_price} | Return = {total_return}% | Number of trades = {nb_trade}")

# Graphiques
fig, axes = plt.subplots(3, 1, figsize=(14, 7))
axes[0].scatter(buy_time, buy_signal, marker='^', color='green', label='Buy Signal', s=100)
axes[0].scatter(sell_time, sell_signal, marker='v', color='red', label='Sell Signal', s=100)
axes[0].plot(time, close, label='Close price')
axes[0].plot(time, SMA, label='SMA')
axes[0].plot(time, SMA_20, label='SMA 20')
axes[0].plot(time, Upper_band, label='Upper band', linestyle='--', color='#00004d')
axes[0].plot(time, Lower_band, label='Lower band', linestyle='--', color='#00004d')
axes[0].fill_between(time, Upper_band, Lower_band, color='gray', alpha=0.3)
axes[0].set_title("Close price with Buy/Sell Signals")
axes[0].legend(loc='upper left')

axes[1].plot(time, RSI, label='RSI')
axes[1].axhline(y=rsi_low, color='r', linestyle='--', label='RSI Low')
axes[1].axhline(y=rsi_high, color='g', linestyle='--', label='RSI High')
axes[1].set_title('RSI')
axes[1].legend(loc='upper left')

axes[2].plot(time, SO, label='SO')
axes[2].axhline(y=20, color='r', linestyle='--', label='SO Low')
axes[2].axhline(y=80, color='g', linestyle='--', label='SO High')
axes[2].set_title('Stochastic Oscillator')
axes[2].legend(loc='upper left')

plt.tight_layout()
plt.show()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.stats import linregress

# Paramètres d'initialisation
ticker = "AAPL"
file_path = "../data/resultat_s&p500_trie.xlsx"
start_date = datetime(2023, 12, 31) - timedelta(days=2 * 365)

# Paramètres des fenêtres
sma_window = 26
sma_20_window = 20
rsi_window = 13
so_window = 6
volatility_window = 20
trend_window = 4
ema_short_window = 5
ema_long_window = 23
signal_line_window=13

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
    

# Charger les données
df = read_excel(file_path, ticker, start_date)

# Initialisation des variables
time, close, pnl, vol, vola, ret = [], [], [], [], [], []
# SMA, SMA_20 = [], []
RSI = []
# SO = []
# Upper_band, Lower_band = [], []
EMA_short, EMA_long = [], []
MACD, signal_line, MACD_histogram = [], [], []

buy_time, buy_signal, sell_time, sell_signal = [], [], [], []

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
    # vola.append(calculate_volatility(close, volatility_window))

    # Calcul des indicateurs si assez de données
    # sma = calculate_sma(close, sma_window)
    # SMA_20.append(calculate_sma(close, sma_20_window))
    rsi = calculate_rsi(close, rsi_window)
    
    # SO.append(calculate_stochastic_oscillator(close, so_window))
    
    if len(close) == ema_short_window:
        EMA_short.append(calculate_sma(close, ema_short_window))
    elif len(close) < ema_short_window:
        EMA_short.append(None)
    else:
        EMA_short.append(EMA(EMA_short[-1], price, ema_short_window))
    
    
    if len(close) == ema_long_window:
        EMA_long.append(calculate_sma(close, ema_long_window))
        MACD.append(calculate_MACD(EMA_short, EMA_long))
        signal_line.append(MACD[-1])
    elif len(close) < ema_long_window:
        EMA_long.append(None)
        MACD.append(None)
        signal_line.append(None)   
    else:
        EMA_long.append(EMA(EMA_long[-1], price, ema_long_window))
        MACD.append(calculate_MACD(EMA_short, EMA_long))
        signal_line.append(calculate_signal_line(MACD[-1], signal_line, signal_line_window))
        
    
    
    MACD_histogram.append(calculate_MACD_histogram(MACD, signal_line))


    # SMA.append(sma)
    RSI.append(rsi)

    # Bollinger Bands
    # if SMA_20[-1] is not None and vola[-1] is not None:
    #     Upper_band.append(SMA_20[-1] + 2 * vola[-1])
    #     Lower_band.append(SMA_20[-1] - 2 * vola[-1])
    # else:
    #     Upper_band.append(np.nan)
    #     Lower_band.append(np.nan)

    # Logique de trading
    if len(EMA_short) > ema_long_window and len(EMA_long) > ema_short_window and rsi is not None:
        # slope = sma_trend(SMA, window=trend_window)

        # Achat
        if position == 0 and (MACD[-1] > signal_line[-1] and rsi < rsi_low):
            position = 1
            buy_price = price
            max_price = price
            total_buy_price += buy_price
            buy_time.append(date)
            buy_signal.append(price)
            print(f"BUY: {date} | Price: {price:.2f}")

        # Vente
        elif position == 1 and ((MACD[-1] < signal_line[-1] and rsi > rsi_high) ): 
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

# Vérification si une position est ouverte à la fin
if position == 1:
    total_sell_price += price  # On clôture la position au dernier prix
    trade_pnl = price - buy_price
    nb_trade += 1
    cumulative_pnl += trade_pnl
    print(f"CLOSING OPEN POSITION: {date} | Closing Price: {price:.2f} | Trade PnL: ${trade_pnl:.2f} | Cumulative PnL: ${cumulative_pnl:.2f}")

# Résultats finaux
if total_buy_price == 0:
    print('No position has been taken')
else:
    total_return = (total_sell_price - total_buy_price) / total_buy_price * 100
    print(f"Total buy price = {total_buy_price} | Total sell price = {total_sell_price} | Return = {total_return}% | Number of trades = {nb_trade} | Underlying return = {((close[-1] - close[0])  / close[0]) * 100}%")

# Graphiques
fig, axes = plt.subplots(2,1, figsize=(14, 7))
axes[0].scatter(buy_time, buy_signal, marker='^', color='green', label='Buy Signal', s=100)
axes[0].scatter(sell_time, sell_signal, marker='v', color='red', label='Sell Signal', s=100)
axes[0].plot(time, close, label='Close price')
axes[0].plot(time, EMA_short, label='EMA short')
axes[0].plot(time, EMA_long, label='EMA long')
# plt.plot(time, Upper_band, label='Upper band', linestyle='--', color='#00004d')
# plt.plot(time, Lower_band, label='Lower band', linestyle='--', color='#00004d')
# plt.fill_between(time, Upper_band, Lower_band, color='gray', alpha=0.3)
axes[0].set_title("Close price with Buy/Sell Signals")
axes[0].legend(loc='upper left')

axes[1].plot(time, MACD, label='MACD')
axes[1].plot(time, signal_line, label='Signal Line')
colors = np.where(np.array(MACD_histogram) >= 0, 'green', 'red')
axes[1].bar(time, MACD_histogram, label='MACD Histogram', color=colors)
axes[1].set_title('RSI')
axes[1].legend(loc='upper left')

# axes[2].plot(time, SO, label='SO')
# axes[2].axhline(y=20, color='r', linestyle='--', label='SO Low')
# axes[2].axhline(y=80, color='g', linestyle='--', label='SO High')
# axes[2].set_title('Stochastic Oscillator')
# axes[2].legend(loc='upper left')

plt.tight_layout()
plt.show()

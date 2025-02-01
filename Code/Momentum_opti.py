import numpy as np
import pandas as pd
from itertools import product
from datetime import datetime, timedelta
from scipy.stats import linregress

# Charger les données depuis Excel
def read_excel(file_path, ticker, start_date):
    df = pd.read_excel(file_path, sheet_name=ticker)
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= start_date]
    df['RET'] = pd.to_numeric(df['RET'].astype(str).str.replace(',', '.', regex=False), errors='coerce')
    return df

# Calcul SMA
def calculate_sma(prices, N):
    if len(prices) < N:
        return None
    return np.mean(prices[-N:])

# Calcul RSI
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

# Appliquer la stratégie
def apply_strategy(df, sma_window, so_window, window_sma_trend):
    prices, SMA, SO = [], [], []
    position = 0
    buy_price = 0
    cumulative_pnl = 0
    PnL = 0
    nb_trade = 0
    
    for _, row in df.iterrows():
        price = row["PRC"]
        prices.append(price)

        # Calcul des indicateurs
        sma = calculate_sma(prices, sma_window)
        so = calculate_stochastic_oscillator(prices, so_window)
        SMA.append(sma)
        SO.append(so)
        
        # if len(SMA) > 8:
        #     slope = sma_trend(SMA, window=4)

        if len(SMA) > sma_window+window_sma_trend+1 and len(SO) >= so_window+1:
            slope = sma_trend(SMA, window_sma_trend)
            # Logique de trading
            if position == 0 and (slope < 0) and (price > sma) and (so < 20):
                position = 1
                buy_price = price
            elif position == 1 and (slope > 0) and (price < sma) and (so > 80):
                position = 0
                trade_pnl = price - buy_price
                cumulative_pnl += trade_pnl
                nb_trade += 1

        # Mise à jour du PnL
        if position == 1:
            PnL = price - buy_price
        else:
            PnL = cumulative_pnl
    
    return PnL, nb_trade

# Recherche sur grille
def grid_search(file_path, ticker, start_date, sma_range, so_range, window_sma_trend):
    df = read_excel(file_path, ticker, start_date)
    results = []

    for sma_window, so_window in product(sma_range, so_range):
        pnl, nb_trade = apply_strategy(df, sma_window, so_window, window_sma_trend)
        results.append((sma_window, so_window, pnl, nb_trade))

    # Trier les résultats par PnL décroissant
    results.sort(key=lambda x: x[2], reverse=True)
    return results

# Paramètres
file_path = "../data/resultat_s&p500_trie.xlsx"
ticker = "AAPL"
start_date = datetime(2023, 12, 31) - timedelta(days=2 * 365)
sma_range = range(5, 31, 1)  # Fenêtres pour SMA
so_range = range(5, 25, 1)  # Fenêtres pour Stochastic Oscillator

# Exécution de la recherche sur grille
optimal_results = grid_search(file_path, ticker, start_date, sma_range, so_range, 4)

# Affichage des résultats optimaux
best_sma, best_so, best_pnl, nb_trade = optimal_results[0]
print(f"Meilleure combinaison : SMA = {best_sma}, SO = {best_so}, PnL = {best_pnl:.2f}€, Nombre de trades = {nb_trade}")
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

# Calcul EMA
def EMA(previous_ema, price, window):
    multiplier = 2 / (window + 1)
    return price * multiplier + previous_ema * (1 - multiplier)

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

# Appliquer la stratégie
def apply_strategy(df, ema_short_window, ema_long_window, rsi_window):
    prices, EMA_short, EMA_long = [], [], []
    position = 0
    buy_price = 0
    cumulative_pnl = 0
    nb_trade = 0
    max_price = 0
    
    for _, row in df.iterrows():
        price = row["PRC"]
        prices.append(price)

        # Calcul EMA
        if len(prices) == ema_short_window:
            EMA_short.append(np.mean(prices[-ema_short_window:]))
        elif len(prices) > ema_short_window:
            EMA_short.append(EMA(EMA_short[-1], price, ema_short_window))
        else:
            EMA_short.append(None)
        
        if len(prices) == ema_long_window:
            EMA_long.append(np.mean(prices[-ema_long_window:]))
        elif len(prices) > ema_long_window:
            EMA_long.append(EMA(EMA_long[-1], price, ema_long_window))
        else:
            EMA_long.append(None)

        # Calcul RSI à chaque itération
        rsi = calculate_rsi(prices, rsi_window) if len(prices) >= rsi_window else None

        # Vérification des conditions de trading
        if len(EMA_short) > ema_long_window and len(EMA_long) > ema_short_window and rsi is not None:
            if position == 0 and (EMA_short[-1] > EMA_long[-1] and rsi < rsi_low):
                position = 1
                buy_price = price
                max_price = price
            elif position == 1 and ((EMA_short[-1] < EMA_long[-1] and rsi > rsi_high) or price < 0.95 * max_price):
                position = 0
                trade_pnl = price - buy_price
                cumulative_pnl += trade_pnl
                nb_trade += 1
                max_price = 0

        # Mise à jour du max_price
        if position == 1:
            max_price = max(max_price, price)

    # Comptabiliser la dernière position si encore ouverte
    if position == 1:
        trade_pnl = prices[-1] - buy_price
        cumulative_pnl += trade_pnl
        nb_trade += 1

    return cumulative_pnl, nb_trade

# Recherche sur grille
def grid_search(file_path, ticker, start_date, ema_short_range, ema_long_range, rsi_range):
    df = read_excel(file_path, ticker, start_date)
    results = []

    for ema_short, ema_long, rsi_window in product(ema_short_range, ema_long_range, rsi_range):
        if ema_short >= ema_long:
            continue  # Éviter les EMA courtes plus longues que les EMA longues
        
        pnl, nb_trade = apply_strategy(df, ema_short, ema_long, rsi_window)
        results.append((ema_short, ema_long, rsi_window, pnl, nb_trade))

    # Trier les résultats par PnL décroissant
    results.sort(key=lambda x: x[3], reverse=True)  
    return results

# Paramètres
file_path = "../data/resultat_s&p500_trie.xlsx"
ticker = "AAPL"
start_date = datetime(2023, 12, 31) - timedelta(days=2 * 365)
ema_short_range = range(5, 15, 1)  # Fenêtres pour EMA courte
ema_long_range = range(10, 30, 1)  # Fenêtres pour EMA longue
rsi_range = range(5, 30, 1)  # Fenêtres pour RSI

# Exécution de la recherche sur grille
optimal_results = grid_search(file_path, ticker, start_date, ema_short_range, ema_long_range, rsi_range)

# Affichage des résultats optimaux
if optimal_results:
    best_ema_short, best_ema_long, best_rsi, best_pnl, nb_trade = optimal_results[0]
    print(f"Meilleure combinaison : EMA court = {best_ema_short}, EMA long = {best_ema_long}, RSI = {best_rsi}, PnL = {best_pnl:.2f}€, Nombre de trades = {nb_trade}")
else:
    print("Aucune combinaison optimale trouvée.")

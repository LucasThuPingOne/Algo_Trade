import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation
from datetime import datetime, timedelta
import time

# Paramètres d'initialisation
fichier_csv = "data/flux_financier.csv"
start_date = datetime(2023, 12, 31) - timedelta(days=2 * 365)

# Calcul des indicateurs techniques
def calculate_sma(price_series, N):
    return price_series.rolling(window=N).mean().iloc[-1]

def calculate_rsi(price_series, N):
    delta = price_series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=N).mean().iloc[-1]
    loss = -delta.where(delta < 0, 0).rolling(window=N).mean().iloc[-1]
    rs = gain / loss if loss != 0 else np.inf
    return 100 - (100 / (1 + rs))

def traiter_donnees(fichier_csv):
    # Initialisation des variables pour le traitement
    position = 0
    PnL = 0
    cumulative_pnl = 0
    buy_price = 0
    max_price = 0
    timestamps, close, pnl = [], [], []
    buy_time, buy_signal, sell_time, sell_signal = [], [], [], []
    prices = []

    # Préparer les graphiques
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    def draw_graph(i):
        axes[0].cla()
        axes[1].cla()
        
        axes[0].scatter(buy_time, buy_signal, marker='^', color='green', label='Buy Signal', s=100)
        axes[0].scatter(sell_time, sell_signal, marker='v', color='red', label='Sell Signal', s=100)
        axes[0].plot(timestamps, close, label='Close price')
        axes[0].set_title("Intersection between Close price and SMA 5 days with buy or sell indicator")
        axes[0].set_xlabel("Date")
        axes[0].set_ylabel("Price")
        axes[0].legend(loc='upper left')

        axes[1].fill_between(timestamps, pnl, where=(np.array(pnl) >= 0), color='green', alpha=0.3)
        axes[1].fill_between(timestamps, pnl, where=(np.array(pnl) < 0), color='red', alpha=0.3)
        axes[1].plot(timestamps, pnl, label='Cumulative PnL')
        axes[1].set_xlabel("Date")
        axes[1].set_ylabel("PnL")
        axes[1].set_title("PnL over time")
        axes[1].legend(loc='upper left')

    last_processed_row = 0  # Indicateur de la dernière ligne traitée

    while True:
        try:
            df = pd.read_csv(fichier_csv)

            # Vérifier si la colonne 'Date' existe
            if 'date' not in df.columns:
                raise KeyError("'Date' column not found in the CSV file.")

            # Convertir la colonne 'Date' en datetime
            df['date'] = pd.to_datetime(df['date'])

            # Ne traiter que les nouvelles lignes
            new_rows = df.iloc[last_processed_row:]

            if new_rows.empty:
                print("Aucune nouvelle ligne à traiter.")
            else:
                for _, row in new_rows.iterrows():
                    date = row['date']
                    price = row['PRC']

                    if date < start_date:
                        continue

                    # Mise à jour des listes
                    timestamps.append(date)
                    close.append(price)
                    prices.append(price)

                    # Calcul des indicateurs si assez de données
                    if len(prices) >= 5:
                        sma = calculate_sma(pd.Series(prices[-5:]), 5)
                        rsi = calculate_rsi(pd.Series(prices[-25:]), 25) if len(prices) >= 25 else None

                        # Logique de trading
                        if position == 0 and price > sma and rsi is not None and rsi <= 40:
                            position = 1
                            buy_price = price
                            max_price = price
                            buy_time.append(date)
                            buy_signal.append(price)
                        elif position == 1 and (price < sma or (rsi is not None and rsi >= 70) or price <= max_price * 0.95):
                            position = 0
                            sell_time.append(date)
                            sell_signal.append(price)
                            cumulative_pnl += price - buy_price
                            max_price = 0

                    # Mise à jour du PnL
                    if position == 1:
                        PnL = price - buy_price
                    else:
                        PnL = cumulative_pnl

                    pnl.append(PnL)

                # Mettre à jour l'indicateur de la dernière ligne traitée
                last_processed_row = len(df)

                # Animation du graphique
                draw_graph(0)  # Redessiner le graphique après chaque ligne traitée
                plt.pause(0.1)  # Pause pour permettre à l'animation de se mettre à jour

        except FileNotFoundError:
            print("Fichier CSV introuvable.")
        except KeyError as e:
            print(f"Erreur de colonne : {e}")
        except Exception as e:
            print(f"Erreur : {e}")

        time.sleep(0.5)  # Attendre 4 secondes avant de relire le fichier et traiter les nouvelles lignes

if __name__ == "__main__":
    traiter_donnees(fichier_csv)

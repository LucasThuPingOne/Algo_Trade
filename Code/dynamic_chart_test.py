import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation
from datetime import datetime, timedelta

ticker = "AAPL"
file_path = "data/resultat_s&p500_trie.xlsx"
start_date = datetime(2023, 12, 31) - timedelta(days=2 * 365)

# Charger les données depuis Excel avec gestion des exceptions
try:
    xls = pd.ExcelFile(file_path)
    if ticker not in xls.sheet_names:
        raise ValueError(f"La feuille '{ticker}' est introuvable dans le fichier.")
    df = pd.read_excel(xls, sheet_name=ticker)
except Exception as e:
    print(f"Erreur lors du chargement des données : {e}")
    exit()
    
# Prétraitement des données
df["date"] = pd.to_datetime(df['date'])
df['RET'] = pd.to_numeric(df['RET'].astype(str).str.replace(',', '.', regex=False), errors='coerce')
df = df[df['date'] >= start_date]

close = []
time = []

fig, axes =plt.subplots(1,2, figsize=(14,7))
axes[0].plot(df['date'],df['PRC'], label='Close')
def draw_graph(i):
    close.append(df['PRC'].iloc[i])
    time.append(df['date'].iloc[i])
    axes[1].cla()
    axes[1].scatter(time,close)
    axes[1].plot(time, close)
    
anima = animation.FuncAnimation(plt.gcf(),draw_graph,interval=10)

plt.show()
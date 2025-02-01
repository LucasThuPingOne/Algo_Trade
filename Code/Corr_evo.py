import pandas as pd
import matplotlib.pyplot as plt

# Charger le fichier Excel
file_path = 'data/resultat_s&p500_trie.xlsx'  # Remplacez par le chemin de votre fichier Excel
xls = pd.ExcelFile(file_path)
returns_dict = {}
price_dict = {}

# Charger les données de rendement pour les tickers choisis
tickers = ['JPM', 'BAC']
for ticker in tickers:
    df = pd.read_excel(xls, sheet_name=ticker)
    
    # Convertir la colonne "Date" en datetime et la définir comme index
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # Remplacer la virgule par un point dans la colonne 'RET' si nécessaire
    df['RET'] = df['RET'].astype(str).str.replace(',', '.', regex=False)
    
    # Convertir la colonne 'RET' en type numérique
    df['RET'] = pd.to_numeric(df['RET'], errors='coerce')
    # Supprimer les lignes avec des dates en double pour éviter les erreurs de reindexation
    df = df[~df.index.duplicated(keep='first')]
    
    # Stocker les rendements et les prix dans les dictionnaires
    returns_dict[ticker] = df['RET']
    price_dict[ticker] = df['PRC'] /  df.loc[df.index[0], 'PRC']

# Paramètres pour la corrélation glissante
window_size = 90

# Calcul de la corrélation glissante
rolling_corr = returns_dict['JPM'].rolling(window=window_size).corr(returns_dict['BAC'])

# Tracer l'évolution du coefficient de corrélation et des prix
fig, ax1 = plt.subplots(figsize=(14, 6))

# Courbe de corrélation glissante
ax1.plot(rolling_corr.index, rolling_corr, label=f'Corrélation glissante {tickers[0]}-{tickers[1]}', color='blue')
ax1.set_ylabel('Coefficient de corrélation', color='blue')
ax1.set_xlabel('Date')
ax1.legend(loc='upper left')
ax1.grid()

# Axe secondaire pour les prix des actions
ax2 = ax1.twinx()
ax2.plot(price_dict['JPM'].index, price_dict['JPM'], label=tickers[0], color='green', alpha=0.4)
ax2.plot(price_dict['BAC'].index, price_dict['BAC'], label=tickers[1], color='red', alpha=0.4)
ax2.set_ylabel('Prix des actions', color='gray')
ax2.legend(loc='upper right')

# Affichage du graphique
plt.title(f'Évolution du coefficient de corrélation et des prix des actions {tickers[0]} et {tickers[1]} sur une fenêtre de {window_size} jours')
plt.show()

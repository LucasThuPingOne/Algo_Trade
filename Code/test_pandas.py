import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import os 

tickers = ["AAPL"] #SPY: ETF S&P500, QQQ: ETF Nasdaq 

# Date de début et de fin (ici 1 an)
end_date = datetime.today()
start_date = end_date - timedelta(days = 1*365)

# Constante de la volatilité de Parkinson
k = 1 / (4 * np.log(2))

# DataFrame pour stocker la volatilité de Parkinson
parkinson_vol_df = pd.DataFrame()

for ticker in tickers:
    data = yf.download(ticker, start = start_date, end = end_date)
    # Calcul de la volatilité de Parkinson pour chaque jour
    data['ParkinsonVol'] = np.sqrt(k * (np.log(data['High'] / data['Low']))**2)
    # Ajouter la colonne de volatilité au DataFrame principal
    parkinson_vol_df[ticker] = data['ParkinsonVol']

extreme_vol_df = pd.DataFrame()

# Identifier les valeurs extrêmes à droite de la distribution
for ticker in tickers:
    # Calcul de la moyenne et de l'écart-type pour chaque ticker
    mean = parkinson_vol_df[ticker].mean()
    std = parkinson_vol_df[ticker].std()
    
    # Définir le seuil à droite (ici, 2 fois l'écart-type au-dessus de la moyenne)
    upper_bound = mean + 2 * std
    
    # Identifier les valeurs qui dépassent le seuil (à droite de la distribution)
    extreme_vol_df[ticker] = parkinson_vol_df[ticker][parkinson_vol_df[ticker] > upper_bound]

# Sauvegarder les résultats des volatilités extrêmes dans un fichier Excel
output_folder = "data/"  #CHEMIN A MODIFIER SELON VOTRE EMPLACEMENT DANS VOS DOSSIERS
output_file = os.path.join(output_folder, 'Extreme_Positive_Parkinson_Volatility.xlsx')
extreme_vol_df.to_excel(output_file)
import pandas as pd
import yfinance as yf
import os
from datetime import datetime

tickers = ['MSFT', 'AAPL', 'GOOG', 'MS', 'BAC', 'JPM', 'MRO', 'EDF', 'WTI', 'RNO.PA', 'TSLA']

end_date = datetime.today()
start_date = datetime(2024, 1, 1)

df_return = pd.DataFrame()

output_folder = r"H:\Documents\ING3\Cash\Python_Trading"  #CHEMIN A MODIFIER SELON VOTRE EMPLACEMENT DANS VOS DOSSIERS
output_file = os.path.join(output_folder, 'Corellation.xlsx')

for ticker in tickers:
    temp = yf.download(ticker, start = start_date, end = end_date)
    temp['return'] = temp['Close']/temp['Open']
    df_return[ticker] = temp['return']
    
    
corr_mat = df_return.corr()
    
print(corr_mat)

corr_mat.to_excel(output_file)


    

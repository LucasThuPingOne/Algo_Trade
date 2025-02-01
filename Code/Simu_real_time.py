import pandas as pd
import time
import csv
from datetime import datetime, timedelta

# Chemins des fichiers
fichier_excel = "data/resultat_s&p500_trie.xlsx"
fichier_csv = "data/flux_financier.csv"
ticker = "AAPL"
start_date = datetime(2023, 12, 31) - timedelta(days=2 * 365)  # Date de début

def generer_flux(fichier_excel, fichier_csv):
    # Lecture du fichier Excel pour le ticker
    df = pd.read_excel(fichier_excel, sheet_name=ticker)

    # Assurez-vous que la colonne de dates est bien en format datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])  # Conversion si nécessaire
    else:
        raise ValueError("La colonne 'Date' est absente du fichier Excel.")

    # Filtrer les données à partir de la date choisie
    df = df[df['date'] >= start_date]

    # Création ou écrasement du fichier CSV
    with open(fichier_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Écrire les en-têtes
        writer.writerow(df.columns)

    # Simuler un flux en temps réel
    for index, row in df.iterrows():
        with open(fichier_csv, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(row)
        print(f"Ligne {index + 1} envoyée : {row.values}")
        time.sleep(0.5)  # Délai de 1 seconde pour simuler un flux

if __name__ == "__main__":
    generer_flux(fichier_excel, fichier_csv)
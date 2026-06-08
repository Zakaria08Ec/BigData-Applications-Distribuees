import pandas as pd
import numpy as np
import logging

# Configuration du logging pour suivre les étapes dans pipeline.log
logging.basicConfig(
    filename='../logs/pipeline.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extract(file_path):
    """Étape 1 : Extraction des données brutes"""
    logging.info("Extraction : Chargement du fichier CSV.")
    return pd.read_csv(file_path)

def transform(df):
    """Étape 2 : Nettoyage complet des anomalies (Image 2)"""
    logging.info("Transform : Début du nettoyage des données.")
    
    # Correction Ligne 6 : Suppression du doublon exact de la ligne 2
    df = df.drop_duplicates()

    # Correction Ligne 4 : 'station' en majuscules et 'temperature' texte vers numérique
    df['station'] = df['station'].str.upper()
    df['temperature'] = df['temperature'].replace('vingt', '20.0')
    df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')

    # Correction Ligne 5 & 9 : Dates (format et dates impossibles comme 30 février)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']) # Supprime la ligne 9 (date impossible) et 15 (date manquante)

    # Correction Lignes 7, 10, 12 : Humidité manquante ou invalide (-5) et Rain manquante
    df.loc[df['humidity'] < 0, 'humidity'] = np.nan
    df['humidity'] = df['humidity'].fillna(df['humidity'].mean())
    df['rain_mm'] = df['rain_mm'].fillna(0.0)

    # Correction Ligne 8 & 11 : Outliers (Temp 999 et Vent 150)
    df.loc[df['temperature'] > 100, 'temperature'] = np.nan
    df.loc[df['wind_kmh'] > 130, 'wind_kmh'] = np.nan

    # Correction Lignes 3, 8, 13 : Irrigation (Minuscules 'off' et catégorie 'OUI')
    df['irrigation'] = df['irrigation'].str.upper().replace('OUI', 'ON')

    logging.info("Transform : Nettoyage terminé.")
    return df

def build_features(df):
    """Étape 3 : Création de 3 features vectorisées"""
    logging.info("Build Features : Création des nouvelles colonnes.")
    
    # Feature 1 : Température en Fahrenheit
    df['temp_f'] = (df['temperature'] * 9/5) + 32
    
    # Feature 2 : Indicateur de pluie (Booléen)
    df['is_raining'] = df['rain_mm'] > 0
    
    # Feature 3 : Catégorie de vent (Vectorisation avec pd.cut)
    df['wind_status'] = pd.cut(df['wind_kmh'], bins=[0, 15, 30, 200], labels=['Calme', 'Modéré', 'Fort'])
    
    return df

def load(df_clean, df_features):
    """Étape 4 : Exportation des résultats et rapport de qualité"""
    logging.info("Load : Exportation des fichiers vers /outputs.")
    
    # Export des datasets
    df_clean.to_csv('../outputs/meteo_clean.csv', index=False)
    df_features.to_csv('../outputs/meteo_features.csv', index=False)
    
    # Génération du rapport de qualité (TXT)
    with open('../outputs/quality_report.txt', 'w', encoding='utf-8') as f:
        f.write("RAPPORT DE QUALITÉ DES DONNÉES\n")
        f.write("="*30 + "\n")
        f.write(f"- Lignes traitées : {len(df_clean)}\n")
        f.write("- Anomalies corrigées : Doublons, types (vingt), dates invalides, et outliers.\n")
        f.write("- Features créées : temp_f, is_raining, wind_status.\n")

def run_pipeline():
    try:
        # Chemin vers le fichier brut créé à l'étape précédente
        input_file = '../data/raw/meteo_brut.csv'
        
        # Exécution du pipeline ETL
        df_raw = extract(input_file)
        df_transformed = transform(df_raw)
        df_final = build_features(df_transformed)
        
        load(df_transformed, df_final)
        
        print("✅ Pipeline exécuté avec succès !")
        print("Consultez les dossiers /outputs pour les résultats et /logs pour le suivi.")
        
    except Exception as e:
        logging.error(f"Erreur critique durant le pipeline : {e}")
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    run_pipeline()
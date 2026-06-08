import os
import json
import time

class RealTimeAggregator:
    def __init__(self, data_directory="data"):
        self.data_directory = data_directory

    def compute_metrics(self) -> dict:
        """Parcourt le stockage partitionné et calcule les KPIs."""
        metrics = {
            "total_commandes": 0,
            "chiffre_affaires_total": 0.0,
            "stats_par_ville": {}
        }

        if not os.path.exists(self.data_directory):
            return metrics

        # On parcourt chaque dossier (partition)
        for city in os.listdir(self.data_directory):
            city_path = os.path.join(self.data_directory, city)
            
            if os.path.isdir(city_path):
                file_path = os.path.join(city_path, "processed_orders.jsonl")
                
                if os.path.exists(file_path):
                    ville_ca = 0.0
                    ville_commandes = 0
                    
                    # On lit le fichier JSONL ligne par ligne
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                event = json.loads(line)
                                montant = event["payload"].get("amount", 0)
                                
                                ville_ca += montant
                                ville_commandes += 1
                                metrics["total_commandes"] += 1
                                metrics["chiffre_affaires_total"] += montant
                    
                    # On stocke l'agrégation pour cette ville
                    metrics["stats_par_ville"][city] = {
                        "commandes": ville_commandes,
                        "ca": round(ville_ca, 2)
                    }

        return metrics

def run_dashboard():
    """Affiche les métriques dans la console et se rafraîchit en boucle."""
    aggregator = RealTimeAggregator()
    
    while True:
        # 1. Calcul des métriques à l'instant T
        stats = aggregator.compute_metrics()
        
        # 2. Nettoyage de la console (pour faire un effet "Dashboard")
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 3. Affichage
        print("="*50)
        print(" 📊 DASHBOARD TEMPS RÉEL - SUIVI DES COMMANDES 📊 ")
        print("="*50)
        print(f"📦 Total Commandes traitées : {stats['total_commandes']}")
        print(f"💰 Chiffre d'Affaires Global : {round(stats['chiffre_affaires_total'], 2)} €")
        print("-" * 50)
        print("📍 Statistiques par Partition (Ville) :")
        
        if not stats["stats_par_ville"]:
            print("   Aucune donnée reçue pour le moment...")
        else:
            for ville, data in stats["stats_par_ville"].items():
                print(f"   ➤ {ville.upper():<10} : {data['commandes']} commandes | CA : {data['ca']} €")
                
        print("\n(Actualisation toutes les 3 secondes... Appuyez sur Ctrl+C pour quitter)")
        
        # 4. Pause avant le prochain rafraîchissement
        time.sleep(3)

if __name__ == "__main__":
    run_dashboard()
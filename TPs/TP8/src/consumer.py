import time
import json
import os

class OrderConsumer:
    def __init__(self, broker, partition_key: str, consumer_group_id: str):
        self.broker = broker
        self.partition_key = partition_key
        self.consumer_group_id = consumer_group_id
        
        # Fichier où l'on va persister notre avancement (pour ne rien perdre en cas de crash)
        self.offset_file = "offsets.json"
        
        # On charge le dernier offset connu au démarrage
        self.current_offset = self._load_offset()

    def _load_offset(self) -> int:
        """Lit le fichier offsets.json pour savoir où reprendre."""
        if not os.path.exists(self.offset_file):
            return 0  # Si le fichier n'existe pas, on commence au début (0)
            
        with open(self.offset_file, "r") as f:
            try:
                offsets = json.load(f)
                # On retourne l'offset de ce consumer spécifique, ou 0 s'il est nouveau
                return offsets.get(self.consumer_group_id, 0)
            except json.JSONDecodeError:
                return 0 # Sécurité si le fichier est vide

    def _save_offset(self, offset: int):
        """Sauvegarde le nouvel offset dans le fichier JSON."""
        offsets = {}
        if os.path.exists(self.offset_file):
            with open(self.offset_file, "r") as f:
                try:
                    offsets = json.load(f)
                except json.JSONDecodeError:
                    pass
                
        # On met à jour l'offset pour CE consumer
        offsets[self.consumer_group_id] = offset + 1
        
        with open(self.offset_file, "w") as f:
            json.dump(offsets, f, indent=4)

    def _save_to_storage(self, event: dict):
        """Sauvegarde l'événement validé dans un stockage partitionné sur disque."""
        # On crée un dossier 'data' et un sous-dossier par partition/ville (ex: data/Paris/)
        directory = f"data/{self.partition_key}"
        os.makedirs(directory, exist_ok=True)
        
        file_path = f"{directory}/processed_orders.jsonl"
        
        # Format JSON Lines : une ligne par événement (très utilisé en Big Data)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def process_event(self, event: dict):
        """La logique métier de ce consumer."""
        print(f"[{self.consumer_group_id}] ⚙️  Traitement de la commande {event['payload']['order_id']}...")
        
        # Simulation d'un traitement métier asynchrone (ex: facturation, validation stock)
        time.sleep(1) 
        
        # Une fois traité, on sauvegarde le résultat sur le disque pour le Dashboard
        self._save_to_storage(event)
        
        print(f"[{self.consumer_group_id}] ✅ Sauvegardé dans data/{self.partition_key}/")

    def start(self):
        """La boucle infinie qui interroge (poll) le broker en continu."""
        print(f"🚀 Démarrage du {self.consumer_group_id} sur la partition '{self.partition_key}' (Offset de départ : {self.current_offset})")
        
        while True:
            # 1. On demande le message à l'offset actuel
            event = self.broker.consume(self.partition_key, self.current_offset)
            
            if event:
                # 2. Si un message existe, on le traite (et on l'écrit sur le disque)
                self.process_event(event)
                
                # 3. CRITIQUE : On sauvegarde l'avancement SEULEMENT si le traitement a réussi
                self._save_offset(self.current_offset)
                
                # 4. On incrémente notre compteur local pour lire le suivant au prochain tour
                self.current_offset += 1
            else:
                # S'il n'y a pas de nouveau message, on fait une petite pause pour ne pas saturer le CPU
                time.sleep(2)


# ==========================================
# 🧪 TEST : L'écosystème complet
# ==========================================
if __name__ == "__main__":
    # Assure-toi que les fichiers broker.py et producer.py sont dans le même dossier
    from broker import MiniBroker
    from producer import OrderService 
    import threading

    # 1. Initialisation de l'infrastructure
    mon_broker = MiniBroker()
    api = OrderService(mon_broker)

    # 2. On crée deux Consumers pour des villes (partitions) différentes
    consumer_paris = OrderConsumer(mon_broker, partition_key="Paris", consumer_group_id="Consumer_Paris_01")
    consumer_lyon = OrderConsumer(mon_broker, partition_key="Lyon", consumer_group_id="Consumer_Lyon_01")

    # 3. On lance les consumers dans des Threads séparés pour qu'ils tournent en arrière-plan
    threading.Thread(target=consumer_paris.start, daemon=True).start()
    threading.Thread(target=consumer_lyon.start, daemon=True).start()

    # 4. Le Producteur génère des commandes aléatoires
    time.sleep(1) # Laisse le temps aux consumers de démarrer correctement
    
    print("\n--- Simulation de trafic client ---")
    api.place_order("Alice", 150.0, "Paris")
    api.place_order("Bob", 20.0, "Lyon") 
    api.place_order("Charlie", 99.9, "Paris")

    # On fait patienter le programme principal pour voir les logs s'afficher
    time.sleep(5)
    print("\n🏁 Test terminé. Vous pouvez vérifier la création du dossier 'data/' et du fichier 'offsets.json'.")
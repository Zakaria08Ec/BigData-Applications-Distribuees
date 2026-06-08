import json
import time
from typing import Dict, List, Optional

class MiniBroker:
    def __init__(self):
        # Dictionnaire pour stocker les partitions en mémoire.
        # Clé : Nom de la partition (ex: "Paris", "Lyon")
        # Valeur : Liste des événements (notre log append-only)
        self.partitions: Dict[str, List[dict]] = {}

    def publish(self, partition_key: str, event: dict) -> int:
        """
        Reçoit un événement et le place dans la bonne partition.
        Retourne l'offset (l'index) auquel le message a été enregistré.
        """
        # Si la partition n'existe pas encore, on la crée
        if partition_key not in self.partitions:
            self.partitions[partition_key] = []
        
        # On ajoute l'événement à la fin de la liste
        self.partitions[partition_key].append(event)
        
        # L'offset est simplement l'index de ce nouvel élément
        offset = len(self.partitions[partition_key]) - 1
        
        print(f"[Broker] 📥 Message publié dans '{partition_key}' à l'offset {offset}")
        return offset

    def consume(self, partition_key: str, offset: int) -> Optional[dict]:
        """
        Permet à un consumer de lire un message précis via son offset.
        Retourne l'événement, ou None si l'offset n'existe pas encore.
        """
        if partition_key not in self.partitions:
            return None
        
        partition_log = self.partitions[partition_key]
        
        # On vérifie que le consumer ne demande pas un message dans le futur
        if offset < 0 or offset >= len(partition_log):
            return None
        
        return partition_log[offset]

    def get_latest_offset(self, partition_key: str) -> int:
        """Utile pour savoir combien de messages contient une partition."""
        if partition_key not in self.partitions or not self.partitions[partition_key]:
            return -1
        return len(self.partitions[partition_key]) - 1

# ==========================================
# 🧪 TEST RAPIDE POUR COMPRENDRE LE FONCTIONNEMENT
# ==========================================
if __name__ == "__main__":
    # 1. On démarre notre broker
    broker = MiniBroker()

    # 2. Définition de notre "Contrat" (Un événement type)
    event_1 = {
        "event_id": "evt_9876",
        "type": "order_created",
        "timestamp": time.time(),
        "payload": {"order_id": "cmd_123", "montant": 45.50}
    }
    
    event_2 = {
        "event_id": "evt_9877",
        "type": "order_dispatched",
        "timestamp": time.time(),
        "payload": {"order_id": "cmd_123", "livreur": "Jean"}
    }

    # 3. Le Producteur publie les événements (Partitionnés par ville)
    print("--- Phase de Production ---")
    broker.publish(partition_key="Paris", event=event_1)
    broker.publish(partition_key="Paris", event=event_2)
    broker.publish(partition_key="Lyon", event={"type": "order_created", "payload": {"order_id": "cmd_999"}})

    # 4. Le Consumer lit les événements (ex: Le consumer de Paris lit l'offset 0 puis 1)
    print("\n--- Phase de Consommation ---")
    msg_0 = broker.consume(partition_key="Paris", offset=0)
    print(f"Lecture Paris Offset 0 : {msg_0['type']}")
    
    msg_1 = broker.consume(partition_key="Paris", offset=1)
    print(f"Lecture Paris Offset 1 : {msg_1['type']}")
    
    # Tentative de lire un message qui n'existe pas encore (le consumer devra patienter)
    msg_2 = broker.consume(partition_key="Paris", offset=2)
    print(f"Lecture Paris Offset 2 : {msg_2} (Pas encore de message)")
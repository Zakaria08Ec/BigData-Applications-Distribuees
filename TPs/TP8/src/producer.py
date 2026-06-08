import time
import uuid

class OrderService:
    def __init__(self, broker):
        # Le service a besoin de connaître le broker pour y envoyer les messages
        self.broker = broker

    def place_order(self, customer_name: str, amount: float, city: str) -> dict:
        """
        Méthode SYNCHRONE : Appelée par l'utilisateur (ou une interface web).
        """
        print(f"\n[Service Commande] 🛒 Réception d'une commande de {customer_name} ({city})...")

        # 1. Validation métier basique
        if amount <= 0:
            return {"status": "error", "message": "Le montant doit être supérieur à 0."}

        # 2. Génération d'un ID de commande unique
        order_id = f"cmd_{uuid.uuid4().hex[:8]}"

        # 3. Création de l'événement (Le fameux "Contrat JSON")
        event = {
            "event_id": f"evt_{uuid.uuid4().hex[:12]}",
            "type": "order_created",
            "timestamp": time.time(),
            "partition_key": city, # On utilise la ville comme clé de partition
            "payload": {
                "order_id": order_id,
                "customer": customer_name,
                "amount": amount,
            }
        }

        # 4. Le "Producteur" entre en jeu : publication dans le broker
        # L'événement est assigné à la partition correspondant à la ville
        self.broker.publish(partition_key=city, event=event)

        # 5. Réponse immédiate au client (pendant que l'événement est dans le broker)
        return {
            "status": "success", 
            "order_id": order_id, 
            "message": "Commande acceptée et en cours de traitement."
        }

# ==========================================
# 🧪 TEST : Lier le Broker et le Producteur
# ==========================================
if __name__ == "__main__":
    # Importer le broker qu'on a créé précédemment (si dans un autre fichier)
    from broker import MiniBroker 
    
    # Initialisation
    mon_broker = MiniBroker()
    api_commande = OrderService(broker=mon_broker)

    # Simulation d'utilisateurs qui passent commande en même temps
    reponse_1 = api_commande.place_order(customer_name="Alice", amount=120.50, city="Paris")
    print(f"[Client] Réponse reçue : {reponse_1}\n")

    reponse_2 = api_commande.place_order(customer_name="Bob", amount=45.00, city="Lyon")
    print(f"[Client] Réponse reçue : {reponse_2}\n")
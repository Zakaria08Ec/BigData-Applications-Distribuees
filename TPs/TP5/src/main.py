# src/main.py
import threading
import logging
import os
import time
import json
import queue

from .messages import EventMessage
from .producers import burst_producer
from .workers import worker_loop
from .metrics import PipelineMetrics, monitor_loop
from .storage import CSVStorage
from .pipeline import Pipeline

def main():
    os.makedirs("logs", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(threadName)s] %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("logs/pipeline.log", mode="w"),
            logging.StreamHandler(),
        ]
    )

    # Composants
    pipe = Pipeline(maxsize=50)
    metrics = PipelineMetrics()
    storage = CSVStorage("outputs/valid_readings.csv")

    # Lancer les workers (2)
    for i in range(2):
        t = threading.Thread(
            target=worker_loop,
            args=(pipe.main_queue, pipe.dead_letter_queue, storage, metrics,
                  pipe.stop_event, f"Worker-{i+1}"),
            name=f"Worker-{i+1}", daemon=True
        )
        t.start()
        pipe.threads.append(t)

    # Lancer le moniteur
    t_mon = threading.Thread(
        target=monitor_loop,
        args=(pipe.main_queue, metrics, pipe.stop_event, 2),
        name="Monitor", daemon=True
    )
    t_mon.start()
    pipe.threads.append(t_mon)

    # Lancer les producteurs (3)
    prod_threads = []
    for i in range(3):
        t = threading.Thread(
            target=burst_producer,
            args=(pipe.main_queue, f"Prod-{i+1}", 5, 30, 0.5),
            name=f"Prod-{i+1}"
        )
        t.start()
        prod_threads.append(t)

    # Attendre la fin des producteurs
    for t in prod_threads:
        t.join()
    logging.info("Tous les producteurs ont terminé.")

    # Attendre que la queue se vide
    pipe.main_queue.join()
    logging.info("Queue vidée.")

    # Shutdown
    pipe.shutdown(timeout=5)

    # Résultats
    snap = metrics.snapshot()
    logging.info(f"=== RÉSULTAT FINAL ===")
    logging.info(f"Messages traités avec succès : {snap['success']}")
    logging.info(f"Messages échoués (DLQ)       : {snap['failures']}")
    logging.info(f"Retries effectués             : {snap['retries']}")
    logging.info(f"Débit moyen                   : {snap['rate_per_sec']} msg/s")
    logging.info(f"Latence moyenne               : {snap['avg_latency_ms']} ms")

    # Sauvegarder DLQ
    dead = []
    while not pipe.dead_letter_queue.empty():
        try:
            msg = pipe.dead_letter_queue.get_nowait()
            dead.append(msg.to_dict())
        except queue.Empty:
            break
    with open("outputs/dead_letters.json", "w") as f:
        json.dump(dead, f, indent=2, default=str)
    logging.info(f"Dead-letters sauvegardés : {len(dead)}")

    # Agrégation
    agg = storage.aggregate()
    logging.info(f"Agrégation par capteur : {json.dumps(agg, indent=2)}")

    # Assertions de base
    assert snap["success"] > 0, "Aucun message traité !"
    assert snap["success"] + snap["failures"] + snap["retries"] > 0
    logging.info("✅ Toutes les assertions passent.")

if __name__ == "__main__":
    main()
# src/producers.py
import queue
import time
import random
import logging
from .messages import EventMessage

VALID_RANGE = {"temperature": (-20, 60), "humidity": (0, 100), "luminosity": (0, 2000)}

def burst_producer(q: queue.Queue, name: str, bursts: int = 5,
                   burst_size: int = 30, pause: float = 0.5):
    """Produit des rafales de messages IoT."""
    sensors = [f"sensor-{name[-1]}{i}" for i in range(1, 4)]
    metrics = list(VALID_RANGE.keys())
    produced = 0
    for b in range(bursts):
        for _ in range(burst_size):
            metric = random.choice(metrics)
            # 10% de valeurs invalides
            if random.random() < 0.1:
                value = -999.0
            else:
                lo, hi = VALID_RANGE[metric]
                value = round(random.uniform(lo, hi), 2)
            msg = EventMessage(
                msg_type="sensor_reading",
                payload={
                    "sensor_id": random.choice(sensors),
                    "metric": metric,
                    "value": value,
                }
            )
            try:
                q.put(msg, timeout=2)
                produced += 1
            except queue.Full:
                logging.warning(f"[{name}] Queue PLEINE — message droppé {msg.msg_id[:8]}")
            time.sleep(random.uniform(0.005, 0.02))
        logging.info(f"[{name}] Burst {b+1}/{bursts} terminé ({produced} msg)")
        time.sleep(pause)
    logging.info(f"[{name}] Terminé : {produced} messages produits")
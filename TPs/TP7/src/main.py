# src/main.py
import argparse, logging, threading, time, random
from pathlib import Path
from .events import make_random_event
from .broker import Broker
from .offsets import OffsetStore
from .storage import Storage
from .metrics import Metrics
from .consumers import Consumer, assign

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s :: %(message)s",
    handlers=[logging.FileHandler("logs/run.log"), logging.StreamHandler()]
)
log = logging.getLogger("main")

SENSORS = [f"sensor-{i:02d}" for i in range(1, 11)] + ["sensor-HOT-01"] * 5
SITES = ["SITE-01", "SITE-02", "SITE-03", "SITE-04"]

def producer_loop(broker: Broker, stop_event, rate_ms: int):
    while not stop_event.is_set():
        evt = make_random_event(random.choice(SENSORS), random.choice(SITES))
        broker.publish(evt)
        time.sleep(rate_ms / 1000)

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--partitions", type=int, default=4)
    p.add_argument("--consumers", type=int, default=2)
    p.add_argument("--key-field", default="sensor_id")
    p.add_argument("--producer-rate", type=int, default=50)
    p.add_argument("--consumer-delay", type=int, default=30)
    p.add_argument("--commit-every", type=int, default=5)
    p.add_argument("--duration", type=int, default=30)
    p.add_argument("--group", default="agri-stats")
    return p.parse_args()

def main():
    args = parse_args()
    Path("logs").mkdir(exist_ok=True)
    broker = Broker(args.partitions, args.key_field)
    offsets = OffsetStore("state/offsets.json")
    storage = Storage("outputs")
    metrics = Metrics(broker, offsets, args.group)

    consumer_ids = [f"C{i}" for i in range(args.consumers)]
    assignment = assign(args.partitions, consumer_ids)
    log.info("assignment: %s", assignment)

    stop_event = threading.Event()
    consumers = []
    for cid in consumer_ids:
        c = Consumer(cid, assignment[cid], broker, offsets, storage, metrics,
                     args.group, args.consumer_delay, args.commit_every, stop_event)
        c.start()
        consumers.append(c)

    prod_thread = threading.Thread(target=producer_loop,
                                    args=(broker, stop_event, args.producer_rate),
                                    daemon=True)
    prod_thread.start()

    t0 = time.time()
    try:
        while time.time() - t0 < args.duration:
            time.sleep(2)
            log.info("[metrics] %s", metrics.snapshot())
    except KeyboardInterrupt:
        log.warning("interruption clavier, arrêt propre…")
    finally:
        stop_event.set()
        for c in consumers: c.join(timeout=3)
        prod_thread.join(timeout=2)
        log.info("final offsets: %s", offsets._data)

if __name__ == "__main__":
    main()
# src/consumers.py
import threading, time, logging
from .broker import Broker
from .offsets import OffsetStore
from .storage import Storage
from .metrics import Metrics

log = logging.getLogger("consumers")

def assign(num_partitions: int, consumer_ids: list[str]) -> dict[str, list[int]]:
    assignment = {cid: [] for cid in consumer_ids}
    for p in range(num_partitions):
        cid = consumer_ids[p % len(consumer_ids)]
        assignment[cid].append(p)
    return assignment

class Consumer(threading.Thread):
    def __init__(self, cid, partitions, broker: Broker,
                 offsets: OffsetStore, storage: Storage,
                 metrics: Metrics, group: str,
                 delay_ms=30, commit_every=5, stop_event=None):
        super().__init__(name=cid, daemon=True)
        self.cid = cid
        self.partitions = partitions
        self.broker = broker
        self.offsets = offsets
        self.storage = storage
        self.metrics = metrics
        self.group = group
        self.delay = delay_ms / 1000
        self.commit_every = commit_every
        self.stop_event = stop_event

    def run(self):
        log.info("[%s] assigned partitions: %s", self.cid, self.partitions)
        counters = {p: 0 for p in self.partitions}
        while not self.stop_event.is_set():
            progressed = False
            for p in self.partitions:
                off = self.offsets.get(self.group, p)
                evt = self.broker.fetch(p, off)
                if evt is None:
                    continue
                # traitement : stockage + métriques
                self.storage.write(evt, p)
                self.metrics.mark_processed(self.cid, p)
                time.sleep(self.delay)
                new_off = off + 1
                counters[p] += 1
                if counters[p] % self.commit_every == 0:
                    self.offsets.commit(self.group, p, new_off)
                else:
                    self.offsets.set_memory(self.group, p, new_off)
                progressed = True
            if not progressed:
                time.sleep(0.05)
        # Flush final
        for p in self.partitions:
            self.offsets.flush(self.group, p)
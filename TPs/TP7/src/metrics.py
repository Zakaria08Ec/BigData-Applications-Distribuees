# src/metrics.py
import threading, time
from collections import deque, defaultdict
from .broker import Broker
from .offsets import OffsetStore

class Metrics:
    def __init__(self, broker: Broker, offsets: OffsetStore, group: str, window_s=5):
        self.broker = broker
        self.offsets = offsets
        self.group = group
        self.window = window_s
        self._history = defaultdict(deque)  # consumer -> deque[timestamps]
        self._lock = threading.Lock()

    def mark_processed(self, consumer: str, partition: int):
        now = time.time()
        with self._lock:
            dq = self._history[consumer]
            dq.append(now)
            while dq and now - dq[0] > self.window:
                dq.popleft()

    def snapshot(self) -> dict:
        backlog = {}
        total_lag = 0
        for p in range(self.broker.num_partitions):
            sz = self.broker.size(p)
            off = self.offsets.get(self.group, p)
            backlog[p] = max(0, sz - off)
            total_lag += backlog[p]
        throughput = {}
        with self._lock:
            for c, dq in self._history.items():
                throughput[c] = round(len(dq) / self.window, 2)
        return {"backlog": backlog, "lag": total_lag, "throughput": throughput}
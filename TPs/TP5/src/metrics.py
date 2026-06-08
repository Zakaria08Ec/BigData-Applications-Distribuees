# src/metrics.py
import threading
import time
import queue as queue_mod
import logging

class PipelineMetrics:
    def __init__(self):
        self._lock = threading.Lock()
        self.success = 0
        self.failures = 0
        self.retries = 0
        self.total_latency = 0.0
        self.start_time = time.time()

    def record_success(self, latency: float):
        with self._lock:
            self.success += 1
            self.total_latency += latency

    def record_failure(self):
        with self._lock:
            self.failures += 1

    def record_retry(self):
        with self._lock:
            self.retries += 1

    def snapshot(self) -> dict:
        with self._lock:
            elapsed = time.time() - self.start_time
            rate = self.success / elapsed if elapsed > 0 else 0
            avg_lat = (self.total_latency / self.success) if self.success else 0
            return {
                "success": self.success,
                "failures": self.failures,
                "retries": self.retries,
                "rate_per_sec": round(rate, 1),
                "avg_latency_ms": round(avg_lat * 1000, 1),
                "elapsed_sec": round(elapsed, 1),
            }

def monitor_loop(q: queue_mod.Queue, metrics: PipelineMetrics,
                 stop: threading.Event, interval: float = 2):
    while not stop.is_set():
        s = metrics.snapshot()
        print(f"[DASHBOARD] backlog={q.qsize():>4} | "
              f"success={s['success']:>5} | fail={s['failures']:>3} | "
              f"retry={s['retries']:>3} | rate={s['rate_per_sec']:>6.1f} msg/s | "
              f"latency={s['avg_latency_ms']:>7.1f}ms")
        time.sleep(interval)
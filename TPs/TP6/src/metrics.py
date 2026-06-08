# src/metrics.py
import time, logging

logger = logging.getLogger(__name__)

class Metrics:
    def __init__(self):
        self.start_time = time.time()
        self.latencies: list[float] = []

    def record_latency(self, event_time: float):
        self.latencies.append(time.time() - event_time)

    def report(self, processor, q_size: int):
        elapsed = time.time() - self.start_time
        throughput = processor.events_processed / max(elapsed, 0.01)
        avg_lat = (sum(self.latencies) / len(self.latencies)
                   if self.latencies else 0)
        logger.info(
            f"[METRICS] elapsed={elapsed:.1f}s | "
            f"processed={processor.events_processed} | "
            f"throughput={throughput:.1f} evt/s | "
            f"avg_latency={avg_lat:.2f}s | "
            f"backlog={q_size} | "
            f"late={len(processor.late_events)} | "
            f"dropped={len(processor.dropped_events)} | "
            f"state_keys={len(processor.state)}"
        )
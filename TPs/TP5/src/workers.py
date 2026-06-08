# src/workers.py
import queue
import time
import logging
from .messages import EventMessage

VALID_RANGE = {"temperature": (-20, 60), "humidity": (0, 100), "luminosity": (0, 2000)}

def validate(msg: EventMessage) -> bool:
    """Vérifie que la valeur du capteur est dans la plage attendue."""
    metric = msg.payload.get("metric", "")
    value = msg.payload.get("value")
    if metric not in VALID_RANGE or value is None:
        return False
    lo, hi = VALID_RANGE[metric]
    return lo <= value <= hi

def worker_loop(main_q: queue.Queue, dlq: queue.Queue,
                storage, metrics, stop, name: str):
    """Boucle principale du worker."""
    while not stop.is_set():
        try:
            msg = main_q.get(timeout=1)
        except queue.Empty:
            continue

        msg.attempts += 1
        if validate(msg):
            latency = time.time() - msg.created_at
            storage.write(msg)
            metrics.record_success(latency)
            logging.debug(f"[{name}] OK {msg.msg_id[:8]} lat={latency:.3f}s")
        else:
            if msg.should_retry():
                main_q.put(msg)  # retry
                metrics.record_retry()
                logging.info(f"[{name}] Retry {msg.msg_id[:8]} (#{msg.attempts})")
            else:
                dlq.put(msg)
                metrics.record_failure()
                logging.warning(f"[{name}] DLQ {msg.msg_id[:8]}")
        main_q.task_done()
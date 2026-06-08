# src/source.py
import json, queue, threading, time, logging

logger = logging.getLogger(__name__)

class EventSource:
    def __init__(self, events_json: list[dict], q: queue.Queue,
                 delay: float = 0.5):
        self.events = events_json
        self.queue = q
        self.delay = delay

    def run(self):
        for raw in self.events:
            self.queue.put(raw)
            logger.info(f"Source: émis {raw['event_id']}")
            time.sleep(self.delay)
        self.queue.put(None)  # sentinel
        logger.info("Source: flux terminé (sentinel envoyé)")

    def start(self) -> threading.Thread:
        t = threading.Thread(target=self.run, daemon=True, name="source")
        t.start()
        return t
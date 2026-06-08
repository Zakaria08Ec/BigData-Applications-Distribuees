# src/pipeline.py
import queue
import threading

class Pipeline:
    def __init__(self, maxsize: int = 50):
        self.main_queue = queue.Queue(maxsize=maxsize)
        self.dead_letter_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.threads: list[threading.Thread] = []

    def shutdown(self, timeout: float = 10):
        """Arrêt propre : signale l'arrêt et attend les threads."""
        self.stop_event.set()
        for t in self.threads:
            t.join(timeout=timeout)
# src/broker.py
import threading
from typing import Optional
from .events import Event
from .partitioner import partition_of

class Broker:
    def __init__(self, num_partitions: int, key_field: str):
        self.num_partitions = num_partitions
        self.key_field = key_field
        self.partitions: list[list[Event]] = [[] for _ in range(num_partitions)]
        self._lock = threading.Lock()

    def publish(self, event: Event) -> int:
        key = event.partition_key(self.key_field)
        p = partition_of(key, self.num_partitions)
        with self._lock:
            self.partitions[p].append(event)
        return p

    def fetch(self, partition: int, offset: int) -> Optional[Event]:
        with self._lock:
            if 0 <= offset < len(self.partitions[partition]):
                return self.partitions[partition][offset]
        return None

    def size(self, partition: int) -> int:
        with self._lock:
            return len(self.partitions[partition])
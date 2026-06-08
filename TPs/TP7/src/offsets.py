# src/offsets.py
import json, threading
from pathlib import Path

class OffsetStore:
    def __init__(self, path="state/offsets.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._data = self._load()

    def _load(self):
        if self.path.exists():
            try: return json.loads(self.path.read_text())
            except json.JSONDecodeError: return {}
        return {}

    def get(self, group, partition):
        return self._data.get(group, {}).get(str(partition), 0)

    def set_memory(self, group, partition, offset):
        with self._lock:
            self._data.setdefault(group, {})[str(partition)] = offset

    def commit(self, group, partition, offset):
        with self._lock:
            self._data.setdefault(group, {})[str(partition)] = offset
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self._data, indent=2))
            tmp.replace(self.path)

    def flush(self, group, partition):
        off = self.get(group, partition)
        self.commit(group, partition, off)
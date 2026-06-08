# src/storage.py
import json, threading
from pathlib import Path
from .events import Event

class Storage:
    def __init__(self, base="outputs"):
        self.base = Path(base)
        self.base.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def write(self, evt: Event, partition: int):
        date = evt.event_time[:10]
        site = evt.site_id
        target_dir = self.base / f"date={date}" / f"site={site}" / f"partition={partition}"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "events.jsonl"
        line = json.dumps(evt.to_dict(), ensure_ascii=False)
        with self._lock:
            with target_file.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
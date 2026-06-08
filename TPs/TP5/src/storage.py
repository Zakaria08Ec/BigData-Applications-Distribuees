# src/storage.py
import csv
import threading
import statistics
from collections import defaultdict
from .messages import EventMessage

class CSVStorage:
    def __init__(self, path: str = "outputs/valid_readings.csv"):
        self.path = path
        self._lock = threading.Lock()
        self._records: list[dict] = []
        # Écrire l'en-tête
        with open(self.path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["msg_id", "sensor_id", "metric", "value", "timestamp"])

    def write(self, msg: EventMessage):
        row = {
            "msg_id": msg.msg_id[:8],
            "sensor_id": msg.payload["sensor_id"],
            "metric": msg.payload["metric"],
            "value": msg.payload["value"],
            "timestamp": msg.created_at,
        }
        with self._lock:
            self._records.append(row)
            with open(self.path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(row.values())

    def aggregate(self) -> dict:
        """Résumé par capteur : count, mean, min, max."""
        by_sensor = defaultdict(list)
        with self._lock:
            for r in self._records:
                by_sensor[r["sensor_id"]].append(r["value"])
        summary = {}
        for sid, vals in by_sensor.items():
            summary[sid] = {
                "count": len(vals),
                "mean": round(statistics.mean(vals), 2),
                "min": round(min(vals), 2),
                "max": round(max(vals), 2),
            }
        return summary
import threading
import time
import statistics
from models import SensorReading

# ═══════════════════════════════════════════════════════
# STOCKAGE THREAD-SAFE (protégé par un verrou)
# ═══════════════════════════════════════════════════════
class DataStore:
    """Stockage en mémoire, protégé pour accès concurrent."""

    def __init__(self):
        self._readings: list[dict] = []
        self._lock = threading.Lock()      # 🔒 Le verrou !

    def add(self, readings: list[dict]) -> int:
        with self._lock:               # 🔒 Un seul thread à la fois
            self._readings.extend(readings)
            return len(self._readings)

    def get_all(self) -> list[dict]:
        with self._lock:
            return list(self._readings)   # Copie !

    def get_by_date(self, date: str) -> list[dict]:
        with self._lock:
            return [r for r in self._readings if r["ts"].startswith(date)]

# Instance globale partagée par tous les threads
store = DataStore()
MAX_BATCH = 1000


# ═══════════════════════════════════════════════════════
# MÉTHODE : health.ping
# ═══════════════════════════════════════════════════════
def health_ping(params: dict) -> dict:
    """Vérifie que le serveur est vivant."""
    return {"status": "ok", "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}


# ═══════════════════════════════════════════════════════
# MÉTHODE : ingest.batch
# ═══════════════════════════════════════════════════════
def ingest_batch(params: dict) -> dict:
    """Ingère un lot de lectures capteur avec validation individuelle."""
    readings_raw = params.get("readings")

    # Vérifications préalables
    if readings_raw is None:
        raise ValueError("Missing: readings")
    if not isinstance(readings_raw, list):
        raise ValueError("readings doit être une liste")
    if len(readings_raw) > MAX_BATCH:
        raise OverflowError(f"Trop gros : {len(readings_raw)} > {MAX_BATCH}")

    accepted, rejected = [], []

    for i, raw in enumerate(readings_raw):
        if not isinstance(raw, dict):
            rejected.append({"index": i, "error": "Not a dict"})
            continue

        reading = SensorReading(
            sensor_id=raw.get("sensor_id", ""),
            ts=raw.get("ts", ""),
            value=raw.get("value")
        )
        errors = reading.validate()

        if errors:
            rejected.append({"index": i, "errors": errors})
        else:
            accepted.append({"sensor_id": reading.sensor_id,
                            "ts": reading.ts, "value": reading.value})

    if accepted:
        store.add(accepted)

    return {"accepted": len(accepted), "rejected": len(rejected),
            "errors": rejected}


# ═══════════════════════════════════════════════════════
# MÉTHODE : stats.daily_summary
# ═══════════════════════════════════════════════════════
def stats_daily_summary(params: dict) -> dict:
    """Calcule les stats d'une journée."""
    date = params.get("date")
    if not date:
        raise ValueError("Missing: date")

    readings = store.get_by_date(date)
    if not readings:
        return {"date": date, "count": 0,
                "avg": None, "min": None, "max": None}

    vals = [r["value"] for r in readings]
    return {"date": date, "count": len(vals),
            "avg": round(statistics.mean(vals), 2),
            "min": min(vals), "max": max(vals)}


# ═══════════════════════════════════════════════════════
# MÉTHODE : stats.top_sensors
# ═══════════════════════════════════════════════════════
def stats_top_sensors(params: dict) -> dict:
    """Classement des N capteurs avec la plus haute moyenne."""
    n = params.get("n", 5)
    if not isinstance(n, int) or n < 1:
        raise ValueError("n doit être un entier positif")

    all_data = store.get_all()
    if not all_data:
        return {"sensors": []}

    # Grouper par capteur
    by_sensor = {}
    for r in all_data:
        by_sensor.setdefault(r["sensor_id"], []).append(r["value"])

    # Trier par moyenne décroissante
    ranking = sorted(
        [{"sensor_id": sid, "avg": round(statistics.mean(v), 2)}
         for sid, v in by_sensor.items()],
        key=lambda x: x["avg"], reverse=True
    )
    return {"sensors": ranking[:n]}
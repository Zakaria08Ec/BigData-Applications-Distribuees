# src/events.py
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

@dataclass
class Event:
    event_id: str
    sensor_id: str
    site_id: str
    event_time: str
    temperature_c: float
    humidity_pct: float

    def partition_key(self, field: str) -> str:
        return str(getattr(self, field))

    def to_dict(self) -> dict:
        return asdict(self)

def make_random_event(sensor_id: str, site_id: str) -> Event:
    import random
    return Event(
        event_id=f"e-{uuid.uuid4().hex[:8]}",
        sensor_id=sensor_id,
        site_id=site_id,
        event_time=datetime.utcnow().isoformat(timespec="seconds"),
        temperature_c=round(20 + random.uniform(-2, 8), 2),
        humidity_pct=round(55 + random.uniform(-10, 10), 2),
    )
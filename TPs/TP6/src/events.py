# src/events.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Event:
    event_id: str
    sensor_id: str
    site_id: str
    event_time: float  # epoch seconds
    temperature_c: float
    humidity_pct: float
    soil_moisture: Optional[float] = None

    @classmethod
    def from_dict(cls, d: dict) -> "Event":
        et = datetime.fromisoformat(d["event_time"]).timestamp()
        sm = d.get("soil_moisture")
        if isinstance(sm, str) or sm is None:
            sm = None
        else:
            sm = float(sm)
        return cls(
            event_id=d["event_id"],
            sensor_id=d["sensor_id"],
            site_id=d["site_id"],
            event_time=et,
            temperature_c=float(d["temperature_c"]),
            humidity_pct=float(d["humidity_pct"]),
            soil_moisture=sm,
        )
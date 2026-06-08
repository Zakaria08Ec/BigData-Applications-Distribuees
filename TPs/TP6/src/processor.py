# src/processor.py
import queue, logging, time
from dataclasses import dataclass, field, asdict
from src.events import Event

logger = logging.getLogger(__name__)

@dataclass
class WindowState:
    count: int = 0
    sum_temp: float = 0.0
    sum_humidity: float = 0.0
    min_temp: float = float('inf')
    max_temp: float = float('-inf')

    def update(self, event: Event):
        self.count += 1
        self.sum_temp += event.temperature_c
        self.sum_humidity += event.humidity_pct
        self.min_temp = min(self.min_temp, event.temperature_c)
        self.max_temp = max(self.max_temp, event.temperature_c)

    @property
    def avg_temp(self): return self.sum_temp / self.count if self.count else 0
    @property
    def avg_humidity(self): return self.sum_humidity / self.count if self.count else 0

    def to_dict(self):
        return {"count": self.count, "sum_temp": self.sum_temp,
                "sum_humidity": self.sum_humidity,
                "min_temp": self.min_temp, "max_temp": self.max_temp,
                "avg_temp": round(self.avg_temp, 2),
                "avg_humidity": round(self.avg_humidity, 2)}

class StreamProcessor:
    def __init__(self, window_size: int = 60,
                 allowed_lateness: int = 120,
                 watermark_margin: float = 5.0):
        self.window_size = window_size
        self.allowed_lateness = allowed_lateness
        self.state: dict[tuple[str, int], WindowState] = {}
        self.max_event_time: float = 0.0
        self.watermark_margin = watermark_margin
        self.late_events: list[dict] = []
        self.dropped_events: list[dict] = []
        self.flushed_windows: list[dict] = []
        self.events_processed = 0

    @property
    def watermark(self) -> float:
        return self.max_event_time - self.watermark_margin

    def _window_key(self, event_time: float) -> int:
        return int(event_time // self.window_size) * self.window_size

    def process_event(self, event: Event) -> str:
        self.events_processed += 1
        wk = self._window_key(event.event_time)
        window_end = wk + self.window_size
        self.max_event_time = max(self.max_event_time, event.event_time)

        # Lateness check
        if self.watermark > window_end:
            lateness = self.watermark - window_end
            if lateness > self.allowed_lateness:
                self.dropped_events.append({
                    "event_id": event.event_id,
                    "reason": "too-late",
                    "lateness_s": round(lateness, 1)
                })
                logger.warning(f"DROPPED {event.event_id} (lateness={lateness:.0f}s)")
                return "dropped"
            else:
                self.late_events.append({
                    "event_id": event.event_id,
                    "reason": "late-accepted",
                    "lateness_s": round(lateness, 1)
                })
                logger.info(f"LATE-ACCEPTED {event.event_id}")

        key = (event.sensor_id, wk)
        if key not in self.state:
            self.state[key] = WindowState()
        self.state[key].update(event)
        return "ok"

    def flush_closed_windows(self):
        """Flush les fenêtres dont window_end <= watermark."""
        to_flush = []
        for (sid, wk), ws in self.state.items():
            window_end = wk + self.window_size
            if self.watermark >= window_end:
                to_flush.append((sid, wk, ws))
        for sid, wk, ws in to_flush:
            record = {"sensor_id": sid, "window_start": wk,
                      "window_end": wk + self.window_size,
                      **ws.to_dict()}
            self.flushed_windows.append(record)
            del self.state[(sid, wk)]
            logger.info(f"FLUSH window ({sid}, {wk}): {ws.to_dict()}")
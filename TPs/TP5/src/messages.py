# src/messages.py
from dataclasses import dataclass, field, asdict
from typing import Any
import uuid
import time

@dataclass
class EventMessage:
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    msg_type: str = "sensor_reading"
    payload: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    attempts: int = 0
    max_attempts: int = 3

    def should_retry(self) -> bool:
        return self.attempts < self.max_attempts

    def to_dict(self) -> dict:
        return asdict(self)
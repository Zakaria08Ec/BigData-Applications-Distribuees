"""models.py — Contrats de données pour le service d'ingestion IoT."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ValidationError:
    field: str
    code: str
    message: str

    def to_dict(self) -> dict:
        return {"field": self.field, "code": self.code, "message": self.message}


@dataclass
class SensorReading:
    timestamp: str
    site_id: str
    sensor_id: str
    temperature_c: float
    humidity_pct: float
    soil_moisture: Optional[float] = None
    pump_status: str = "off"
    irrigation_l_min: float = 0.0

    def __post_init__(self):
        if not self.sensor_id or not self.sensor_id.strip():
            raise ValueError("sensor_id est obligatoire et ne peut pas être vide")

    def to_dict(self) -> dict:
        # TODO : retourner un dict avec tous les champs
        pass

    @classmethod
    def from_dict(cls, data: dict) -> "SensorReading":
        # TODO : construire un SensorReading depuis un dict
        # Gérer les champs manquants avec .get() et des défauts
        pass


@dataclass
class IngestRequest:
    request_id: str
    api_key: str
    readings: List[SensorReading] = field(default_factory=list)
    sent_at: str = ""

    def to_dict(self) -> dict:
        # TODO : attention à sérialiser chaque reading via to_dict()
        # NE PAS inclure api_key dans la sortie (secret !)
        pass

    @classmethod
    def from_dict(cls, data: dict) -> "IngestRequest":
        # TODO : reconstruire chaque reading via SensorReading.from_dict()
        pass


@dataclass
class IngestResponse:
    status: str  # "ok", "partial", "error"
    accepted_count: int = 0
    rejected_count: int = 0
    errors: List[ValidationError] = field(default_factory=list)

    def to_dict(self) -> dict:
        # TODO : sérialiser les erreurs via to_dict()
        pass
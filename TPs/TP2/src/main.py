"""main.py — Point d'entrée du service d'ingestion IoT (TP Séance 2)."""
import json
import logging
import uuid
from datetime import datetime, timezone

from models import SensorReading, IngestRequest, IngestResponse, ValidationError
from validators import (
    Validator, RangeValidator, ConsistencyValidator,
    RequiredFieldsValidator, run_validators,
)

# --- Configuration du logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ingestion")


def sanitize_for_log(value: str, max_len: int = 200) -> str:
    """Supprime les caractères dangereux pour le log."""
    sanitized = value.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    return sanitized[:max_len] + "...[TRONQUÉ]" if len(sanitized) > max_len else sanitized


def mask_api_key(key: str) -> str:
    """Masque une clé API pour le logging."""
    if len(key) >= 8:
        return "****" + key[-4:]
    return "****"


# --- Définition des validateurs ---
VALIDATORS = [
    RequiredFieldsValidator(["timestamp", "site_id", "sensor_id"]),
    RangeValidator("temperature_c", -50.0, 60.0),
    RangeValidator("humidity_pct", 0.0, 100.0),
    RangeValidator("soil_moisture", 0.0, 1.0),
    RangeValidator("irrigation_l_min", 0.0, 50.0),
    ConsistencyValidator(),
]


# --- Données de test ---
sample_readings_raw = [
    {"timestamp": "2026-02-16T08:00:00Z", "site_id": "site-alpha",
     "sensor_id": "sensor-01", "temperature_c": 22.5, "humidity_pct": 65.0,
     "soil_moisture": 0.42, "pump_status": "off", "irrigation_l_min": 0.0},
    {"timestamp": "2026-02-16T08:05:00Z", "site_id": "site-alpha",
     "sensor_id": "sensor-02", "temperature_c": 23.1, "humidity_pct": 150.0,
     "soil_moisture": 0.38, "pump_status": "off", "irrigation_l_min": 0.0},
    {"timestamp": "2026-02-16T08:10:00Z", "site_id": "site-beta",
     "sensor_id": "", "temperature_c": 19.8, "humidity_pct": 70.2,
     "soil_moisture": 0.55, "pump_status": "on", "irrigation_l_min": 0.0},
    {"timestamp": "2026-02-16T08:15:00Z", "site_id": "site-beta",
     "sensor_id": "sensor-04", "temperature_c": -60.0, "humidity_pct": 72.0,
     "soil_moisture": 0.60, "pump_status": "on", "irrigation_l_min": 3.5},
    {"timestamp": "", "site_id": "site-gamma", "sensor_id": "sensor-05",
     "temperature_c": 25.0, "humidity_pct": 55.0, "soil_moisture": None,
     "pump_status": "off", "irrigation_l_min": 0.0},
]


def process_ingestion(raw_readings: list, api_key: str) -> IngestResponse:
    """Traite une requête d'ingestion complète."""
    request_id = str(uuid.uuid4())
    logger.info("Requête reçue | request_id=%s | api_key=%s | nb_readings=%d",
                request_id, mask_api_key(api_key), len(raw_readings))

    accepted = []
    all_errors = []

    for i, raw in enumerate(raw_readings):
        sid = sanitize_for_log(str(raw.get("sensor_id", "?")))
        # Étape 1 : validation sur le dict brut
        errors = run_validators(raw, VALIDATORS)

        if errors:
            logger.warning("  Reading #%s (sensor=%s) : %d erreur(s)", i, sid, len(errors))
            for e in errors:
                logger.warning("    -> [%s] %s : %s", e.code, e.field, e.message)
                all_errors.append(e)
        else:
            # Étape 2 : construction de l'objet (peut lever ValueError)
            try:
                reading = SensorReading.from_dict(raw)
                accepted.append(reading)
                logger.info("  Reading #%s (sensor=%s) : ACCEPTÉ", i, sid)
            except (ValueError, TypeError) as exc:
                err = ValidationError("__construction__", "BUILD_ERROR", str(exc))
                all_errors.append(err)
                logger.warning("  Reading #%s (sensor=%s) : REJETÉ à la construction : %s",
                               i, sid, exc)

    # Construire la réponse
    rejected_count = len(raw_readings) - len(accepted)
    if rejected_count == 0:
        status = "ok"
    elif len(accepted) > 0:
        status = "partial"
    else:
        status = "error"

    response = IngestResponse(
        status=status,
        accepted_count=len(accepted),
        rejected_count=rejected_count,
        errors=all_errors,
    )
    logger.info("Réponse | request_id=%s | status=%s | accepted=%d | rejected=%d",
                request_id, response.status, response.accepted_count, response.rejected_count)
    return response


# --- Exécution principale ---
if __name__ == "__main__":
    print("=" * 60)
    print("  SERVICE D'INGESTION IoT — Séance 2 (TP)")
    print("=" * 60)

    result = process_ingestion(sample_readings_raw, api_key="sk-secret-key-12345678")

    print("\n--- Réponse (JSON) ---")
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))

    # --- Vérifications rapides ---
    print("\n--- Vérifications ---")

    # Test sérialisation aller-retour
    valid_data = sample_readings_raw[0]
    r1 = SensorReading.from_dict(valid_data)
    r2 = SensorReading.from_dict(r1.to_dict())
    assert r1 == r2, "Échec : sérialisation aller-retour"
    print("[OK] Sérialisation aller-retour SensorReading")

    # Test sensor_id vide
    try:
        SensorReading.from_dict({"timestamp": "t", "site_id": "s", "sensor_id": "",
                                  "temperature_c": 20, "humidity_pct": 50})
        assert False, "Aurait dû lever ValueError"
    except ValueError:
        print("[OK] sensor_id vide lève ValueError")

    # Test validation humidity hors plage
    errs = run_validators(sample_readings_raw[1], VALIDATORS)
    assert any(e.code == "OUT_OF_RANGE" and e.field == "humidity_pct" for e in errs)
    print("[OK] humidity_pct=150 détectée comme OUT_OF_RANGE")

    # Test masquage API key
    assert mask_api_key("sk-abcdef1234") == "****1234"
    print("[OK] mask_api_key fonctionne")

    print("\n✅ Toutes les vérifications sont passées !")
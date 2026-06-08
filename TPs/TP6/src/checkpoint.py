# src/checkpoint.py
import json, pathlib, logging
from src.processor import WindowState

logger = logging.getLogger(__name__)

def save_checkpoint(processor, path: str):
    state_ser = {}
    for (sid, wk), ws in processor.state.items():
        key_str = f"{sid}|{wk}"
        state_ser[key_str] = ws.to_dict()
    payload = {
        "max_event_time": processor.max_event_time,
        "events_processed": processor.events_processed,
        "state": state_ser,
    }
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2))
    logger.info(f"Checkpoint sauvegardé → {path} ({len(state_ser)} clés)")

def load_checkpoint(processor, path: str) -> bool:
    p = pathlib.Path(path)
    if not p.exists():
        logger.info("Pas de checkpoint trouvé, démarrage à froid.")
        return False
    data = json.loads(p.read_text())
    processor.max_event_time = data["max_event_time"]
    processor.events_processed = data["events_processed"]
    for key_str, ws_dict in data["state"].items():
        sid, wk_str = key_str.split("|")
        ws = WindowState()
        ws.count = ws_dict["count"]
        ws.sum_temp = ws_dict["sum_temp"]
        ws.sum_humidity = ws_dict["sum_humidity"]
        ws.min_temp = ws_dict.get("min_temp", float('inf'))
        ws.max_temp = ws_dict.get("max_temp", float('-inf'))
        processor.state[(sid, int(float(wk_str)))] = ws
    logger.info(f"Checkpoint chargé ← {path} ({len(processor.state)} clés)")
    return True
# src/sink.py
import csv, json, pathlib, logging

logger = logging.getLogger(__name__)

def export_aggregates_csv(records: list[dict], path: str):
    if not records:
        logger.warning("Aucun agrégat à exporter.")
        return
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    logger.info(f"Agrégats exportés → {path} ({len(records)} lignes)")

def export_json(data, path: str):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, default=str))
    logger.info(f"JSON exporté → {path}")

def generate_run_report(processor, duration: float, path: str):
    report = {
        "events_processed": processor.events_processed,
        "windows_flushed": len(processor.flushed_windows),
        "late_accepted": len(processor.late_events),
        "dropped": len(processor.dropped_events),
        "duration_seconds": round(duration, 2),
        "throughput_eps": round(processor.events_processed / max(duration, 0.01), 2),
        "remaining_state_keys": len(processor.state),
    }
    export_json(report, path)
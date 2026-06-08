# src/main.py
import queue, time, json, logging, pathlib, sys
from src.events import Event
from src.source import EventSource
from src.processor import StreamProcessor
from src.checkpoint import save_checkpoint, load_checkpoint
from src.sink import export_aggregates_csv, export_json, generate_run_report
from src.metrics import Metrics

# --- Config ---
WINDOW_SIZE = 60
ALLOWED_LATENESS = 120
CHECKPOINT_INTERVAL = 10
QUEUE_MAXSIZE = 50
WATERMARK_MARGIN = 5.0
EVENTS_FILE = "data/events.json"
CHECKPOINT_PATH = "checkpoints/state.json"

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("main")

def main():
    # Créer dossiers
    for d in ["outputs", "logs", "checkpoints", "data"]:
        pathlib.Path(d).mkdir(exist_ok=True)

    # Charger événements
    events_raw = json.loads(pathlib.Path(EVENTS_FILE).read_text())

    # Init
    q = queue.Queue(maxsize=QUEUE_MAXSIZE)
    processor = StreamProcessor(WINDOW_SIZE, ALLOWED_LATENESS, WATERMARK_MARGIN)
    metrics = Metrics()

    # Reprise checkpoint ?
    load_checkpoint(processor, CHECKPOINT_PATH)

    # Lancer source
    source = EventSource(events_raw, q, delay=0.3)
    source_thread = source.start()

    # Boucle principale
    last_checkpoint = time.time()
    start_time = time.time()

    while True:
        try:
            raw = q.get(timeout=2.0)
        except queue.Empty:
            if not source_thread.is_alive():
                break
            continue

        if raw is None:
            logger.info("Sentinel reçu, fin du flux.")
            break

        event = Event.from_dict(raw)
        status = processor.process_event(event)
        metrics.record_latency(event.event_time)
        processor.flush_closed_windows()

        # Checkpoint périodique
        if time.time() - last_checkpoint >= CHECKPOINT_INTERVAL:
            save_checkpoint(processor, CHECKPOINT_PATH)
            last_checkpoint = time.time()

        metrics.report(processor, q.qsize())

    # Flush final (fenêtres encore ouvertes)
    for key in list(processor.state.keys()):
        sid, wk = key
        ws = processor.state[key]
        record = {"sensor_id": sid, "window_start": wk,
                  "window_end": wk + WINDOW_SIZE,
                  **ws.to_dict()}
        processor.flushed_windows.append(record)
    processor.state.clear()

    duration = time.time() - start_time

    # Exports
    export_aggregates_csv(processor.flushed_windows, "outputs/aggregates.csv")
    export_json(processor.late_events, "outputs/late_events.json")
    export_json(processor.dropped_events, "outputs/dropped_events.json")
    generate_run_report(processor, duration, "outputs/run_report.json")
    save_checkpoint(processor, CHECKPOINT_PATH)

    logger.info("Pipeline terminé avec succès.")

if __name__ == "__main__":
    main()
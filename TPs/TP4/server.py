from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json, time

from router import MethodRouter
from rpc_protocol import validate_rpc_request, build_response, build_error_response
from services import health_ping, ingest_batch, stats_daily_summary, stats_top_sensors


class RPCHandler(BaseHTTPRequestHandler):
    """Gère chaque requête HTTP entrante."""

    def do_POST(self):
        start = time.monotonic()

        # ── ÉTAPE 1 : Lire le body HTTP ──
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return self._send(build_error_response("", -32700, "Empty body"))
        raw = self.rfile.read(length)

        # ── ÉTAPE 2 : Valider le message RPC ──
        parsed, error = validate_rpc_request(raw)
        if error:
            return self._send(error)

        rpc_id = parsed["id"]
        method = parsed["method"]

        # ── ÉTAPE 3 : Router et exécuter ──
        try:
            result = self.server.router.dispatch(method, parsed.get("params", {}))
            self._send(build_response(rpc_id, result))

        except KeyError:
            self._send(build_error_response(rpc_id, -32601,
                       "Method not found", f"Inconnue: {method}"))

        except (ValueError, TypeError) as e:
            self._send(build_error_response(rpc_id, -32602,
                       "Invalid params", str(e)))

        except OverflowError as e:
            self._send(build_error_response(rpc_id, 1002,
                       "Payload too large", str(e)))

        except Exception as e:
            # Filet de sécurité : JAMAIS de crash
            self._send(build_error_response(rpc_id, -32603,
                       "Internal error", "Unexpected failure"))
            print(f"[ERROR] {rpc_id} {method}: {e}")

        # ── LOG ──
        ms = (time.monotonic() - start) * 1000
        print(f"[{rpc_id[:8]}] {method} → {ms:.1f}ms")

    def _send(self, data: dict):
        """Envoie une réponse JSON au client."""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # Désactiver les logs par défaut


# ════════════════════════════════════════════════════
# LANCEMENT DU SERVEUR
# ════════════════════════════════════════════════════
if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8080), RPCHandler)

    # Créer et peupler le routeur
    server.router = MethodRouter()
    server.router.register("health.ping",         health_ping)
    server.router.register("ingest.batch",        ingest_batch)
    server.router.register("stats.daily_summary", stats_daily_summary)
    server.router.register("stats.top_sensors",   stats_top_sensors)

    print("🚀 Serveur RPC démarré sur http://127.0.0.1:8080")
    print(f"📋 Méthodes : {server.router.list_methods()}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur.")
        server.server_close()
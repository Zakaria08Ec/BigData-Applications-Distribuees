import urllib.request
import urllib.error
import json, time, uuid, socket


class RpcClient:
    """Client RPC avec timeout automatique et retries."""

    def __init__(self, url: str,
                 timeout: float = 5.0,
                 max_retries: int = 3,
                 backoff_base: float = 1.0):
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base = backoff_base

    def call(self, method: str, params: dict = None) -> dict:
        """
        Appelle une méthode RPC distante.
        Réessaye automatiquement en cas d'erreur réseau.
        """
        rpc_id = str(uuid.uuid4())
        params = params or {}
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                # Construire le message RPC
                body = json.dumps({
                    "rpc_version": "1.0",
                    "id": rpc_id,
                    "method": method,
                    "params": params,
                    "sent_at": time.strftime("%Y-%m-%dT%H:%M:%S")
                }).encode("utf-8")

                # Envoyer la requête HTTP
                req = urllib.request.Request(
                    self.url, data=body,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    response = json.loads(resp.read().decode("utf-8"))

                print(f"  ✅ [{rpc_id[:8]}] {method} tentative {attempt} → OK")

                # Erreur applicative ? Pas de retry.
                if response.get("error"):
                    code = response["error"].get("code", 0)
                    if code != -32603:
                        return response  # Erreur client → pas de retry

                return response

            except (urllib.error.URLError, socket.timeout,
                    ConnectionError, OSError) as e:
                last_error = e
                print(f"  ❌ [{rpc_id[:8]}] {method} tentative {attempt} → {e}")

                if attempt < self.max_retries:
                    delay = self.backoff_base * (2 ** (attempt - 1))
                    print(f"    ⏳ Attente {delay:.0f}s...")
                    time.sleep(delay)

        raise ConnectionError(
            f"Échec après {self.max_retries} tentatives : {last_error}"
        )
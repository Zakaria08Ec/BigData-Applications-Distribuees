import json, uuid, time

def build_request(method: str, params: dict = None) -> dict:
    """Construit un message RPC Request prêt à envoyer."""
    return {
        "rpc_version": "1.0",
        "id": str(uuid.uuid4()),
        "method": method,
        "params": params or {},
        "sent_at": time.strftime("%Y-%m-%dT%H:%M:%S")
    }

def build_response(rpc_id: str, result) -> dict:
    """Construit une réponse de SUCCÈS."""
    return {"rpc_version": "1.0", "id": rpc_id,
            "result": result, "error": None}

def build_error_response(rpc_id: str, code: int, message: str,
                         details: str = "") -> dict:
    """Construit une réponse d'ERREUR."""
    return {"rpc_version": "1.0", "id": rpc_id or "",
            "result": None,
            "error": {"code": code, "message": message,
                      "details": details}}

MAX_PAYLOAD = 1_000_000  # 1 Mo maximum

def validate_rpc_request(raw_bytes: bytes) -> tuple[dict | None, dict | None]:
    """
    Valide le body brut d'une requête RPC.
    Retourne (parsed, None) si OK, ou (None, error_response) si KO.
    """
    # Étape 1 : taille
    if len(raw_bytes) > MAX_PAYLOAD:
        return None, build_error_response("", 1002, "Payload too large")

    # Étape 2 : JSON valide ?
    try:
        data = json.loads(raw_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return None, build_error_response("", -32700, "Parse error", str(e))

    # Étape 3 : c'est un objet JSON ?
    if not isinstance(data, dict):
        return None, build_error_response("", -32600, "Must be a JSON object")

    # Étape 4 : champs obligatoires
    rpc_id = data.get("id", "")
    for f in ("id", "method"):
        if not data.get(f):
            return None, build_error_response(rpc_id, -32600,
                   "Invalid request", f"Missing: {f}")

    return data, None
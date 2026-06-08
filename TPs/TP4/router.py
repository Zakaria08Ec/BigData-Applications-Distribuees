class MethodRouter:
    """Standard téléphonique : nom de méthode → fonction Python."""

    def __init__(self):
        self._registry: dict[str, callable] = {}

    def register(self, name: str, func: callable):
        """Enregistre une nouvelle méthode."""
        if name in self._registry:
            raise ValueError(f"Méthode déjà enregistrée : {name}")
        self._registry[name] = func

    def dispatch(self, name: str, params: dict):
        """Appelle la fonction correspondante. Lève KeyError si inconnue."""
        func = self._registry.get(name)
        if func is None:
            raise KeyError(name)
        return func(params)

    def list_methods(self) -> list[str]:
        return sorted(self._registry.keys())


# --- Exemple d'utilisation ---
router = MethodRouter()

def ping(params):
    return {"status": "ok"}

router.register("health.ping", ping)
print(router.dispatch("health.ping", {}))
# → {'status': 'ok'}
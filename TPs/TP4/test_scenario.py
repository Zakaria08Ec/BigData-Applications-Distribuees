"""Scénario de test complet. Lancer le serveur avant d'exécuter."""
import json
from client import RpcClient

client = RpcClient("http://127.0.0.1:8080", timeout=5.0, max_retries=2)

# ═══ TEST 1 : PING ═══
print("=" * 50)
print("TEST 1 : health.ping")
r = client.call("health.ping")
assert r["error"] is None
assert r["result"]["status"] == "ok"
print("  ✅ Ping OK\n")

# ═══ TEST 2 : INGESTION ═══
print("=" * 50)
print("TEST 2 : ingest.batch")
with open("test_batch.json") as f:
    readings = json.load(f)
r = client.call("ingest.batch", {"readings": readings})
assert r["error"] is None
assert r["result"]["accepted"] == 6, f"Attendu 6, obtenu {r['result']['accepted']}"
assert r["result"]["rejected"] == 4
print(f"  ✅ accepted={r['result']['accepted']}, rejected={r['result']['rejected']}\n")

# ═══ TEST 3 : STATS DAILY ═══
print("=" * 50)
print("TEST 3 : stats.daily_summary")
r = client.call("stats.daily_summary", {"date": "2026-03-09"})
assert r["result"]["count"] == 6
assert r["result"]["min"] == -5.1
assert r["result"]["max"] == 25.3
print(f"  ✅ count={r['result']['count']}, avg={r['result']['avg']}\n")

# ═══ TEST 4 : TOP SENSORS ═══
print("=" * 50)
print("TEST 4 : stats.top_sensors")
r = client.call("stats.top_sensors", {"n": 3})
assert len(r["result"]["sensors"]) <= 3
print(f"  ✅ Top 3 : {r['result']['sensors']}\n")

# ═══ TEST 5 : MÉTHODE INCONNUE ═══
print("=" * 50)
print("TEST 5 : méthode inconnue")
r = client.call("unknown.method")
assert r["error"]["code"] == -32601
print(f"  ✅ Correctement rejeté (code {r['error']['code']})\n")

print("🎉 TOUS LES TESTS SONT PASSÉS !")
# src/partitioner.py
import hashlib

def partition_of(key: str, num_partitions: int) -> int:
    h = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(h[:4], "big") % num_partitions

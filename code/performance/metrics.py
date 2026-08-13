from dataclasses import dataclass

@dataclass
class Metrics:
    fast_count:int=0
    smart_count:int=0
    cache_hits:int=0
    cache_misses:int=0
    total_requests:int=0
    total_latency_ms:float=0.0
    p50_latency:float=0.0
    p90_latency:float=0.0
    p95_latency:float=0.0
    p99_latency:float=0.0
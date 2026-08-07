import requests
import time
from typing import Dict, Any

def benchmark(url: str, payload: Dict[str, Any], timeout: int = 30) -> float:
    """
    Run a single benchmark test
    """
    t0 = time.perf_counter()
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        elapsed = (time.perf_counter() - t0) * 1000  # Convert to milliseconds
        return elapsed
    except Exception as e:
        # If request fails, still return timing for the attempt
        elapsed = (time.perf_counter() - t0) * 1000
        print(f"Benchmark failed after {elapsed:.2f}ms: {e}")
        return elapsed

def run_benchmark_suite(url: str, test_cases: list) -> Dict[str, Any]:
    """
    Run a suite of benchmark tests
    """
    results = {
        "total_time": 0,
        "avg_time": 0,
        "min_time": float('inf'),
        "max_time": 0,
        "results": []
    }
    
    total_time = 0
    
    for i, payload in enumerate(test_cases):
        elapsed = benchmark(url, payload)
        total_time += elapsed
        results["min_time"] = min(results["min_time"], elapsed)
        results["max_time"] = max(results["max_time"], elapsed)
        results["results"].append({
            "test_id": i,
            "time_ms": elapsed
        })
    
    results["total_time"] = total_time
    results["avg_time"] = total_time / len(test_cases) if test_cases else 0
    
    return results
class ExecutorBenchmark:
    def __init__(self):
        self.benchmarks = {}

    def benchmark(self, executor, task):
        # Record start time
        import time
        start = time.perf_counter()
        
        # Execute task
        result = executor.execute(task)
        
        # Record end time
        end = time.perf_counter()
        
        # Calculate latency
        latency = (end - start) * 1000  # Convert to milliseconds
        
        # Store benchmark data
        if executor.__class__.__name__ not in self.benchmarks:
            self.benchmarks[executor.__class__.__name__] = []
        self.benchmarks[executor.__class__.__name__].append(latency)
        
        return {
            "result": result,
            "latency_ms": latency,
            "executor": executor.__class__.__name__
        }

    def get_benchmark_stats(self, executor_name):
        if executor_name in self.benchmarks:
            latencies = self.benchmarks[executor_name]
            return {
                "count": len(latencies),
                "avg_latency": sum(latencies) / len(latencies),
                "min_latency": min(latencies),
                "max_latency": max(latencies)
            }
        return None
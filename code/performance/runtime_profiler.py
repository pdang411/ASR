import time

class RuntimeProfiler:
    def __init__(self):
        self.samples={}
        self.stages={}

    def start(self,name):
        self.samples[name]=time.perf_counter()

    def stop(self,name):
        if name in self.samples:
            elapsed = (time.perf_counter()-self.samples[name])*1000
            del self.samples[name]
            return elapsed
        return 0.0

    def add_stage(self,stage_name,latency_ms):
        if stage_name not in self.stages:
            self.stages[stage_name]=[]
        self.stages[stage_name].append(latency_ms)

    def get_stage_times(self):
        return self.stages
class FastDispatcher:

    def dispatch(self, task, runtime, smart_pipeline):
        mode = task.mode

        if mode == "fast":
            return runtime.execute(task)

        return smart_pipeline.execute(task)
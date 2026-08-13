class LifecycleManager:
    def __init__(self):
        self.startup_hooks=[]
        self.shutdown_hooks=[]

    def on_startup(self, fn):
        self.startup_hooks.append(fn)

    def on_shutdown(self, fn):
        self.shutdown_hooks.append(fn)

    def startup(self):
        for fn in self.startup_hooks:
            fn()

    def shutdown(self):
        for fn in reversed(self.shutdown_hooks):
            fn()
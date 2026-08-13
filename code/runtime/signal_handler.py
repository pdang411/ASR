import signal

def install(runtime):
    def handler(sig, frame):
        runtime.shutdown()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
class EventBus:
    def __init__(self):
        self.listeners=[]

    def subscribe(self, listener):
        self.listeners.append(listener)

    def publish(self, event):
        for listener in self.listeners:
            listener.on_event(event)
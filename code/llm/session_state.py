from enum import Enum

class SessionState(Enum):
    READY = "ready"
    DRAINING = "draining"
    CONNECTING = "connecting"
    WARMUP = "warmup"
    CLOSED = "closed"
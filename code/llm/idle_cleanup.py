import time

class IdleCleanup:
    def cleanup(self, pool, timeout_seconds=300):
        now = time.time()
        for key, session in list(pool.sessions.items()):
            if now - session.last_used > timeout_seconds:
                session.close()
                del pool.sessions[key]
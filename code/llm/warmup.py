class Warmup:
    def initialize(self, session):
        session.connect()
        session.provider.keepalive()
        return True
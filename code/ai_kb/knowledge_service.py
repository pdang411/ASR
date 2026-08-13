class KnowledgeService:
    def __init__(self, search_engine, cache):
        self.search_engine = search_engine
        self.cache = cache

    def query(self, text):
        cached = self.cache.get(text)
        if cached:
            return cached
        result = self.search_engine.search(text)
        self.cache.put(text, result)
        return result
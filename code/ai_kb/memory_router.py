class MemoryRouter:
    def build_context(self, task):
        return {
            "knowledge": [],
            "history": [],
            "workflow": None,
            "capabilities": []
        }
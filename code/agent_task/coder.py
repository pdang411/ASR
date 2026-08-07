class Coder:
    def execute(self, task):
        return {
            "role":"coder",
            "goal":task.goal,
            "artifacts":[]
        }
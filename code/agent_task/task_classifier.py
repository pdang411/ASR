class TaskClassifier:
    SIMPLE = {"chat","lookup","freecad.command","tool.call"}
    COMPLEX = {"research","planning","multi_agent","project"}

    def classify(self, task):
        if task.intent in self.SIMPLE:
            return "fast"
        return "smart"
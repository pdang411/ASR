class Analyst:
    def execute(self, task, aikb):
        task.context["knowledge"]=aikb.search(task.goal)
        return task
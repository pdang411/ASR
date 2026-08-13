class TaskExecutor:
    def __init__(self,workflow_engine):
        self.workflow_engine=workflow_engine

    def execute(self,task):
        return self.workflow_engine.execute(task)
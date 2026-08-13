class TaskValidator:
    def validate(self,task)->None:
        if not task.goal:
            raise ValueError("Missing goal")
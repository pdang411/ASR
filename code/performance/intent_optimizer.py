class IntentOptimizer:
    FAST={"chat","lookup","tool.call","freecad.command"}

    def use_fast_path(self,intent):
        return intent in self.FAST

    def get_fast_intents(self):
        return self.FAST

    def add_fast_intent(self, intent):
        self.FAST.add(intent)
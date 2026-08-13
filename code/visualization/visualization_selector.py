class VisualizationSelector:

    def select(self, task, state):
        if getattr(task,'interactive',False):
            return VisualizationLevel.INTERACTIVE
        if getattr(task,'requires_chart',False) and state.chart_available:
            return VisualizationLevel.RICH
        return VisualizationLevel.TEXT
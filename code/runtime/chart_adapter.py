class ChartAdapter:
    def accepts(self, task):
        return getattr(task, "media_type", "") in ("chart", "graph", "diagram")

    def dispatch(self, task):
        return {
            "executor": "chart_mcp",
            "reference": getattr(task, "input_ref", ""),
            "pipeline": getattr(task, "pipeline", ""),
        }

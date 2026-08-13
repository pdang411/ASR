from runtime.visualization import VisualizationLevel


class VisualizationSelector:
    def _flag(self, task, name: str) -> bool:
        value = getattr(task, name, None)
        if isinstance(value, bool):
            return value

        metadata = getattr(task, "metadata", None)
        if isinstance(metadata, dict):
            raw = metadata.get(name)
            if isinstance(raw, bool):
                return raw
            if isinstance(raw, str):
                return raw.strip().lower() in {"1", "true", "yes", "y", "on"}
        return False

    def select(self, task, state):
        if self._flag(task, "interactive"):
            return VisualizationLevel.INTERACTIVE
        if self._flag(task, "requires_chart") and getattr(state, "chart_available", False):
            return VisualizationLevel.RICH
        return VisualizationLevel.TEXT

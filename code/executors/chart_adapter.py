from ai_kb.universal_task import UniversalTask

class ChartAdapter:

    def accepts(self, task):
        return task.media_type in ("chart","graph","diagram")

    def dispatch(self, task):
        return {
            "executor":"chart_mcp",
            "reference":task.input_ref,
            "pipeline":task.pipeline
        }

class VoiceAdapter:

    def accepts(self, task):
        return task.media_type in ("voice","mp3","music")

    def dispatch(self, task):
        return {
            "executor":"voice_mcp",
            "reference":task.input_ref
        }
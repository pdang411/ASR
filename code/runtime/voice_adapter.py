class VoiceAdapter:
    def accepts(self, task):
        return getattr(task, "media_type", "") in ("voice", "mp3", "music")

    def dispatch(self, task):
        return {
            "executor": "voice_mcp",
            "reference": getattr(task, "input_ref", ""),
        }

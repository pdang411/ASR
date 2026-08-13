from enum import Enum

class Capability(str, Enum):
    KNOWLEDGE_SEARCH='knowledge.search'
    CODE_GENERATE='code.generate'
    CODE_REVIEW='code.review'
    CAD_MODEL='cad.model'
    WORKFLOW_PLAN='workflow.plan'
    REPOSITORY_SEARCH='repository.search'
    IMAGE_ANALYZE='image.analyze'
    AUDIO_TRANSCRIBE='audio.transcribe'
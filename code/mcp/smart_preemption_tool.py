async def asr_smart_preemption_status(preemption):
    """Return live Smart Preemption status and cached FLASH announcement."""
    return preemption.status()

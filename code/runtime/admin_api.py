# Optional future HTTP adapter

from fastapi import APIRouter, Header, HTTPException

router = APIRouter()

runtime_control = None
SETTINGS = None


@router.post("/admin/shutdown")
def shutdown(api_key: str = Header(default="")):
    expected = getattr(SETTINGS, "ADMIN_API_KEY", "") if SETTINGS is not None else ""
    if api_key != expected:
        raise HTTPException(status_code=401)

    if runtime_control is None:
        raise HTTPException(status_code=503)

    runtime_control.request_shutdown("http")
    return {"status": "draining"}

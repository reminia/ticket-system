from fastapi import APIRouter

router = APIRouter(prefix="/v1")


@router.get("/ping")
def ping():
    return {"status": "ok", "message": "pong"}

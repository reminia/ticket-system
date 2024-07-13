from fastapi import FastAPI

from src.api.v1 import ticket_api
from src.models.database import Base, engine

# create tickets db
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ticket system api",
              description="Rest api for create, query and process tickets.",
              version="0.1.0",
              openapi_url="/openapi.json",
              docs_url="/docs",  # swagger UI
              redoc_url="/redoc")  # ReDoc
app.include_router(ticket_api.router)


@app.get("/ping")
def root_ping():
    """
    Server liveness check.
    """
    return {"status": "ok", "message": "I'm up!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

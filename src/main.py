from fastapi import FastAPI

from src.api.v1 import routes
from src.models.database import Base, engine

# create tickets db
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(routes.router)


@app.get("/ping")
def root_ping():
    return {"status": "ok", "message": "I'm up!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI

from src.api.v1 import routes

app = FastAPI()
app.include_router(routes.router)


@app.get("/ping")
def root_ping():
    return {"status": "ok", "message": "I'm up!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

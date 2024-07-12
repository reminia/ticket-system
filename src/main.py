from fastapi import FastAPI

app = FastAPI()


@app.get("/ping")
def root_ping():
    return {"status": "ok", "message": "I'm up!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

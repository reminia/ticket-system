# ticket system
![CI](https://github.com/reminia/ticket-system/actions/workflows/ci.yml/badge.svg)

Rest api for a support ticket system including create, query and process tickets. <br/>
It leverages LLM models to categorize, priority and respond to tickets.

## features

* create ticket, new ticket will be added to redis queue for processing.
* query ticket by ticket id.
* assign ticket priority, category and initial response by AI providers automatically.
* filter tickets by status, priority and category.
* trigger ticket processing manually.

## tech stack

* fastapi for webservice
* rq for task queue
* sqlalchemy and pydantic for ORM & data validation
* sqlite as database
* langchain for LLM(anthropic or openai)processing

## setup

* install redis using docker by `docker run --name my-redis -p 6379:6379 -d redis`.
* install rq(redis queue) by `pip install rq`.
* setup env variables, please refer to the [env](.env.example) file.
AI proxy urls could be empty, set them if u access the api through a proxy.

## build & run

* build: `poetry install && poetry build`.
* lint: `poetry run flake8`.
* run:
    - `poetry run uvicorn src.main:app`, server will start at `localhost:8000` by default.
    -  start rq worker: `poetry run rq worker -u redis://localhost:6379`
* dev mode: `poetry run uvicorn src.main:app --reload`, reload when codes changed.
* test: `poetry run pytest`.
* docs: visit `localhost:8000/docs` for Swagger UI, `localhost:8000/redoc` for ReDoc.

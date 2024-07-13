# ticket system
![CI](https://github.com/reminia/ticket-system/actions/workflows/ci.yml/badge.svg)

Rest api for a support ticket system including submit, query, process tickets.

## features

* create ticket.
* query ticket by ticket id.
* assign ticket priority, category and initial response by AI providers automatically.
* filter tickets by status, priority and category.
* manually trigger ticket processing in queue.

## tech stack

* fastapi for webservice
* rq for task queue
* sqlalchemy and pydantic for ORM & data validation
* sqlite as database

## setup

* install redis using docker by `docker run --name my-redis -p 6379:6379 -d redis`.
* setup env variables, please refer to the [env](.env.example) file.

## build & run

* build: `poetry build`.
* run: `poetry run uvicorn src.main:app`, server will start at `localhost:8000` by default.
* dev mode: `poetry run uvicorn src.main:app --reload`, reload when codes changed.
* test: `poetry run pytest`.
* docs: visit `localhost:8000/docs` for Swagger UI, `localhost:8000/redoc` for ReDoc.

# ticket system

Rest api for a support ticket system including submit, query, process ticket.

## tech stack

* fastapi for webservice
* rq for task queue
* sqlalchemy and pydantic for ORM & data validation
* sqlite as database

## build & run

* build. `poetry build`
* run. `poetry run uvicorn src.main:app`
* dev mode. `poetry run uvicorn src.main:app --reload`, reload when codes changed.

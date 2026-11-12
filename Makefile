.PHONY: up down migrate lint typecheck test

up:
	docker compose up --build -d

down:
	docker compose down

migrate:
	docker compose run --rm app alembic upgrade head

lint:
	ruff check .
	ruff format --check .

typecheck:
	mypy app

test:
	pytest

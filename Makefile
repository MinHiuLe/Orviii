.PHONY: up down migrate

up:
	docker compose up --build -d

down:
	docker compose down

migrate:
	docker compose run --rm app alembic upgrade head

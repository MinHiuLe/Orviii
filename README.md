# Orviii

Orviii is a production-minded real-time chat app built with Python and FastAPI.

## Run locally

Requirements: Python 3.12, Docker Compose, and GNU Make.

```bash
git clone git@github.com:MinHiuLe/Orviii.git
cd Orviii
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
make up
make migrate
make test
```

The app is available at <http://localhost:8000>. Use `make down` to stop the
Compose services.

## Checks

Run `make lint` and `make typecheck` inside the activated virtual environment.
The test suite runs without a live database; the migration check uses the
PostgreSQL service in Compose or CI.

## Layout

- `app/auth/`, `app/chat/`, `app/realtime/`, `app/core/`: application modules
- `migrations/`: Alembic schema migrations
- `tests/`: automated tests
- `docs/decisions/`: architecture decision records
- `loadtest/`: load testing assets (planned)

## Current tier

Tier 1: authentication and one-to-one chat on one node, with production-minded
foundations. Distributed delivery and the AI assistant are later tiers.

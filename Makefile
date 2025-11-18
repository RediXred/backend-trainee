.PHONY: build up down restart logs test clean load-test-ui migrate


build:
	docker compose build

up:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f app

test: test-setup-db
	docker compose exec app pytest tests/

test-setup-db:
	@if [ -f .env ]; then \
		export $$(cat .env | grep -v '^#' | grep -v '^$$' | xargs); \
	fi; \
	POSTGRES_USER=$${POSTGRES_USER:-postgres}; \
	POSTGRES_DB=$${POSTGRES_DB:-postgres}; \
	TEST_POSTGRES_DB=$${TEST_POSTGRES_DB:-pr_reviewer_db_test}; \
	echo "Creating test database"; \
	docker compose exec db psql -U $$POSTGRES_USER -d $$POSTGRES_DB -c "SELECT 1 FROM pg_database WHERE datname = '$$TEST_POSTGRES_DB'" | grep -q 1 || \
	docker compose exec db psql -U $$POSTGRES_USER -d $$POSTGRES_DB -c "CREATE DATABASE $$TEST_POSTGRES_DB;"; \
	echo "Test database ready"

clean:
	docker compose down -v
	docker system prune -f

migrate:
	docker compose exec app alembic upgrade head

load-test-ui:
	@if [ -f .env ]; then \
		export $$(cat .env | grep -v '^#' | xargs); \
	fi; \
	APP_HOST=$${APP_HOST:-localhost}; \
	APP_PORT=$${APP_PORT:-8080}; \
	locust -f locustfile.py --host=http://$${APP_HOST}:$${APP_PORT}

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
	@echo "Creating test database"
	docker compose exec db psql -U postgres -c "SELECT 1 FROM pg_database WHERE datname = 'pr_reviewer_db_test'" | grep -q 1 || \
	docker compose exec db psql -U postgres -c "CREATE DATABASE pr_reviewer_db_test;"
	@echo "Test database ready"

clean:
	docker compose down -v
	docker system prune -f

migrate:
	docker compose exec app alembic upgrade head

load-test-ui:
	locust -f locustfile.py --host=http://localhost:8080

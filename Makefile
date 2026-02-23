.PHONY: run-postgres run-redis

run-postgres:
	@echo Starting postgres container
	docker run \
	  -e POSTGRES_PASSWORD=foobarbaz \
	  -v pgdata:/var/lib/postgresql/data \
	  -p 5432:5432 \
	  postgres:15.1-alpine

run-redis:
	@echo Starting redis container
	docker run \
	  -p 6379:6379 \
	  redis:alpine

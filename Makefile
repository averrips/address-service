.PHONY: manage

start:
	docker compose up

migrate:
	docker compose exec app ./manage.py migrate app
startapp:
	docker-compose up

startkong:
	cd kong && docker-compose up

postgres-migrate:
	docker-compose run $(SERVICE) alembic revision --autogenerate -m "$(MESSAGE)"
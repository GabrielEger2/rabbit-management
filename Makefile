startapp:
	docker-compose up

startkong:
	cd kong && docker-compose up

create-network:
	docker network create kong-net

alembic-init:
	docker-compose run $(SERVICE) alembic init alembic

postgres-migrate:
	docker-compose run $(SERVICE) alembic revision --autogenerate -m "$(MESSAGE)"

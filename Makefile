startapp:
	docker-compose up

startkong:
	cd kong && docker-compose up

lint:
	black .
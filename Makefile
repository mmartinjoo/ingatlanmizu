deploy:
	./deploy/deploy.sh

ssh:
	ssh alwyzon@203.34.137.201

up:
	docker compose up --remove-orphans
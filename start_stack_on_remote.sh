set -e

cd /home/alwyzon/ingatlanmizu

docker compose down
docker compose up -d --remove-orphans
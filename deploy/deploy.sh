set -e

rsync -avz \
  --exclude='api/.venv/' \
  --exclude='minio/' \
  --exclude='postgres/' \
  --exclude='.env' \
  --exclude='.env.example' \
  --exclude='.git' \
  --exclude='.claude' \
  --exclude='api/transform/target/' \
  --exclude='api/transform/logs/' \
  --exclude='frontend/node_modules/' \
  --exclude='frontend/.vscode/' \
  ../ alwyzon@203.34.137.201:/home/alwyzon/ingatlanmizu

ssh -tt -o StrictHostKeyChecking=no alwyzon@203.34.137.201 "cd /home/alwyzon/ingatlanmizu && docker compose -f docker-compose.yml -f docker-compose.prod.yml down"
ssh -tt -o StrictHostKeyChecking=no alwyzon@203.34.137.201 "cd /home/alwyzon/ingatlanmizu && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build"
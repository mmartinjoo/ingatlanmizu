set -e

rsync -avz \
  --exclude='.venv/' \
  --exclude='minio/' \
  --exclude='postgres/' \
  --exclude='.env' \
  --exclude='.env.example' \
  --exclude='.git' \
  --exclude='transform/target/' \
  ./ alwyzon@203.34.137.201:/home/alwyzon/ingatlanmizu

ssh -tt -o StrictHostKeyChecking=no alwyzon@203.34.137.201 "/home/alwyzon/ingatlanmizu/start_stack_on_remote.sh"
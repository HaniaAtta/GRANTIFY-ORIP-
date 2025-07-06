#!/bin/bash -xe

# === Load environment variables from parent directory ===
set -o allexport
source ../.env
set +o allexport

# === Clone the project ===
git clone -b main https://github.com/HaniaAtta/GRANTIFY-ORIP-.git
cd GRANTIFY-ORIP-

# === System Updates & Tools ===
sudo apt update -y
sudo apt install -y python3-venv git curl docker.io

# === Python Virtual Environment ===
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# === Redis with Docker ===
sudo systemctl start docker
docker run -d --name redis-stack -p 6379:6379 redis

# === Start Celery Worker ===
celery -A celery_worker.celery worker --loglevel=info &

# === Start FastAPI app ===
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# === Trigger Scraping ===
sleep 5
echo "[INFO] Triggering /scrape_all..."
curl -X POST "$NEON_CURL_ENDPOINT"

# === Wait for scraping to complete ===
echo "[INFO] Waiting for 2 minutes..."
sleep 120

echo "[INFO] Scraping done. This server can now be safely destroyed."

# === Destroy the Droplet ===
echo "[INFO] Destroying Droplet ID: $DROPLET_ID ..."
curl -X DELETE \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DO_API_TOKEN" \
  "https://api.digitalocean.com/v2/droplets/$DROPLET_ID"

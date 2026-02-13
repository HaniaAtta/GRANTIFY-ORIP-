#!/bin/bash
# Clean up Docker containers and start fresh

echo "=========================================="
echo "Cleaning Up Docker Containers"
echo "=========================================="
echo ""

# Stop and remove all containers
echo "🛑 Stopping and removing containers..."
docker-compose down --remove-orphans

# Remove any orphaned containers
echo "🧹 Removing orphaned containers..."
docker ps -a --filter "name=gtw" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true
docker ps -a --filter "name=grantly" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true

# Remove any conflicting containers
echo "🔧 Removing conflicting containers..."
docker rm -f grantly_redis grantly_app grantly_celery 2>/dev/null || true

echo ""
echo "✅ Cleanup complete!"
echo ""

# Start services
echo "=========================================="
echo "Starting Services"
echo "=========================================="
echo ""

docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

echo ""
echo "📊 Checking services..."
docker-compose ps

echo ""
echo "=========================================="
echo "✅ Dashboard Ready!"
echo "=========================================="
echo ""
echo "🌐 Access: http://localhost:8000"
echo ""
echo "👤 Admin: admin / secret123@"
echo "👤 User: user / user123@"
echo ""


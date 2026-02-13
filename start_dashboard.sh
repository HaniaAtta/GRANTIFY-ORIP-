#!/bin/bash
# Quick script to start dashboard and show access information

echo "=========================================="
echo "Starting Grant Dashboard"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with:"
    echo "  - DATABASE_URL"
    echo "  - OPENAI_API_KEY"
    echo "  - REDIS_URL"
    exit 1
fi

echo "✅ .env file found"
echo ""

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Start services
echo "🐳 Starting Docker services..."
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check services
echo ""
echo "📊 Checking services..."
docker-compose ps

echo ""
echo "=========================================="
echo "✅ Dashboard is Ready!"
echo "=========================================="
echo ""
echo "🌐 Access Dashboard:"
echo "   http://localhost:8000"
echo ""
echo "👤 Login Credentials:"
echo ""
echo "   ADMIN PANEL (Full Access):"
echo "   Username: admin"
echo "   Password: secret123@"
echo ""
echo "   USER PANEL (Read-Only):"
echo "   Username: user"
echo "   Password: user123@"
echo ""
echo "=========================================="
echo "Admin Panel Features:"
echo "  ✅ Add new grant URLs"
echo "  ✅ Delete grants"
echo "  ✅ Update grant information"
echo "  ✅ Search and filter"
echo "  ✅ Trigger scraping"
echo ""
echo "User Panel Features:"
echo "  ✅ View all grants"
echo "  ✅ Search grants"
echo "  ✅ Filter by category"
echo "  ❌ Cannot add/delete (read-only)"
echo "=========================================="
echo ""
echo "📋 Useful Commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop: docker-compose down"
echo "   Restart: docker-compose restart"
echo ""
echo "🔍 Test Scraping:"
echo "   docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers"
echo ""


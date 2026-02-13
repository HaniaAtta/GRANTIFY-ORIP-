#!/bin/bash
# Quick start script for the grant dashboard

set -e

echo "=========================================="
echo "Grant Dashboard - Quick Start"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with:"
    echo "  - DATABASE_URL (your NeonDB connection string)"
    echo "  - OPENAI_API_KEY (your OpenAI API key)"
    echo "  - REDIS_URL=redis://redis:6379/0"
    exit 1
fi

echo "✅ .env file found"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Ask user what they want to do
echo "What would you like to do?"
echo "1. Export data from categories.json to NeonDB"
echo "2. Start Docker services (FastAPI + Celery + Redis)"
echo "3. Run scraping for all grants"
echo "4. Do everything (export + start + scrape)"
echo "5. Just start Docker services"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "📊 Exporting data from categories.json to NeonDB..."
        python export_json_to_db.py
        ;;
    2)
        echo ""
        echo "🐳 Starting Docker services..."
        docker-compose up --build -d
        echo ""
        echo "✅ Services started!"
        echo "📊 Check status: docker-compose ps"
        echo "📋 View logs: docker-compose logs -f"
        echo "🌐 Dashboard: http://localhost:8000"
        ;;
    3)
        echo ""
        echo "🔍 Running scraping for all grants..."
        docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers
        echo ""
        echo "✅ Scraping started! Check logs: docker-compose logs -f celery"
        ;;
    4)
        echo ""
        echo "📊 Step 1: Exporting data from categories.json..."
        python export_json_to_db.py
        echo ""
        echo "🐳 Step 2: Starting Docker services..."
        docker-compose up --build -d
        echo ""
        echo "⏳ Waiting for services to be ready..."
        sleep 5
        echo ""
        echo "🔍 Step 3: Running scraping for all grants..."
        docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers
        echo ""
        echo "✅ All done!"
        echo "🌐 Dashboard: http://localhost:8000"
        echo "📋 View logs: docker-compose logs -f"
        ;;
    5)
        echo ""
        echo "🐳 Starting Docker services..."
        docker-compose up --build -d
        echo ""
        echo "✅ Services started!"
        echo ""
        echo "Next steps:"
        echo "  📊 Export data: python export_json_to_db.py"
        echo "  🔍 Scrape grants: docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers"
        echo "  🌐 Dashboard: http://localhost:8000"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="


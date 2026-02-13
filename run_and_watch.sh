#!/bin/bash
# Run scraper directly and watch progress

echo "=========================================="
echo "🚀 Running Scraper Directly (No Celery)"
echo "=========================================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated"
    echo "   Activating: source HandM/bin/activate"
    source HandM/bin/activate 2>/dev/null || {
        echo "❌ Could not activate virtual environment"
        echo "   Please activate manually: source HandM/bin/activate"
        exit 1
    }
fi

echo "✅ Virtual environment: $VIRTUAL_ENV"
echo ""

# Run scraper in background and capture output
echo "Starting scraper..."
echo ""

# Run scraper and show progress
python3 run_scraper_direct.py 2>&1 | while IFS= read -r line; do
    # Show all output with formatting
    if echo "$line" | grep -qiE "(starting|scraping|finished|completed|error|success)"; then
        # Format based on content
        if echo "$line" | grep -qi "starting"; then
            echo "🔄 $line"
        elif echo "$line" | grep -qi "finished\|completed\|success"; then
            echo "✅ $line"
        elif echo "$line" | grep -qi "error"; then
            echo "❌ $line"
        else
            echo "$line"
        fi
    else
        echo "$line"
    fi
done

echo ""
echo "=========================================="
echo "✅ Scraping Complete!"
echo "=========================================="
echo ""
echo "Check results:"
echo "  python3 show_scraper_results.py"
echo ""


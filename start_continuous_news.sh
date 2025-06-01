#!/bin/bash
# Start Heart of News in continuous mode

echo "🚀 Starting Heart of News in Continuous Mode..."
echo "📅 Will post every 5-10 minutes"
echo "⏰ Started at: $(date)"
echo ""

# Run the fixed system in continuous mode
python3 /tmp/heart-of-news-backend/start_heart_of_news_fixed.py --continuous
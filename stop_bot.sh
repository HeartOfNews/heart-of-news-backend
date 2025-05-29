#!/bin/bash
# Script to stop the background Russian news bot

echo "🛑 Stopping Russian News Bot..."

if [ -f "bot.pid" ]; then
    BOT_PID=$(cat bot.pid)
    if ps -p $BOT_PID > /dev/null; then
        kill $BOT_PID
        echo "✅ Bot with PID $BOT_PID stopped"
        rm bot.pid
    else
        echo "⚠️ No bot process found with PID $BOT_PID"
        rm bot.pid
    fi
else
    echo "⚠️ No bot.pid file found"
    echo "Checking for any running bot processes..."
    
    # Find and kill any running bot processes
    pkill -f "verified_russian_news_bot.py"
    
    if [ $? -eq 0 ]; then
        echo "✅ Stopped any running bot processes"
    else
        echo "ℹ️ No bot processes found running"
    fi
fi
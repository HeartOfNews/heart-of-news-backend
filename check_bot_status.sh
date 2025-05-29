#!/bin/bash
# Script to check Russian news bot status

echo "🔍 Checking Russian News Bot Status..."
echo "=" * 40

# Check if bot.pid file exists
if [ -f "bot.pid" ]; then
    BOT_PID=$(cat bot.pid)
    echo "📋 Bot PID file found: $BOT_PID"
    
    # Check if process is running
    if ps -p $BOT_PID > /dev/null; then
        echo "✅ Bot is RUNNING (PID: $BOT_PID)"
        
        # Show process details
        echo "📊 Process details:"
        ps aux | grep $BOT_PID | grep -v grep
        
        # Show recent log output
        if [ -f "bot_output.log" ]; then
            echo ""
            echo "📄 Recent log output (last 10 lines):"
            tail -n 10 bot_output.log
        fi
    else
        echo "❌ Bot process not found (PID $BOT_PID may have died)"
    fi
else
    echo "⚠️ No bot.pid file found"
    
    # Check for any running processes
    RUNNING_BOTS=$(pgrep -f "verified_russian_news_bot.py")
    if [ ! -z "$RUNNING_BOTS" ]; then
        echo "⚠️ Found running bot processes without PID file:"
        echo "$RUNNING_BOTS"
    else
        echo "❌ No bot processes running"
    fi
fi

echo ""
echo "💡 Commands:"
echo "   Start bot: ./run_bot_background.sh"
echo "   Stop bot:  ./stop_bot.sh"
echo "   View logs: tail -f bot_output.log"
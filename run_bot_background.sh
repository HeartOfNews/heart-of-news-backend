#!/bin/bash
# Script to run Russian news bot in background

echo "🇷🇺 Starting Russian News Bot in background..."

# Option 1: Using nohup (keeps running after terminal closes)
echo "Starting with nohup..."
nohup python3 verified_russian_news_bot.py > bot_output.log 2>&1 &

# Get the process ID
BOT_PID=$!
echo "✅ Bot started with PID: $BOT_PID"
echo "📋 Bot PID saved to bot.pid file"
echo $BOT_PID > bot.pid

echo "📊 To check status: ps aux | grep verified_russian_news_bot.py"
echo "🛑 To stop bot: kill $BOT_PID"
echo "📄 To view logs: tail -f bot_output.log"
echo ""
echo "Bot is now running in background and will continue even if you close terminal!"
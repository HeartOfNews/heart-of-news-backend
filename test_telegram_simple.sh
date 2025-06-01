#!/bin/bash

echo "🤖 Testing Heart of News Telegram Bot..."
echo "Bot: @HeartOfNews_bot"
echo "Channel: @heartofnews"
echo ""

echo "1. Testing bot connection..."
curl -s "https://api.telegram.org/bot7568175094:AAHh3nHCoRqssSUo9A1FLnM5yi5K1bu54vs/getMe" | grep -o '"first_name":"[^"]*"' | cut -d'"' -f4

echo ""
echo "2. Sending test message to channel..."

curl -X POST "https://api.telegram.org/bot7568175094:AAHh3nHCoRqssSUo9A1FLnM5yi5K1bu54vs/sendMessage" \
-H "Content-Type: application/json" \
-d '{
  "chat_id": "@heartofnews",
  "text": "🎉 **Heart of News Bot is Now Live!**\n\n✅ Telegram integration successfully configured\n🤖 Automated news publishing is ready\n📰 Stay tuned for bias-free news updates\n\n🔗 Website: http://localhost:3000",
  "parse_mode": "Markdown"
}' | python3 -m json.tool

echo ""
echo "✅ Test complete! Check your @heartofnews channel."
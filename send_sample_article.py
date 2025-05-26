#!/usr/bin/env python3
"""
Send a sample news article to Telegram
"""

import json
import subprocess

BOT_TOKEN = "7568175094:AAHh3nHCoRqssSUo9A1FLnM5yi5K1bu54vs"
CHANNEL_ID = "-1002643653940"

# Sample article
article_message = """🗞️ **Breaking: New Scientific Discovery in Quantum Computing**

📰 Researchers at leading universities have achieved a major breakthrough in quantum computing stability, potentially accelerating the development of practical quantum computers for everyday use.

🔗 [Read more](http://localhost:3000/articles/quantum-breakthrough-2024)

📊 Bias Score: 9/10
📈 Source Reliability: 9/10

#Science #Technology #QuantumComputing #Research #Innovation"""

payload = {
    "chat_id": CHANNEL_ID,
    "text": article_message,
    "parse_mode": "Markdown",
    "disable_web_page_preview": False
}

curl_command = [
    "curl", "-X", "POST",
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    "-H", "Content-Type: application/json",
    "-d", json.dumps(payload)
]

print("📤 Sending sample news article to @heartofnews...")
result = subprocess.run(curl_command, capture_output=True, text=True)
response = json.loads(result.stdout)

if response.get("ok"):
    print(f"✅ Article published successfully!")
    print(f"📱 Message ID: {response['result']['message_id']}")
    print(f"🔗 Check your channel: https://t.me/heartofnews")
else:
    print(f"❌ Failed: {response.get('description', 'Unknown error')}")
    print(f"🔍 Response: {response}")
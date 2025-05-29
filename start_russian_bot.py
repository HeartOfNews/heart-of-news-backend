#!/usr/bin/env python3
"""
Quick start script for Verified Russian News Bot
ONLY PUBLISHES REAL NEWS FROM TRUSTED SOURCES
"""

import subprocess
import sys
import os

def main():
    print("🇷🇺 HEART OF NEWS - RUSSIAN NEWS BOT")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("Select mode:")
        print("1. Test connection (--test)")
        print("2. Publish news once (--once)")
        print("3. Run continuously - posts every 1-5 minutes (default)")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            mode = "--test"
        elif choice == "2":
            mode = "--once"
        else:
            mode = "continuous"
    
    bot_script = os.path.join(os.path.dirname(__file__), "verified_russian_news_bot.py")
    
    if mode == "--test":
        print("🧪 Testing bot connection...")
        subprocess.run([sys.executable, bot_script, "--test"])
    elif mode == "--once":
        print("📤 Publishing news...")
        subprocess.run([sys.executable, bot_script, "--once"])
    else:
        print("🔄 Starting continuous mode...")
        print("⏰ Posts every 1-5 minutes when news is available")
        print("Press Ctrl+C to stop")
        subprocess.run([sys.executable, bot_script])

if __name__ == "__main__":
    main()
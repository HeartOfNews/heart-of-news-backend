#!/usr/bin/env python3
"""
Start Russian Verified News Publishing
Easy startup script for the Russian Telegram news channel
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_environment():
    """Check if environment is properly configured"""
    required_env_vars = [
        'TELEGRAM_RU_BOT_TOKEN',
        'TELEGRAM_RU_CHANNEL_ID'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error("❌ Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        logger.error("\nPlease set these environment variables before running:")
        logger.error("export TELEGRAM_RU_BOT_TOKEN='your_bot_token'")
        logger.error("export TELEGRAM_RU_CHANNEL_ID='@your_channel_id'")
        logger.error("export TELEGRAM_RU_ENABLED=true")
        return False
    
    logger.info("✅ Environment variables configured")
    return True


def check_dependencies():
    """Check if required Python packages are available"""
    required_packages = [
        'httpx',
        'feedparser', 
        'beautifulsoup4',
        'lxml'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error("❌ Missing required packages:")
        for package in missing_packages:
            logger.error(f"   - {package}")
        logger.error("\nInstall missing packages with:")
        logger.error(f"pip install {' '.join(missing_packages)}")
        return False
    
    logger.info("✅ All required packages available")
    return True


def create_logs_directory():
    """Create logs directory if it doesn't exist"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir()
        logger.info("📁 Created logs directory")


def show_menu():
    """Show the startup menu"""
    print("\n" + "="*60)
    print("🇷🇺 RUSSIAN VERIFIED NEWS PUBLISHER")
    print("="*60)
    print("Publishes real, verified news to Russian Telegram channel")
    print("Automatically detects and removes propaganda content")
    print("\nOptions:")
    print("1. Run once (test mode)")
    print("2. Run continuously (production mode)")
    print("3. Test propaganda detection only")
    print("4. Check configuration")
    print("5. Exit")
    print("="*60)


def run_test_mode():
    """Run the worker once for testing"""
    logger.info("🧪 Running in test mode (single cycle)...")
    try:
        result = subprocess.run([
            sys.executable, 
            "russian_verified_news_worker.py", 
            "--once"
        ], check=True, capture_output=True, text=True)
        
        logger.info("✅ Test run completed successfully")
        if result.stdout:
            print("Output:", result.stdout)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Test run failed: {e}")
        if e.stderr:
            print("Error:", e.stderr)
    except FileNotFoundError:
        logger.error("❌ Russian news worker script not found")


def run_continuous_mode():
    """Run the worker continuously"""
    logger.info("🔄 Starting continuous mode...")
    logger.info("Press Ctrl+C to stop")
    
    try:
        subprocess.run([
            sys.executable,
            "russian_verified_news_worker.py"
        ], check=True)
        
    except KeyboardInterrupt:
        logger.info("🛑 Stopped by user")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Worker failed: {e}")
    except FileNotFoundError:
        logger.error("❌ Russian news worker script not found")


def run_propaganda_test():
    """Run propaganda detection test"""
    logger.info("🔍 Testing propaganda detection...")
    
    try:
        result = subprocess.run([
            sys.executable,
            "test_russian_news_processing.py"
        ], check=True)
        
        logger.info("✅ Propaganda detection test completed")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Test failed: {e}")
    except FileNotFoundError:
        logger.error("❌ Test script not found")


def check_configuration():
    """Check and display current configuration"""
    print("\n📋 CURRENT CONFIGURATION:")
    print("-" * 40)
    
    # Check environment variables
    bot_token = os.getenv('TELEGRAM_RU_BOT_TOKEN', 'NOT SET')
    channel_id = os.getenv('TELEGRAM_RU_CHANNEL_ID', 'NOT SET')
    enabled = os.getenv('TELEGRAM_RU_ENABLED', 'NOT SET')
    
    # Mask bot token for security
    if bot_token != 'NOT SET':
        bot_token = bot_token[:10] + "..." + bot_token[-5:]
    
    print(f"Bot Token: {bot_token}")
    print(f"Channel ID: {channel_id}")
    print(f"Enabled: {enabled}")
    
    # Check files
    files_to_check = [
        "russian_verified_news_worker.py",
        "test_russian_news_processing.py",
        "app/services/scraper/sources_ru.py",
        "app/services/telegram_service_ru.py",
        "app/services/ai/propaganda_detector.py"
    ]
    
    print(f"\n📁 FILES:")
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")


def main():
    """Main entry point"""
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🇷🇺 RUSSIAN VERIFIED NEWS PUBLISHER")
    print("Starting up...")
    
    # Create logs directory
    create_logs_directory()
    
    # Check environment and dependencies
    if not check_environment():
        sys.exit(1)
    
    # Show menu and handle user choice
    while True:
        show_menu()
        
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                run_test_mode()
            elif choice == "2":
                run_continuous_mode()
            elif choice == "3":
                run_propaganda_test()
            elif choice == "4":
                check_configuration()
            elif choice == "5":
                logger.info("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except KeyboardInterrupt:
            logger.info("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
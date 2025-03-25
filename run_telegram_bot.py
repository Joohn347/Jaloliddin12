"""
This file is only for running the Telegram bot using the python-telegram-bot library.
It is meant to be run as a standalone script, not imported.
"""
import logging
import os
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """
    Run the Telegram bot as a standalone application.
    This is the entry point for the bot workflow.
    """
    try:
        # Check if token is available
        token = os.environ.get('TELEGRAM_TOKEN')
        if not token:
            logger.error("TELEGRAM_TOKEN environment variable not set!")
            return
            
        # Import and run the bot
        from simple_telegram_bot import main as run_bot
        logger.info("Starting Qur'on bot using python-telegram-bot library")
        await run_bot()
    except Exception as e:
        logger.error(f"Error running Telegram bot: {e}")

if __name__ == "__main__":
    # Run the main function using asyncio
    asyncio.run(main())
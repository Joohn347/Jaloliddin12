"""
This is the main entry point for the Telegram bot.
It imports the telebot_main module and runs the bot.
"""
import logging
import os
from telebot_main import bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check if the Telegram token is set
if not os.environ.get('TELEGRAM_TOKEN'):
    logger.error("TELEGRAM_TOKEN environment variable not set!")
    exit(1)

if __name__ == "__main__":
    logger.info("Starting Qur'on bot using PyTelegramBotAPI")
    try:
        # Start the bot
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Error running Telegram bot: {e}")
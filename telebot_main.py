"""
Telegram bot using telebot (PyTelegramBotAPI) library.
This is a simpler implementation that avoids package conflicts.
"""
import os
import logging
import telebot
from quran_api import QuranAPI
from utils import format_verse_message, format_search_results, parse_verse_command

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Quran API
quran_api = QuranAPI()

# Create bot instance
TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    logger.error("TELEGRAM_TOKEN environment variable not set!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# Command handlers
@bot.message_handler(commands=['start'])
def start_command(message):
    """Handle the /start command"""
    user_first_name = message.from_user.first_name
    bot.reply_to(message, 
        f"Assalomu alaykum, {user_first_name}! 🌙\n\n"
        "Qurʼon botiga xush kelibsiz. Bu bot sizga Qurʼon oyatlarini o'qish, qidirish va ulashish imkonini beradi.\n\n"
        "Buyruqlar:\n"
        "/start - Botni qayta ishga tushirish\n"
        "/help - Yordam olish\n"
        "/verse [sura]:[oyat] - Muayyan oyatni olish (masalan, /verse 1:1)\n"
        "/surah [sura] - Suradan oyatlarni olish (masalan, /surah 1)\n"
        "/search [so'z] - Kalit so'z bo'yicha qidirish (masalan, /search rahmat)"
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    """Handle the /help command"""
    bot.reply_to(message,
        "Qurʼon botidan foydalanish uchun quyidagi buyruqlardan foydalaning:\n\n"
        "/start - Botni qayta ishga tushirish\n"
        "/help - Yordam olish\n"
        "/verse [sura]:[oyat] - Muayyan oyatni olish (masalan, /verse 1:1)\n"
        "/surah [sura] - Suradan oyatlarni olish (masalan, /surah 1)\n"
        "/search [so'z] - Kalit so'z bo'yicha qidirish (masalan, /search rahmat)"
    )

@bot.message_handler(commands=['verse'])
def verse_command(message):
    """Handle the /verse command to retrieve a specific verse"""
    command_parts = message.text.split()
    
    if len(command_parts) < 2:
        bot.reply_to(message, "Iltimos, surah va oyat raqamini kiriting. Masalan: /verse 1:1")
        return
    
    verse_ref = command_parts[1]
    surah, ayah = parse_verse_command(verse_ref)
    
    if not surah or not ayah:
        bot.reply_to(message, "Noto'g'ri format. Iltimos, surah:oyat shaklida kiriting (masalan, 1:1)")
        return
    
    # Get verse data
    verse_data = quran_api.get_verse(surah, ayah)
    if not verse_data.get('success', False):
        bot.reply_to(message, f"Xato: {verse_data.get('message', 'Nomalum xato')}")
        return
    
    # Format and send verse
    formatted_verse = format_verse_message(verse_data.get('verse', {}))
    bot.reply_to(message, formatted_verse, parse_mode='Markdown')

@bot.message_handler(commands=['surah'])
def surah_command(message):
    """Handle the /surah command to retrieve verses from a surah"""
    command_parts = message.text.split()
    
    if len(command_parts) < 2:
        bot.reply_to(message, "Iltimos, surah raqamini kiriting. Masalan: /surah 1")
        return
    
    try:
        surah = int(command_parts[1])
        if surah < 1 or surah > 114:
            bot.reply_to(message, "Surah raqami 1 dan 114 gacha bo'lishi kerak.")
            return
    except ValueError:
        bot.reply_to(message, "Noto'g'ri format. Iltimos, surah raqamini kiriting (masalan, 1)")
        return
    
    # Get first 3 verses from the surah
    bot.reply_to(message, f"🔍 *Surah {surah}* dan dastlabki oyatlar...", parse_mode='Markdown')
    
    for ayah in range(1, 4):  # Get first 3 verses
        verse_data = quran_api.get_verse(surah, ayah)
        if not verse_data.get('success', False):
            if ayah == 1:  # If even the first verse fails
                bot.reply_to(message, f"Xato: {verse_data.get('message', 'Nomalum xato')}")
            break
        
        # Format and send verse
        formatted_verse = format_verse_message(verse_data.get('verse', {}))
        bot.send_message(message.chat.id, formatted_verse, parse_mode='Markdown')

@bot.message_handler(commands=['search'])
def search_command(message):
    """Handle the /search command to search for verses by keyword"""
    command_parts = message.text.split()
    
    if len(command_parts) < 2:
        bot.reply_to(message, "Iltimos, qidiruv so'zini kiriting. Masalan: /search rahmat")
        return
    
    query = ' '.join(command_parts[1:])
    
    # Indicate search is in progress
    progress_message = bot.reply_to(message, f"🔍 *{query}* so'zi bo'yicha qidirilmoqda...", parse_mode='Markdown')
    
    # Perform search
    search_results = quran_api.search_verses(query)
    if not search_results.get('success', False):
        bot.reply_to(message, f"Xato: {search_results.get('message', 'Nomalum xato')}")
        return
    
    # Format and send results
    results = search_results.get('results', [])
    if not results:
        bot.reply_to(message, f"*{query}* so'zi bo'yicha hech qanday natija topilmadi.", parse_mode='Markdown')
        return
    
    formatted_results = format_search_results(results)
    bot.reply_to(message, formatted_results, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def echo(message):
    """Handle all other messages as search queries"""
    query = message.text.strip()
    if not query:
        return
    
    # Indicate search is in progress
    progress_message = bot.reply_to(message, f"🔍 *{query}* so'zi bo'yicha qidirilmoqda...", parse_mode='Markdown')
    
    # Perform search
    search_results = quran_api.search_verses(query)
    if not search_results.get('success', False):
        bot.reply_to(message, f"Xato: {search_results.get('message', 'Nomalum xato')}")
        return
    
    # Format and send results
    results = search_results.get('results', [])
    if not results:
        bot.reply_to(message, f"*{query}* so'zi bo'yicha hech qanday natija topilmadi.", parse_mode='Markdown')
        return
    
    formatted_results = format_search_results(results)
    bot.reply_to(message, formatted_results, parse_mode='Markdown')

if __name__ == "__main__":
    logger.info("Starting Qur'on bot using PyTelegramBotAPI")
    try:
        # Start the bot
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Error running Telegram bot: {e}")
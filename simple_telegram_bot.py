import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from quran_api import QuranAPI
from utils import format_verse_message, format_search_results, parse_verse_command

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Quran API
quran_api = QuranAPI()

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}! 🌙\n\n"
        "Qurʼon botiga xush kelibsiz. Bu bot sizga Qurʼon oyatlarini o'qish, qidirish va ulashish imkonini beradi.\n\n"
        "Buyruqlar:\n"
        "/start - Botni qayta ishga tushirish\n"
        "/help - Yordam olish\n"
        "/verse [sura]:[oyat] - Muayyan oyatni olish (masalan, /verse 1:1)\n"
        "/surah [sura] - Suradan oyatlarni olish (masalan, /surah 1)\n"
        "/search [so'z] - Kalit so'z bo'yicha qidirish (masalan, /search rahmat)"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Qurʼon botidan foydalanish uchun quyidagi buyruqlardan foydalaning:\n\n"
        "/start - Botni qayta ishga tushirish\n"
        "/help - Yordam olish\n"
        "/verse [sura]:[oyat] - Muayyan oyatni olish (masalan, /verse 1:1)\n"
        "/surah [sura] - Suradan oyatlarni olish (masalan, /surah 1)\n"
        "/search [so'z] - Kalit so'z bo'yicha qidirish (masalan, /search rahmat)"
    )

async def verse_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /verse command to retrieve a specific verse."""
    if not context.args:
        await update.message.reply_text("Iltimos, surah va oyat raqamini kiriting. Masalan: /verse 1:1")
        return
    
    verse_ref = context.args[0]
    surah, ayah = parse_verse_command(verse_ref)
    
    if not surah or not ayah:
        await update.message.reply_text("Noto'g'ri format. Iltimos, surah:oyat shaklida kiriting (masalan, 1:1)")
        return
    
    # Get verse data
    verse_data = quran_api.get_verse(surah, ayah)
    if not verse_data.get('success', False):
        await update.message.reply_text(f"Xato: {verse_data.get('message', 'Nomalum xato')}")
        return
    
    # Format and send verse
    formatted_verse = format_verse_message(verse_data.get('verse', {}))
    await update.message.reply_text(formatted_verse, parse_mode='Markdown')

async def surah_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /surah command to retrieve verses from a surah."""
    if not context.args:
        await update.message.reply_text("Iltimos, surah raqamini kiriting. Masalan: /surah 1")
        return
    
    try:
        surah = int(context.args[0])
        if surah < 1 or surah > 114:
            await update.message.reply_text("Surah raqami 1 dan 114 gacha bo'lishi kerak.")
            return
    except ValueError:
        await update.message.reply_text("Noto'g'ri format. Iltimos, surah raqamini kiriting (masalan, 1)")
        return
    
    # Get first 3 verses from the surah
    await update.message.reply_text(f"🔍 *Surah {surah}* dan dastlabki oyatlar...", parse_mode='Markdown')
    
    for ayah in range(1, 4):  # Get first 3 verses
        verse_data = quran_api.get_verse(surah, ayah)
        if not verse_data.get('success', False):
            if ayah == 1:  # If even the first verse fails
                await update.message.reply_text(f"Xato: {verse_data.get('message', 'Nomalum xato')}")
            break
        
        # Format and send verse
        formatted_verse = format_verse_message(verse_data.get('verse', {}))
        await update.message.reply_text(formatted_verse, parse_mode='Markdown')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /search command to search for verses by keyword."""
    if not context.args:
        await update.message.reply_text("Iltimos, qidiruv so'zini kiriting. Masalan: /search rahmat")
        return
    
    query = ' '.join(context.args)
    
    # Indicate search is in progress
    progress_message = await update.message.reply_text(f"🔍 *{query}* so'zi bo'yicha qidirilmoqda...", parse_mode='Markdown')
    
    # Perform search
    search_results = quran_api.search_verses(query)
    if not search_results.get('success', False):
        await update.message.reply_text(f"Xato: {search_results.get('message', 'Nomalum xato')}")
        return
    
    # Format and send results
    results = search_results.get('results', [])
    if not results:
        await update.message.reply_text(f"*{query}* so'zi bo'yicha hech qanday natija topilmadi.", parse_mode='Markdown')
        return
    
    formatted_results = format_search_results(results)
    await update.message.reply_text(formatted_results, parse_mode='Markdown')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Treat text as a search query."""
    query = update.message.text.strip()
    if not query:
        return
    
    # Indicate search is in progress
    progress_message = await update.message.reply_text(f"🔍 *{query}* so'zi bo'yicha qidirilmoqda...", parse_mode='Markdown')
    
    # Perform search
    search_results = quran_api.search_verses(query)
    if not search_results.get('success', False):
        await update.message.reply_text(f"Xato: {search_results.get('message', 'Nomalum xato')}")
        return
    
    # Format and send results
    results = search_results.get('results', [])
    if not results:
        await update.message.reply_text(f"*{query}* so'zi bo'yicha hech qanday natija topilmadi.", parse_mode='Markdown')
        return
    
    formatted_results = format_search_results(results)
    await update.message.reply_text(formatted_results, parse_mode='Markdown')

async def main() -> None:
    """Start the bot."""
    # Get token from environment variable
    token = os.environ.get('TELEGRAM_TOKEN')
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable not set!")
        return
    
    # Create the Application and pass it your bot's token
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("verse", verse_command))
    application.add_handler(CommandHandler("surah", surah_command))
    application.add_handler(CommandHandler("search", search_command))
    
    # Add message handler for text messages that are not commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Start the Bot
    logger.info("Bot ishga tushdi! 🚀")
    await application.initialize()
    await application.start_polling()
    await application.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
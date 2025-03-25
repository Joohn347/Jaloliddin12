import telebot
import logging
from telebot import types
import os

from quran_service import QuranService
from utilities import (
    format_verse_message, format_search_results, format_help_message,
    format_start_message, parse_verse_reference, DEFAULT_RESULTS_LIMIT
)
from config import TELEGRAM_TOKEN

def initialize_bot():
    """Initialize and configure the Telegram bot"""
    if not TELEGRAM_TOKEN:
        raise ValueError("Telegram bot token is not set. Please set the TELEGRAM_TOKEN environment variable.")
    
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    
    # Start command handler
    @bot.message_handler(commands=['start'])
    def start_command(message):
        """Handle the /start command"""
        user_first_name = message.from_user.first_name
        welcome_message = format_start_message(user_first_name)
        bot.send_message(message.chat.id, welcome_message, parse_mode='Markdown')
    
    # Help command handler
    @bot.message_handler(commands=['help'])
    def help_command(message):
        """Handle the /help command"""
        help_message = format_help_message()
        bot.send_message(message.chat.id, help_message, parse_mode='Markdown')
    
    # Verse command handler
    @bot.message_handler(commands=['verse'])
    def verse_command(message):
        """Handle the /verse command to retrieve a specific verse"""
        try:
            # Extract parameters from message
            command_parts = message.text.split(maxsplit=1)
            if len(command_parts) != 2:
                bot.send_message(message.chat.id, 
                                "Please specify a verse in format: `/verse surah:ayah`\n"
                                "Example: `/verse 1:1`", 
                                parse_mode='Markdown')
                return
            
            verse_ref = command_parts[1].strip()
            surah_number, verse_number = parse_verse_reference(verse_ref)
            
            if not surah_number or not verse_number:
                bot.send_message(message.chat.id, 
                                "Invalid verse reference. Please use format: `surah:ayah`\n"
                                "Example: `1:1` for Al-Fatiha, verse 1", 
                                parse_mode='Markdown')
                return
            
            # Send typing action to show the bot is processing
            bot.send_chat_action(message.chat.id, 'typing')
            
            # Get verse data
            verse_data = QuranService.get_verse(surah_number, verse_number)
            if not verse_data:
                bot.send_message(message.chat.id, 
                                f"Sorry, couldn't find verse {surah_number}:{verse_number}. "
                                f"Please check if the surah and verse numbers are valid.")
                return
            
            # Format and send verse
            formatted_message = format_verse_message(verse_data)
            bot.send_message(message.chat.id, formatted_message, parse_mode='Markdown')
            
        except Exception as e:
            logging.error(f"Error in verse command: {e}")
            bot.send_message(message.chat.id, "An error occurred while retrieving the verse. Please try again later.")
    
    # Surah command handler
    @bot.message_handler(commands=['surah'])
    def surah_command(message):
        """Handle the /surah command to retrieve verses from a surah"""
        try:
            # Extract parameters from message
            command_parts = message.text.split()
            if len(command_parts) < 2:
                bot.send_message(message.chat.id, 
                                "Please specify a surah number: `/surah number [start_verse]`\n"
                                "Example: `/surah 1` or `/surah 2 255`", 
                                parse_mode='Markdown')
                return
            
            try:
                surah_number = int(command_parts[1])
                start_verse = int(command_parts[2]) if len(command_parts) > 2 else 1
            except ValueError:
                bot.send_message(message.chat.id, 
                                "Invalid surah or verse number. Please use numeric values.")
                return
            
            if not 1 <= surah_number <= 114:
                bot.send_message(message.chat.id, 
                                "Surah number must be between 1 and 114.")
                return
            
            # Send typing action
            bot.send_chat_action(message.chat.id, 'typing')
            
            # Get surah info
            surah_info = QuranService.get_surah_info(surah_number)
            if not surah_info:
                bot.send_message(message.chat.id, 
                                f"Sorry, couldn't find information for Surah {surah_number}.")
                return
            
            # Get verses
            verses = QuranService.get_surah_verses(surah_number, start_verse, 3)
            if not verses:
                bot.send_message(message.chat.id, 
                                f"Sorry, couldn't find verses for Surah {surah_number} starting from verse {start_verse}.")
                return
            
            # Send surah info
            surah_message = (
                f"🕌 *Surah {surah_info['englishName']} ({surah_info['name']})*\n"
                f"Number {surah_info['number']} • {surah_info['numberOfAyahs']} verses • "
                f"Revealed in {surah_info['revelationType']}\n\n"
            )
            bot.send_message(message.chat.id, surah_message, parse_mode='Markdown')
            
            # Send verses one by one
            for verse in verses:
                formatted_message = format_verse_message(verse)
                bot.send_message(message.chat.id, formatted_message, parse_mode='Markdown')
            
        except Exception as e:
            logging.error(f"Error in surah command: {e}")
            bot.send_message(message.chat.id, "An error occurred while retrieving the surah. Please try again later.")
    
    # Search command handler
    @bot.message_handler(commands=['search'])
    def search_command(message):
        """Handle the /search command to search for verses by keyword"""
        try:
            # Extract search query
            command_parts = message.text.split(maxsplit=1)
            if len(command_parts) != 2 or not command_parts[1].strip():
                bot.send_message(message.chat.id, 
                                "Please specify a search term: `/search keyword`\n"
                                "Example: `/search mercy`", 
                                parse_mode='Markdown')
                return
            
            search_query = command_parts[1].strip()
            
            # Send typing action
            bot.send_chat_action(message.chat.id, 'typing')
            
            # Inform user that search is in progress for better UX, especially for slower searches
            progress_message = bot.send_message(
                message.chat.id, 
                f"🔍 Searching for verses containing *{search_query}*...",
                parse_mode='Markdown'
            )
            
            # Perform search
            results = QuranService.search_verses(search_query, DEFAULT_RESULTS_LIMIT)
            
            # Delete the progress message
            bot.delete_message(message.chat.id, progress_message.message_id)
            
            # Format and send results
            formatted_results = format_search_results(results)
            bot.send_message(message.chat.id, formatted_results, parse_mode='Markdown')
            
        except Exception as e:
            logging.error(f"Error in search command: {e}")
            bot.send_message(message.chat.id, "An error occurred while searching. Please try again later.")
    
    # Handle unknown commands
    @bot.message_handler(func=lambda message: message.text.startswith('/'))
    def unknown_command(message):
        """Handle unknown commands"""
        bot.send_message(message.chat.id, 
                        "Sorry, I don't recognize that command. Type `/help` to see available commands.",
                        parse_mode='Markdown')
    
    # Handle regular messages
    @bot.message_handler(func=lambda message: True)
    def regular_message(message):
        """Handle regular text messages"""
        # Check if it's a verse reference (e.g. "1:1")
        surah_number, verse_number = parse_verse_reference(message.text)
        
        if surah_number and verse_number:
            # Send typing action
            bot.send_chat_action(message.chat.id, 'typing')
            
            # Get verse data
            verse_data = QuranService.get_verse(surah_number, verse_number)
            if verse_data:
                formatted_message = format_verse_message(verse_data)
                bot.send_message(message.chat.id, formatted_message, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, 
                                f"Sorry, couldn't find verse {surah_number}:{verse_number}. "
                                f"Please check if the surah and verse numbers are valid.")
        else:
            # Respond with a helpful message
            bot.send_message(message.chat.id, 
                           "If you're looking for a verse, use `/verse surah:ayah` format.\n"
                           "For search, use `/search keyword`.\n"
                           "Type `/help` to see all available commands.",
                           parse_mode='Markdown')
    
    logging.info("Bot initialized successfully")
    return bot

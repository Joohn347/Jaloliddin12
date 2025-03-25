def format_verse_message(verse_data):
    """
    Format verse data for Telegram message
    
    Args:
        verse_data (dict): Verse data from API
        
    Returns:
        str: Formatted message with verse text
    """
    if 'verse_key' not in verse_data:
        return "Error formatting verse data"
    
    # Get verse data
    verse_key = verse_data.get('verse_key', 'Unknown')
    surah_name = verse_data.get('surah_name', '')
    text_arabic = verse_data.get('text_arabic', '')
    text_translation = verse_data.get('text_translation', '')
    
    # Format message
    message = f"*Quran {verse_key}*"
    
    if surah_name:
        message += f" - Surah {surah_name}\n\n"
    else:
        message += "\n\n"
    
    # Add Arabic text
    message += f"{text_arabic}\n\n"
    
    # Add translation
    message += f"*Translation:*\n{text_translation}"
    
    return message

def format_search_results(results):
    """
    Format search results for Telegram message
    
    Args:
        results (list): List of verse results
        
    Returns:
        str: Formatted message with search results
    """
    if not results:
        return "No results found."
    
    message = "*Search Results:*\n\n"
    
    for i, verse in enumerate(results, 1):
        verse_key = verse.get('verse_key', 'Unknown')
        text_snippet = verse.get('text_translation', '')
        
        # Truncate long translations
        if len(text_snippet) > 100:
            text_snippet = text_snippet[:97] + "..."
        
        message += f"*{i}. Quran {verse_key}*\n"
        message += f"{text_snippet}\n\n"
        message += f"_View complete verse: /verse {verse_key}_\n\n"
    
    return message

def format_surah_info(surah_data):
    """
    Format surah information for Telegram message
    
    Args:
        surah_data (dict): Surah data from API
        
    Returns:
        str: Formatted message with surah information
    """
    # Get surah data
    surah_id = surah_data.get('id', 'Unknown')
    name_arabic = surah_data.get('name_arabic', '')
    name_simple = surah_data.get('name_simple', '')
    revelation_place = surah_data.get('revelation_place', '').capitalize()
    verses_count = surah_data.get('verses_count', 0)
    description = surah_data.get('description', 'No description available')
    
    # Format message
    message = f"*Surah {surah_id}: {name_simple}*\n"
    message += f"*{name_arabic}*\n\n"
    message += f"*Revealed in:* {revelation_place}\n"
    message += f"*Number of verses:* {verses_count}\n\n"
    message += f"*Description:*\n{description}\n\n"
    message += f"_Read first verse: /verse {surah_id}:1_"
    
    return message

def parse_verse_command(command_text):
    """
    Parse verse command to extract surah and ayah
    
    Args:
        command_text (str): Command text (e.g., "1:1", "2:255")
        
    Returns:
        tuple: (surah, ayah) or (None, None) if invalid
    """
    try:
        if ':' not in command_text:
            return None, None
            
        parts = command_text.strip().split(':')
        if len(parts) != 2:
            return None, None
            
        surah = int(parts[0])
        ayah = int(parts[1])
        
        if not (1 <= surah <= 114):
            return None, None
            
        return surah, ayah
    except ValueError:
        return None, None

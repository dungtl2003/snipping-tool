from googletrans import Translator

def translate(input_text: str, target_language: str) -> str:
    """
    Translate text into other language
    
    :param str input_text: The text to be translated
    :param str target_language: Target language
    :return: translated text in target language
    :rtype: str
    :raises TypeError: if the input_text is not a string
    :raises TypeError: if the target_language is not a string
    :raises ValueError: if target_language is not a supported language
    """
    language_map = {
        'English': 'en', 'Vietnamese': 'vi', 'Afrikaans': 'af', 'Albanian': 'sq',
        'Arabic': 'ar', 'Armenian': 'hy', 'Azerbaijani': 'az', 'Basque': 'eu',
        'Belarusian': 'be', 'Bengali': 'bn', 'Bosnian': 'bs', 'Bulgarian': 'bg',
        'Catalan': 'ca', 'Cebuano': 'ceb', 'Chinese': 'zh-CN', 'Corsican': 'co',
        'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl',
        'Esperanto': 'eo', 'Estonian': 'et', 'Finnish': 'fi', 'French': 'fr',
        'Galician': 'gl', 'Georgian': 'ka', 'German': 'de', 'Greek': 'el',
        'Gujarati': 'gu', 'Haitian Creole': 'ht', 'Hebrew': 'he', 'Hindi': 'hi',
        'Hungarian': 'hu', 'Icelandic': 'is', 'Igbo': 'ig', 'Indonesian': 'id',
        'Irish': 'ga', 'Italian': 'it', 'Japanese': 'ja', 'Korean': 'ko',
        'Latin': 'la', 'Latvian': 'lv', 'Lithuanian': 'lt', 'Malay': 'ms',
        'Malayalam': 'ml', 'Maltese': 'mt', 'Maori': 'mi', 'Mongolian': 'mn',
        'Nepali': 'ne', 'Norwegian': 'no', 'Persian': 'fa', 'Polish': 'pl',
        'Portuguese': 'pt', 'Punjabi': 'pa', 'Romanian': 'ro', 'Russian': 'ru',
        'Serbian': 'sr', 'Sinhala': 'si', 'Slovak': 'sk', 'Slovenian': 'sl',
        'Somali': 'so', 'Spanish': 'es', 'Swahili': 'sw', 'Swedish': 'sv',
        'Tamil': 'ta', 'Telugu': 'te', 'Thai': 'th', 'Turkish': 'tr',
        'Ukrainian': 'uk', 'Urdu': 'ur', 'Uzbek': 'uz', 'Welsh': 'cy',
        'Yiddish': 'yi', 'Yoruba': 'yo', 'Zulu': 'zu'
    }
    
    # Check if target_language is supported
    if target_language not in language_map:
        raise ValueError(f"Target language '{target_language}' is not supported.")

    # Get the target language code from the language map
    to_lang = language_map.get(target_language, 'en')  # Default to English if not found

    # Initialize the translator and perform translation
    translator = Translator()
    translated_text = translator.translate(input_text, dest=to_lang)
    
    return translated_text.text.strip()

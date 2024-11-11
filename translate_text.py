from googletrans import Translator

def translate(input_text: str, target_language: str) -> str:
    """
    Args:
      input_text: Language to be translated
      target_language: Target language

    Returns:
      Translated text
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

    to_lang = language_map.get(target_language, 'en')  # Default to English if not found
    translator = Translator()
    translated_text = translator.translate(input_text, dest=to_lang)
    return translated_text.text.strip()

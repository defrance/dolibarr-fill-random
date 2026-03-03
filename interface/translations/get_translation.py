from . import TRANSLATIONS

def get_translation(key: str, lang: str = "fr_FR") -> str:

    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][key]
    # Fallback sur fr_FR si la langue demandée n'existe pas
    if "fr_FR" in TRANSLATIONS and key in TRANSLATIONS["fr_FR"]:
        return TRANSLATIONS["fr_FR"][key]
    return key
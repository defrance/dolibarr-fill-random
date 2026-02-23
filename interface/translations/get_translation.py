from . import TRANSLATIONS

def get_translation(key, lang="fr_FR"):
    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][key]
    return key
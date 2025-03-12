import gettext as gt
import pathlib

_default_lang = None
_translation = None
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGE = ["pt", "en"]


pathlib.Path(__file__).parent.resolve()

_path = (pathlib.Path(__file__).parent.parent / "i18n" / "locales").resolve()

def active_translation(lang: str):
    global _default_lang
    global _translation
    
    _default_lang = DEFAULT_LANGUAGE if lang not in SUPPORTED_LANGUAGE else lang
    _translation = gt.translation("messages", localedir=_path, languages=[_default_lang])


def gettext(message: str) -> str:
    return _translation.gettext(message)

import json
import os

_current_lang = {}
_fallback_lang = {}
_lang_code = "en"

def set_language(lang_code="en"):
    global _current_lang, _fallback_lang, _lang_code
    _lang_code = lang_code

    base_path = os.path.join(os.path.dirname(__file__), "lang")
    try:
        with open(os.path.join(base_path, f"{lang_code}.json"), "r", encoding="utf-8") as f:
            _current_lang = json.load(f)
    except FileNotFoundError:
        _current_lang = {}

    # Load fallback (English)
    try:
        with open(os.path.join(base_path, "en.json"), "r", encoding="utf-8") as f:
            _fallback_lang = json.load(f)
    except FileNotFoundError:
        _fallback_lang = {}

def lang(key):
    return _current_lang.get(key) or _fallback_lang.get(key, key)
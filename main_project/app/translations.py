import json
import os
from PyQt6.QtCore import QObject, pyqtSignal
from app.helper import resource_path


class TranslationManager(QObject):
    languageChanged = pyqtSignal(str)

    def __init__(self, translations_dir=None):
        super().__init__()
        if translations_dir is None:
            translations_dir = resource_path("translations")
        self.translations_dir = translations_dir
        self._data = {}
        self._lang = 'en'
        self.load_all()

    def load_all(self):
        self._data = {}
        if not os.path.isdir(self.translations_dir):
            return
        for fname in os.listdir(self.translations_dir):
            if fname.endswith('.json'):
                lang = fname[:-5]
                try:
                    with open(os.path.join(self.translations_dir, fname), 'r', encoding='utf-8') as f:
                        self._data[lang] = json.load(f)
                except Exception:
                    self._data[lang] = {}

    def available_languages(self):
        return list(self._data.keys())

    def set_language(self, lang):
        if lang == self._lang:
            return
        if lang not in self._data:
            return
        self._lang = lang
        self.languageChanged.emit(lang)

    def language(self):
        return self._lang

    def t(self, key):
        parts = key.split('.')
        node = self._data.get(self._lang, {})
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return key
        if isinstance(node, str):
            return node
        return key


# singleton instance
_manager = None


def get_translator():
    global _manager
    if _manager is None:
        _manager = TranslationManager()
    return _manager

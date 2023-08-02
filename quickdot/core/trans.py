import json
import logging
from pathlib import Path

import polib


class TranslationManager:
    """Manages the translations for the website."""
    
    def __init__(self, config):
        self.config = config
        self.locale = {}
        self.logger = logging.getLogger(__name__)
        self._load_locale()
        
    def gather_texts(self):
        """Gathers texts from string_table.json files and saves to .po files."""
        self.logger.info("Gathering texts...")
        collected_data = self._gather_texts_from_files()
        self._save_texts_to_po_files(collected_data)
        self.logger.info("Finished gathering texts.")

    def _gather_texts_from_files(self):
        """Gathers texts from string_table.json files."""
        collected_data = {}
        files = self.config.ROOT_PATH.rglob('string_table.json')

        for file in files:
            with open(file, 'r+', encoding='utf-8') as f:
                try:
                    self.logger.info(f"Gathering texts from {file}...")
                    data = json.load(f)
                    for item in data:
                        key = item['KEY']
                        if key not in collected_data:
                            collected_data[key] = item['VALUE']
                        else:
                            raise ValueError(f"Duplicate key {key} found in {file}.")
                except Exception as e:
                    self.logger.error(f"Failed to gather texts from {file}: {str(e)}")
        return collected_data

    def _save_texts_to_po_files(self, collected_data):
        """Saves the gathered texts to .po files."""
        self.config.site_translation_path.mkdir(parents=True, exist_ok=True)

        for lang in self.config.site_languages:
            path = self.config.site_translation_path / f'texts_{lang}.po'
            str_path = str(path).replace('\\', '/')
            po = polib.pofile(str_path) if path.exists() else polib.POFile()

            for id, text in collected_data.items():
                if po.find(id) is None:
                    entry = polib.POEntry(msgid=id, msgstr=text)
                    po.append(entry)
            try:
                po.save(str_path)
            except Exception as e:
                raise IOError(f"Failed to save {path}: {str(e)}")

    def _load_locale(self):
        """Loads the locale data from .po files."""
        for lang in self.config.site_languages:
            path = self.config.site_translation_path / f'texts_{lang}.po'

            if path.exists() is False:
                self.locale[lang] = {}
                continue

            str_path = str(path).replace('\\', '/')
            try:
                po = polib.pofile(str_path)
                self.locale[lang] = {entry.msgid: entry.msgstr for entry in po}
            except Exception as e:
                raise IOError(f"Failed to load {path}: {str(e)}")
    
    def get_text(self, key, lang):
        """Returns the text for the given key and language."""
        return self.locale[lang].get(key, key)

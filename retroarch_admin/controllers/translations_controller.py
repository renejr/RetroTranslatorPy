# controllers/translations_controller.py
from kivymd.app import MDApp
from models.translation import Translation

class TranslationsController:
    """Controlador para gerenciar as traduções."""
    
    def __init__(self):
        self.app = MDApp.get_running_app()
    
    def get_translations(self, offset=0, limit=10, search_text=None, source_lang=None, target_lang=None):
        """Obtém traduções paginadas e filtradas."""
        data, total_count = self.app.db_manager.get_translations_data(
            offset=offset,
            limit=limit,
            search_text=search_text,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        # Converter linhas do banco de dados em objetos Translation
        translations = [Translation.from_db_row(row) for row in data]
        
        return translations, total_count
    
    def get_translation_by_id(self, translation_id):
        """Obtém uma tradução pelo ID."""
        row = self.app.db_manager.get_translation_by_id(translation_id)
        return Translation.from_db_row(row)
    
    def get_languages(self):
        """Obtém a lista de idiomas disponíveis."""
        return self.app.db_manager.get_languages()
    
    def get_translators(self):
        """Obtém a lista de tradutores disponíveis."""
        return self.app.db_manager.get_translators()
# controllers/ocr_results_controller.py
from kivymd.app import MDApp
from models.ocr_result import OCRResult

class OCRResultsController:
    """Controlador para gerenciar os resultados de OCR."""
    
    def __init__(self):
        self.app = MDApp.get_running_app()
    
    def get_ocr_results(self, offset=0, limit=10, search_text=None, lang=None):
        """Obtém resultados de OCR paginados e filtrados."""
        data, total_count = self.app.db_manager.get_ocr_results_data(
            offset=offset,
            limit=limit,
            search_text=search_text,
            lang=lang
        )
        
        # Converter linhas do banco de dados em objetos OCRResult
        ocr_results = [OCRResult.from_db_row(row) for row in data]
        
        return ocr_results, total_count
    
    def get_ocr_result_by_id(self, ocr_result_id):
        """Obtém um resultado de OCR pelo ID."""
        row = self.app.db_manager.get_ocr_result_by_id(ocr_result_id)
        return OCRResult.from_db_row(row)
    
    def get_languages(self):
        """Obtém a lista de idiomas disponíveis."""
        return self.app.db_manager.get_languages()
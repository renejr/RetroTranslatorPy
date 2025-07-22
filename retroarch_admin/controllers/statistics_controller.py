# controllers/statistics_controller.py
from kivymd.app import MDApp
from models.statistic import Statistic

class StatisticsController:
    """Controlador para gerenciar as estatísticas."""
    
    def __init__(self):
        self.app = MDApp.get_running_app()
    
    def get_daily_statistics(self, days=30):
        """Obtém estatísticas diárias dos últimos N dias."""
        data = self.app.db_manager.get_daily_statistics(days)
        
        # Converter linhas do banco de dados em objetos Statistic
        statistics = []
        for row in data:
            stat = {
                'date': row[0],
                'total_requests': row[1],
                'ocr_cache_hits': row[2],
                'translation_cache_hits': row[3],
                'avg_processing_time': row[4]
            }
            statistics.append(stat)
        
        return statistics
    
    def get_general_statistics(self):
        """Obtém estatísticas gerais do sistema."""
        return self.app.db_manager.get_general_statistics()
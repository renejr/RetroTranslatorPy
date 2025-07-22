# models/statistic.py

class Statistic:
    """Modelo para representar uma estatística diária no banco de dados."""
    
    def __init__(self, id=None, date=None, total_requests=0, ocr_cache_hits=0, 
                 translation_cache_hits=0, avg_processing_time=0):
        self.id = id
        self.date = date
        self.total_requests = total_requests
        self.ocr_cache_hits = ocr_cache_hits
        self.translation_cache_hits = translation_cache_hits
        self.avg_processing_time = avg_processing_time
    
    @classmethod
    def from_db_row(cls, row):
        """Cria uma instância de Statistic a partir de uma linha do banco de dados."""
        if not row:
            return None
        
        return cls(
            id=row[0],
            date=row[1],
            total_requests=row[2],
            ocr_cache_hits=row[3],
            translation_cache_hits=row[4],
            avg_processing_time=row[5]
        )
    
    def to_dict(self):
        """Converte a instância em um dicionário."""
        return {
            'id': self.id,
            'date': self.date,
            'total_requests': self.total_requests,
            'ocr_cache_hits': self.ocr_cache_hits,
            'translation_cache_hits': self.translation_cache_hits,
            'avg_processing_time': self.avg_processing_time
        }
    
    @property
    def ocr_cache_hit_rate(self):
        """Retorna a taxa de acertos de cache de OCR."""
        if self.total_requests > 0:
            return (self.ocr_cache_hits / self.total_requests) * 100
        return 0
    
    @property
    def translation_cache_hit_rate(self):
        """Retorna a taxa de acertos de cache de tradução."""
        if self.total_requests > 0:
            return (self.translation_cache_hits / self.total_requests) * 100
        return 0
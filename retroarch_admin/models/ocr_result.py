# models/ocr_result.py
import json
import base64

class OCRResult:
    """Modelo para representar um resultado de OCR no banco de dados."""
    
    def __init__(self, id=None, text_results=None, lang=None, image_base64=None, 
                 created_at=None, last_used=None, use_count=None, image_hash=None):
        self.id = id
        self.text_results = text_results  # JSON ou dicionário
        self.lang = lang
        self.image_base64 = image_base64
        self.created_at = created_at
        self.last_used = last_used
        self.use_count = use_count
        self.image_hash = image_hash
    
    @classmethod
    def from_db_row(cls, row):
        """Cria uma instância de OCRResult a partir de uma linha do banco de dados."""
        if not row:
            return None
        
        # Converter text_results de JSON para dicionário
        text_results = json.loads(row[1]) if row[1] else {}
        
        return cls(
            id=row[0],
            text_results=text_results,
            lang=row[2],
            image_base64=row[3],
            created_at=row[4],
            last_used=row[5],
            use_count=row[6],
            image_hash=row[7]
        )
    
    def to_dict(self):
        """Converte a instância em um dicionário."""
        return {
            'id': self.id,
            'text_results': self.text_results,
            'lang': self.lang,
            'image_base64': self.image_base64,
            'created_at': self.created_at,
            'last_used': self.last_used,
            'use_count': self.use_count,
            'image_hash': self.image_hash
        }
    
    @property
    def text(self):
        """Retorna o texto detectado."""
        if isinstance(self.text_results, str):
            try:
                text_results = json.loads(self.text_results)
                return text_results.get('text', '')
            except json.JSONDecodeError:
                return ''
        elif isinstance(self.text_results, dict):
            return self.text_results.get('text', '')
        return ''
    
    @property
    def confidence(self):
        """Retorna a confiança média da detecção."""
        if isinstance(self.text_results, str):
            try:
                text_results = json.loads(self.text_results)
                return text_results.get('confidence', 0)
            except json.JSONDecodeError:
                return 0
        elif isinstance(self.text_results, dict):
            return self.text_results.get('confidence', 0)
        return 0
    
    @property
    def metadata(self):
        """Retorna os metadados da detecção."""
        if isinstance(self.text_results, str):
            try:
                text_results = json.loads(self.text_results)
                return text_results.get('metadata', {})
            except json.JSONDecodeError:
                return {}
        elif isinstance(self.text_results, dict):
            return self.text_results.get('metadata', {})
        return {}
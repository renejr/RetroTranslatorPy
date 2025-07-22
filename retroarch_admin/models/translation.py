# models/translation.py

class Translation:
    """Modelo para representar uma tradução no banco de dados."""
    
    def __init__(self, id=None, source_text=None, translated_text=None, 
                 source_lang=None, target_lang=None, translator=None, 
                 confidence=None, created_at=None, last_used=None, 
                 use_count=None, source_text_hash=None):
        self.id = id
        self.source_text = source_text
        self.translated_text = translated_text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.translator = translator
        self.confidence = confidence
        self.created_at = created_at
        self.last_used = last_used
        self.use_count = use_count
        self.source_text_hash = source_text_hash
    
    @classmethod
    def from_db_row(cls, row):
        """Cria uma instância de Translation a partir de uma linha do banco de dados."""
        if not row:
            return None
        
        return cls(
            id=row[0],
            source_text=row[1],
            translated_text=row[2],
            source_lang=row[3],
            target_lang=row[4],
            translator=row[5],
            confidence=row[6],
            created_at=row[7],
            last_used=row[8],
            use_count=row[9],
            source_text_hash=row[10]
        )
    
    def to_dict(self):
        """Converte a instância em um dicionário."""
        return {
            'id': self.id,
            'source_text': self.source_text,
            'translated_text': self.translated_text,
            'source_lang': self.source_lang,
            'target_lang': self.target_lang,
            'translator': self.translator,
            'confidence': self.confidence,
            'created_at': self.created_at,
            'last_used': self.last_used,
            'use_count': self.use_count,
            'source_text_hash': self.source_text_hash
        }
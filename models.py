from pydantic import BaseModel
from typing import Optional, List

class RetroArchRequest(BaseModel):
    image: str
    format: Optional[str] = 'png'
    lang_source: Optional[str] = 'en'
    lang_target: Optional[str] = 'pt'
    coords: Optional[List[int]] = None
    viewport: Optional[List[int]] = None
    label: Optional[str] = None
    state: Optional[str] = None  # Campo adicional que o RetroArch envia
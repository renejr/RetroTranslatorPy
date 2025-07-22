import asyncio
import base64
import cv2
import numpy as np
from PIL import Image
import io
import os

# Importa as funções dos módulos que queremos testar
from ocr_module import extract_text_with_positions
from service_logic import create_positioned_translation_image, process_ai_request
from translation_module import translate_text
from models import RetroArchRequest

async def test_fragmented_image():
    """Testa o processo completo com a imagem fragmentada"""
    print("\n=== Testando processo completo com imagem fragmentada ===\n")
    
    # Carrega a imagem
    image_path = 'test_fragmented_text.png'
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    # Converte para base64 para simular requisição do RetroArch
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Cria uma requisição simulada
    request = RetroArchRequest(
        image=image_base64,
        lang_source='en',
        lang_target='pt',
        format='png'
    )
    
    # Processa a requisição
    print("1. Processando requisição completa...")
    result = await process_ai_request(request)
    
    # Salva a imagem resultante
    if result and 'image' in result:
        output_image_bytes = base64.b64decode(result['image'])
        with open('test_fragmented_result.png', 'wb') as f:
            f.write(output_image_bytes)
        print(f"Imagem de resultado salva em: test_fragmented_result.png")
    else:
        print("Erro: Nenhuma imagem retornada no resultado")

# Executa o teste
asyncio.run(test_fragmented_image())
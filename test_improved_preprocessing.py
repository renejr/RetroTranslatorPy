# test_improved_preprocessing.py

import asyncio
import base64
import cv2
import numpy as np
from PIL import Image
import io
import os
import time

# Importa as funções dos módulos que queremos testar
from ocr_module import extract_text_with_positions
from service_logic import create_positioned_translation_image, process_ai_request
from translation_module import translate_text
from models import RetroArchRequest

async def test_improved_preprocessing(image_path, source_lang='en', target_lang='pt'):
    """
    Testa o pré-processamento de imagem melhorado.
    
    Args:
        image_path: Caminho para a imagem de teste
        source_lang: Idioma de origem para OCR
        target_lang: Idioma de destino para tradução
    """
    print(f"\n=== Testando pré-processamento melhorado com a imagem: {image_path} ===\n")
    
    # Carrega a imagem
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    # Converte para base64 para simular requisição do RetroArch
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Cria uma requisição simulada
    request = RetroArchRequest(
        image=image_base64,
        lang_source=source_lang,
        lang_target=target_lang
    )
    
    # Processa a requisição
    print("1. Processando requisição completa...")
    start_time = time.time()
    result = await process_ai_request(request)
    end_time = time.time()
    
    print(f"Tempo de processamento: {end_time - start_time:.2f} segundos")
    
    # Salva a imagem resultante
    if result and 'image' in result:
        output_image_bytes = base64.b64decode(result['image'])
        output_filename = f"improved_result_{os.path.basename(image_path)}"
        with open(output_filename, 'wb') as f:
            f.write(output_image_bytes)
        print(f"Imagem resultante salva como: {output_filename}")
    
    # Teste apenas do OCR com pré-processamento melhorado
    print("\n2. Testando apenas o OCR com pré-processamento melhorado...")
    start_time = time.time()
    detections = await extract_text_with_positions(image_bytes, source_lang)
    end_time = time.time()
    
    print(f"Tempo de OCR: {end_time - start_time:.2f} segundos")
    print(f"\nTotal de detecções após pré-processamento: {len(detections)}")
    for i, detection in enumerate(detections):
        is_grouped = detection.get('is_grouped', False)
        group_size = detection.get('group_size', 1)
        group_info = f" (grupo de {group_size} textos)" if is_grouped else ""
        print(f"Detecção {i+1}{group_info}: '{detection['text']}' (confiança: {detection['confidence']:.2f})")

async def main():
    # Verifica se existem imagens de teste
    test_images = []
    for file in os.listdir('.'):
        if file.endswith(('.png', '.jpg', '.jpeg')) and file.startswith('test_'):
            test_images.append(file)
    
    if not test_images:
        print("Nenhuma imagem de teste encontrada. Por favor, adicione imagens com prefixo 'test_' no diretório atual.")
        return
    
    # Testa com cada imagem encontrada
    for image_path in test_images:
        await test_improved_preprocessing(image_path)

if __name__ == "__main__":
    asyncio.run(main())
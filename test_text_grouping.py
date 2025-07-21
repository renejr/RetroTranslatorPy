# test_text_grouping.py

import asyncio
import base64
import cv2
import numpy as np
from PIL import Image
import io
import os

# Importa as funções dos módulos que queremos testar
from ocr_module import extract_text_with_positions, group_text_detections
from service_logic import create_positioned_translation_image, process_ai_request
from translation_module import translate_text
from models import RetroArchRequest

async def test_text_grouping_with_image(image_path, source_lang='en', target_lang='pt'):
    """
    Testa o agrupamento de texto com uma imagem real.
    
    Args:
        image_path: Caminho para a imagem de teste
        source_lang: Idioma de origem para OCR
        target_lang: Idioma de destino para tradução
    """
    print(f"\n=== Testando agrupamento de texto com a imagem: {image_path} ===")
    
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
    print("\n1. Processando requisição completa...")
    result = await process_ai_request(request)
    
    # Salva a imagem resultante
    if result and 'image' in result:
        output_image_bytes = base64.b64decode(result['image'])
        with open('test_grouped_result.png', 'wb') as f:
            f.write(output_image_bytes)
        print(f"Imagem resultante salva como: test_grouped_result.png")
    
    # Teste apenas do OCR com agrupamento
    print("\n2. Testando apenas o OCR com agrupamento...")
    detections = await extract_text_with_positions(image_bytes, source_lang)
    
    print(f"\nTotal de detecções após agrupamento: {len(detections)}")
    for i, detection in enumerate(detections):
        is_grouped = detection.get('is_grouped', False)
        group_size = detection.get('group_size', 1)
        group_info = f" (grupo de {group_size} textos)" if is_grouped else ""
        print(f"Detecção {i+1}{group_info}: '{detection['text']}' (confiança: {detection['confidence']:.2f})")
    
    # Teste manual do agrupamento
    print("\n3. Testando manualmente a função de agrupamento...")
    # Cria algumas detecções de teste para simular texto fragmentado
    test_detections = [
        {'text': 'Hello', 'bbox': [[10, 10], [50, 10], [50, 30], [10, 30]], 'confidence': 0.9},
        {'text': 'World', 'bbox': [[60, 10], [100, 10], [100, 30], [60, 30]], 'confidence': 0.8},
        {'text': 'This is', 'bbox': [[10, 50], [50, 50], [50, 70], [10, 70]], 'confidence': 0.7},
        {'text': 'a test', 'bbox': [[60, 50], [100, 50], [100, 70], [60, 70]], 'confidence': 0.6},
        {'text': 'of grouping', 'bbox': [[110, 50], [180, 50], [180, 70], [110, 70]], 'confidence': 0.5},
    ]
    
    # Aplica o agrupamento
    grouped = group_text_detections(test_detections)
    
    print(f"\nDetecções originais: {len(test_detections)}")
    print(f"Detecções após agrupamento: {len(grouped)}")
    
    for i, detection in enumerate(grouped):
        is_grouped = detection.get('is_grouped', False)
        group_size = detection.get('group_size', 1)
        group_info = f" (grupo de {group_size} textos)" if is_grouped else ""
        print(f"Grupo {i+1}{group_info}: '{detection['text']}' (confiança: {detection['confidence']:.2f})")

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
        await test_text_grouping_with_image(image_path)

if __name__ == "__main__":
    asyncio.run(main())
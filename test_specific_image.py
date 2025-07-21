import asyncio
import base64
import os
import sys
from PIL import Image
import io

# Adiciona o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from improved_ocr_module import extract_text_with_positions
from translation_module import translate_text
from service_logic import create_positioned_translation_image

async def test_specific_image():
    # Caminho para a imagem de teste
    image_path = "test_image.png"  # Substitua pelo caminho da sua imagem
    
    # Verifica se a imagem existe
    if not os.path.exists(image_path):
        print(f"Imagem não encontrada: {image_path}")
        return
    
    # Carrega a imagem
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    # Extrai texto com posições
    detections = await extract_text_with_positions(image_data, 'en')
    
    print("\nTextos detectados:")
    for i, detection in enumerate(detections):
        print(f"Detecção {i+1}: '{detection['text']}' (Confiança: {detection['confidence']:.2f})")
        print(f"  Posição: {detection['bbox']}")
        if 'is_grouped' in detection and detection['is_grouped']:
            print(f"  Agrupado: Sim (Tamanho do grupo: {detection.get('group_size', 'N/A')})")
        else:
            print(f"  Agrupado: Não")
    
    # Traduz cada texto detectado
    detections_with_translations = []
    for detection in detections:
        translated = await translate_text(detection['text'], 'pt', 'en')
        print(f"Original: '{detection['text']}' -> Traduzido: '{translated}'")
        detections_with_translations.append({
            'text': detection['text'],
            'translation': translated,
            'bbox': detection['bbox'],
            'confidence': detection['confidence'],
            'is_grouped': detection.get('is_grouped', False),
            'group_size': detection.get('group_size', 1)
        })
        print(f"\nOriginal: '{detection['text']}' -> Traduzido: '{translated}'")
    
    # Cria imagem com traduções posicionadas
    with Image.open(io.BytesIO(image_data)) as img:
        width, height = img.size
    
    overlay_image_base64 = create_positioned_translation_image(detections_with_translations, width, height)
    
    # Converte base64 para imagem
    overlay_image_bytes = base64.b64decode(overlay_image_base64)
    overlay_image = Image.open(io.BytesIO(overlay_image_bytes))
    
    # Salva a imagem de overlay
    overlay_path = "test_overlay.png"
    overlay_image.save(overlay_path)
    print(f"\nImagem de overlay salva em: {overlay_path}")
    
    # Combina as imagens para visualização
    with Image.open(io.BytesIO(image_data)) as original_img:
        combined = Image.new('RGBA', (width, height * 2), (0, 0, 0, 0))
        combined.paste(original_img, (0, 0))
        combined.paste(overlay_image, (0, height), mask=overlay_image)
    
    # Salva a imagem combinada
    combined_path = "test_combined.png"
    combined.save(combined_path)
    print(f"Imagem combinada salva em: {combined_path}")

if __name__ == "__main__":
    asyncio.run(test_specific_image())
import ocr_module
import cv2
import base64
import numpy as np
import asyncio

async def main():
    print('Testando agrupamento com imagem fragmentada...')

    # Carrega a imagem de teste
    img = cv2.imread('test_fragmented_text.png')
    _, img_bytes = cv2.imencode('.png', img)
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    img_bytes = base64.b64decode(img_base64)

    # Executa o OCR com agrupamento
    detections = await ocr_module.extract_text_with_positions(img_bytes, 'en')

    # Exibe as detecções originais
    print(f'\nDetecções originais: {len(detections)}')
    for i, d in enumerate(detections):
        is_grouped = d.get('is_grouped', False)
        group_size = d.get('group_size', 1)
        group_info = f" (grupo de {group_size} textos)" if is_grouped else ""
        print(f'Detecção {i+1}{group_info}: "{d["text"]}" (confiança: {d["confidence"]:.2f})')

# Executa a função assíncrona
asyncio.run(main())
# test_ocr_comparison.py

import asyncio
import base64
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import os
import time
import matplotlib.pyplot as plt

# Importa as funções dos módulos que queremos testar
import ocr_module
import improved_ocr_module
from models import RetroArchRequest

def create_test_image(filename="test_ocr_comparison.png", width=800, height=600):
    """
    Cria uma imagem de teste com diferentes desafios para OCR.
    """
    # Cria uma imagem com fundo preto
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img.fill(0)  # Fundo preto
    
    # Converte para PIL para usar fontes
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)
    
    try:
        # Tenta usar uma fonte do sistema
        font_regular = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 16)
        font_large = ImageFont.truetype("arial.ttf", 32)
        font_bold = ImageFont.truetype("arialbd.ttf", 24) if os.path.exists("arialbd.ttf") else font_regular
    except:
        # Fallback para fonte padrão
        font_regular = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_bold = ImageFont.load_default()
    
    # Adiciona texto com baixo contraste
    draw.text((100, 50), "Texto com baixo contraste", fill=(50, 50, 50), font=font_regular)
    
    # Adiciona texto com ruído
    draw.text((100, 100), "Texto com ruído", fill=(255, 255, 255), font=font_regular)
    # Adiciona ruído ao redor do texto
    for _ in range(500):
        x = np.random.randint(100, 300)
        y = np.random.randint(90, 130)
        draw.point((x, y), fill=(np.random.randint(100, 255), np.random.randint(100, 255), np.random.randint(100, 255)))
    
    # Adiciona texto inclinado
    pil_img_np = np.array(pil_img)
    h, w = pil_img_np.shape[:2]
    center = (w // 2, h // 2)
    angle = 15
    scale = 1.0
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)
    rotated_img = cv2.warpAffine(pil_img_np, rotation_matrix, (w, h))
    pil_img = Image.fromarray(rotated_img)
    draw = ImageDraw.Draw(pil_img)
    
    # Adiciona texto com fonte pequena
    draw.text((100, 150), "Texto com fonte pequena e difícil de ler", fill=(255, 255, 255), font=font_small)
    
    # Adiciona texto com fonte grande
    draw.text((100, 200), "TEXTO GRANDE", fill=(255, 255, 255), font=font_large)
    
    # Adiciona texto com fundo complexo
    for i in range(300, 350):
        for j in range(250, 300):
            pil_img_np = np.array(pil_img)
            pil_img_np[j, i] = [np.random.randint(100, 200), np.random.randint(100, 200), np.random.randint(100, 200)]
    pil_img = Image.fromarray(pil_img_np)
    draw = ImageDraw.Draw(pil_img)
    draw.text((300, 250), "Texto com fundo complexo", fill=(255, 255, 255), font=font_regular)
    
    # Adiciona texto com sombra
    draw.text((103, 303), "Texto com sombra", fill=(50, 50, 50), font=font_regular)
    draw.text((100, 300), "Texto com sombra", fill=(255, 255, 255), font=font_regular)
    
    # Adiciona texto com caracteres especiais
    draw.text((100, 350), "Texto com caracteres especiais: @#$%&*()!", fill=(255, 255, 255), font=font_regular)
    
    # Adiciona texto com espaçamento irregular
    draw.text((100, 400), "Texto  com    espaçamento   irregular", fill=(255, 255, 255), font=font_regular)
    
    # Adiciona texto em negrito
    draw.text((100, 450), "Texto em negrito", fill=(255, 255, 255), font=font_bold)
    
    # Adiciona texto com diferentes cores
    draw.text((100, 500), "Texto", fill=(255, 0, 0), font=font_regular)
    draw.text((170, 500), "com", fill=(0, 255, 0), font=font_regular)
    draw.text((220, 500), "cores", fill=(0, 0, 255), font=font_regular)
    draw.text((290, 500), "diferentes", fill=(255, 255, 0), font=font_regular)
    
    # Converte de volta para OpenCV
    img = np.array(pil_img)
    
    # Aplica um leve desfoque para simular uma captura de tela de baixa qualidade
    img = cv2.GaussianBlur(img, (3, 3), 0)
    
    # Salva a imagem
    cv2.imwrite(filename, img)
    print(f"Imagem de teste criada: {os.path.abspath(filename)}")
    return os.path.abspath(filename)

async def compare_ocr_modules(image_path, source_lang='en'):
    """
    Compara o desempenho do módulo OCR original com o módulo OCR melhorado.
    
    Args:
        image_path: Caminho para a imagem de teste
        source_lang: Idioma de origem para OCR
    """
    print(f"\n=== Comparando módulos OCR com a imagem: {image_path} ===\n")
    
    # Carrega a imagem
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    # Teste com o módulo OCR original
    print("\n1. Testando módulo OCR original...")
    start_time = time.time()
    original_detections = await ocr_module.extract_text_with_positions(image_bytes, source_lang)
    original_time = time.time() - start_time
    
    print(f"Tempo de processamento (original): {original_time:.2f} segundos")
    print(f"Total de detecções (original): {len(original_detections)}")
    
    original_texts = []
    for i, detection in enumerate(original_detections):
        is_grouped = detection.get('is_grouped', False)
        group_size = detection.get('group_size', 1)
        group_info = f" (grupo de {group_size} textos)" if is_grouped else ""
        text = detection['text']
        confidence = detection['confidence']
        print(f"Original {i+1}{group_info}: '{text}' (confiança: {confidence:.2f})")
        original_texts.append(text)
    
    # Teste com o módulo OCR melhorado
    print("\n2. Testando módulo OCR melhorado...")
    start_time = time.time()
    improved_detections = await improved_ocr_module.extract_text_with_positions(image_bytes, source_lang)
    improved_time = time.time() - start_time
    
    print(f"Tempo de processamento (melhorado): {improved_time:.2f} segundos")
    print(f"Total de detecções (melhorado): {len(improved_detections)}")
    
    improved_texts = []
    for i, detection in enumerate(improved_detections):
        is_grouped = detection.get('is_grouped', False)
        group_size = detection.get('group_size', 1)
        group_info = f" (grupo de {group_size} textos)" if is_grouped else ""
        text = detection['text']
        confidence = detection['confidence']
        print(f"Melhorado {i+1}{group_info}: '{text}' (confiança: {confidence:.2f})")
        improved_texts.append(text)
    
    # Calcula estatísticas de comparação
    original_char_count = sum(len(text) for text in original_texts)
    improved_char_count = sum(len(text) for text in improved_texts)
    
    original_avg_confidence = sum(d['confidence'] for d in original_detections) / len(original_detections) if original_detections else 0
    improved_avg_confidence = sum(d['confidence'] for d in improved_detections) / len(improved_detections) if improved_detections else 0
    
    print("\n=== Resumo da comparação ===")
    print(f"Módulo original: {len(original_detections)} detecções, {original_char_count} caracteres, confiança média: {original_avg_confidence:.2f}")
    print(f"Módulo melhorado: {len(improved_detections)} detecções, {improved_char_count} caracteres, confiança média: {improved_avg_confidence:.2f}")
    print(f"Diferença em detecções: {len(improved_detections) - len(original_detections)} ({(len(improved_detections) - len(original_detections)) / len(original_detections) * 100:.1f}% {'' if len(improved_detections) < len(original_detections) else '+'})")
    print(f"Diferença em caracteres: {improved_char_count - original_char_count} ({(improved_char_count - original_char_count) / original_char_count * 100:.1f}% {'' if improved_char_count < original_char_count else '+'})")
    print(f"Diferença em confiança média: {improved_avg_confidence - original_avg_confidence:.2f} ({(improved_avg_confidence - original_avg_confidence) / original_avg_confidence * 100:.1f}% {'' if improved_avg_confidence < original_avg_confidence else '+'})")
    
    # Cria um gráfico de comparação
    try:
        labels = ['Detecções', 'Caracteres', 'Confiança x100']
        original_values = [len(original_detections), original_char_count, original_avg_confidence * 100]
        improved_values = [len(improved_detections), improved_char_count, improved_avg_confidence * 100]
        
        x = np.arange(len(labels))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(10, 6))
        rects1 = ax.bar(x - width/2, original_values, width, label='OCR Original')
        rects2 = ax.bar(x + width/2, improved_values, width, label='OCR Melhorado')
        
        ax.set_ylabel('Valores')
        ax.set_title('Comparação entre OCR Original e Melhorado')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        
        # Adiciona rótulos nas barras
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'{height:.1f}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')
        
        autolabel(rects1)
        autolabel(rects2)
        
        fig.tight_layout()
        plt.savefig('ocr_comparison_chart.png')
        print("Gráfico de comparação salvo como: ocr_comparison_chart.png")
    except Exception as e:
        print(f"Erro ao criar gráfico de comparação: {e}")
    
    return {
        'original': {
            'detections': len(original_detections),
            'char_count': original_char_count,
            'avg_confidence': original_avg_confidence,
            'time': original_time
        },
        'improved': {
            'detections': len(improved_detections),
            'char_count': improved_char_count,
            'avg_confidence': improved_avg_confidence,
            'time': improved_time
        }
    }

async def main():
    # Cria uma imagem de teste
    test_image_path = create_test_image()
    
    # Compara os módulos OCR
    results = await compare_ocr_modules(test_image_path)
    
    # Verifica se existem outras imagens de teste
    test_images = []
    for file in os.listdir('.'):
        if file.endswith(('.png', '.jpg', '.jpeg')) and file.startswith('test_') and file != 'test_ocr_comparison.png':
            test_images.append(file)
    
    # Testa com cada imagem encontrada
    for image_path in test_images:
        await compare_ocr_modules(image_path)

if __name__ == "__main__":
    asyncio.run(main())
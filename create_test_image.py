# create_test_image.py

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image(filename="test_fragmented_text.png", width=800, height=600):
    """
    Cria uma imagem de teste com texto fragmentado para testar o agrupamento.
    """
    # Cria uma imagem com fundo preto
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img.fill(0)  # Fundo preto
    
    # Converte para PIL para usar fontes
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)
    
    try:
        # Tenta usar uma fonte do sistema
        font = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except:
        # Fallback para fonte padrão
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Adiciona texto fragmentado que deveria ser agrupado
    # Exemplo 1: Frase fragmentada horizontalmente
    draw.text((100, 100), "This is a", fill=(255, 255, 255), font=font)
    draw.text((220, 100), "fragmented sentence", fill=(255, 255, 255), font=font)
    draw.text((450, 100), "that should be grouped.", fill=(255, 255, 255), font=font)
    
    # Exemplo 2: Frase fragmentada verticalmente (mas próxima)
    draw.text((100, 200), "This text is", fill=(255, 255, 255), font=font)
    draw.text((100, 230), "split across", fill=(255, 255, 255), font=font)
    draw.text((100, 260), "multiple lines.", fill=(255, 255, 255), font=font)
    
    # Exemplo 3: Texto que não deve ser agrupado (distante)
    draw.text((100, 350), "This text", fill=(255, 255, 255), font=font)
    draw.text((100, 450), "is far away.", fill=(255, 255, 255), font=font)
    
    # Exemplo 4: Texto de jogo típico
    draw.text((500, 350), "GAME OVER", fill=(255, 0, 0), font=font)
    draw.text((500, 380), "PRESS START", fill=(255, 255, 0), font=font)
    draw.text((500, 410), "TO CONTINUE", fill=(255, 255, 0), font=font)
    
    # Exemplo 5: Texto pequeno próximo
    draw.text((300, 500), "Small", fill=(200, 200, 200), font=font_small)
    draw.text((350, 500), "adjacent", fill=(200, 200, 200), font=font_small)
    draw.text((420, 500), "text.", fill=(200, 200, 200), font=font_small)
    
    # Converte de volta para OpenCV
    img = np.array(pil_img)
    
    # Salva a imagem
    cv2.imwrite(filename, img)
    print(f"Imagem de teste criada: {os.path.abspath(filename)}")
    return os.path.abspath(filename)

if __name__ == "__main__":
    create_test_image()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar se o EasyOCR está usando GPU após a correção.
"""

import sys
import os
import time
from PIL import Image, ImageDraw, ImageFont
import io

# Adiciona o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_module import extract_text_with_positions

def create_test_image():
    """
    Cria uma imagem de teste com texto em inglês.
    """
    # Cria uma imagem branca
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Adiciona texto
    try:
        # Tenta usar uma fonte padrão
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Se não encontrar, usa a fonte padrão
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Hello World!", fill='black', font=font)
    draw.text((50, 100), "Testing GPU OCR", fill='black', font=font)
    draw.text((50, 150), "EasyOCR with CUDA", fill='black', font=font)
    
    # Converte para bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

async def test_ocr_gpu():
    """
    Testa o OCR e verifica se está usando GPU.
    """
    print("=== TESTE DE USO DA GPU NO EASYOCR ===")
    print("Criando imagem de teste...")
    
    # Cria imagem de teste
    test_image_bytes = create_test_image()
    print(f"Imagem criada com {len(test_image_bytes)} bytes")
    
    print("\nIniciando OCR (observe se aparece mensagem sobre CPU/GPU)...")
    start_time = time.time()
    
    # Executa o OCR
    try:
        results = await extract_text_with_positions(test_image_bytes, 'en')
        end_time = time.time()
        
        print(f"\nOCR concluído em {end_time - start_time:.2f} segundos")
        print(f"Resultados encontrados: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"  {i+1}. Texto: '{result['text']}' (Confiança: {result['confidence']:.2f})")
            
        if results:
            print("\n✅ OCR funcionando corretamente!")
        else:
            print("\n⚠️  Nenhum texto detectado na imagem de teste")
            
    except Exception as e:
        print(f"\n❌ Erro durante o OCR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    import asyncio
    
    print("Testando uso da GPU no EasyOCR...")
    print("IMPORTANTE: Observe se aparece a mensagem 'Using CPU' durante a inicialização do modelo.")
    print("Se não aparecer essa mensagem, significa que está usando a GPU!\n")
    
    # Executa o teste
    success = asyncio.run(test_ocr_gpu())
    
    if success:
        print("\n🎉 Teste concluído com sucesso!")
    else:
        print("\n💥 Teste falhou!")
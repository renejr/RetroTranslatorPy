#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de integração completa do sistema principal com tradução concorrente
"""

import asyncio
import os
import sys
import json
import base64
from PIL import Image, ImageDraw, ImageFont
import io

# Configurar variáveis de ambiente para habilitar o sistema concorrente
os.environ['ENABLE_DEEP_TRANSLATOR'] = 'true'
os.environ['DEEP_TRANSLATOR_PRIORITY'] = 'high'
os.environ['CONCURRENT_TRANSLATION_ENABLED'] = 'true'
os.environ['MAX_CONCURRENT_TRANSLATIONS'] = '3'
os.environ['TRANSLATION_TIMEOUT'] = '10'
os.environ['MIN_CONFIDENCE_SCORE'] = '0.6'

# Importar o service_logic
from service_logic import process_ai_request

def create_test_image_with_text():
    """
    Cria uma imagem de teste com texto em inglês para simular um jogo
    """
    # Criar uma imagem de teste
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(image)
    
    # Tentar usar uma fonte padrão
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Adicionar textos de teste em posições diferentes
    test_texts = [
        ("GAME OVER", (300, 100)),
        ("PRESS START", (280, 200)),
        ("HIGH SCORE: 15000", (220, 300)),
        ("PLAYER ONE", (300, 400)),
        ("CONTINUE?", (320, 500))
    ]
    
    for text, position in test_texts:
        draw.text(position, text, fill='white', font=font)
    
    # Converter para base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_data = buffer.getvalue()
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    return base64_image

async def test_service_integration():
    """
    Testa a integração completa do sistema principal com tradução concorrente
    """
    print("=== Teste de Integração Completa do Sistema Principal ===")
    print()
    
    # Criar imagem de teste
    print("Criando imagem de teste...")
    test_image_base64 = create_test_image_with_text()
    print(f"Imagem criada com {len(test_image_base64)} caracteres base64")
    print()
    
    # Criar requisição de teste simulando o RetroArch
    from models import RetroArchRequest
    
    test_request = RetroArchRequest(
        image=test_image_base64,
        format="png",
        lang_source="en",
        lang_target="pt"
    )
    
    print("Processando requisição com o sistema principal...")
    print()
    
    try:
        import time
        start_time = time.time()
        
        # Processar a requisição usando o service_logic
        result = await process_ai_request(test_request)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Processamento concluído em {duration:.3f}s")
        print()
        
        # Analisar o resultado
        if result:
            print("=== Resultado do Processamento ===")
            
            if isinstance(result, dict):
                # Verificar se há imagem de resultado
                if 'image' in result:
                    print(f"✓ Imagem de resultado gerada ({len(result['image'])} caracteres base64)")
                
                # Verificar estatísticas
                if 'stats' in result:
                    stats = result['stats']
                    print(f"✓ Estatísticas disponíveis:")
                    for key, value in stats.items():
                        print(f"  - {key}: {value}")
                
                # Verificar traduções
                if 'translations' in result:
                    translations = result['translations']
                    print(f"✓ {len(translations)} traduções realizadas:")
                    for i, translation in enumerate(translations, 1):
                        if isinstance(translation, dict):
                            original = translation.get('original', 'N/A')
                            translated = translation.get('translated', 'N/A')
                            print(f"  [{i}] '{original}' → '{translated}'")
                        else:
                            print(f"  [{i}] {translation}")
                
                # Verificar outros campos
                for key, value in result.items():
                    if key not in ['image', 'stats', 'translations']:
                        print(f"✓ {key}: {value}")
            
            else:
                print(f"Resultado: {type(result)} - {str(result)[:200]}...")
        
        else:
            print("❌ Nenhum resultado retornado")
    
    except Exception as e:
        print(f"❌ Erro durante o processamento: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=== Teste de Integração Concluído ===")

if __name__ == "__main__":
    asyncio.run(test_service_integration())
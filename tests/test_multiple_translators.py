# test_multiple_translators.py

import sys
import os
import time
import asyncio

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retroarch_ai_service.translation_module import translate_text

async def test_multiple_translators():
    """
    Testa o sistema de fallback com múltiplos tradutores.
    Tenta traduzir textos usando diferentes tradutores e verifica se o sistema de fallback funciona.
    """
    print("\n===== TESTE DO SISTEMA DE FALLBACK COM MÚLTIPLOS TRADUTORES =====")
    
    # Lista de textos para testar
    test_texts = [
        "PRESS START BUTTON",
        "GAME OVER SCREEN",
        "PLAYER ONE WINS",
        "HIGH SCORE TABLE",
        "This is a longer text to test the translation system with multiple translators. The system should try different translators if one fails."
    ]
    
    for i, text in enumerate(test_texts):
        print(f"\nTexto {i+1}: '{text}'")
        
        try:
            # Traduzir para português
            start_time = time.time()
            translated = await translate_text(text, target_lang='pt')
            end_time = time.time()
            
            print(f"Tradução: '{translated}'")
            print(f"Tempo de execução: {end_time - start_time:.2f} segundos")
            
        except Exception as e:
            print(f"Erro ao traduzir: {e}")
    
    print("\n===== TESTE DE FALLBACK FORÇADO =====")
    print("Forçando falha no primeiro tradutor para testar o fallback...")
    
    # Aqui podemos simular uma falha no primeiro tradutor
    # Isso é apenas para demonstração, na prática o sistema já vai tentar o próximo tradutor automaticamente
    try:
        # Tentar traduzir um texto muito grande ou complexo que pode fazer o primeiro tradutor falhar
        complex_text = "A" * 5000  # Texto muito longo que pode causar falha em alguns tradutores
        print(f"Tentando traduzir texto muito longo...")
        
        start_time = time.time()
        translated = await translate_text(complex_text, target_lang='pt')
        end_time = time.time()
        
        print(f"Tradução bem-sucedida com fallback")
        print(f"Tempo de execução: {end_time - start_time:.2f} segundos")
        
    except Exception as e:
        print(f"Erro mesmo com fallback: {e}")

if __name__ == "__main__":
    # Executar a função assíncrona
    asyncio.run(test_multiple_translators())
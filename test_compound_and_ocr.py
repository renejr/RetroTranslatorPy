# test_compound_and_ocr.py

import asyncio
from translation_module import translate_text, translate_game_terms, correct_ocr_errors

async def test_compound_terms_with_ocr_errors():
    """
    Testa a combinação de correção de erros de OCR e tradução de termos compostos.
    Verifica se os erros de OCR são corrigidos antes da tradução de termos compostos.
    """
    print("\n===== TESTE DE CORREÇÃO DE OCR + TRADUÇÃO DE TERMOS COMPOSTOS =====\n")
    
    # Lista de frases com erros de OCR para testar
    test_phrases = [
        # Frases com erros de OCR e termos compostos
        "STAHT GAME BUTTON",  # Deve corrigir para "START GAME BUTTON" e traduzir corretamente
        "PLAVER ONE WINS",    # Deve corrigir para "PLAYER ONE WINS" e traduzir corretamente
        "CONTIMUE SCREEN",    # Deve corrigir para "CONTINUE SCREEN" e traduzir corretamente
        "SELEGT OPTION MENU", # Deve corrigir para "SELECT OPTION MENU" e traduzir corretamente
        "HEALIH: 100 POINTS", # Deve corrigir para "HEALTH: 100 POINTS" e traduzir corretamente
        "ATTACX: 50 DAMAGE",  # Deve corrigir para "ATTACK: 50 DAMAGE" e traduzir corretamente
        "CONGRATULATIOMS YOU WIN", # Deve corrigir para "CONGRATULATIONS YOU WIN" e traduzir corretamente
        "MISSICN COMPLETE BONUS", # Deve corrigir para "MISSION COMPLETE BONUS" e traduzir corretamente
        "GAME OVEH SCREEN",   # Deve corrigir para "GAME OVER SCREEN" e traduzir corretamente
        "PRESS STAHT TO CONTINUE" # Deve corrigir para "PRESS START TO CONTINUE" e traduzir corretamente
    ]
    
    print("----- Correção de OCR + Tradução de termos compostos -----")
    for phrase in test_phrases:
        # Primeiro corrige os erros de OCR
        corrected = correct_ocr_errors(phrase)
        # Depois traduz os termos compostos
        translated = translate_game_terms(corrected, 'pt')
        print(f"Original: '{phrase}' -> Corrigido: '{corrected}' -> Traduzido: '{translated}'")
    
    print("\n----- Usando a função translate_text completa -----")
    for phrase in test_phrases:
        # Usa a função translate_text que integra correção de OCR e tradução
        translated = await translate_text(phrase, 'pt')
        print(f"Original: '{phrase}' -> Traduzido: '{translated}'")

async def main():
    await test_compound_terms_with_ocr_errors()

if __name__ == "__main__":
    asyncio.run(main())
# test_game_terms.py

import asyncio
from translation_module import translate_text, translate_game_terms, correct_ocr_errors

async def test_game_terms_dictionary():
    """
    Testa o dicionário expandido de termos de jogos.
    Verifica se os termos são traduzidos corretamente usando o dicionário.
    """
    print("\n===== TESTE DO DICIONÁRIO DE TERMOS DE JOGOS =====\n")
    
    # Lista de termos de jogos para testar
    test_terms = [
        # Termos básicos
        "PRESS START",
        "GAME OVER",
        "INSERT COIN",
        "CONTINUE?",
        "HIGH SCORE",
        
        # Jogabilidade
        "PLAYER ONE",
        "LEVEL 5",
        "WORLD 1-2",
        "EXTRA LIFE",
        "HP: 100 MP: 50",
        
        # Menus e configurações
        "OPTIONS MENU",
        "DIFFICULTY: HARD",
        "SAVE GAME",
        "PRESS ANY BUTTON",
        
        # Status e mensagens
        "STAGE CLEAR",
        "MISSION COMPLETE",
        "CONGRATULATIONS",
        "GAME COMPLETE",
        "TRY AGAIN"
    ]
    
    # Testa a tradução direta usando o dicionário de termos
    print("\n----- Tradução usando apenas o dicionário de termos -----")
    for term in test_terms:
        translated = translate_game_terms(term, 'pt')
        print(f"Original: '{term}' -> Traduzido: '{translated}'")
    
    # Testa a tradução completa (incluindo API de tradução)
    print("\n----- Tradução completa (dicionário + API) -----")
    for term in test_terms:
        translated = await translate_text(term, 'pt', 'en')
        print(f"Original: '{term}' -> Traduzido: '{translated}'")

async def test_ocr_corrections():
    """
    Testa as correções de OCR expandidas.
    Verifica se os erros comuns de OCR são corrigidos corretamente.
    """
    print("\n===== TESTE DE CORREÇÕES DE OCR =====\n")
    
    # Lista de termos com erros de OCR para testar
    test_ocr_errors = [
        "STAHT GAME",
        "PLAVER ONE",
        "CONTIMUE?",
        "SELEGT OPTION",
        "HEALIH: 100",
        "ATTACX: 50",
        "CONGRATULATIOMS",
        "MISSICN COMPLETE"
    ]
    
    for error_text in test_ocr_errors:
        corrected = correct_ocr_errors(error_text)
        print(f"Texto com erro: '{error_text}' -> Corrigido: '{corrected}'")

async def main():
    await test_game_terms_dictionary()
    await test_ocr_corrections()

if __name__ == "__main__":
    asyncio.run(main())
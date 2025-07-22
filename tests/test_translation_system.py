# test_translation_system.py

import asyncio
from translation_module import translate_text, translate_game_terms, correct_ocr_errors, is_mostly_portuguese

async def test_ocr_corrections():
    """
    Testa a correção de erros comuns de OCR.
    """
    print("\n===== TESTE DE CORREÇÃO DE ERROS DE OCR =====\n")
    
    test_phrases = [
        "STAHT GAME",
        "PLAVER ONE",
        "CONTIMUE?",
        "SELEGT OPTION",
        "HEALIH: 100",
        "ATTACX: 50",
        "CONGRATULATIOMS",
        "MISSICN COMPLETE",
        "GAME OVEH SCREEN",
        "GAHE OVER"
    ]
    
    for phrase in test_phrases:
        corrected = correct_ocr_errors(phrase)
        print(f"Original: '{phrase}' -> Corrigido: '{corrected}'")

async def test_game_terms_dictionary():
    """
    Testa a tradução de termos específicos de jogos usando o dicionário.
    """
    print("\n===== TESTE DE TRADUÇÃO DE TERMOS DE JOGOS =====\n")
    
    test_phrases = [
        "PRESS START",
        "GAME OVER",
        "INSERT COIN",
        "HIGH SCORE",
        "PLAYER ONE",
        "LEVEL 5",
        "WORLD 1-2",
        "HP: 100 MP: 50",
        "OPTIONS MENU",
        "DIFFICULTY: HARD",
        "SAVE GAME",
        "PRESS ANY BUTTON",
        "STAGE CLEAR",
        "MISSION COMPLETE",
        "CONGRATULATIONS",
        "GAME COMPLETE",
        "TRY AGAIN"
    ]
    
    for phrase in test_phrases:
        translated = translate_game_terms(phrase, 'pt')
        print(f"Original: '{phrase}' -> Traduzido: '{translated}'")

async def test_compound_terms_priority():
    """
    Testa a priorização de termos compostos na tradução.
    """
    print("\n===== TESTE DE PRIORIZAÇÃO DE TERMOS COMPOSTOS =====\n")
    
    test_phrases = [
        "PRESS START BUTTON",
        "GAME OVER SCREEN",
        "PLAYER ONE WINS",
        "PRESS ANY KEY NOW",
        "STAGE CLEAR BONUS",
        "MISSION COMPLETE CONGRATULATIONS",
        "OPTIONS MENU SETTINGS",
        "DIFFICULTY: HARD MODE",
        "HIGH SCORE TABLE",
        "PRESS START TO CONTINUE"
    ]
    
    for phrase in test_phrases:
        translated = translate_game_terms(phrase, 'pt')
        print(f"Original: '{phrase}' -> Traduzido: '{translated}'")

async def test_ocr_and_translation_integration():
    """
    Testa a integração entre correção de OCR e tradução.
    """
    print("\n===== TESTE DE INTEGRAÇÃO OCR + TRADUÇÃO =====\n")
    
    test_phrases = [
        "STAHT GAME BUTTON",
        "PLAVER ONE WINS",
        "CONTIMUE SCREEN",
        "SELEGT OPTION MENU",
        "HEALIH: 100 POINTS",
        "ATTACX: 50 DAMAGE",
        "CONGRATULATIOMS YOU WIN",
        "MISSICN COMPLETE BONUS",
        "GAME OVEH SCREEN",
        "PRESS STAHT TO CONTINUE"
    ]
    
    for phrase in test_phrases:
        corrected = correct_ocr_errors(phrase)
        translated = translate_game_terms(corrected, 'pt')
        print(f"Original: '{phrase}' -> Corrigido: '{corrected}' -> Traduzido: '{translated}'")

async def test_full_translation_system():
    """
    Testa o sistema completo de tradução usando a função translate_text.
    """
    print("\n===== TESTE DO SISTEMA COMPLETO DE TRADUÇÃO =====\n")
    
    test_phrases = [
        # Frases simples
        "PRESS START",
        "GAME OVER",
        "INSERT COIN",
        
        # Frases com erros de OCR
        "STAHT GAME",
        "PLAVER ONE",
        "GAME OVEH",
        
        # Frases compostas
        "PRESS START BUTTON",
        "GAME OVER SCREEN",
        "HIGH SCORE TABLE",
        
        # Frases compostas com erros de OCR
        "STAHT GAME BUTTON",
        "PLAVER ONE WINS",
        "GAME OVEH SCREEN",
        
        # Frases mais complexas
        "PRESS START TO CONTINUE THE GAME",
        "PLAYER ONE HAS DEFEATED THE FINAL BOSS",
        "CONGRATULATIONS! YOU HAVE COMPLETED THE GAME",
        
        # Frases complexas com erros de OCR
        "PRESS STAHT TO CONTIMUE THE GAHE",
        "PLAVER ONE HAS DEFEAIED THE FIHAL BOSS",
        "CONGRATULATIOMS! YOU HAVE COMPLETEO THE GAHE"
    ]
    
    for phrase in test_phrases:
        translated = await translate_text(phrase, 'pt')
        print(f"Original: '{phrase}' -> Traduzido: '{translated}'")

async def test_portuguese_detection():
    """
    Testa a detecção de texto já em português.
    """
    print("\n===== TESTE DE DETECÇÃO DE TEXTO EM PORTUGUÊS =====\n")
    
    test_phrases = [
        # Textos em inglês
        "PRESS START TO CONTINUE",
        "GAME OVER",
        "PLAYER ONE WINS",
        
        # Textos em português
        "Pressione Iniciar para Continuar",
        "Fim de Jogo",
        "Jogador Um Vence",
        
        # Textos mistos
        "PRESS START para Continuar",
        "Fim de GAME",
        "Jogador ONE Vence"
    ]
    
    for phrase in test_phrases:
        is_portuguese = is_mostly_portuguese(phrase)
        print(f"Texto: '{phrase}' -> É português? {is_portuguese}")

async def main():
    await test_ocr_corrections()
    await test_game_terms_dictionary()
    await test_compound_terms_priority()
    await test_ocr_and_translation_integration()
    await test_portuguese_detection()
    await test_full_translation_system()

if __name__ == "__main__":
    asyncio.run(main())
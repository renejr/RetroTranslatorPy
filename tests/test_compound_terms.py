# test_compound_terms.py

import asyncio
from translation_module import translate_game_terms

async def test_compound_terms_priority():
    """
    Testa a priorização de termos compostos na tradução.
    Verifica se os termos compostos são traduzidos corretamente antes dos termos individuais.
    """
    print("\n===== TESTE DE PRIORIZAÇÃO DE TERMOS COMPOSTOS =====\n")
    
    # Lista de frases para testar a priorização de termos compostos
    test_phrases = [
        # Frases que contêm termos compostos e individuais
        "PRESS START BUTTON",  # Deve traduzir como "Pressione o Botão Iniciar" e não "Pressione Iniciar Botão"
        "GAME OVER SCREEN",    # Deve traduzir "Fim de Jogo" corretamente
        "PLAYER ONE WINS",     # Deve traduzir "Jogador Um" corretamente
        "PRESS ANY KEY NOW",   # Deve traduzir "Pressione Qualquer Tecla" corretamente
        "STAGE CLEAR BONUS",   # Deve traduzir "Fase Concluída" corretamente
        "MISSION COMPLETE CONGRATULATIONS",  # Deve traduzir ambos os termos compostos corretamente
        "OPTIONS MENU SETTINGS",  # Deve traduzir "Menu de Opções" corretamente
        "DIFFICULTY: HARD MODE",  # Deve traduzir "Dificuldade: Difícil" corretamente
        "HIGH SCORE TABLE",    # Deve traduzir "Recorde" corretamente
        "PRESS START TO CONTINUE"  # Deve traduzir ambos os termos corretamente
    ]
    
    print("----- Tradução com priorização de termos compostos -----")
    for phrase in test_phrases:
        translated = translate_game_terms(phrase, 'pt')
        print(f"Original: '{phrase}' -> Traduzido: '{translated}'")

async def main():
    await test_compound_terms_priority()

if __name__ == "__main__":
    asyncio.run(main())
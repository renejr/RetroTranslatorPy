# translation_module.py

import translators as ts
import re

# Dicionário de termos comuns de jogos arcade/retro
GAME_TERMS_DICT = {
    'en': {
        '2UP': '2 Jogadores',
        '1UP': '1 Jogador', 
        'CREDIT': 'Crédito',
        'CREDITS': 'Créditos',
        'CRED IT': 'Crédito',
        'JOIN': 'Entrar',
        'JOIM': 'Entrar',  # Correção de OCR
        'PUSH TO': 'Pressione para',
        'PUSH': 'Pressione',
        'START': 'Iniciar',
        'GAME OVER': 'Fim de Jogo',
        'CONTINUE': 'Continuar',
        'PLAYER': 'Jogador',
        'SCORE': 'Pontuação',
        'HIGH SCORE': 'Recorde',
        'LEVEL': 'Nível',
        'STAGE': 'Fase',
        'LIVES': 'Vidas',
        'TIME': 'Tempo',
        'BONUS': 'Bônus'
    }
}

# Correções comuns de OCR
OCR_CORRECTIONS = {
    'JOIM': 'JOIN',
    'CRED IT': 'CREDIT',
    'CRED ITS': 'CREDITS',
    'PIJSH': 'PUSH',
    'STAKT': 'START',
    'GANE': 'GAME',
    'OVEK': 'OVER'
}

def correct_ocr_errors(text: str) -> str:
    """Corrige erros comuns de OCR"""
    corrected = text
    for error, correction in OCR_CORRECTIONS.items():
        corrected = re.sub(r'\b' + re.escape(error) + r'\b', correction, corrected, flags=re.IGNORECASE)
    return corrected

def translate_game_terms(text: str, target_lang: str) -> str:
    """Traduz termos específicos de jogos usando dicionário"""
    if target_lang not in ['pt', 'pt-br']:
        return text
        
    translated = text
    game_terms = GAME_TERMS_DICT.get('en', {})
    
    for term, translation in game_terms.items():
        # Substitui o termo exato (case insensitive)
        pattern = r'\b' + re.escape(term) + r'\b'
        translated = re.sub(pattern, translation, translated, flags=re.IGNORECASE)
    
    return translated

def is_mostly_portuguese(text: str) -> bool:
    """Verifica se o texto já está majoritariamente em português"""
    portuguese_words = ['jogador', 'jogadores', 'crédito', 'créditos', 'entrar', 'pressione', 
                       'iniciar', 'continuar', 'pontuação', 'recorde', 'nível', 'fase', 
                       'vidas', 'tempo', 'bônus', 'fim', 'jogo']
    
    words = text.lower().split()
    portuguese_count = sum(1 for word in words if any(pt_word in word for pt_word in portuguese_words))
    
    return portuguese_count > len(words) * 0.3  # Se mais de 30% das palavras parecem portuguesas

async def translate_text(text: str, target_lang: str = 'en', source_lang: str = 'auto') -> str:
    """
    Traduz um texto de um idioma de origem para um idioma de destino.
    Inclui correções de OCR e dicionário de termos de jogos.

    Args:
        text: O texto a ser traduzido.
        target_lang: O código do idioma de destino (ex: 'pt' para português).
        source_lang: O código do idioma de origem (ex: 'en' para inglês). 'auto' para detecção automática.

    Returns:
        O texto traduzido.
    """
    if not text:
        return ""
        
    try:
        print(f"Módulo de Tradução: Recebeu texto '{text}' para traduzir para '{target_lang}'.")
        
        # Etapa 1: Corrigir erros comuns de OCR
        corrected_text = correct_ocr_errors(text)
        if corrected_text != text:
            print(f"Módulo de Tradução: Texto após correção OCR: '{corrected_text}'")
        
        # Etapa 2: Verificar se já está em português
        if target_lang in ['pt', 'pt-br'] and is_mostly_portuguese(corrected_text):
            print(f"Módulo de Tradução: Texto já parece estar em português, retornando sem traduzir.")
            return corrected_text
        
        # Etapa 3: Traduzir termos específicos de jogos primeiro
        game_translated = translate_game_terms(corrected_text, target_lang)
        if game_translated != corrected_text:
            print(f"Módulo de Tradução: Texto após tradução de termos de jogos: '{game_translated}'")
        
        # Etapa 4: Traduzir o restante usando Google Translate
        try:
            final_translated = ts.translate_text(
                game_translated,
                translator='google',
                from_language=source_lang,
                to_language=target_lang
            )
        except Exception as e:
            print(f"Módulo de Tradução: Erro no Google Translate: {e}")
            print(f"Módulo de Tradução: Tentando tradução palavra por palavra...")
            
            # Fallback: traduzir palavra por palavra
            words = game_translated.split()
            translated_words = []
            
            for word in words:
                try:
                    if word.isdigit() or len(word) <= 2:  # Números e palavras muito curtas
                        translated_words.append(word)
                    else:
                        word_translated = ts.translate_text(
                            word,
                            translator='google', 
                            from_language=source_lang,
                            to_language=target_lang
                        )
                        translated_words.append(word_translated)
                except:
                    translated_words.append(word)  # Manter palavra original se falhar
            
            final_translated = ' '.join(translated_words)
            
        print(f"Módulo de Tradução: Texto final traduzido: '{final_translated}'")
        
        return final_translated
        
    except Exception as e:
        print(f"Erro no módulo de tradução: {e}")
        return f"Erro ao traduzir: {e}"
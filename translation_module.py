# translation_module.py

import translators as ts
import re

# Dicionário de termos comuns de jogos arcade/retro
GAME_TERMS_DICT = {
    'en': {
        # Termos básicos de interface
        '2UP': '2 Jogadores',
        '1UP': '1 Jogador', 
        'CREDIT': 'Crédito',
        'CREDITS': 'Créditos',
        'CRED IT': 'Crédito',
        'INSERT COIN': 'Insira Moeda',
        'INSERT COINS': 'Insira Moedas',
        'FREE PLAY': 'Jogo Livre',
        'JOIN': 'Entrar',
        'JOIM': 'Entrar',  # Correção de OCR
        'PUSH TO': 'Pressione para',
        'PUSH': 'Pressione',
        'PRESS': 'Pressione',
        'PRESS START': 'Pressione Iniciar',
        'PRESS START BUTTON': 'Pressione o Botão Iniciar',
        'PRESS ANY BUTTON': 'Pressione Qualquer Botão',
        'PRESS ANY KEY': 'Pressione Qualquer Tecla',
        'PUSH SPACE KEY': 'Pressione a Tecla Espaço',
        'PUSH SPACE KEY TO START': 'Pressione a Tecla Espaço para Iniciar',
        'PUSH SPACE KEY TO CONTINUE': 'Pressione a Tecla Espaço para Continuar',
        'PUSH SPACE TO START': 'Pressione Espaço para Iniciar',
        'PUSH SPACE TO CONTINUE': 'Pressione Espaço para Continuar',
        'SPACE KEY': 'Tecla Espaço',
        'SPACE': 'Espaço',
        'ANY': 'Qualquer',  # Para melhorar traduções parciais
        'BUTTON': 'Botão',  # Para melhorar traduções parciais
        'KEY': 'Tecla',  # Para melhorar traduções parciais
        'START': 'Iniciar',
        'GAME OVER': 'Fim de Jogo',
        'GAME': 'Jogo',  # Para melhorar traduções parciais
        'OVER': 'Fim',  # Para melhorar traduções parciais
        'CONTINUE': 'Continuar',
        'CONTINUE?': 'Continuar?',
        'YES': 'Sim',
        'NO': 'Não',
        'EXIT': 'Sair',
        'QUIT': 'Sair',
        'RETRY': 'Tentar Novamente',
        'RESTART': 'Reiniciar',
        'MENU': 'Menu',  # Para melhorar traduções parciais
        
        # Jogabilidade
        'PLAYER': 'Jogador',
        'PLAYER ONE': 'Jogador Um',
        'PLAYER TWO': 'Jogador Dois',
        '1 PLAYER': '1 Jogador',
        '2 PLAYERS': '2 Jogadores',
        'ONE': 'Um',  # Para melhorar traduções parciais
        'TWO': 'Dois',  # Para melhorar traduções parciais
        'SCORE': 'Pontuação',
        'HIGH SCORE': 'Recorde',
        'HIGH': 'Alta',  # Para melhorar traduções parciais
        'HI-SCORE': 'Recorde',
        'TOP SCORE': 'Melhor Pontuação',
        'TOP': 'Melhor',  # Para melhorar traduções parciais
        'LEVEL': 'Nível',
        'STAGE': 'Fase',
        'WORLD': 'Mundo',
        'ROUND': 'Rodada',
        'AREA': 'Área',
        'ZONE': 'Zona',
        'MISSION': 'Missão',
        'QUEST': 'Missão',
        'LIVES': 'Vidas',
        'LIFE': 'Vida',
        'TIME': 'Tempo',
        'TIME LEFT': 'Tempo Restante',
        'LEFT': 'Restante',  # Para melhorar traduções parciais
        'TIMER': 'Temporizador',
        'BONUS': 'Bônus',
        'EXTRA': 'Extra',
        'EXTRA LIFE': 'Vida Extra',
        'POWER': 'Poder',
        'POWER UP': 'Poder Especial',
        'UP': 'Especial',  # Para melhorar traduções parciais
        'ENERGY': 'Energia',
        'HEALTH': 'Saúde',
        'HP': 'PS', # Pontos de Saúde
        'MP': 'PM', # Pontos de Magia
        'EXP': 'EXP', # Experiência
        'EXPERIENCE': 'Experiência',
        'ATTACK': 'Ataque',
        'DEFENSE': 'Defesa',
        'MAGIC': 'Magia',
        'SPEED': 'Velocidade',
        'STRENGTH': 'Força',
        'AGILITY': 'Agilidade',
        'INTELLIGENCE': 'Inteligência',
        'WISDOM': 'Sabedoria',
        'LUCK': 'Sorte',
        
        # Menus e configurações
        'OPTIONS': 'Opções',
        'OPTIONS MENU': 'Menu de Opções',  # Termo composto
        'SETTINGS': 'Configurações',
        'CONFIG': 'Configuração',
        'SOUND': 'Som',
        'MUSIC': 'Música',
        'VOLUME': 'Volume',
        'CONTROLS': 'Controles',
        'DIFFICULTY': 'Dificuldade',
        'DIFFICULTY: EASY': 'Dificuldade: Fácil',  # Termos compostos
        'DIFFICULTY: NORMAL': 'Dificuldade: Normal',
        'DIFFICULTY: HARD': 'Dificuldade: Difícil',
        'DIFFICULTY: EXPERT': 'Dificuldade: Especialista',
        'EASY': 'Fácil',
        'NORMAL': 'Normal',
        'HARD': 'Difícil',
        'EXPERT': 'Especialista',
        'LANGUAGE': 'Idioma',
        'SAVE': 'Salvar',
        'LOAD': 'Carregar',
        'SAVING': 'Salvando',
        'LOADING': 'Carregando',
        'SAVE GAME': 'Salvar Jogo',
        'LOAD GAME': 'Carregar Jogo',
        'DELETE': 'Excluir',
        'CANCEL': 'Cancelar',
        'CONFIRM': 'Confirmar',
        'SELECT': 'Selecionar',
        'BACK': 'Voltar',
        'RETURN': 'Retornar',
        
        # Status e mensagens
        'WIN': 'Vitória',
        'LOSE': 'Derrota',
        'VICTORY': 'Vitória',
        'DEFEAT': 'Derrota',
        'CONGRATULATIONS': 'Parabéns',
        'CONGRATULATION': 'Parabéns',
        'CONGRATS': 'Parabéns',
        'THANK YOU': 'Obrigado',
        'THANK': 'Obrigado',  # Para melhorar traduções parciais
        'YOU': 'Você',  # Para melhorar traduções parciais
        'THANKS FOR PLAYING': 'Obrigado por Jogar',
        'THANKS': 'Obrigado',  # Para melhorar traduções parciais
        'FOR': 'Por',  # Para melhorar traduções parciais
        'PLAYING': 'Jogar',  # Para melhorar traduções parciais
        'THE END': 'Fim',
        'THE': 'O',  # Para melhorar traduções parciais
        'END': 'Fim',  # Para melhorar traduções parciais
        'PAUSE': 'Pausa',
        'PAUSED': 'Pausado',
        'READY': 'Pronto',
        'GO': 'Vai',
        'FIGHT': 'Lutar',
        'BATTLE': 'Batalha',
        'PERFECT': 'Perfeito',
        'GREAT': 'Ótimo',
        'GOOD': 'Bom',
        'OK': 'OK',
        'BAD': 'Ruim',
        'MISS': 'Errou',
        'FAILED': 'Falhou',
        'CLEAR': 'Concluído',  # Para melhorar traduções parciais
        'GAME CLEAR': 'Jogo Concluído',
        'STAGE CLEAR': 'Fase Concluída',
        'LEVEL CLEAR': 'Nível Concluído',
        'COMPLETE': 'Completa',  # Para melhorar traduções parciais
        'MISSION COMPLETE': 'Missão Completa',
        'MISSION ACCOMPLISHED': 'Missão Cumprida',
        'ACCOMPLISHED': 'Cumprida',  # Para melhorar traduções parciais
        'GAME COMPLETE': 'Jogo Completo',
        'TRY': 'Tentar',  # Para melhorar traduções parciais
        'AGAIN': 'Novamente',  # Para melhorar traduções parciais
        'TRY AGAIN': 'Tente Novamente',
        'WARNING': 'Aviso',
        'DANGER': 'Perigo',
        'ERROR': 'Erro',
        'DEBUG': 'Depuração',
        
        # Frases completas adicionais
        'PRESS START TO CONTINUE': 'Pressione Iniciar para Continuar',
        'PRESS ANY KEY TO CONTINUE': 'Pressione Qualquer Tecla para Continuar',
        'PRESS ANY BUTTON TO CONTINUE': 'Pressione Qualquer Botão para Continuar',
        'PUSH SPACE KEY TO START': 'Pressione a Tecla Espaço para Iniciar',
        'PUSH SPACE KEY TO CONTINUE': 'Pressione a Tecla Espaço para Continuar',
        'GAME OVER SCREEN': 'Tela de Fim de Jogo',
        'HIGH SCORE TABLE': 'Tabela de Recordes',
        'PLAYER ONE WINS': 'Jogador Um Vence',
        'PLAYER TWO WINS': 'Jogador Dois Vence',
        'STAGE CLEAR BONUS': 'Bônus de Fase Concluída',
        'BONUS STAGE': 'Fase Bônus',
        'BONUS POINTS': 'Pontos Bônus',
        'TIME BONUS': 'Bônus de Tempo',
        'SCORE BONUS': 'Bônus de Pontuação',
        'CONTINUE SCREEN': 'Tela de Continuação',
        'OPTIONS MENU SETTINGS': 'Configurações do Menu de Opções',
        'DIFFICULTY: HARD MODE': 'Dificuldade: Modo Difícil',
        'SCREEN': 'Tela',  # Para melhorar traduções parciais
        'TABLE': 'Tabela',  # Para melhorar traduções parciais
        'WINS': 'Vence',  # Para melhorar traduções parciais
        'MODE': 'Modo',  # Para melhorar traduções parciais
        'TO': 'para',  # Para melhorar traduções parciais
        'NOW': 'Agora'  # Para melhorar traduções parciais
    }
}

# Correções comuns de OCR
OCR_CORRECTIONS = {
    # Correções básicas
    'JOIM': 'JOIN',
    'CRED IT': 'CREDIT',
    'CRED ITS': 'CREDITS',
    'PIJSH': 'PUSH',
    'STAKT': 'START',
    'GANE': 'GAME',
    'OVEK': 'OVER',
    'OVEH': 'OVER',
    'STAHT': 'START',
    'STAPT': 'START',
    'GAHE': 'GAME',
    'PLAVER': 'PLAYER',
    'PLAYEP': 'PLAYER',
    'SCOHE': 'SCORE',
    'SCOKE': 'SCORE',
    'LEVEI': 'LEVEL',
    'LEVFL': 'LEVEL',
    'TINE': 'TIME',
    'TIHE': 'TIME',
    'BOMS': 'BONUS',
    'BOMJS': 'BONUS',
    'COMTINUE': 'CONTINUE',
    'CONTIMUE': 'CONTINUE',
    'PLESS': 'PRESS',
    'PHESS': 'PRESS',
    'SELEGT': 'SELECT',
    'SELECI': 'SELECT',
    'OPTIDNS': 'OPTIONS',
    'OPTIOMS': 'OPTIONS',
    'ENEHGY': 'ENERGY',
    'ENERCY': 'ENERGY',
    'HEALIH': 'HEALTH',
    'HEAITH': 'HEALTH',
    'ATTACX': 'ATTACK',
    'ATTAOK': 'ATTACK',
    'DEFEISE': 'DEFENSE',
    'DEFEMSE': 'DEFENSE',
    'MAGIG': 'MAGIC',
    'MAGC': 'MAGIC',
    'SPEEO': 'SPEED',
    'SPEFD': 'SPEED',
    'STRENGIH': 'STRENGTH',
    'STRENGTM': 'STRENGTH',
    'AGILITV': 'AGILITY',
    # Correções específicas para PUSH SPACE KEY
    'PUSHGPACE KEY': 'PUSH SPACE KEY',
    'PUSHGPACBKEY': 'PUSH SPACE KEY',
    'PUSHEPACBKEY': 'PUSH SPACE KEY',
    'PUSh SPACE': 'PUSH SPACE',
    'PUSH SPACE KEY': 'PUSH SPACE KEY',
    'AGILIFY': 'AGILITY',
    'INTELLIGENGE': 'INTELLIGENCE',
    'INTELLIGEMCE': 'INTELLIGENCE',
    'WISOOM': 'WISDOM',
    'WISDON': 'WISDOM',
    'LICK': 'LUCK',
    'LIJCK': 'LUCK',
    'VICTOPY': 'VICTORY',
    'VICTOHY': 'VICTORY',
    'DEFEAI': 'DEFEAT',
    'DEFERT': 'DEFEAT',
    'CONGRATULATIOMS': 'CONGRATULATIONS',
    'CONGRATUIATIONS': 'CONGRATULATIONS',
    'PAUSEO': 'PAUSED',
    'PAUSFD': 'PAUSED',
    'READV': 'READY',
    'REABY': 'READY',
    'BATTIE': 'BATTLE',
    'BATILE': 'BATTLE',
    'PERFECI': 'PERFECT',
    'PERFEOT': 'PERFECT',
    'MISSICN': 'MISSION',
    'MISSIGN': 'MISSION',
    'WARNIIG': 'WARNING',
    'WARNIMG': 'WARNING',
    'DANGEH': 'DANGER',
    'DANGFR': 'DANGER'
}

def correct_ocr_errors(text: str) -> str:
    """Corrige erros comuns de OCR"""
    if not text:
        return text
        
    # Verifica padrões específicos para PUSH SPACE KEY com regex
    # Caso especial para texto que contém apenas variações de PUSH SPACE KEY
    if re.match(r'^\s*(?:KEY\s+)?PUSH\s*(?:G|E)?(?:SPACE|PAC[B]?)\s*KEY\s*(?:PUSH\s*(?:G|E)?(?:SPACE|PAC[B]?)\s*KEY\s*)*$', text, re.IGNORECASE):
        return 'PUSH SPACE KEY'
    
    # Primeiro verifica se o texto contém variações de PUSH SPACE KEY
    if re.search(r'PUSH\s*SPACE\s*KEY', text, re.IGNORECASE) or \
       re.search(r'PUSH[G]?[E]?PAC[B]?KEY', text, re.IGNORECASE) or \
       re.search(r'KEY\s+PUSH\s+SPACE', text, re.IGNORECASE):
        # Normaliza para PUSH SPACE KEY para garantir tradução correta
        text = re.sub(r'PUSH[G]?[E]?PAC[B]?KEY', 'PUSH SPACE KEY', text, flags=re.IGNORECASE)
        text = re.sub(r'PUSH\s+SPACE\s+KEY', 'PUSH SPACE KEY', text, flags=re.IGNORECASE)
        text = re.sub(r'KEY\s+PUSH\s+SPACE', 'PUSH SPACE KEY', text, flags=re.IGNORECASE)
    
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
    
    # Primeiro traduzir frases completas e termos compostos (mais longos)
    sorted_terms = sorted(game_terms.items(), key=lambda x: len(x[0]), reverse=True)
    
    # Primeiro passo: traduzir frases completas e termos compostos
    for term, translation in sorted_terms:
        if len(term.split()) > 1:  # Apenas termos compostos/frases
            pattern = r'\b' + re.escape(term) + r'\b'
            translated = re.sub(pattern, translation, translated, flags=re.IGNORECASE)
    
    # Segundo passo: traduzir termos individuais que não foram traduzidos como parte de frases
    for term, translation in sorted_terms:
        if len(term.split()) == 1:  # Apenas termos individuais
            pattern = r'\b' + re.escape(term) + r'\b'
            translated = re.sub(pattern, translation, translated, flags=re.IGNORECASE)
    
    return translated

def is_mostly_portuguese(text: str) -> bool:
    """Verifica se o texto já está majoritariamente em português"""
    portuguese_words = [
        # Termos básicos de interface
        'jogador', 'jogadores', 'crédito', 'créditos', 'entrar', 'pressione', 
        'iniciar', 'continuar', 'pontuação', 'recorde', 'nível', 'fase', 
        'vidas', 'tempo', 'bônus', 'fim', 'jogo', 'insira', 'moeda', 'livre',
        'qualquer', 'botão', 'sim', 'não', 'sair', 'tentar', 'novamente', 'reiniciar',
        
        # Jogabilidade
        'um', 'dois', 'melhor', 'mundo', 'rodada', 'área', 'zona', 'missão',
        'vida', 'restante', 'temporizador', 'extra', 'poder', 'especial', 'energia',
        'saúde', 'experiência', 'ataque', 'defesa', 'magia', 'velocidade', 'força',
        'agilidade', 'inteligência', 'sabedoria', 'sorte',
        
        # Menus e configurações
        'opções', 'configurações', 'configuração', 'som', 'música', 'volume',
        'controles', 'botão', 'dificuldade', 'fácil', 'normal', 'difícil',
        'especialista', 'idioma', 'salvar', 'carregar', 'salvando', 'carregando',
        'excluir', 'cancelar', 'confirmar', 'selecionar', 'voltar', 'retornar',
        
        # Status e mensagens
        'vitória', 'derrota', 'parabéns', 'obrigado', 'por', 'pausa', 'pausado',
        'pronto', 'vai', 'lutar', 'batalha', 'perfeito', 'ótimo', 'bom', 'ruim',
        'errou', 'falhou', 'concluído', 'completa', 'cumprida', 'completo',
        'aviso', 'perigo', 'erro', 'depuração'
    ]
    
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
        
    # Tratamento especial para PUSH SPACE KEY e variações
    if target_lang in ['pt', 'pt-br']:
        # Caso especial para texto que contém apenas variações de PUSH SPACE KEY
        import re
        
        # Se o texto contém principalmente variações de PUSH SPACE KEY
        if 'PUSHGPACE' in text.upper() or 'PUSHGPACBKEY' in text.upper() or 'PUSHEPACBKEY' in text.upper():
            # Simplifica para uma única instrução
            return 'Pressione a Tecla Espaço'
        
        # Padrões para detectar variações de PUSH SPACE KEY
        push_space_patterns = [
            r'PUSH\s*SPACE\s*KEY', 
            r'PUSH[G]?[E]?PAC[B]?KEY',
            r'KEY\s+PUSH\s+SPACE'
        ]
        
        # Verifica se o texto contém algum dos padrões
        for pattern in push_space_patterns:
            if re.search(pattern, text.upper(), re.IGNORECASE):
                # Substitui todas as ocorrências pelo texto traduzido
                for p in push_space_patterns:
                    text = re.sub(p, 'Pressione a Tecla Espaço', text, flags=re.IGNORECASE)
                return text
                
        # Caso mais simples
        if 'PUSH SPACE' in text.upper():
            return text.upper().replace('PUSH SPACE', 'Pressione Espaço')
        
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
        
        # Etapa 4: Traduzir o restante usando múltiplos tradutores com sistema de fallback
        # Lista de tradutores a tentar, em ordem de preferência
        translators_to_try = ['google', 'bing', 'deepl', 'baidu', 'youdao']
        
        # Tentar cada tradutor em sequência
        final_translated = None
        translation_errors = []
        
        for translator in translators_to_try:
            try:
                print(f"Módulo de Tradução: Tentando tradutor: {translator}")
                final_translated = ts.translate_text(
                    game_translated,
                    translator=translator,
                    from_language=source_lang,
                    to_language=target_lang
                )
                print(f"Módulo de Tradução: Tradução bem-sucedida com {translator}")
                break  # Se a tradução for bem-sucedida, sair do loop
            except Exception as e:
                error_msg = f"Erro com tradutor {translator}: {str(e)}"
                print(f"Módulo de Tradução: {error_msg}")
                translation_errors.append(error_msg)
                continue  # Tentar o próximo tradutor
        
        # Se todos os tradutores falharem, tentar tradução palavra por palavra
        if final_translated is None:
            print(f"Módulo de Tradução: Todos os tradutores falharam. Tentando tradução palavra por palavra...")
            words = game_translated.split()
            translated_words = []
            
            for word in words:
                if len(word) <= 2:  # Palavras muito curtas
                    translated_words.append(word)
                    continue
                    
                # Tentar cada tradutor para cada palavra
                word_translated = None
                for translator in translators_to_try:
                    try:
                        word_translated = ts.translate_text(
                            word,
                            translator=translator,
                            from_language=source_lang,
                            to_language=target_lang
                        )
                        break  # Se a tradução for bem-sucedida, sair do loop
                    except:
                        continue  # Tentar o próximo tradutor
                
                # Se todos os tradutores falharem para esta palavra, manter a palavra original
                if word_translated:
                    translated_words.append(word_translated)
                else:
                    translated_words.append(word)
            
            final_translated = ' '.join(translated_words)
            print(f"Módulo de Tradução: Tradução palavra por palavra concluída")
        
        if not final_translated:  # Se ainda assim falhar
            print(f"Módulo de Tradução: Falha em todos os métodos de tradução. Retornando texto original.")
            final_translated = game_translated  # Retornar o texto com tradução parcial de termos de jogos
            
        print(f"Módulo de Tradução: Texto final traduzido: '{final_translated}'")
        
        return final_translated
        
    except Exception as e:
        print(f"Erro no módulo de tradução: {e}")
        return f"Erro ao traduzir: {e}"
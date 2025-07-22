# service_logic.py

import base64
import io
import time
import cv2
import numpy as np
from datetime import datetime
from fastapi import HTTPException
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Importa as funções dos nossos módulos especializados
from models import RetroArchRequest
from ocr_module import extract_text_from_image, extract_text_with_positions
from translation_module import translate_text
from database import db_manager, calculate_image_hash, initialize_database

def create_translation_image(text: str, width: int = 800, height: int = 200) -> str:
    """
    Cria uma imagem com o texto traduzido e retorna como base64.
    
    Args:
        text: O texto traduzido a ser exibido
        width: Largura da imagem
        height: Altura da imagem
        
    Returns:
        String base64 da imagem PNG
    """
    # Cria uma imagem com fundo semi-transparente
    img = Image.new('RGBA', (width, height), (0, 0, 0, 180))  # Fundo preto semi-transparente
    draw = ImageDraw.Draw(img)
    
    try:
        # Tenta usar uma fonte do sistema
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        try:
            # Fallback para fonte padrão do PIL
            font = ImageFont.load_default()
        except:
            font = None
    
    # Quebra o texto em linhas para caber na imagem
    max_chars_per_line = width // 10  # Aproximadamente
    lines = textwrap.wrap(text, width=max_chars_per_line)
    
    # Limita o número de linhas para caber na altura
    max_lines = height // 20  # Aproximadamente
    if len(lines) > max_lines:
        lines = lines[:max_lines-1]
        lines.append("...")
    
    # Desenha o texto
    y_offset = 10
    for line in lines:
        draw.text((10, y_offset), line, fill=(255, 255, 255, 255), font=font)  # Texto branco
        y_offset += 20
    
    # Salva a imagem overlay no diretório para debug/comparação
    overlay_filename = "overlay_translation_debug.png"
    img.save(overlay_filename)
    print(f"Overlay salvo como: {overlay_filename}")
    
    # Converte para base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_base64

def save_debug_images(original_image_data: bytes, overlay_base64: str, original_width: int, original_height: int):
    """Salva imagens para debug e comparação visual"""
    try:
        # Salva imagem original em um arquivo temporário para processamento
        with open("temp_received_image.png", "wb") as f:
            f.write(original_image_data)
        
        # Abre a imagem original para processamento
        original_img = Image.open(io.BytesIO(original_image_data))
        
        # Salva a imagem corrigida (não a original) como debug_original.png
        # Esta é a imagem que será usada como base para o overlay
        corrected_img = original_img.copy()
        corrected_img.save("temp_corrected_image.png")
        corrected_img.save("debug_original.png")
        
        # Decodifica o overlay
        overlay_data = base64.b64decode(overlay_base64)
        overlay_img = Image.open(io.BytesIO(overlay_data))
        
        # Combina as imagens (corrigida + overlay)
        combined = corrected_img.copy()
        combined.paste(overlay_img, (0, 0), overlay_img)  # overlay_img como máscara de transparência
        
        # Salva versão combinada
        combined.save("debug_combined_result.png")
        print("Imagens de debug salvas: debug_original.png (corrigida), overlay_translation_debug.png, debug_combined_result.png")
        
    except Exception as e:
        print(f"Erro ao salvar imagens de debug: {e}")

def create_positioned_translation_image(detections_with_translations: list, original_width: int = 800, original_height: int = 600) -> str:
    """
    Cria uma imagem overlay com traduções posicionadas individualmente.
    
    Args:
        detections_with_translations: Lista de dicionários com 'text', 'translation', 'bbox', 'confidence'
        original_width: Largura da imagem original
        original_height: Altura da imagem original
        
    Returns:
        String base64 da imagem PNG overlay
    """
    # Cria uma imagem transparente do tamanho original
    img = Image.new('RGBA', (original_width, original_height), (0, 0, 0, 0))  # Completamente transparente
    draw = ImageDraw.Draw(img)
    
    try:
        # Tenta usar uma fonte do sistema
        font_small = ImageFont.truetype("arial.ttf", 14)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_large = ImageFont.truetype("arial.ttf", 18)
        font_xlarge = ImageFont.truetype("arial.ttf", 20)  # Nova fonte para textos agrupados maiores
    except:
        try:
            # Fallback para fonte padrão do PIL
            font_small = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_large = ImageFont.load_default()
            font_xlarge = ImageFont.load_default()
        except:
            font_small = font_medium = font_large = font_xlarge = None
    
    print(f"Criando overlay com {len(detections_with_translations)} traduções posicionadas")
    
    for i, detection in enumerate(detections_with_translations):
        text = detection['text']
        translation = detection['translation']
        bbox = detection['bbox']
        confidence = detection['confidence']
        is_grouped = detection.get('is_grouped', False)
        group_size = detection.get('group_size', 1)
        
        # Calcula o centro da bbox original
        # bbox é uma lista de 4 pontos: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        x_coords = [point[0] for point in bbox]
        y_coords = [point[1] for point in bbox]
        
        # Calcula posição central e dimensões
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        bbox_width = max_x - min_x
        bbox_height = max_y - min_y
        
        # Escolhe fonte baseada no tamanho do texto original e se é um grupo
        if is_grouped and group_size > 2:
            # Para grupos maiores, usa fonte maior para melhor legibilidade
            font = font_xlarge
        elif bbox_height > 25 or (is_grouped and group_size > 1):
            font = font_large
        elif bbox_height > 15:
            font = font_medium
        else:
            font = font_small
        
        # Ajusta o texto para quebrar linhas se for muito longo
        # Especialmente importante para textos agrupados
        max_chars_per_line = 30 if is_grouped else 20
        if len(translation) > max_chars_per_line:
            # Quebra o texto em linhas para melhor legibilidade
            import textwrap
            wrapped_text = textwrap.fill(translation, width=max_chars_per_line)
            translation = wrapped_text
        
        # Calcula dimensões do texto traduzido
        if font:
            text_bbox = draw.textbbox((0, 0), translation, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        else:
            text_width = len(translation) * 8  # Estimativa
            text_height = 12 * (1 + translation.count('\n'))  # Ajusta para múltiplas linhas
        
        # Posiciona o texto traduzido
        text_x = max(0, min(center_x - text_width // 2, original_width - text_width))
        text_y = max(0, min(center_y - text_height // 2, original_height - text_height))
        
        # Desenha fundo semi-transparente para o texto
        # Aumenta o padding para textos agrupados
        padding = 4 if is_grouped else 2
        bg_x1 = text_x - padding
        bg_y1 = text_y - padding
        bg_x2 = text_x + text_width + padding
        bg_y2 = text_y + text_height + padding
        
        # Ajusta a opacidade do fundo com base no tamanho do grupo
        # Grupos maiores têm fundo mais opaco para melhor legibilidade
        bg_opacity = min(200, 180 + (group_size * 5)) if is_grouped else 180
        draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=(0, 0, 0, bg_opacity))  # Fundo preto semi-transparente
        
        # Desenha o texto traduzido
        draw.text((text_x, text_y), translation, fill=(255, 255, 255, 255), font=font)  # Texto branco
        
        group_info = f" (grupo de {group_size} textos)" if is_grouped else ""
        print(f"Posicionado '{translation}'{group_info} em ({text_x}, {text_y}) - original: '{text}' (confiança: {confidence:.2f})")
    
    # Converte para base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_base64

async def process_ai_request(request: RetroArchRequest) -> dict:
    """
    Orquestra o processo de tradução: recebe os bytes da imagem, extrai o texto, 
    traduz o texto e formata a resposta.

    Args:
        request: Um objeto RetroArchRequest contendo os dados da requisição.

    Returns:
        Um dicionário contendo os dados da resposta para o RetroArch.
    """
    try:
        # Inicializa o temporizador para medir o tempo de processamento
        start_time = time.time()
        
        # Garante que o banco de dados está inicializado
        if not db_manager.connected:
            initialize_database()
        
        print("Lógica de Serviço: Iniciando processamento da requisição.")
        
        # Flags para rastrear hits de cache
        ocr_cache_hit = False
        translation_cache_hits = 0
        
        # 1. Decodificar a imagem de Base64 para bytes
        try:
            image_bytes = base64.b64decode(request.image)
        except (base64.binascii.Error, TypeError) as e:
            print(f"Erro de decodificação Base64: {e}")
            raise HTTPException(status_code=400, detail="Imagem em Base64 inválida.")

        source_lang = request.lang_source
        target_lang = request.lang_target

        print(f"Lógica de Serviço: Recebidos {len(image_bytes)} bytes de imagem após decodificação.")
        
        # Decodifica a imagem para obter dimensões originais
        import cv2
        import numpy as np
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        original_height, original_width = img_cv.shape[:2]
        print(f"Lógica de Serviço: Dimensões da imagem original: {original_width}x{original_height}")
        
        # Calcula o hash da imagem para verificar no cache
        image_hash = calculate_image_hash(image_bytes)
        print(f"Lógica de Serviço: Hash da imagem calculado: {image_hash[:10]}...")
        
        # 2. Verificar se já temos resultados de OCR para esta imagem no cache
        cached_ocr_result = db_manager.get_ocr_result(image_hash, source_lang)
        
        if cached_ocr_result:
            print(f"Lógica de Serviço: Resultados de OCR encontrados no cache!")
            detections = cached_ocr_result['text_results']
            ocr_cache_hit = True
        else:
            # Extrair textos individuais com posições usando o módulo de OCR
            print("Lógica de Serviço: Extraindo textos com posições individuais...")
            detections = await extract_text_with_positions(image_bytes, lang_source=source_lang)
            
            # Salva os resultados de OCR no cache, incluindo a imagem original e metadados
            if detections:
                # Calcula a confiança média dos resultados de OCR
                avg_confidence = sum(d['confidence'] for d in detections) / len(detections) if detections else 0
                
                # Prepara os metadados da imagem
                image_metadata = {
                    'width': original_width,
                    'height': original_height,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'format': request.format,
                    'timestamp': datetime.now().isoformat(),
                    'coords': request.coords,
                    'viewport': request.viewport,
                    'label': request.label,
                    'state': request.state
                }
                
                # Salva os resultados de OCR, a imagem original e os metadados
                db_manager.save_ocr_result(
                    image_hash, 
                    source_lang, 
                    detections, 
                    avg_confidence, 
                    original_image=image_bytes, 
                    image_metadata=image_metadata
                )
        
        if not detections:
            print("Lógica de Serviço: Nenhum texto foi detectado. Retornando resposta vazia.")
            # Registra a requisição nas estatísticas
            processing_time = time.time() - start_time
            db_manager.record_request_processing(ocr_hit=ocr_cache_hit, processing_time=processing_time)
            return {"image": ""} # Retorna vazio se não houver texto

        # 3. Traduzir cada texto individualmente
        print(f"Lógica de Serviço: Traduzindo {len(detections)} textos de '{source_lang}' para '{target_lang}'.")
        detections_with_translations = []
        
        for i, detection in enumerate(detections):
            original_text = detection['text']
            is_grouped = detection.get('is_grouped', False)
            group_size = detection.get('group_size', 1)
            
            group_info = f" (grupo de {group_size} textos)" if is_grouped else ""
            print(f"Lógica de Serviço: Traduzindo texto {i+1}/{len(detections)}{group_info}: '{original_text}'")
            
            # Verifica se já temos esta tradução no cache
            cached_translation = db_manager.get_translation(original_text, source_lang, target_lang)
            
            if cached_translation:
                print(f"Lógica de Serviço: Tradução encontrada no cache!")
                translated_text = cached_translation['translated_text']
                translation_cache_hits += 1
            else:
                # Traduz o texto usando o módulo de tradução
                translated_text = await translate_text(
                    text=original_text,
                    source_lang=source_lang,
                    target_lang=target_lang
                )
                
                # Salva a tradução no cache
                # Estima a confiança como a confiança do OCR
                confidence = detection.get('confidence', 0.8)
                db_manager.save_translation(
                    original_text, 
                    source_lang, 
                    target_lang, 
                    translated_text, 
                    translator_used="multiple", 
                    confidence=confidence
                )
            
            # Garante que todos os valores sejam tipos Python padrão para evitar problemas de serialização JSON
            detections_with_translations.append({
                'text': original_text,
                'translation': translated_text,
                'bbox': [[int(point[0]), int(point[1])] for point in detection['bbox']],
                'confidence': float(detection['confidence']),
                'is_grouped': bool(is_grouped),
                'group_size': int(group_size)
            })
            
            print(f"Lógica de Serviço: '{original_text}' -> '{translated_text}'")
            if is_grouped:
                print(f"Lógica de Serviço: Texto agrupado traduzido com sucesso (grupo de {group_size} textos).")

        # 4. Criar imagem overlay com traduções posicionadas
        print(f"Lógica de Serviço: Criando overlay com traduções posicionadas.")
        
        translation_image_b64 = create_positioned_translation_image(
            detections_with_translations, 
            original_width, 
            original_height
        )
        
        # Salva imagens de debug para comparação
        save_debug_images(image_bytes, translation_image_b64, original_width, original_height)
        
        # Calcula o tempo total de processamento
        processing_time = time.time() - start_time
        
        # Registra a requisição nas estatísticas
        db_manager.record_request_processing(
            ocr_hit=ocr_cache_hit, 
            translation_hit=(translation_cache_hits > 0), 
            processing_time=processing_time
        )
        
        # Log de desempenho
        cache_info = f"Cache: OCR {'✓' if ocr_cache_hit else '✗'}, Traduções: {translation_cache_hits}/{len(detections)}"
        print(f"Lógica de Serviço: Processamento concluído em {processing_time:.2f}s. {cache_info}")
        
        # 5. Formatar a resposta para o RetroArch conforme documentação oficial
        # O RetroArch espera um campo 'image' com a representação base64 da imagem
        response_data = {
            "image": translation_image_b64
        }
        
        print(f"Lógica de Serviço: Processamento concluído. Overlay de tradução criado com {len(translation_image_b64)} caracteres base64.")
        return response_data

    except Exception as e:
        print(f"Erro na lógica de serviço: {e}")
        # Lança uma exceção que será capturada pelo main.py para retornar um erro 500.
        raise HTTPException(status_code=500, detail=f"Erro interno no processamento: {e}")
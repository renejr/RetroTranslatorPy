# improved_ocr_module.py

import easyocr
import cv2
import numpy as np
import os
import time
from typing import List, Dict, Any, Tuple
import math

# Cache para os modelos EasyOCR
reader_cache = {}

def get_reader(lang_list):
    """
    Obtém um leitor EasyOCR para os idiomas especificados, usando cache para evitar recarregar modelos.
    
    Args:
        lang_list: Lista de códigos de idioma ou string única com código de idioma.
        
    Returns:
        Um objeto Reader do EasyOCR.
    """
    # Converte string única para lista
    if isinstance(lang_list, str):
        lang_list = [lang_list]
    
    # Adiciona inglês como fallback se não estiver na lista
    if 'en' not in lang_list:
        lang_list.append('en')
    
    # Cria uma chave de cache baseada nos idiomas
    cache_key = ",".join(sorted(lang_list))
    
    # Verifica se já temos este leitor em cache
    if cache_key in reader_cache:
        print(f"Usando leitor em cache para idiomas: {lang_list}")
        return reader_cache[cache_key]
    
    # Cria um novo leitor
    print(f"Criando novo leitor para idiomas: {lang_list}")
    try:
        # Tenta usar GPU se disponível
        reader = easyocr.Reader(lang_list, gpu=True)
        print("Leitor EasyOCR criado com suporte a GPU")
    except Exception as e:
        print(f"Erro ao criar leitor com GPU: {e}. Tentando sem GPU...")
        reader = easyocr.Reader(lang_list, gpu=False)
        print("Leitor EasyOCR criado sem suporte a GPU")
    
    # Armazena no cache
    reader_cache[cache_key] = reader
    return reader

def group_text_detections(detections: List[Dict[str, Any]], horizontal_threshold: float = 50, vertical_threshold: float = 25) -> List[Dict[str, Any]]:
    """
    Agrupa detecções de texto que estão próximas espacialmente.
    
    Args:
        detections: Lista de detecções, cada uma com 'text', 'bbox' e 'confidence'.
        horizontal_threshold: Distância horizontal máxima para agrupar textos.
        vertical_threshold: Distância vertical máxima para agrupar textos.
        
    Returns:
        Lista de detecções agrupadas.
    """
    if not detections:
        return []
    
    # Cria uma cópia para não modificar a original
    detections = [d.copy() for d in detections]
    
    # Ordena as detecções por coordenada Y (de cima para baixo)
    detections.sort(key=lambda d: min(point[1] for point in d['bbox']))
    
    # Lista para armazenar os grupos
    grouped_detections = []
    processed = [False] * len(detections)
    
    for i in range(len(detections)):
        if processed[i]:
            continue
        
        # Marca esta detecção como processada
        processed[i] = True
        
        # Inicia um novo grupo com esta detecção
        current_group = [detections[i]]
        current_text = detections[i]['text']
        current_confidence = detections[i]['confidence']
        
        # Coordenadas da bounding box atual
        current_bbox = detections[i]['bbox']
        min_x = min(point[0] for point in current_bbox)
        max_x = max(point[0] for point in current_bbox)
        min_y = min(point[1] for point in current_bbox)
        max_y = max(point[1] for point in current_bbox)
        
        # Procura por detecções próximas para agrupar
        changed = True
        while changed:
            changed = False
            for j in range(len(detections)):
                if processed[j]:
                    continue
                
                # Coordenadas da bounding box candidata
                candidate_bbox = detections[j]['bbox']
                candidate_min_x = min(point[0] for point in candidate_bbox)
                candidate_max_x = max(point[0] for point in candidate_bbox)
                candidate_min_y = min(point[1] for point in candidate_bbox)
                candidate_max_y = max(point[1] for point in candidate_bbox)
                
                # Verifica proximidade horizontal (para mesma linha)
                horizontal_close = (
                    (candidate_min_x <= max_x + horizontal_threshold and candidate_max_x >= min_x - horizontal_threshold) and
                    abs(candidate_min_y - min_y) < vertical_threshold
                )
                
                # Verifica proximidade vertical (para linhas consecutivas)
                vertical_close = (
                    (candidate_min_y <= max_y + vertical_threshold and candidate_max_y >= min_y - vertical_threshold) and
                    abs(candidate_min_x - min_x) < horizontal_threshold * 3  # Mais tolerante horizontalmente para linhas
                )
                
                if horizontal_close or vertical_close:
                    # Adiciona ao grupo atual
                    current_group.append(detections[j])
                    processed[j] = True
                    changed = True
                    
                    # Atualiza o texto do grupo
                    if horizontal_close:
                        # Para texto na mesma linha, adiciona espaço
                        if candidate_min_x > max_x:
                            current_text += " " + detections[j]['text']
                        else:
                            current_text = detections[j]['text'] + " " + current_text
                    else:
                        # Para texto em linhas diferentes, adiciona quebra de linha
                        if candidate_min_y > max_y:
                            current_text += "\n" + detections[j]['text']
                        else:
                            current_text = detections[j]['text'] + "\n" + current_text
                    
                    # Atualiza a confiança (média)
                    current_confidence = (current_confidence * len(current_group) + detections[j]['confidence']) / (len(current_group) + 1)
                    
                    # Atualiza as coordenadas da bounding box
                    min_x = min(min_x, candidate_min_x)
                    max_x = max(max_x, candidate_max_x)
                    min_y = min(min_y, candidate_min_y)
                    max_y = max(max_y, candidate_max_y)
        
        # Cria uma nova bounding box para o grupo
        grouped_bbox = [
            [min_x, min_y],  # top-left
            [max_x, min_y],  # top-right
            [max_x, max_y],  # bottom-right
            [min_x, max_y]   # bottom-left
        ]
        
        # Adiciona o grupo à lista de resultados
        is_grouped = len(current_group) > 1
        grouped_detections.append({
            'text': current_text.strip(),
            'bbox': grouped_bbox,
            'confidence': current_confidence,
            'is_grouped': is_grouped,
            'group_size': len(current_group)
        })
    
    return grouped_detections

def apply_adaptive_thresholding(image):
    """
    Aplica threshold adaptativo para melhorar o contraste e a legibilidade do texto.
    
    Args:
        image: Imagem em escala de cinza.
        
    Returns:
        Imagem com threshold adaptativo aplicado.
    """
    # Aplica threshold adaptativo
    thresh = cv2.adaptiveThreshold(
        image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh

def apply_otsu_thresholding(image):
    """
    Aplica threshold de Otsu para binarização automática.
    
    Args:
        image: Imagem em escala de cinza.
        
    Returns:
        Imagem binarizada usando o método de Otsu.
    """
    # Aplica threshold de Otsu
    _, thresh = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    
    return thresh

def apply_clahe(image):
    """
    Aplica CLAHE (Contrast Limited Adaptive Histogram Equalization) 
    para melhorar o contraste local.
    
    Args:
        image: Imagem em escala de cinza.
        
    Returns:
        Imagem com contraste melhorado.
    """
    # Cria o objeto CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
    # Aplica CLAHE
    equalized = clahe.apply(image)
    
    return equalized

def denoise_image(image):
    """
    Remove ruído da imagem usando filtros de desfoque.
    
    Args:
        image: Imagem em escala de cinza.
        
    Returns:
        Imagem com ruído reduzido.
    """
    # Aplica filtro de desfoque bilateral para preservar bordas
    denoised = cv2.bilateralFilter(image, 9, 75, 75)
    
    return denoised

def sharpen_image(image):
    """
    Aplica filtro de nitidez para realçar bordas e detalhes.
    
    Args:
        image: Imagem em escala de cinza.
        
    Returns:
        Imagem com nitidez aumentada.
    """
    # Kernel para nitidez
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    
    # Aplica o filtro de nitidez
    sharpened = cv2.filter2D(image, -1, kernel)
    
    return sharpened

def detect_and_correct_skew(image, delta=1, limit=5):
    """
    Detecta e corrige a inclinação da imagem.
    
    Args:
        image: Imagem em escala de cinza.
        delta: Incremento do ângulo em graus.
        limit: Limite máximo de ângulo em graus.
        
    Returns:
        Imagem com inclinação corrigida.
    """
    # Detecta bordas
    edges = cv2.Canny(image, 50, 150, apertureSize=3)
    
    # Detecta linhas usando a transformada de Hough
    lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
    
    if lines is None:
        return image
    
    # Calcula o ângulo médio das linhas
    angles = []
    for line in lines:
        rho, theta = line[0]
        # Converte para graus e normaliza
        angle = np.degrees(theta) % 180
        # Ajusta para encontrar o ângulo de inclinação
        if angle > 45 and angle < 135:
            angle = angle - 90
        angles.append(angle)
    
    # Filtra outliers e calcula a média
    angles = np.array(angles)
    angles = angles[np.abs(angles) <= limit]
    
    if len(angles) == 0:
        return image
    
    median_angle = np.median(angles)
    
    # Corrige a inclinação se necessário
    if abs(median_angle) > 0.5:  # Ignora inclinações muito pequenas
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
    
    return image

def create_preprocessed_variants(image):
    """
    Cria variantes pré-processadas da imagem para melhorar o OCR.
    
    Args:
        image: Imagem original em formato BGR.
        
    Returns:
        Lista de imagens pré-processadas.
    """
    variants = []
    
    # Adiciona a imagem original
    variants.append(("original", image))
    
    # Converte para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variants.append(("gray", gray))
    
    # Aplica desfoque gaussiano para reduzir ruído
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    variants.append(("blurred", blurred))
    
    # Aplica denoising bilateral
    denoised = denoise_image(gray)
    variants.append(("denoised", denoised))
    
    # Aplica CLAHE para melhorar contraste
    clahe = apply_clahe(gray)
    variants.append(("clahe", clahe))
    
    # Aplica nitidez
    sharpened = sharpen_image(gray)
    variants.append(("sharpened", sharpened))
    
    # Aplica threshold adaptativo
    adaptive_thresh = apply_adaptive_thresholding(blurred)
    variants.append(("adaptive_thresh", adaptive_thresh))
    
    # Aplica threshold de Otsu
    otsu_thresh = apply_otsu_thresholding(blurred)
    variants.append(("otsu_thresh", otsu_thresh))
    
    # Combina CLAHE com threshold adaptativo
    clahe_thresh = apply_adaptive_thresholding(clahe)
    variants.append(("clahe_thresh", clahe_thresh))
    
    # Combina nitidez com threshold adaptativo
    sharp_thresh = apply_adaptive_thresholding(sharpened)
    variants.append(("sharp_thresh", sharp_thresh))
    
    # Detecta e corrige inclinação
    deskewed = detect_and_correct_skew(gray)
    variants.append(("deskewed", deskewed))
    
    # Aplica threshold adaptativo na imagem sem inclinação
    deskewed_thresh = apply_adaptive_thresholding(deskewed)
    variants.append(("deskewed_thresh", deskewed_thresh))
    
    return variants

async def extract_text_with_positions(image_bytes: bytes, lang_source: str) -> list:
    """
    Recebe os bytes de uma imagem, realiza o OCR para um idioma específico e retorna
    uma lista de detecções com texto, coordenadas e confiança.

    Args:
        image_bytes: A imagem como um objeto de bytes.
        lang_source: O código do idioma de origem (ex: 'en', 'ja') para o OCR.

    Returns:
        Uma lista de dicionários, cada um contendo 'text', 'bbox' e 'confidence'.
    """
    try:
        print(f"Módulo OCR Melhorado: Recebeu imagem para extração de texto com posições. Idioma: {lang_source}")
        
        # Decodifica os bytes da imagem para um formato que o OpenCV/EasyOCR entenda.
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img_cv is None:
            print("Módulo OCR Melhorado: Erro ao decodificar a imagem. A imagem pode estar corrompida ou em um formato inválido.")
            return []

        # Log das dimensões da imagem para depuração
        height, width, channels = img_cv.shape
        print(f"Módulo OCR Melhorado: Dimensões da imagem - Largura: {width}px, Altura: {height}px, Canais: {channels}")
        
        # Salva a imagem original para análise visual
        temp_image_path = "temp_received_image.png"
        cv2.imwrite(temp_image_path, img_cv)
        print(f"Módulo OCR Melhorado: Imagem original salva em: {os.path.abspath(temp_image_path)}")
        
        # Função para testar diferentes rotações e encontrar a melhor orientação
        def test_rotation_and_get_best_image(image):
            rotations = {
                0: image,
                90: cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE),
                180: cv2.rotate(image, cv2.ROTATE_180),
                270: cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            }
            
            best_rotation = 0
            max_text_count = 0
            best_image = image
            
            print("Módulo OCR Melhorado: Testando diferentes rotações para encontrar a melhor orientação...")
            
            # Obtém o leitor de OCR primeiro para usar na detecção de rotação
            ocr_reader = get_reader(lang_source)
            
            for angle, rotated_img in rotations.items():
                # Teste rápido de OCR para cada rotação
                try:
                    quick_result = ocr_reader.readtext(rotated_img, detail=1)
                    text_count = len([r for r in quick_result if r[2] > 0.3])  # Conta textos com boa confiança
                    total_chars = sum(len(r[1].strip()) for r in quick_result if r[2] > 0.3)
                    
                    print(f"Módulo OCR Melhorado: Rotação {angle}° - {text_count} detecções, {total_chars} caracteres")
                    
                    # Prioriza rotações com mais caracteres detectados
                    if total_chars > max_text_count:
                        max_text_count = total_chars
                        best_rotation = angle
                        best_image = rotated_img
                        
                except Exception as e:
                    print(f"Módulo OCR Melhorado: Erro ao testar rotação {angle}°: {e}")
            
            print(f"Módulo OCR Melhorado: Melhor orientação encontrada: {best_rotation}° ({max_text_count} caracteres)")
            return best_image, best_rotation
        
        # Obtém o leitor de OCR
        ocr_reader = get_reader(lang_source)
        
        # Encontra a melhor rotação
        img_corrected, best_angle = test_rotation_and_get_best_image(img_cv)
        
        # Salva a imagem corrigida
        corrected_image_path = "temp_corrected_image.png"
        cv2.imwrite(corrected_image_path, img_corrected)
        print(f"Módulo OCR Melhorado: Imagem corrigida (rotação {best_angle}°) salva em: {os.path.abspath(corrected_image_path)}")
        
        # Cria variantes pré-processadas da imagem
        print("Módulo OCR Melhorado: Criando variantes pré-processadas da imagem...")
        preprocessed_variants = create_preprocessed_variants(img_corrected)
        
        # Salva as variantes pré-processadas para análise visual
        for variant_name, variant_img in preprocessed_variants:
            variant_path = f"temp_{variant_name}_image.png"
            cv2.imwrite(variant_path, variant_img)
            print(f"Módulo OCR Melhorado: Variante '{variant_name}' salva em: {os.path.abspath(variant_path)}")
        
        # Lista para armazenar todos os resultados de OCR
        all_detections = []
        
        # Executa OCR em cada variante pré-processada
        print("Módulo OCR Melhorado: Executando OCR em todas as variantes...")
        for variant_name, variant_img in preprocessed_variants:
            print(f"Módulo OCR Melhorado: Processando variante '{variant_name}'...")
            try:
                # Ajusta parâmetros de OCR com base no tipo de variante
                if variant_name in ["original", "gray", "blurred", "denoised", "clahe", "sharpened", "deskewed"]:
                    # Para imagens em tons de cinza ou coloridas
                    text_list_detailed = ocr_reader.readtext(variant_img, detail=1)
                else:
                    # Para imagens binarizadas, ajusta parâmetros para melhor detecção
                    text_list_detailed = ocr_reader.readtext(variant_img, detail=1, contrast_ths=0.1, adjust_contrast=0.5)
                
                print(f"Módulo OCR Melhorado: Variante '{variant_name}' - {len(text_list_detailed)} detecções")
                
                # Adiciona as detecções à lista geral
                for detection in text_list_detailed:
                    bbox, text, confidence = detection
                    if confidence > 0.2 and text.strip():  # Filtra por confiança e texto não vazio
                        print(f"Módulo OCR Melhorado: '{variant_name}' - '{text}' (confiança: {confidence:.2f})")
                        all_detections.append({
                            'text': text,
                            'bbox': bbox,
                            'confidence': confidence,
                            'variant': variant_name
                        })
            except Exception as e:
                print(f"Módulo OCR Melhorado: Erro ao processar variante '{variant_name}': {e}")
        
        # Filtra detecções por confiança mínima
        filtered_detections = [d for d in all_detections if d['confidence'] > 0.3]
        print(f"Módulo OCR Melhorado: Total de detecções após filtragem: {len(filtered_detections)}")
        
        # Remove duplicatas (mesmo texto em posições muito próximas)
        unique_detections = []
        for detection in filtered_detections:
            # Verifica se já temos uma detecção similar
            is_duplicate = False
            for unique in unique_detections:
                # Calcula sobreposição de bounding boxes
                bbox1 = detection['bbox']
                bbox2 = unique['bbox']
                
                # Calcula centros das bounding boxes
                center1_x = sum(p[0] for p in bbox1) / 4
                center1_y = sum(p[1] for p in bbox1) / 4
                center2_x = sum(p[0] for p in bbox2) / 4
                center2_y = sum(p[1] for p in bbox2) / 4
                
                # Calcula distância entre centros
                distance = math.sqrt((center1_x - center2_x)**2 + (center1_y - center2_y)**2)
                
                # Se os textos são similares e estão próximos, considera duplicata
                if distance < 20 and (detection['text'].lower() == unique['text'].lower() or 
                                     detection['text'] in unique['text'] or 
                                     unique['text'] in detection['text']):
                    is_duplicate = True
                    # Mantém a detecção com maior confiança
                    if detection['confidence'] > unique['confidence']:
                        unique['text'] = detection['text']
                        unique['confidence'] = detection['confidence']
                        unique['variant'] = detection['variant']
                    break
            
            if not is_duplicate:
                unique_detections.append(detection)
        
        print(f"Módulo OCR Melhorado: Total de detecções únicas: {len(unique_detections)}")
        
        # Agrupa detecções próximas
        grouped_detections = group_text_detections(unique_detections)
        print(f"Módulo OCR Melhorado: Total de detecções após agrupamento: {len(grouped_detections)}")
        
        # Exibe as detecções agrupadas
        for i, detection in enumerate(grouped_detections):
            is_grouped = detection.get('is_grouped', False)
            group_size = detection.get('group_size', 1)
            group_info = f" (grupo de {group_size} textos)" if is_grouped else ""
            print(f"Módulo OCR Melhorado: Detecção {i+1}{group_info}: '{detection['text']}' (confiança: {detection['confidence']:.2f})")
        
        return grouped_detections
        
    except Exception as e:
        print(f"Erro no módulo OCR Melhorado (com posições): {e}")
        return []

async def extract_text_from_image(image_bytes: bytes, lang_source: str) -> str:
    """
    Recebe os bytes de uma imagem, realiza o OCR para um idioma específico e retorna o texto.

    Args:
        image_bytes: A imagem como um objeto de bytes.
        lang_source: O código do idioma de origem (ex: 'en', 'ja') para o OCR.

    Returns:
        O texto encontrado na imagem, concatenado em uma única string.
    """
    try:
        # Usa a função extract_text_with_positions e extrai apenas o texto
        detections = await extract_text_with_positions(image_bytes, lang_source)
        
        # Junta os textos de todas as detecções
        extracted_text = " ".join(d['text'] for d in detections)
        
        if extracted_text:
            print(f"Módulo OCR Melhorado: Texto extraído: '{extracted_text}'")
        else:
            print("Módulo OCR Melhorado: Nenhum texto foi encontrado na imagem.")

        return extracted_text
        
    except Exception as e:
        print(f"Erro no módulo OCR Melhorado: {e}")
        return ""
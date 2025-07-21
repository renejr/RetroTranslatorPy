# ocr_module.py

# ocr_module.py

import easyocr
import cv2
import numpy as np

# --- GERENCIAMENTO DO MODELO ---
# Dicionário para armazenar instâncias do leitor de OCR para diferentes idiomas.
# Isso evita recarregar modelos desnecessariamente, agindo como um cache.
readers = {}

def get_reader(lang_code: str):
    """
    Retorna uma instância do leitor EasyOCR para o idioma especificado.
    Se um leitor para o idioma ainda não existir, ele será criado e armazenado em cache.
    """
    # Se o idioma padrão for solicitado, mapeia para o código correto que o EasyOCR espera.
    if lang_code.lower() == 'default':
        lang_code = 'en' # O RetroArch usa 'Default' para inglês.

    if lang_code not in readers:
        print(f"Modelo de OCR para o idioma '{lang_code}' não encontrado no cache. Carregando...")
        # Cria uma nova instância do Reader para o idioma solicitado e a armazena.
        # Usamos gpu=True para aproveitar a aceleração por hardware, se disponível.
        readers[lang_code] = easyocr.Reader([lang_code], gpu=True)
        print(f"Modelo de OCR para '{lang_code}' carregado e adicionado ao cache.")
    else:
        print(f"Usando modelo de OCR para '{lang_code}' do cache.")
        
    return readers[lang_code]

async def extract_text_with_positions(image_bytes: bytes, lang_source: str) -> list:
    """
    Recebe os bytes de uma imagem, realiza o OCR para um idioma específico e retorna
    uma lista de detecções com texto, coordenadas e confiança.

    Args:
        image_bytes: A imagem como um objeto de bytes.
        lang_source: O código do idioma de origem (ex: 'en', 'ja') para o OCR.

    Returns:
        Lista de dicionários com 'text', 'bbox', 'confidence' para cada detecção.
    """
    try:
        print(f"Módulo OCR: Recebeu imagem para extração de texto com posições - idioma: {lang_source}")
        
        # Decodifica os bytes da imagem para um formato que o OpenCV/EasyOCR entenda.
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img_cv is None:
            print("Módulo OCR: Erro ao decodificar a imagem. A imagem pode estar corrompida ou em um formato inválido.")
            return []

        # Log das dimensões da imagem para depuração
        height, width, channels = img_cv.shape
        print(f"Módulo OCR: Dimensões da imagem - Largura: {width}px, Altura: {height}px, Canais: {channels}")
        
        # Salva a imagem temporariamente para análise visual (opcional)
        import os
        temp_image_path = "temp_received_image.png"
        cv2.imwrite(temp_image_path, img_cv)
        print(f"Módulo OCR: Imagem salva temporariamente em: {os.path.abspath(temp_image_path)}")
        
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
            
            print("Módulo OCR: Testando diferentes rotações para encontrar a melhor orientação...")
            
            for angle, rotated_img in rotations.items():
                # Teste rápido de OCR para cada rotação
                try:
                    quick_result = ocr_reader.readtext(rotated_img, detail=1)
                    text_count = len([r for r in quick_result if r[2] > 0.3])  # Conta textos com boa confiança
                    total_chars = sum(len(r[1].strip()) for r in quick_result if r[2] > 0.3)
                    
                    print(f"Módulo OCR: Rotação {angle}° - {text_count} detecções, {total_chars} caracteres")
                    
                    # Prioriza rotações com mais caracteres detectados
                    if total_chars > max_text_count:
                        max_text_count = total_chars
                        best_rotation = angle
                        best_image = rotated_img
                        
                except Exception as e:
                    print(f"Módulo OCR: Erro ao testar rotação {angle}°: {e}")
            
            print(f"Módulo OCR: Melhor orientação encontrada: {best_rotation}° ({max_text_count} caracteres)")
            return best_image, best_rotation
        
        # Obtém o leitor de OCR primeiro para usar na detecção de rotação
        ocr_reader = get_reader(lang_source)
        
        # Encontra a melhor rotação
        img_corrected, best_angle = test_rotation_and_get_best_image(img_cv)
        
        # Salva a imagem corrigida
        corrected_image_path = "temp_corrected_image.png"
        cv2.imwrite(corrected_image_path, img_corrected)
        print(f"Módulo OCR: Imagem corrigida (rotação {best_angle}°) salva em: {os.path.abspath(corrected_image_path)}")
        
        # Realiza OCR na imagem corrigida
        detections = ocr_reader.readtext(img_corrected, detail=1)
        
        # Processa as detecções e filtra por confiança
        processed_detections = []
        for detection in detections:
            bbox, text, confidence = detection
            if confidence > 0.3 and text.strip():  # Filtro de confiança
                clean_text = text.strip().replace('\n', ' ').replace('\t', ' ')
                if len(clean_text) > 0:
                    processed_detections.append({
                        'text': clean_text,
                        'bbox': bbox,
                        'confidence': confidence
                    })
                    print(f"Módulo OCR: Detectado '{clean_text}' (confiança: {confidence:.2f})")
        
        print(f"Módulo OCR: Total de detecções válidas: {len(processed_detections)}")
        return processed_detections
        
    except Exception as e:
        print(f"Erro no módulo OCR (com posições): {e}")
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
        print(f"Módulo OCR: Recebeu imagem para extração de texto com idioma de origem: {lang_source}")
        
        # Decodifica os bytes da imagem para um formato que o OpenCV/EasyOCR entenda.
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img_cv is None:
            print("Módulo OCR: Erro ao decodificar a imagem. A imagem pode estar corrompida ou em um formato inválido.")
            return ""

        # Log das dimensões da imagem para depuração
        height, width, channels = img_cv.shape
        print(f"Módulo OCR: Dimensões da imagem - Largura: {width}px, Altura: {height}px, Canais: {channels}")
        
        # Salva a imagem temporariamente para análise visual (opcional)
        import os
        temp_image_path = "temp_received_image.png"
        cv2.imwrite(temp_image_path, img_cv)
        print(f"Módulo OCR: Imagem salva temporariamente em: {os.path.abspath(temp_image_path)}")
        
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
            
            print("Módulo OCR: Testando diferentes rotações para encontrar a melhor orientação...")
            
            for angle, rotated_img in rotations.items():
                # Teste rápido de OCR para cada rotação
                try:
                    quick_result = ocr_reader.readtext(rotated_img, detail=1)
                    text_count = len([r for r in quick_result if r[2] > 0.3])  # Conta textos com boa confiança
                    total_chars = sum(len(r[1].strip()) for r in quick_result if r[2] > 0.3)
                    
                    print(f"Módulo OCR: Rotação {angle}° - {text_count} detecções, {total_chars} caracteres")
                    
                    # Prioriza rotações com mais caracteres detectados
                    if total_chars > max_text_count:
                        max_text_count = total_chars
                        best_rotation = angle
                        best_image = rotated_img
                        
                except Exception as e:
                    print(f"Módulo OCR: Erro ao testar rotação {angle}°: {e}")
            
            print(f"Módulo OCR: Melhor orientação encontrada: {best_rotation}° ({max_text_count} caracteres)")
            return best_image, best_rotation
        
        # Obtém o leitor de OCR primeiro para usar na detecção de rotação
        ocr_reader = get_reader(lang_source)
        
        # Encontra a melhor rotação
        img_corrected, best_angle = test_rotation_and_get_best_image(img_cv)
        
        # Salva a imagem corrigida
        corrected_image_path = "temp_corrected_image.png"
        cv2.imwrite(corrected_image_path, img_corrected)
        print(f"Módulo OCR: Imagem corrigida (rotação {best_angle}°) salva em: {os.path.abspath(corrected_image_path)}")
        
        # Cria uma versão pré-processada da imagem corrigida para melhorar o OCR
        # Converte para escala de cinza
        img_gray = cv2.cvtColor(img_corrected, cv2.COLOR_BGR2GRAY)
        
        # Aplica filtro de desfoque gaussiano para reduzir ruído
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)
        
        # Aplica threshold adaptativo para melhorar contraste
        img_thresh = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Salva a imagem pré-processada para comparação
        processed_image_path = "temp_processed_image.png"
        cv2.imwrite(processed_image_path, img_thresh)
        print(f"Módulo OCR: Imagem pré-processada salva em: {os.path.abspath(processed_image_path)}")

        # Lista para armazenar todos os resultados de OCR
        all_detections = []
        
        # Tentativa 1: Imagem corrigida com configurações padrão
        print("Módulo OCR: Tentativa 1 - Imagem corrigida, configurações padrão")
        text_list_detailed_1 = ocr_reader.readtext(img_corrected, detail=1)
        print(f"Módulo OCR: Detecções encontradas (corrigida): {len(text_list_detailed_1)}")
        
        for i, detection in enumerate(text_list_detailed_1):
            bbox, text, confidence = detection
            print(f"Módulo OCR: Corrigida {i+1}: '{text}' (confiança: {confidence:.2f})")
        
        all_detections.extend(text_list_detailed_1)
        
        # Tentativa 2: Imagem pré-processada
        print("Módulo OCR: Tentativa 2 - Imagem pré-processada")
        text_list_detailed_2 = ocr_reader.readtext(img_thresh, detail=1)
        print(f"Módulo OCR: Detecções encontradas (pré-processada): {len(text_list_detailed_2)}")
        
        for i, detection in enumerate(text_list_detailed_2):
            bbox, text, confidence = detection
            print(f"Módulo OCR: Processada {i+1}: '{text}' (confiança: {confidence:.2f})")
        
        all_detections.extend(text_list_detailed_2)
        
        # Tentativa 3: Imagem corrigida com configurações mais sensíveis
        print("Módulo OCR: Tentativa 3 - Imagem corrigida, configurações sensíveis")
        text_list_detailed_3 = ocr_reader.readtext(img_corrected, detail=1, width_ths=0.5, height_ths=0.5)
        print(f"Módulo OCR: Detecções encontradas (sensível): {len(text_list_detailed_3)}")
        
        for i, detection in enumerate(text_list_detailed_3):
            bbox, text, confidence = detection
            print(f"Módulo OCR: Sensível {i+1}: '{text}' (confiança: {confidence:.2f})")
        
        all_detections.extend(text_list_detailed_3)
        
        # Processa todos os resultados e remove duplicatas
        unique_texts = set()
        for detection in all_detections:
            bbox, text, confidence = detection
            if confidence > 0.05 and text.strip():  # Threshold mais baixo para capturar mais texto
                # Remove espaços extras e caracteres especiais desnecessários
                clean_text = text.strip().replace('\n', ' ').replace('\t', ' ')
                if len(clean_text) > 0:
                    unique_texts.add(clean_text)
        
        text_list = list(unique_texts)
        print(f"Módulo OCR: Total de textos únicos encontrados: {len(text_list)}")
        
        # Junta os parágrafos encontrados em uma única string.
        extracted_text = " ".join(text_list)

        if extracted_text:
            print(f"Módulo OCR: Texto extraído: '{extracted_text}'")
        else:
            print("Módulo OCR: Nenhum texto foi encontrado na imagem.")

        return extracted_text
        
    except Exception as e:
        print(f"Erro no módulo OCR: {e}")
        return ""
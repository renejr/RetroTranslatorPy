import cv2
import matplotlib.pyplot as plt
import numpy as np
import os

def show_images():
    """Mostra as imagens de resultado e debug lado a lado"""
    # Lista de imagens para mostrar
    image_paths = [
        'test_fragmented_text.png',  # Imagem original
        'debug_original.png',        # Imagem corrigida
        'debug_combined_result.png', # Resultado combinado
        'test_fragmented_result.png' # Resultado final
    ]
    
    # Verifica quais imagens existem
    existing_images = []
    for path in image_paths:
        if os.path.exists(path):
            existing_images.append(path)
        else:
            print(f"Imagem não encontrada: {path}")
    
    if not existing_images:
        print("Nenhuma imagem encontrada para mostrar.")
        return
    
    # Configura o layout da figura
    n_images = len(existing_images)
    fig, axes = plt.subplots(1, n_images, figsize=(5*n_images, 5))
    
    # Se houver apenas uma imagem, axes não será um array
    if n_images == 1:
        axes = [axes]
    
    # Carrega e mostra cada imagem
    for i, (ax, path) in enumerate(zip(axes, existing_images)):
        img = cv2.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Converte de BGR para RGB
        
        ax.imshow(img)
        ax.set_title(path)
        ax.axis('off')  # Remove os eixos
    
    plt.tight_layout()
    plt.savefig('comparison_results.png')
    print("Comparação salva como 'comparison_results.png'")
    
    # Mostra a figura
    plt.show()

if __name__ == "__main__":
    show_images()
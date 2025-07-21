from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    # Cria uma imagem preta
    width, height = 320, 240
    image = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(image)
    
    # Tenta carregar uma fonte para o texto
    try:
        # Tenta encontrar uma fonte monospace no sistema
        font_path = None
        if os.name == 'nt':  # Windows
            font_path = 'C:\\Windows\\Fonts\\consola.ttf'
        else:  # Linux/Mac
            font_paths = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
                '/usr/share/fonts/TTF/DejaVuSansMono.ttf',
                '/Library/Fonts/Courier New.ttf'
            ]
            for path in font_paths:
                if os.path.exists(path):
                    font_path = path
                    break
        
        # Se encontrou uma fonte, usa ela
        if font_path:
            title_font = ImageFont.truetype(font_path, 36)
            text_font = ImageFont.truetype(font_path, 16)
        else:  # Senão, usa a fonte padrão
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
    except Exception as e:
        print(f"Erro ao carregar fonte: {e}")
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Adiciona o texto "1942" em verde no topo
    title_text = "1942"
    title_color = (0, 255, 0)  # Verde
    title_position = (width // 2 - 50, 30)
    draw.text(title_position, title_text, fill=title_color, font=title_font)
    
    # Adiciona os textos de jogadores e comando em amarelo
    text_color = (255, 255, 0)  # Amarelo
    
    # Texto "1 PLAYER"
    player1_text = "1 PLAYER"
    player1_position = (width // 2 - 40, 100)
    draw.text(player1_position, player1_text, fill=text_color, font=text_font)
    
    # Texto "2 PLAYERS"
    player2_text = "2 PLAYERS"
    player2_position = (width // 2 - 40, 130)
    draw.text(player2_position, player2_text, fill=text_color, font=text_font)
    
    # Texto "PUSH SPACE KEY"
    space_text = "PUSH SPACE KEY"
    space_position = (width // 2 - 60, 180)
    draw.text(space_position, space_text, fill=text_color, font=text_font)
    
    # Salva a imagem
    output_path = "test_image.png"
    image.save(output_path)
    print(f"Imagem de teste criada em: {output_path}")
    return output_path

if __name__ == "__main__":
    create_test_image()
# views/ocr_results_view.py
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
import io
import base64
import json
import datetime

class OCRResultsView(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)
        self.app = MDApp.get_running_app()
        self.dialog = None
        self.page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.lang_menu = None
        self.selected_lang = None
        self.languages = []
        
        # Carregar idiomas
        self._load_languages()
        
        # Criar a interface
        self._create_ui()
        
        # Carregar dados iniciais
        Clock.schedule_once(lambda dt: self.load_data(), 0.5)
    
    def _load_languages(self):
        # Carregar idiomas do banco de dados
        try:
            if self.app.db_manager.connection and self.app.db_manager.connection.is_connected():
                self.languages = self.app.db_manager.get_languages_list()
            else:
                print("Aviso: Conexão com o banco de dados não está ativa")
                self.languages = []
        except Exception as e:
            print(f"Erro ao carregar idiomas: {e}")
            self.languages = []
    
    def _create_ui(self):
        # Área de filtros
        self.filter_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        # Campo de pesquisa
        self.search_field = MDTextField(
            hint_text="Pesquisar texto",
            mode="rectangle",
            size_hint_x=0.6
        )
        self.search_field.bind(on_text_validate=lambda x: self.load_data())
        
        # Botão de idioma
        self.lang_button = MDRaisedButton(
            text="Idioma: Todos",
            size_hint_x=0.3,
            on_release=self.show_lang_menu
        )
        
        # Botão de pesquisa
        self.search_button = MDRaisedButton(
            text="Buscar",
            size_hint_x=0.1,
            on_release=lambda x: self.load_data()
        )
        
        # Adicionar widgets ao layout de filtros
        self.filter_layout.add_widget(self.search_field)
        self.filter_layout.add_widget(self.lang_button)
        self.filter_layout.add_widget(self.search_button)
        
        # Adicionar layout de filtros à view
        self.add_widget(self.filter_layout)
        
        # Criar tabela de dados
        self.data_table = MDDataTable(
            size_hint=(1, 0.85),
            use_pagination=True,
            pagination_menu_pos="auto",
            rows_num=self.items_per_page,
            column_data=[
                ("ID", dp(30)),
                ("Texto Detectado", dp(200)),
                ("Idioma", dp(50)),
                ("Confiança Média", dp(50)),
                ("Criado em", dp(60)),
                ("Último Uso", dp(60)),
                ("Contagem de Uso", dp(50))
            ]
        )
        
        # Vincular eventos da tabela
        self.data_table.bind(on_row_press=self.on_row_press)
        self.data_table.bind(on_pagination=self.on_pagination)
        
        # Adicionar tabela à view
        self.add_widget(self.data_table)
        
        # Layout de navegação de páginas
        self.pagination_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=[0, dp(10), 0, 0]
        )
        
        # Botões de navegação
        self.prev_button = MDFlatButton(
            text="Anterior",
            on_release=lambda x: self.change_page(-1)
        )
        
        self.page_label = MDTextField(
            text="Página 1 de 1",
            readonly=True,
            size_hint_x=0.2,
            halign="center"
        )
        
        self.next_button = MDFlatButton(
            text="Próxima",
            on_release=lambda x: self.change_page(1)
        )
        
        # Adicionar botões ao layout de navegação
        self.pagination_layout.add_widget(self.prev_button)
        self.pagination_layout.add_widget(self.page_label)
        self.pagination_layout.add_widget(self.next_button)
        
        # Adicionar layout de navegação à view
        self.add_widget(self.pagination_layout)
    
    def show_lang_menu(self, button):
        # Criar menu de idiomas
        menu_items = [
            {
                "text": "Todos",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Todos": self.set_lang(x),
            }
        ]
        
        for lang in self.languages:
            menu_items.append({
                "text": lang,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=lang: self.set_lang(x),
            })
        
        self.lang_menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4
        )
        
        self.lang_menu.open()
    
    def set_lang(self, lang):
        # Definir idioma selecionado
        self.selected_lang = None if lang == "Todos" else lang
        self.lang_button.text = f"Idioma: {lang}"
        self.lang_menu.dismiss()
        self.load_data()
    
    def load_data(self):
        # Obter dados do banco de dados
        search_text = self.search_field.text
        offset = (self.page - 1) * self.items_per_page
        
        try:
            # Verificar se a conexão com o banco de dados está ativa
            if not (self.app.db_manager.connection and self.app.db_manager.connection.is_connected()):
                print("Aviso: Conexão com o banco de dados não está ativa")
                data = []
                total_count = 0
            else:
                # Obter dados paginados e filtrados
                data, total_count = self.app.db_manager.get_ocr_results(
                    offset=offset,
                    limit=self.items_per_page,
                    search_text=search_text if search_text else None,
                    source_lang=self.selected_lang
                )
        except Exception as e:
            print(f"Erro ao carregar dados de OCR: {e}")
            data = []
            total_count = 0
        
        # Calcular total de páginas
        self.total_pages = max(1, (total_count + self.items_per_page - 1) // self.items_per_page)
        
        # Verificar se a página atual é válida
        if self.page > self.total_pages and self.total_pages > 0:
            self.page = self.total_pages
            # Recarregar dados com a página corrigida
            return self.load_data()
        
        # Atualizar label de página
        self.page_label.text = f"Página {self.page} de {self.total_pages}"
        
        # Atualizar estado dos botões de navegação
        self.prev_button.disabled = self.page <= 1
        self.next_button.disabled = self.page >= self.total_pages
        
        # Formatar dados para a tabela
        table_data = []
        for row in data:
            # Extrair texto dos resultados JSON
            text_results = row.get('text_results_parsed', {})
            # Verificar se text_results é um dicionário ou uma lista
            if isinstance(text_results, dict):
                text = text_results.get('text', '')
            elif isinstance(text_results, list) and text_results:
                # Se for uma lista, tenta pegar o primeiro item ou texto vazio
                text = text_results[0].get('text', '') if isinstance(text_results[0], dict) else str(text_results[0])
            else:
                text = ''
            
            # Limitar tamanho do texto para exibição na tabela
            text_display = (text[:100] + '...') if len(text) > 100 else text
            
            # Calcular confiança média
            if isinstance(text_results, dict):
                confidence = text_results.get('confidence', 0)
            elif isinstance(text_results, list) and text_results:
                if isinstance(text_results[0], dict):
                    confidence = text_results[0].get('confidence', 0)
                else:
                    confidence = 0
            else:
                confidence = 0
                
            confidence_display = f"{confidence:.2f}" if confidence is not None else 'N/A'
            
            # Formatar datas
            created_at = row.get('created_at')
            created_at = created_at.strftime('%d/%m/%Y %H:%M') if created_at else 'N/A'
            
            last_used = row.get('last_used')
            last_used = last_used.strftime('%d/%m/%Y %H:%M') if last_used else 'N/A'
            
            table_data.append([
                str(row.get('id', 'N/A')),  # ID
                text_display,  # Texto Detectado
                row.get('source_lang', 'N/A'),  # Idioma
                confidence_display,  # Confiança Média
                created_at,  # Criado em
                last_used,  # Último Uso
                str(row.get('usage_count', 0))  # Contagem de Uso
            ])
        
        # Atualizar dados da tabela
        self.data_table.row_data = table_data
    
    def on_pagination(self, table, pagination_menu_instance):
        # Atualizar página atual quando a paginação da tabela é alterada
        # Verificar se a página atual é válida
        if pagination_menu_instance.current_page > 0 and pagination_menu_instance.current_page <= self.total_pages:
            self.page = pagination_menu_instance.current_page
            self.load_data()
        else:
            # Se a página não for válida, voltar para a página 1
            self.page = 1
            self.load_data()
    
    def change_page(self, direction):
        # Mudar de página (anterior ou próxima)
        new_page = self.page + direction
        if 1 <= new_page <= self.total_pages:
            self.page = new_page
            self.load_data()
        elif new_page < 1:
            # Se tentar ir para uma página menor que 1, ficar na página 1
            self.page = 1
            self.load_data()
        elif new_page > self.total_pages:
            # Se tentar ir para uma página maior que o total, ficar na última página
            self.page = self.total_pages
            self.load_data()
    
    def on_row_press(self, instance_table, instance_row):
        # Verificar se há dados na tabela
        if not instance_table.row_data or instance_row.index >= len(instance_table.row_data):
            return
            
        try:
            # Obter ID do resultado OCR selecionado
            row_id = int(instance_table.row_data[instance_row.index][0])
            
            # Obter dados completos do resultado OCR
            ocr_result = self.app.db_manager.get_ocr_result_by_id(row_id)
            if not ocr_result:
                return
        except (IndexError, ValueError):
            print("Erro ao obter dados da linha selecionada")
            return
        
        # Extrair dados
        text_results = ocr_result.get('text_results_parsed', {})
        if not text_results and ocr_result.get('text_results'):
            try:
                text_results = json.loads(ocr_result.get('text_results', '{}'))
            except json.JSONDecodeError:
                text_results = {}
        
        # Verificar se text_results é um dicionário ou uma lista
        if isinstance(text_results, dict):
            text = text_results.get('text', '')
            confidence = text_results.get('confidence', 0)
            metadata = text_results.get('metadata', {})
        elif isinstance(text_results, list) and text_results:
            # Se for uma lista, tenta pegar o primeiro item
            if isinstance(text_results[0], dict):
                text = text_results[0].get('text', '')
                confidence = text_results[0].get('confidence', 0)
                metadata = text_results[0].get('metadata', {})
            else:
                text = str(text_results[0])
                confidence = 0
                metadata = {}
        else:
            text = ''
            confidence = 0
            metadata = {}
        
        # Formatar datas
        created_at = ocr_result.get('created_at')
        created_at = created_at.strftime('%d/%m/%Y %H:%M') if created_at else 'N/A'
        
        last_used = ocr_result.get('last_used')
        last_used = last_used.strftime('%d/%m/%Y %H:%M') if last_used else 'N/A'
        
        # Criar layout do diálogo
        content_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(500)
        )
        
        # Adicionar imagem se disponível
        if ocr_result.get('image_base64'):  # image_base64
            try:
                # Decodificar imagem base64
                image_data = base64.b64decode(ocr_result['image_base64'])
                # Criar buffer de imagem
                buffer = io.BytesIO(image_data)
                # Carregar imagem
                coreimage = CoreImage(buffer, ext='png')
                # Criar widget de imagem
                image = Image(
                    texture=coreimage.texture,
                    size_hint=(1, 0.5),
                    allow_stretch=True,
                    keep_ratio=True
                )
                content_layout.add_widget(image)
            except Exception as e:
                print(f"Erro ao carregar imagem: {e}")
        
        # Adicionar informações de texto
        text_info = f"""**ID:** {ocr_result['id']}\n\n
                    **Texto Detectado:**\n{text}\n\n
                    **Idioma:** {ocr_result['source_lang']}\n
                    **Confiança:** {confidence:.2f}\n
                    **Criado em:** {created_at}\n
                    **Último Uso:** {last_used}\n
                    **Contagem de Uso:** {ocr_result['usage_count']}\n
                    **Hash da Imagem:** {ocr_result.get('image_hash', 'N/A')}"""
        
        # Adicionar metadados se disponíveis
        if metadata:
            text_info += "\n\n**Metadados:**\n"
            for key, value in metadata.items():
                text_info += f"- {key}: {value}\n"
        
        # Mostrar diálogo com detalhes do resultado OCR
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title="Detalhes do Resultado OCR",
            type="custom",
            content_cls=content_layout,
            text=text_info,
            size_hint=(0.9, 0.9),
            buttons=[
                MDFlatButton(
                    text="FECHAR",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        
        self.dialog.open()
# views/translations_view.py
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.clock import Clock
import datetime
import csv
import json
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

class TranslationsView(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)
        self.app = MDApp.get_running_app()
        self.dialog = None
        self.page = 1
        self.items_per_page = 20  # Valor padrão mais adequado
        self.total_pages = 1
        self.items_per_page_menu = None  # Menu para seleção de itens por página
        self.source_lang_menu = None
        self.target_lang_menu = None
        self.selected_source_lang = None
        self.selected_target_lang = None
        self.languages = []
        self.translators = []
        
        # Variáveis de controle de ordenação
        self.current_sort_column = None
        self.current_sort_direction = 'ASC'
        
        # Carregar idiomas e tradutores
        self._load_languages_and_translators()
        
        # Criar a interface
        self._create_ui()
        
        # Carregar dados iniciais
        Clock.schedule_once(lambda dt: self.load_data(), 0.5)
    
    def _load_languages_and_translators(self):
        # Carregar idiomas e tradutores do banco de dados
        try:
            if self.app.db_manager.connection and self.app.db_manager.connection.is_connected():
                self.languages = self.app.db_manager.get_languages_list()
                self.translators = self.app.db_manager.get_translators_list()
            else:
                print("Aviso: Conexão com o banco de dados não está ativa")
                self.languages = []
                self.translators = []
        except Exception as e:
            print(f"Erro ao carregar idiomas e tradutores: {e}")
            self.languages = []
            self.translators = []
    
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
            size_hint_x=0.4
        )
        self.search_field.bind(on_text_validate=lambda x: self.load_data())
        
        # Botões de idioma de origem e destino
        self.source_lang_button = MDRaisedButton(
            text="Idioma Origem: Todos",
            size_hint_x=0.25,
            on_release=self.show_source_lang_menu
        )
        
        self.target_lang_button = MDRaisedButton(
            text="Idioma Destino: Todos",
            size_hint_x=0.25,
            on_release=self.show_target_lang_menu
        )
        
        # Botão de pesquisa
        self.search_button = MDRaisedButton(
            text="Buscar",
            size_hint_x=0.1,
            on_release=lambda x: self.load_data()
        )
        
        # Adicionar widgets ao layout de filtros
        self.filter_layout.add_widget(self.search_field)
        self.filter_layout.add_widget(self.source_lang_button)
        self.filter_layout.add_widget(self.target_lang_button)
        self.filter_layout.add_widget(self.search_button)
        
        # Adicionar layout de filtros à view
        self.add_widget(self.filter_layout)
        
        # Área de botões de exportação
        self.export_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=[0, dp(5), 0, dp(5)]
        )
        
        # Botões de exportação
        self.export_csv_button = MDRaisedButton(
            text="Exportar CSV",
            size_hint_x=0.2,
            on_release=self.export_to_csv
        )
        
        self.export_json_button = MDRaisedButton(
            text="Exportar JSON",
            size_hint_x=0.2,
            on_release=self.export_to_json
        )
        
        self.export_pdf_button = MDRaisedButton(
            text="Exportar PDF",
            size_hint_x=0.2,
            on_release=self.export_to_pdf
        )
        
        # Adicionar botões ao layout de exportação
        self.export_layout.add_widget(self.export_csv_button)
        self.export_layout.add_widget(self.export_json_button)
        self.export_layout.add_widget(self.export_pdf_button)
        
        # Adicionar espaço vazio para alinhar à direita
        from kivymd.uix.label import MDLabel
        self.export_layout.add_widget(MDLabel(size_hint_x=0.4))
        
        # Adicionar layout de exportação à view
        self.add_widget(self.export_layout)
        
        # Criar tabela de dados (sem paginação nativa)
        self.data_table = MDDataTable(
            size_hint=(1, 0.85),
            use_pagination=False,  # Desabilitar paginação nativa
            rows_num=max(self.items_per_page, 100),  # Garantir que rows_num seja suficiente
            column_data=[
                ("ID", dp(18), lambda *args: self.sort_column("ID")),
                ("Original", dp(65), lambda *args: self.sort_column("Original")),
                ("Tradução", dp(65), lambda *args: self.sort_column("Tradução")),
                ("Origem", dp(28), lambda *args: self.sort_column("Origem")),
                ("Destino", dp(28), lambda *args: self.sort_column("Destino")),
                ("Tradutor", dp(35), lambda *args: self.sort_column("Tradutor")),
                ("Confiança", dp(32), lambda *args: self.sort_column("Confiança")),
                ("Criação", dp(40), lambda *args: self.sort_column("Criação")),
                ("Últ. Uso", dp(40), lambda *args: self.sort_column("Últ. Uso")),
                ("Usos", dp(22), lambda *args: self.sort_column("Usos"))
            ]
        )
        
        # Vincular eventos
        self.data_table.bind(on_row_press=self.on_row_press)
        
        # Adicionar tabela à view
        self.add_widget(self.data_table)
        
        # Card de navegação de páginas com melhor estilização
        self.pagination_card = MDCard(
            size_hint_y=None,
            height=dp(60),
            padding=dp(10),
            spacing=dp(10),
            elevation=2,
            md_bg_color=(0.95, 0.95, 0.95, 1)  # Cor de fundo clara
        )
        
        self.pagination_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(15),
            adaptive_width=True,
            pos_hint={'center_x': 0.5}
        )
        
        # Botão anterior com ícone
        self.prev_button = MDRaisedButton(
            text="◀ Anterior",
            theme_icon_color="Custom",
            md_bg_color=(0.2, 0.6, 1, 1),  # Azul
            text_color=(1, 1, 1, 1),  # Texto branco
            on_release=lambda x: self.change_page(-1)
        )
        
        # Label de informação da página com melhor estilização
        self.page_info_layout = MDBoxLayout(
            orientation='vertical',
            adaptive_width=True,
            spacing=dp(2)
        )
        
        self.page_label = MDLabel(
            text="Página 1 de 1",
            theme_text_color="Primary",
            font_style="H6",
            halign="center",
            adaptive_width=True
        )
        
        self.records_label = MDLabel(
            text="0 registros encontrados",
            theme_text_color="Secondary",
            font_style="Caption",
            halign="center",
            adaptive_width=True
        )
        
        # Botão próxima com ícone
        self.next_button = MDRaisedButton(
            text="Próxima ▶",
            theme_icon_color="Custom",
            md_bg_color=(0.2, 0.6, 1, 1),  # Azul
            text_color=(1, 1, 1, 1),  # Texto branco
            on_release=lambda x: self.change_page(1)
        )
        
        # Adicionar labels ao layout de informação
        self.page_info_layout.add_widget(self.page_label)
        self.page_info_layout.add_widget(self.records_label)
        
        # Seletor de itens por página
        self.items_per_page_layout = MDBoxLayout(
            orientation='horizontal',
            adaptive_width=True,
            spacing=dp(5)
        )
        
        self.items_per_page_label = MDLabel(
            text="Itens por página:",
            theme_text_color="Primary",
            font_style="Body2",
            adaptive_width=True
        )
        
        self.items_per_page_button = MDRaisedButton(
            text=str(self.items_per_page),
            size_hint_x=None,
            width=dp(60),
            on_release=self.show_items_per_page_menu
        )
        
        self.items_per_page_layout.add_widget(self.items_per_page_label)
        self.items_per_page_layout.add_widget(self.items_per_page_button)
        
        # Adicionar widgets ao layout de navegação
        self.pagination_layout.add_widget(self.items_per_page_layout)
        self.pagination_layout.add_widget(self.prev_button)
        self.pagination_layout.add_widget(self.page_info_layout)
        self.pagination_layout.add_widget(self.next_button)
        
        # Adicionar layout ao card
        self.pagination_card.add_widget(self.pagination_layout)
        
        # Adicionar card à view
        self.add_widget(self.pagination_card)
    
    def show_source_lang_menu(self, button):
        # Criar menu de idiomas de origem
        menu_items = [
            {
                "text": "Todos",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Todos": self.set_source_lang(x),
            }
        ]
        
        for lang in self.languages:
            menu_items.append({
                "text": lang,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=lang: self.set_source_lang(x),
            })
        
        self.source_lang_menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4
        )
        
        self.source_lang_menu.open()
    
    def show_target_lang_menu(self, button):
        # Criar menu de idiomas de destino
        menu_items = [
            {
                "text": "Todos",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Todos": self.set_target_lang(x),
            }
        ]
        
        for lang in self.languages:
            menu_items.append({
                "text": lang,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=lang: self.set_target_lang(x),
            })
        
        self.target_lang_menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4
        )
        
        self.target_lang_menu.open()
    
    def set_source_lang(self, lang):
        # Definir idioma de origem selecionado
        self.selected_source_lang = None if lang == "Todos" else lang
        self.source_lang_button.text = f"Idioma Origem: {lang}"
        self.source_lang_menu.dismiss()
        self.load_data()
    
    def set_target_lang(self, lang):
        # Definir idioma de destino selecionado
        self.selected_target_lang = None if lang == "Todos" else lang
        self.target_lang_button.text = f"Idioma Destino: {lang}"
        self.target_lang_menu.dismiss()
        self.load_data()
    
    def show_items_per_page_menu(self, button):
        """Exibe menu para seleção de itens por página"""
        items_options = [5, 10, 15, 20, 25, 50]
        menu_items = [
            {
                "text": str(option),
                "viewclass": "OneLineListItem",
                "on_release": lambda x=option: self.set_items_per_page(x),
            } for option in items_options
        ]
        
        self.items_per_page_menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=2,
        )
        self.items_per_page_menu.open()
    
    def set_items_per_page(self, items):
        """Define a quantidade de itens por página"""
        self.items_per_page = items
        self.items_per_page_button.text = str(items)
        # Garantir que rows_num seja suficiente para exibir todos os itens solicitados
        self.data_table.rows_num = max(items, 100)
        self.items_per_page_menu.dismiss()
        self.page = 1  # Voltar para primeira página ao alterar itens por página
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
                # Obter dados paginados, filtrados e ordenados
                data, total_count = self.app.db_manager.get_translations(
                    offset=offset,
                    limit=self.items_per_page,
                    search_text=search_text if search_text else None,
                    source_lang=self.selected_source_lang,
                    target_lang=self.selected_target_lang,
                    order_by=self.current_sort_column,
                    order_direction=self.current_sort_direction
                )
        except Exception as e:
            print(f"Erro ao carregar dados de traduções: {e}")
            data = []
            total_count = 0
        
        # Calcular total de páginas
        self.total_pages = max(1, (total_count + self.items_per_page - 1) // self.items_per_page)
        
        # Verificar se a página atual é válida
        if self.page > self.total_pages and self.total_pages > 0:
            self.page = self.total_pages
            # Recarregar dados com a página corrigida
            return self.load_data()
        
        # Atualizar labels de informação com formatação melhorada
        self.page_label.text = f"Página {self.page} de {self.total_pages}"
        
        # Formatação inteligente do contador de registros
        if total_count == 0:
            self.records_label.text = "Nenhum registro encontrado"
        elif total_count == 1:
            self.records_label.text = "1 registro encontrado"
        else:
            self.records_label.text = f"{total_count:,} registros encontrados".replace(',', '.')
        
        # Atualizar estado dos botões de navegação com melhor feedback visual
        self.prev_button.disabled = self.page <= 1
        self.next_button.disabled = self.page >= self.total_pages
        
        # Alterar cor e texto dos botões baseado no estado
        if self.prev_button.disabled:
            self.prev_button.md_bg_color = (0.6, 0.6, 0.6, 1)  # Cinza mais escuro
            self.prev_button.text_color = (0.8, 0.8, 0.8, 1)  # Texto cinza claro
        else:
            self.prev_button.md_bg_color = (0.2, 0.6, 1, 1)  # Azul
            self.prev_button.text_color = (1, 1, 1, 1)  # Texto branco
            
        if self.next_button.disabled:
            self.next_button.md_bg_color = (0.6, 0.6, 0.6, 1)  # Cinza mais escuro
            self.next_button.text_color = (0.8, 0.8, 0.8, 1)  # Texto cinza claro
        else:
            self.next_button.md_bg_color = (0.2, 0.6, 1, 1)  # Azul
            self.next_button.text_color = (1, 1, 1, 1)  # Texto branco
        
        # Formatar dados para a tabela
        table_data = []
        for row in data:
            # Limitar tamanho dos textos para exibição na tabela e remover quebras de linha
            source_text = row.get('source_text', '')
            source_text = source_text.replace('\n', ' ').replace('\r', ' ')  # Remover quebras de linha
            source_text = (source_text[:25] + '...') if len(source_text) > 25 else source_text
            
            translated_text = row.get('translated_text', '')
            translated_text = translated_text.replace('\n', ' ').replace('\r', ' ')  # Remover quebras de linha
            translated_text = (translated_text[:25] + '...') if len(translated_text) > 25 else translated_text
            
            # Formatar datas com ano de 2 dígitos
            created_at = row.get('created_at')
            created_at = created_at.strftime('%d/%m/%y %H:%M') if created_at else 'N/A'
            
            last_used = row.get('last_used')
            last_used = last_used.strftime('%d/%m/%y %H:%M') if last_used else 'N/A'
            
            # Formatar confiança
            confidence = f"{row.get('confidence', 0):.2f}" if row.get('confidence') is not None else 'N/A'
            
            # Verificar se todas as chaves existem e fornecer valores padrão se não existirem
            table_data.append([
                str(row.get('id', 'N/A')),  # ID
                source_text,  # Texto Original
                translated_text,  # Texto Traduzido
                row.get('source_lang', 'N/A'),  # Idioma Origem
                row.get('target_lang', 'N/A'),  # Idioma Destino
                row.get('translator_used', 'N/A'),  # Tradutor
                confidence,  # Confiança
                created_at,  # Criado em
                last_used,  # Último Uso
                str(row.get('used_count', 0))  # Contagem de Uso
            ])
        
        # Atualizar dados da tabela
        self.data_table.row_data = table_data
    
    # Método on_pagination removido - não é mais necessário pois desabilitamos use_pagination
    
    def sort_column(self, column_name):
        """Gerencia a ordenação das colunas quando o cabeçalho é clicado"""
        # Se é a mesma coluna, alternar direção
        if self.current_sort_column == column_name:
            self.current_sort_direction = 'DESC' if self.current_sort_direction == 'ASC' else 'ASC'
        else:
            # Nova coluna, começar com ASC
            self.current_sort_column = column_name
            self.current_sort_direction = 'ASC'
        
        # Voltar para a primeira página ao ordenar
        self.page = 1
        
        # Recarregar dados com nova ordenação
        self.load_data()
        
        # Obter dados atuais da tabela
        current_data = self.data_table.row_data
        
        # Mapear nome da coluna para índice
        column_mapping = {
            "Original": 0,
            "Tradução": 1,
            "Origem": 2,
            "Destino": 3,
            "Tradutor": 4,
            "Confiança": 5,
            "Criação": 6,
            "Últ. Uso": 7,
            "Usos": 8
        }
        
        column_index = column_mapping.get(column_name, 0)
        
        # Ordenar dados usando o formato requerido pelo MDDataTable
        # Formato: [Index, Sorted_Row_Data] usando zip(*sorted(enumerate(data), key=...))
        if self.current_sort_direction == 'ASC':
            sorted_data = zip(*sorted(enumerate(current_data), key=lambda l: str(l[1][column_index]).lower()))
        else:
            sorted_data = zip(*sorted(enumerate(current_data), key=lambda l: str(l[1][column_index]).lower(), reverse=True))
        
        # Converter para listas
        indices, sorted_rows = map(list, sorted_data)
        
        return [indices, sorted_rows]
    
    def change_page(self, direction):
        # Mudar de página (anterior ou próxima) com validação aprimorada
        new_page = self.page + direction
        
        # Validar limites de página
        if new_page < 1:
            new_page = 1
        elif new_page > self.total_pages:
            new_page = self.total_pages
            
        # Só recarregar se a página realmente mudou
        if new_page != self.page:
            self.page = new_page
            
            # Feedback visual temporário durante carregamento
            original_page_text = self.page_label.text
            self.page_label.text = "Carregando..."
            
            # Agendar carregamento dos dados
            Clock.schedule_once(lambda dt: self._load_page_data(original_page_text), 0.1)
    
    def _load_page_data(self, fallback_text):
        """Método auxiliar para carregar dados da página com tratamento de erro"""
        try:
            self.load_data()
        except Exception as e:
            print(f"Erro ao carregar página: {e}")
            self.page_label.text = fallback_text
    
    def on_row_press(self, instance_table, instance_row):
        # Verificar se há dados na tabela
        if not instance_table.row_data or instance_row.index >= len(instance_table.row_data):
            return
            
        try:
            # Obter ID da tradução selecionada
            row_id = int(instance_table.row_data[instance_row.index][0])
            
            # Obter dados completos da tradução
            translation = self.app.db_manager.get_translation_by_id(row_id)
            if not translation:
                return
        except (IndexError, ValueError):
            print("Erro ao obter dados da linha selecionada")
            return
        
        # Formatar datas
        created_at = translation.get('created_at')
        created_at = created_at.strftime('%d/%m/%Y %H:%M') if created_at else 'N/A'
        
        last_used = translation.get('last_used')
        last_used = last_used.strftime('%d/%m/%Y %H:%M') if last_used else 'N/A'
        
        # Formatar confiança
        confidence = f"{translation.get('confidence', 0):.2f}" if translation.get('confidence') is not None else 'N/A'
        
        # Criar conteúdo do diálogo
        content = f"""**ID:** {translation.get('id', 'N/A')}\n\n
                    **Texto Original:**\n{translation.get('source_text', 'N/A')}\n\n
                    **Texto Traduzido:**\n{translation.get('translated_text', 'N/A')}\n\n
                    **Idioma Origem:** {translation.get('source_lang', 'N/A')}\n
                    **Idioma Destino:** {translation.get('target_lang', 'N/A')}\n
                    **Tradutor:** {translation.get('translator', 'N/A')}\n
                    **Confiança:** {confidence}\n
                    **Criado em:** {created_at}\n
                    **Último Uso:** {last_used}\n
                    **Contagem de Uso:** {translation.get('usage_count', 0)}\n
                    **Hash do Texto:** {translation.get('text_hash', 'N/A')}"""
        
        # Mostrar diálogo com detalhes da tradução
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title="Detalhes da Tradução",
            text=content,
            size_hint=(0.8, 0.8),
            buttons=[
                MDFlatButton(
                    text="FECHAR",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        
        self.dialog.open()
    
    def get_all_data_for_export(self):
        """Obtém todos os dados para exportação (sem paginação)"""
        try:
            if self.app.db_manager and self.app.db_manager.connection:
                # Obter todos os dados sem limite de paginação
                search_text = self.search_field.text if self.search_field.text else None
                source_lang = getattr(self, 'selected_source_lang', None)
                target_lang = getattr(self, 'selected_target_lang', None)
                order_by = getattr(self, 'current_sort_column', None)
                order_direction = getattr(self, 'current_sort_direction', 'ASC')
                
                translations, total = self.app.db_manager.get_translations(
                    limit=None,  # Sem limite para exportação
                    offset=0,
                    search_text=search_text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    order_by=order_by,
                    order_direction=order_direction
                )
                return translations
            else:
                return []
        except Exception as e:
            print(f"Erro ao obter dados para exportação: {e}")
            return []
    
    def export_to_csv(self, instance):
        """Exporta dados para arquivo CSV"""
        try:
            data = self.get_all_data_for_export()
            if not data:
                self.show_export_dialog("Erro", "Nenhum dado disponível para exportação.")
                return
            
            # Criar nome do arquivo com timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"translations_export_{timestamp}.csv"
            filepath = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            
            # Escrever arquivo CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Cabeçalho
                headers = ['ID', 'Texto Original', 'Tradução', 'Idioma Origem', 'Idioma Destino', 
                          'Tradutor', 'Confiança', 'Data Criação', 'Último Uso', 'Contagem Uso']
                writer.writerow(headers)
                
                # Dados
                for row in data:
                    csv_row = [
                        row.get('id', ''),
                        row.get('source_text', ''),
                        row.get('translated_text', ''),
                        row.get('source_lang', ''),
                        row.get('target_lang', ''),
                        row.get('translator_used', ''),
                        row.get('confidence', ''),
                        row.get('created_at', ''),
                        row.get('last_used', ''),
                        row.get('used_count', '')
                    ]
                    writer.writerow(csv_row)
            
            self.show_export_dialog("Sucesso", f"Arquivo CSV exportado com sucesso!\nLocal: {filepath}")
            
        except Exception as e:
            self.show_export_dialog("Erro", f"Erro ao exportar CSV: {str(e)}")
    
    def export_to_json(self, instance):
        """Exporta dados para arquivo JSON"""
        try:
            data = self.get_all_data_for_export()
            if not data:
                self.show_export_dialog("Erro", "Nenhum dado disponível para exportação.")
                return
            
            # Criar nome do arquivo com timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"translations_export_{timestamp}.json"
            filepath = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            
            # Converter dados para formato JSON serializável
            json_data = []
            for row in data:
                json_row = {
                    'id': row.get('id'),
                    'source_text': row.get('source_text'),
                    'translated_text': row.get('translated_text'),
                    'source_lang': row.get('source_lang'),
                    'target_lang': row.get('target_lang'),
                    'translator_used': row.get('translator_used'),
                    'confidence': float(row.get('confidence', 0)) if row.get('confidence') else None,
                    'created_at': str(row.get('created_at')) if row.get('created_at') else None,
                    'last_used': str(row.get('last_used')) if row.get('last_used') else None,
                    'used_count': row.get('used_count'),
                    'text_hash': row.get('text_hash')
                }
                json_data.append(json_row)
            
            # Escrever arquivo JSON
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump({
                    'export_info': {
                        'timestamp': timestamp,
                        'total_records': len(json_data),
                        'exported_by': 'RetroArch Admin Interface'
                    },
                    'translations': json_data
                }, jsonfile, indent=2, ensure_ascii=False)
            
            self.show_export_dialog("Sucesso", f"Arquivo JSON exportado com sucesso!\nLocal: {filepath}")
            
        except Exception as e:
            self.show_export_dialog("Erro", f"Erro ao exportar JSON: {str(e)}")
    
    def export_to_pdf(self, instance):
        """Exporta dados para arquivo PDF"""
        try:
            data = self.get_all_data_for_export()
            if not data:
                self.show_export_dialog("Erro", "Nenhum dado disponível para exportação.")
                return
            
            # Criar nome do arquivo com timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"translations_export_{timestamp}.pdf"
            filepath = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            
            # Criar documento PDF em orientação paisagem
            from reportlab.lib.pagesizes import landscape
            from reportlab.platypus import PageBreak
            doc = SimpleDocTemplate(filepath, pagesize=landscape(A4))
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Centralizado
            )
            
            # Título
            title = Paragraph("Relatório de Traduções - RetroArch", title_style)
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Informações do relatório
            info_style = styles['Normal']
            info_text = f"""Data de Exportação: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br/>
            Total de Registros: {len(data)}<br/>
            Gerado por: RetroArch Admin Interface"""
            info_para = Paragraph(info_text, info_style)
            elements.append(info_para)
            elements.append(Spacer(1, 20))
            
            # Preparar cabeçalho da tabela
            headers = ['ID', 'Original', 'Tradução', 'Origem', 'Destino', 'Tradutor', 'Confiança', 'Criação', 'Últ. Uso', 'Usos']
            
            # Preparar dados das linhas
            rows_data = []
            for row in data:
                # Truncar textos longos para caber na página
                source_text = str(row.get('source_text', ''))[:25] + '...' if len(str(row.get('source_text', ''))) > 25 else str(row.get('source_text', ''))
                translated_text = str(row.get('translated_text', ''))[:25] + '...' if len(str(row.get('translated_text', ''))) > 25 else str(row.get('translated_text', ''))
                
                # Formatar datas
                created_at = row.get('created_at')
                created_at = created_at.strftime('%d/%m/%y %H:%M') if created_at else 'N/A'
                
                last_used = row.get('last_used')
                last_used = last_used.strftime('%d/%m/%y %H:%M') if last_used else 'N/A'
                
                # Formatar confiança
                confidence = f"{row.get('confidence', 0):.2f}" if row.get('confidence') is not None else 'N/A'
                
                pdf_row = [
                    str(row.get('id', '')),
                    source_text,
                    translated_text,
                    str(row.get('source_lang', '')),
                    str(row.get('target_lang', '')),
                    str(row.get('translator_used', 'N/A')),
                    confidence,
                    created_at,
                    last_used,
                    str(row.get('used_count', 0))
                ]
                rows_data.append(pdf_row)
            
            # Dividir dados em páginas (15 linhas por página para garantir que caiba com cabeçalho)
            rows_per_page = 15
            col_widths = [0.7*inch, 2.2*inch, 2.2*inch, 0.7*inch, 0.7*inch, 1.0*inch, 0.8*inch, 1.0*inch, 1.0*inch, 0.6*inch]
            
            # Estilo comum para todas as tabelas
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('WORDWRAP', (0, 0), (-1, -1), True)
            ])
            
            # Criar tabelas com cabeçalho repetido para cada página
            for i in range(0, len(rows_data), rows_per_page):
                # Se não é a primeira tabela, adicionar quebra de página
                if i > 0:
                    elements.append(PageBreak())
                
                # Pegar as linhas para esta página
                page_rows = rows_data[i:i + rows_per_page]
                
                # Criar dados da tabela com cabeçalho + linhas da página
                table_data = [headers] + page_rows
                
                # Criar tabela
                table = Table(table_data, colWidths=col_widths)
                table.setStyle(table_style)
                
                elements.append(table)
                
                # Adicionar pequeno espaço após cada tabela
                elements.append(Spacer(1, 12))
            
            # Construir PDF
            doc.build(elements)
            
            self.show_export_dialog("Sucesso", f"Arquivo PDF exportado com sucesso!\nLocal: {filepath}")
            
        except Exception as e:
            self.show_export_dialog("Erro", f"Erro ao exportar PDF: {str(e)}")
    
    def show_export_dialog(self, title, message):
        """Mostra diálogo de resultado da exportação"""
        if hasattr(self, 'export_dialog') and self.export_dialog:
            self.export_dialog.dismiss()
        
        self.export_dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.export_dialog.dismiss()
                )
            ]
        )
        self.export_dialog.open()
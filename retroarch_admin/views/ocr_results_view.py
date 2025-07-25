# views/ocr_results_view.py
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
import io
import base64
import json
import datetime
import csv
import os
import logging
import traceback
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Configurar logging para OCRResultsView
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ocr_results_view.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('OCRResultsView')

class OCRResultsView(MDBoxLayout):
    def __init__(self, **kwargs):
        logger.info("[DEBUG] Inicializando OCRResultsView")
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
        
        # Variáveis para controle de ordenação (padrão: último uso descendente)
        self.current_sort_column = "last_used"
        self.current_sort_direction = "DESC"
        logger.debug("[DEBUG] Configuração inicial: ordenação por %s %s", self.current_sort_column, self.current_sort_direction)
        
        try:
            # Carregar idiomas
            logger.debug("[DEBUG] Carregando idiomas disponíveis")
            self._load_languages()
            
            # Criar a interface
            logger.debug("[DEBUG] Criando interface do usuário")
            self._create_ui()
            logger.info("[DEBUG] OCRResultsView inicializado com sucesso")
        except Exception as e:
            logger.error("[ERROR] Erro durante inicialização do OCRResultsView: %s", str(e))
            traceback.print_exc()
            raise
        
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
        
        # Área de botões de exportação
        self.export_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=[0, dp(5), 0, dp(5)]
        )
        
        # Botões de ordenação
        self.sort_button = MDRaisedButton(
            text="Ordenar por: Último Uso v",
            size_hint_x=0.3,
            on_release=self.show_sort_menu
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
        self.export_layout.add_widget(self.sort_button)
        self.export_layout.add_widget(self.export_csv_button)
        self.export_layout.add_widget(self.export_json_button)
        self.export_layout.add_widget(self.export_pdf_button)
        self.export_layout.add_widget(MDLabel(size_hint_x=0.1))
        
        # Adicionar layout de exportação à view
        self.add_widget(self.export_layout)
        
        # Criar tabela de dados com ordenação por clique nos cabeçalhos
        self.data_table = MDDataTable(
            size_hint=(1, 0.85),
            use_pagination=False,
            rows_num=max(self.items_per_page, 100),  # Garantir que rows_num seja suficiente
            column_data=[
                ("Row", dp(15)),
                ("ID", dp(25)),
                ("Txt. Detc.", dp(110)),
                ("Idioma", dp(35)),
                ("Confiança", dp(50)),
                ("Criado em", dp(50)),
                ("Últ. Uso", dp(50)),
                ("Cont. de Uso", dp(45))
            ]
        )
        
        # Vincular eventos da tabela
        self.data_table.bind(on_row_press=self.on_row_press)
        self.data_table.bind(on_pagination=self.on_pagination)
        
        # Adicionar tabela à view
        self.add_widget(self.data_table)
        
        # Layout de navegação de páginas
        # --- INÍCIO DA REESTRUTURAÇÃO PARA PADRÃO UNIFICADO ---
        # Layout de paginação e seleção de itens por página
        self.pagination_card = MDCard(
            orientation='vertical',
            padding=[dp(8), dp(8), dp(8), dp(8)],
            size_hint=(1, None),
            height=dp(70),
            elevation=2,
            radius=[12, 12, 12, 12],
            md_bg_color=(0.97, 0.97, 0.97, 1)
        )
        self.pagination_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            adaptive_height=True,
            padding=[dp(0), dp(0), dp(0), dp(0)]
        )
        self.prev_button = MDRaisedButton(
            text="◀ Anterior",
            theme_icon_color="Custom",
            md_bg_color=(0.2, 0.6, 1, 1),
            text_color=(1, 1, 1, 1),
            on_release=lambda x: self.change_page(-1)
        )
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
        self.next_button = MDRaisedButton(
            text="Próxima ▶",
            theme_icon_color="Custom",
            md_bg_color=(0.2, 0.6, 1, 1),
            text_color=(1, 1, 1, 1),
            on_release=lambda x: self.change_page(1)
        )
        self.page_info_layout.add_widget(self.page_label)
        self.page_info_layout.add_widget(self.records_label)
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
        # Botão para selecionar itens por página
        self.items_per_page_button = MDRaisedButton(
            text=f"{self.items_per_page} por página",
            on_release=self.show_items_per_page_menu,
            md_bg_color=(0.2, 0.6, 1, 1),
            text_color=(1, 1, 1, 1),
            pos_hint={"center_y": 0.5}
        )
        self.items_per_page_layout.add_widget(self.items_per_page_label)
        self.items_per_page_layout.add_widget(self.items_per_page_button)
        self.pagination_layout.add_widget(self.items_per_page_layout)
        self.pagination_layout.add_widget(self.prev_button)
        self.pagination_layout.add_widget(self.page_info_layout)
        self.pagination_layout.add_widget(self.next_button)
        self.pagination_card.add_widget(self.pagination_layout)
        self.add_widget(self.pagination_card)
        # --- FIM DA REESTRUTURAÇÃO DE PAGINAÇÃO ---
    
    def show_lang_menu(self, button):
        # Exibe o menu dropdown para seleção de idioma
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
            width_mult=4,
        )
        self.lang_menu.open()
    
    def show_sort_menu(self, button):
        # Exibe o menu dropdown para seleção de ordenação
        sort_options = [
            ("ID ^", "id", "ASC"),
            ("ID v", "id", "DESC"),
            ("Texto ^", "text_results", "ASC"),
            ("Texto v", "text_results", "DESC"),
            ("Idioma ^", "source_lang", "ASC"),
            ("Idioma v", "source_lang", "DESC"),
            ("Confiança ^", "confidence", "ASC"),
            ("Confiança v", "confidence", "DESC"),
            ("Criação ^", "created_at", "ASC"),
            ("Criação v", "created_at", "DESC"),
            ("Último Uso ^", "last_used", "ASC"),
            ("Último Uso v", "last_used", "DESC"),
            ("Uso ^", "usage_count", "ASC"),
            ("Uso v", "usage_count", "DESC")
        ]
        
        menu_items = []
        for display_text, column, direction in sort_options:
            menu_items.append({
                "text": display_text,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=column, y=direction, z=display_text: self.set_sort_option(x, y, z),
            })
        
        self.sort_menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4,
        )
        self.sort_menu.open()
    
    def set_lang(self, lang):
        """Define o idioma selecionado e recarrega os dados com logs detalhados"""
        logger.debug("[DEBUG] Alterando idioma de '%s' para '%s'", self.selected_lang, lang)
        
        # Definir idioma selecionado
        self.selected_lang = None if lang == "Todos" else lang
        self.lang_button.text = f"Idioma: {lang}"
        logger.debug("[DEBUG] Texto do botão de idioma atualizado para: %s", self.lang_button.text)
        
        logger.debug("[DEBUG] Fechando menu de idiomas")
        self.lang_menu.dismiss()
        
        logger.debug("[DEBUG] Recarregando dados com novo filtro de idioma")
        self.load_data()
    

    
    def _update_sort_button_text(self):
        """Atualiza o texto do botão de ordenação com base na coluna e direção atuais"""
        # Mapeamento de colunas para nomes amigáveis
        column_names = {
            "id": "ID",
            "text_results": "Texto",
            "source_lang": "Idioma",
            "confidence": "Confiança",
            "created_at": "Criação",
            "last_used": "Último Uso",
            "usage_count": "Uso"
        }
        
        # Obter nome amigável da coluna
        column_display = column_names.get(self.current_sort_column, self.current_sort_column)
        
        # Adicionar ícone de direção
        arrow_icon = "^" if self.current_sort_direction == "ASC" else "v"
        
        # Atualizar texto do botão
        self.sort_button.text = f"Ordenar por: {column_display} {arrow_icon}"
    
    def set_sort_option(self, column, direction, display_text):
        """Define a opção de ordenação selecionada com logs detalhados"""
        logger.debug("[DEBUG] Alterando ordenação de '%s %s' para '%s %s'", 
                    self.current_sort_column, self.current_sort_direction, column, direction)
        
        self.current_sort_column = column
        self.current_sort_direction = direction
        
        # Adicionar ícones de seta ao texto do botão para indicar direção
        arrow_icon = "^" if direction == "ASC" else "v"
        column_name = display_text.replace(" ^", "").replace(" v", "")
        self.sort_button.text = f"Ordenar por: {column_name} {arrow_icon}"
        logger.debug("[DEBUG] Texto do botão de ordenação atualizado para: %s", self.sort_button.text)
        
        logger.debug("[DEBUG] Fechando menu de ordenação")
        self.sort_menu.dismiss()
        
        # Voltar para a primeira página ao ordenar
        self.page = 1
        logger.debug("[DEBUG] Página resetada para 1 devido à mudança de ordenação")
        
        # Recarregar dados com nova ordenação
        logger.debug("[DEBUG] Recarregando dados com nova ordenação: %s %s", column, direction)
        self.load_data()
    
    def load_data(self):
        """Carrega dados do banco de dados com logs detalhados"""
        logger.debug("[DEBUG] Iniciando carregamento de dados")
        
        # Obter dados do banco de dados
        search_text = self.search_field.text
        offset = (self.page - 1) * self.items_per_page
        
        # Preparar parâmetros de ordenação
        order_by = self.current_sort_column if self.current_sort_column else None
        order_direction = self.current_sort_direction
        
        logger.debug("[DEBUG] Parâmetros de consulta: página=%d, offset=%d, limite=%d, busca='%s', idioma=%s", 
                    self.page, offset, self.items_per_page, search_text or 'None', self.selected_lang or 'None')
        
        if order_by:
            logger.debug("[DEBUG] Aplicando ordenação: %s %s", order_by, order_direction)
        
        try:
            if not (self.app.db_manager.connection and self.app.db_manager.connection.is_connected()):
                logger.warning("[ERROR] Conexão com o banco de dados não está ativa")
                data = []
                total_count = 0
            else:
                logger.debug("[DEBUG] Executando consulta no banco de dados")
                data, total_count = self.app.db_manager.get_ocr_results(
                    offset=offset,
                    limit=self.items_per_page,
                    search_text=search_text if search_text else None,
                    source_lang=self.selected_lang,
                    order_by=order_by,
                    order_direction=order_direction
                )
                logger.debug("[DEBUG] Consulta executada com sucesso: %d registros encontrados", total_count)
        except Exception as e:
            logger.error("[ERROR] Erro ao carregar dados de OCR: %s", str(e))
            traceback.print_exc()
            data = []
            total_count = 0
        # Calcular total de páginas
        self.total_pages = max(1, (total_count + self.items_per_page - 1) // self.items_per_page)
        # Verificar se a página atual é válida
        if self.page > self.total_pages and self.total_pages > 0:
            self.page = self.total_pages
            return self.load_data()
        # Atualizar labels de informação com formatação melhorada
        self.page_label.text = f"Página {self.page} de {self.total_pages}"
        if total_count == 0:
            self.records_label.text = "Nenhum registro encontrado"
        elif total_count == 1:
            self.records_label.text = "1 registro encontrado"
        else:
            self.records_label.text = f"{total_count:,} registros encontrados".replace(',', '.')
        # Atualizar estado dos botões de navegação com melhor feedback visual
        self.prev_button.disabled = self.page <= 1
        self.next_button.disabled = self.page >= self.total_pages
        if self.prev_button.disabled:
            self.prev_button.md_bg_color = (0.6, 0.6, 0.6, 1)
            self.prev_button.text_color = (0.8, 0.8, 0.8, 1)
        else:
            self.prev_button.md_bg_color = (0.2, 0.6, 1, 1)
            self.prev_button.text_color = (1, 1, 1, 1)
        if self.next_button.disabled:
            self.next_button.md_bg_color = (0.6, 0.6, 0.6, 1)
            self.next_button.text_color = (0.8, 0.8, 0.8, 1)
        else:
            self.next_button.md_bg_color = (0.2, 0.6, 1, 1)
            self.next_button.text_color = (1, 1, 1, 1)
        # Criar mapeamento direto: posição visual -> dados reais (similar ao TranslationsView)
        self.row_mapping = {}  # Mapeamento: índice_visual -> dados_completos_da_linha
        
        # Formatar dados para a tabela
        table_data = []
        raw_data_for_debug = []  # Para comparação no debug
        
        for i, row in enumerate(data):
            # Armazenar mapeamento direto da posição visual para os dados reais
            self.row_mapping[i] = row  # Índice visual -> dados completos
            
            text_results = row.get('text_results_parsed', {})
            if isinstance(text_results, dict):
                text = text_results.get('text', '')
            elif isinstance(text_results, list) and text_results:
                text = text_results[0].get('text', '') if isinstance(text_results[0], dict) else str(text_results[0])
            else:
                text = ''
            # Limitar tamanho do texto para exibição na tabela e remover quebras de linha
            text = text.replace('\n', ' ').replace('\r', ' ')  # Remover quebras de linha
            text_display = (text[:80] + '...') if len(text) > 80 else text
            
            # Usar a confiança diretamente da coluna do banco de dados
            confidence = row.get('confidence', 0)
            confidence_display = f"{confidence:.2f}" if confidence is not None else 'N/A'
            
            created_at = row.get('created_at')
            created_at_display = created_at.strftime('%d/%m/%y %H:%M') if created_at else 'N/A'
            
            last_used = row.get('last_used')
            last_used_display = last_used.strftime('%d/%m/%y %H:%M') if last_used else 'N/A'
            
            # Dados formatados para o grid
            formatted_row = [
                str(i + 1),  # Row Index (posição visual) - NOVA COLUNA
                str(row.get('id', 'N/A')),
                text_display,
                row.get('source_lang', 'N/A'),
                confidence_display,
                created_at_display,
                last_used_display,
                str(row.get('usage_count', 0))
            ]
            table_data.append(formatted_row)
            
            # Dados brutos para debug
            raw_data_for_debug.append({
                'id': row.get('id'),
                'confidence_raw': row.get('confidence'),
                'confidence_parsed': confidence,
                'created_at_raw': row.get('created_at'),
                'last_used_raw': row.get('last_used'),
                'usage_count': row.get('usage_count')
            })
        
        # DEBUG: Mostrar dados que estão sendo exibidos no grid
        print(f"[DEBUG] === DADOS EXIBIDOS NO GRID ===")
        print(f"[DEBUG] Total de linhas no grid: {len(table_data)}")
        if table_data:
            print(f"[DEBUG] Primeira linha do grid: {table_data[0]}")
            if len(table_data) > 1:
                print(f"[DEBUG] Última linha do grid: {table_data[-1]}")
        
        # DEBUG: Mostrar dados brutos vs dados formatados (DIFF)
        print(f"[DEBUG] === COMPARAÇÃO: CONSULTA vs GRID ===")
        if data and table_data:
            for i in range(min(3, len(data))):  # Mostrar apenas os 3 primeiros para não poluir
                print(f"[DEBUG] Registro {i+1}:")
                print(f"[DEBUG]   Consulta - ID: {data[i].get('id')}, Confidence: {data[i].get('confidence')}, Created: {data[i].get('created_at')}")
                print(f"[DEBUG]   Grid     - ID: {table_data[i][0]}, Confidence: {table_data[i][3]}, Created: {table_data[i][4]}")
                
                # Verificar se há diferenças
                diff_found = False
                if str(data[i].get('id')) != table_data[i][0]:
                    print(f"[DEBUG]   ⚠️  DIFF ID: {data[i].get('id')} != {table_data[i][0]}")
                    diff_found = True
                if str(data[i].get('confidence')) != table_data[i][3].replace('.', '').replace(',', '.'):
                    print(f"[DEBUG]   ⚠️  DIFF Confidence: {data[i].get('confidence')} != {table_data[i][3]}")
                    diff_found = True
                if not diff_found:
                    print(f"[DEBUG]   ✅ Dados consistentes")
        
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
        """Mudar de página (anterior ou próxima) com logs detalhados"""
        logger.debug("[DEBUG] Mudança de página solicitada: direção=%d, página atual=%d, total de páginas=%d", 
                    direction, self.page, self.total_pages)
        
        new_page = self.page + direction
        logger.debug("[DEBUG] Nova página calculada: %d", new_page)
        
        if 1 <= new_page <= self.total_pages:
            logger.debug("[DEBUG] Página válida, mudando para página %d", new_page)
            self.page = new_page
            self.load_data()
        elif new_page < 1:
            # Se tentar ir para uma página menor que 1, ficar na página 1
            logger.warning("[DEBUG] Tentativa de ir para página %d < 1, mantendo página 1", new_page)
            self.page = 1
            self.load_data()
        elif new_page > self.total_pages:
            # Se tentar ir para uma página maior que o total, ficar na última página
            logger.warning("[DEBUG] Tentativa de ir para página %d > %d, mantendo última página", new_page, self.total_pages)
            self.page = self.total_pages
            self.load_data()
    

    
    def on_row_press(self, instance_table, instance_row):
        """Método chamado quando uma linha da tabela é pressionada - CORRIGIDO para calcular índice real da linha"""
        logger.debug("[DEBUG] on_row_press chamado - instance_row.index bruto: %s", instance_row.index)
        
        # CORREÇÃO: Calcular o índice real da linha baseado no número de colunas
        # A tabela tem 8 colunas (7 originais + 1 nova coluna Row), então dividimos o índice por 8
        number_of_columns = 8
        real_row_index = instance_row.index // number_of_columns
        logger.debug("[DEBUG] Índice real da linha calculado: %d (de %d // %d)", real_row_index, instance_row.index, number_of_columns)
        
        # Verificar se há dados na tabela
        if not instance_table.row_data or real_row_index >= len(instance_table.row_data):
            logger.error("[ERROR] Sem dados na tabela ou índice inválido. Dados: %d, Índice real: %d", 
                        len(instance_table.row_data) if instance_table.row_data else 0, real_row_index)
            return
            
        try:
            # Obter dados da linha usando o índice real calculado
            row_data = instance_table.row_data[real_row_index]
            logger.debug("[DEBUG] Dados da linha %d: %s", real_row_index, row_data)
            
            # Buscar no mapeamento usando o índice real da linha
            if real_row_index in self.row_mapping:
                ocr_result = self.row_mapping[real_row_index]
                logger.debug("[DEBUG] Resultado OCR encontrado no mapeamento:")
                logger.debug("[DEBUG] ID: %s", ocr_result.get('id'))
                logger.debug("[DEBUG] Texto detectado: %s...", str(ocr_result.get('text_results_parsed', {}))[:50])
            else:
                logger.error("[ERROR] Índice %d não encontrado no mapeamento", real_row_index)
                logger.debug("[DEBUG] Índices disponíveis no mapeamento: %s", list(self.row_mapping.keys()))
                return
        except (IndexError, ValueError) as e:
            logger.error("[ERROR] Erro ao obter dados da linha selecionada: %s", str(e))
            traceback.print_exc()
            return
        
        # Extrair dados
        logger.debug("[DEBUG] Extraindo dados do resultado OCR ID: %s", ocr_result.get('id'))
        text_results = ocr_result.get('text_results_parsed', {})
        if not text_results and ocr_result.get('text_results'):
            try:
                text_results = json.loads(ocr_result.get('text_results', '{}'))
                logger.debug("[DEBUG] text_results parseado com sucesso")
            except json.JSONDecodeError as e:
                logger.warning("[ERROR] Erro ao parsear text_results: %s", str(e))
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
            logger.debug("[DEBUG] Carregando imagem base64 para exibição")
            try:
                # Decodificar imagem base64
                image_data = base64.b64decode(ocr_result['image_base64'])
                logger.debug("[DEBUG] Imagem base64 decodificada com sucesso, tamanho: %d bytes", len(image_data))
                
                # Criar buffer de imagem
                buffer = io.BytesIO(image_data)
                # Carregar imagem
                coreimage = CoreImage(buffer, ext='png')
                logger.debug("[DEBUG] CoreImage criada com sucesso")
                
                # Criar widget de imagem
                image = Image(
                    texture=coreimage.texture,
                    size_hint=(1, 0.5),
                    allow_stretch=True,
                    keep_ratio=True
                )
                content_layout.add_widget(image)
                logger.debug("[DEBUG] Widget de imagem adicionado ao layout")
            except Exception as e:
                logger.error("[ERROR] Erro ao carregar imagem: %s", str(e))
                traceback.print_exc()
        else:
            logger.debug("[DEBUG] Nenhuma imagem base64 disponível para este resultado")
        
        # Adicionar informações de texto
        text_info = f"""**ID:** {ocr_result['id']}\n\n
                    **Texto Detectado:**\n{text}\n\n
                    **Idioma:** {ocr_result['source_lang']}\n
                    **Confiança:** {confidence:.2f}\n
                    **Criado em:** {created_at}\n
                    **Último Uso:** {last_used}\n
                    **Contagem de Uso:** {ocr_result.get('used_count', 'N/A')}\n
                    **Hash da Imagem:** {ocr_result.get('image_hash', 'N/A')}"""
        
        # Adicionar metadados se disponíveis
        if metadata:
            text_info += "\n\n**Metadados:**\n"
            for key, value in metadata.items():
                text_info += f"- {key}: {value}\n"
        
        # Mostrar diálogo com detalhes do resultado OCR
        logger.debug("[DEBUG] Criando diálogo de detalhes para resultado OCR ID: %s", ocr_result.get('id'))
        
        if self.dialog:
            logger.debug("[DEBUG] Fechando diálogo anterior")
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
        
        logger.debug("[DEBUG] Exibindo diálogo de detalhes")
        self.dialog.open()
    
    def show_items_per_page_menu(self, instance):
        # Exibe o menu dropdown para selecionar itens por página
        menu_items = [
            {
                "text": str(i),
                "viewclass": "OneLineListItem",
                "on_release": lambda x=i: self.set_items_per_page(x)
            }
            for i in [5, 10, 20, 30, 50]
        ]
        self.items_per_page_menu = MDDropdownMenu(
            caller=self.items_per_page_button,
            items=menu_items,
            width_mult=3
        )
        self.items_per_page_menu.open()

    def set_items_per_page(self, value):
        """Atualiza a quantidade de itens por página e recarrega os dados com logs detalhados"""
        logger.debug("[DEBUG] Alterando itens por página de %d para %d", self.items_per_page, value)
        
        self.items_per_page = value
        self.items_per_page_button.text = f"{value} por página"
        # Garantir que rows_num seja suficiente para exibir todos os itens solicitados
        self.data_table.rows_num = max(value, 100)
        logger.debug("[DEBUG] rows_num da tabela atualizado para %d", self.data_table.rows_num)
        
        self.page = 1
        logger.debug("[DEBUG] Página resetada para 1, recarregando dados")
        
        self.items_per_page_menu.dismiss()
        logger.debug("[DEBUG] Menu de itens por página fechado")
        
        self.load_data()
    
    def get_all_data_for_export(self):
        """Obtém todos os dados para exportação sem paginação com logs detalhados"""
        logger.debug("[DEBUG] Iniciando obtenção de dados para exportação")
        
        try:
            if not self.app.db_manager.connection or not self.app.db_manager.connection.is_connected():
                logger.error("[ERROR] Conexão com o banco de dados não está ativa")
                return []
            
            # Construir query base
            query = """
                SELECT 
                    id,
                    text_results,
                    source_lang,
                    confidence,
                    created_at,
                    last_used,
                    used_count
                FROM ocr_results
            """
            
            params = []
            conditions = []
            
            # Adicionar filtro de pesquisa se houver
            if hasattr(self, 'search_field') and self.search_field.text.strip():
                search_text = self.search_field.text.strip()
                conditions.append("text_results LIKE %s")
                params.append(f"%{search_text}%")
                logger.debug("[DEBUG] Filtro de pesquisa aplicado: '%s'", search_text)
            
            # Adicionar filtro de idioma se houver
            if hasattr(self, 'selected_lang') and self.selected_lang:
                conditions.append("source_lang = %s")
                params.append(self.selected_lang)
                logger.debug("[DEBUG] Filtro de idioma aplicado: '%s'", self.selected_lang)
            
            # Adicionar condições WHERE se houver
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                logger.debug("[DEBUG] Condições WHERE adicionadas: %s", " AND ".join(conditions))
            
            # Aplicar ordenação atual
            if hasattr(self, 'current_sort_column') and self.current_sort_column:
                order_clause = f" ORDER BY {self.current_sort_column} {self.current_sort_direction}"
                query += order_clause
                logger.debug("[DEBUG] Ordenação aplicada: %s %s", self.current_sort_column, self.current_sort_direction)
            else:
                # Ordenar por ID decrescente como padrão
                query += " ORDER BY id DESC"
                logger.debug("[DEBUG] Ordenação padrão aplicada: id DESC")
            
            logger.debug("[DEBUG] Query final para exportação: %s", query)
            logger.debug("[DEBUG] Parâmetros da query: %s", params)
            
            cursor = self.app.db_manager.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            
            logger.info("[DEBUG] Dados obtidos para exportação: %d registros", len(results))
            return results
            
        except Exception as e:
            logger.error("[ERROR] Erro ao obter dados para exportação: %s", str(e))
            traceback.print_exc()
            return []
    
    def export_to_csv(self, instance):
        """Exporta dados para arquivo CSV com logs detalhados"""
        logger.info("[DEBUG] Iniciando exportação para CSV")
        try:
            logger.debug("[DEBUG] Obtendo dados para exportação")
            data = self.get_all_data_for_export()
            if not data:
                logger.warning("[ERROR] Nenhum dado disponível para exportação CSV")
                self.show_export_dialog("Erro", "Nenhum dado disponível para exportação.")
                return
            
            logger.debug("[DEBUG] %d registros obtidos para exportação CSV", len(data))
            
            # Criar nome do arquivo com timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ocr_results_export_{timestamp}.csv"
            filepath = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            logger.debug("[DEBUG] Arquivo CSV será salvo em: %s", filepath)
            
            # Escrever arquivo CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Cabeçalho (incluindo coluna Row)
                writer.writerow([
                    'Row', 'ID', 'Texto Detectado', 'Idioma', 'Confiança', 
                    'Criado em', 'Último Uso', 'Contagem de Uso'
                ])
                
                # Dados
                for index, row in enumerate(data):
                    # Formatar datas
                    created_at = row.get('created_at')
                    created_at = created_at.strftime('%d/%m/%Y %H:%M:%S') if created_at else 'N/A'
                    
                    last_used = row.get('last_used')
                    last_used = last_used.strftime('%d/%m/%Y %H:%M:%S') if last_used else 'N/A'
                    
                    # Extrair texto do campo text_results (JSON)
                    text_results = row.get('text_results', '')
                    if text_results:
                        try:
                            text_data = json.loads(text_results) if isinstance(text_results, str) else text_results
                            if isinstance(text_data, dict):
                                detected_text = text_data.get('text', '')
                            elif isinstance(text_data, list) and text_data:
                                detected_text = text_data[0].get('text', '') if isinstance(text_data[0], dict) else str(text_data[0])
                            else:
                                detected_text = str(text_data)
                        except (json.JSONDecodeError, AttributeError):
                            detected_text = str(text_results)
                    else:
                        detected_text = ''
                    
                    csv_row = [
                        str(index + 1),  # Coluna Row
                        row.get('id', ''),
                        detected_text,
                        row.get('source_lang', ''),
                        row.get('confidence', ''),
                        created_at,
                        last_used,
                        row.get('used_count', '')
                    ]
                    writer.writerow(csv_row)
            
            logger.info("[DEBUG] Arquivo CSV criado com sucesso: %s", filepath)
            self.show_export_dialog("Sucesso", f"Arquivo CSV exportado com sucesso!\nLocal: {filepath}")
            
        except Exception as e:
            logger.error("[ERROR] Erro ao exportar CSV: %s", str(e))
            traceback.print_exc()
            self.show_export_dialog("Erro", f"Erro ao exportar CSV: {str(e)}")
    
    def export_to_json(self, instance):
        """Exporta dados para arquivo JSON com logs detalhados"""
        logger.info("[DEBUG] Iniciando exportação para JSON")
        try:
            logger.debug("[DEBUG] Obtendo dados para exportação JSON")
            data = self.get_all_data_for_export()
            if not data:
                logger.warning("[ERROR] Nenhum dado disponível para exportação JSON")
                self.show_export_dialog("Erro", "Nenhum dado disponível para exportação.")
                return
            
            logger.debug("[DEBUG] %d registros obtidos para exportação JSON", len(data))
            
            # Criar nome do arquivo com timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ocr_results_export_{timestamp}.json"
            filepath = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            logger.debug("[DEBUG] Arquivo JSON será salvo em: %s", filepath)
            
            # Converter dados para formato JSON serializável
            json_data = []
            for index, row in enumerate(data):
                # Formatar datas para string
                created_at = row.get('created_at')
                created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else None
                
                last_used = row.get('last_used')
                last_used = last_used.strftime('%Y-%m-%d %H:%M:%S') if last_used else None
                
                # Extrair texto do campo text_results (JSON)
                text_results = row.get('text_results', '')
                if text_results:
                    try:
                        text_data = json.loads(text_results) if isinstance(text_results, str) else text_results
                        if isinstance(text_data, dict):
                            detected_text = text_data.get('text', '')
                        elif isinstance(text_data, list) and text_data:
                            detected_text = text_data[0].get('text', '') if isinstance(text_data[0], dict) else str(text_data[0])
                        else:
                            detected_text = str(text_data)
                    except (json.JSONDecodeError, AttributeError):
                        detected_text = str(text_results)
                else:
                    detected_text = ''
                
                json_row = {
                    'row': index + 1,  # Coluna Row
                    'id': row.get('id'),
                    'detected_text': detected_text,
                    'language': row.get('source_lang'),
                    'confidence': float(row.get('confidence', 0)) if row.get('confidence') is not None else None,
                    'created_at': created_at,
                    'last_used': last_used,
                    'used_count': row.get('used_count', 0)
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
                    'ocr_results': json_data
                }, jsonfile, indent=2, ensure_ascii=False)
            
            logger.info("[DEBUG] Arquivo JSON criado com sucesso: %s", filepath)
            self.show_export_dialog("Sucesso", f"Arquivo JSON exportado com sucesso!\nLocal: {filepath}")
            
        except Exception as e:
            logger.error("[ERROR] Erro ao exportar JSON: %s", str(e))
            traceback.print_exc()
            self.show_export_dialog("Erro", f"Erro ao exportar JSON: {str(e)}")
    
    def export_to_pdf(self, instance):
        """Exporta dados para arquivo PDF com logs detalhados"""
        logger.info("[DEBUG] Iniciando exportação para PDF")
        try:
            logger.debug("[DEBUG] Obtendo dados para exportação PDF")
            data = self.get_all_data_for_export()
            if not data:
                logger.warning("[ERROR] Nenhum dado disponível para exportação PDF")
                self.show_export_dialog("Erro", "Nenhum dado disponível para exportação.")
                return
            
            logger.debug("[DEBUG] %d registros obtidos para exportação PDF", len(data))
            
            # Criar nome do arquivo com timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ocr_results_export_{timestamp}.pdf"
            filepath = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            logger.debug("[DEBUG] Arquivo PDF será salvo em: %s", filepath)
            
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
            title = Paragraph("Relatório de Resultados OCR - RetroArch", title_style)
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
            
            # Preparar cabeçalho da tabela (incluindo coluna Row)
            headers = ['Row', 'ID', 'Texto Detectado', 'Idioma', 'Confiança', 'Criação', 'Últ. Uso', 'Usos']
            
            # Preparar dados das linhas
            rows_data = []
            for index, row in enumerate(data):
                # Extrair texto do campo text_results (JSON)
                text_results = row.get('text_results', '')
                if text_results:
                    try:
                        text_data = json.loads(text_results) if isinstance(text_results, str) else text_results
                        if isinstance(text_data, dict):
                            detected_text = text_data.get('text', '')
                        elif isinstance(text_data, list) and text_data:
                            detected_text = text_data[0].get('text', '') if isinstance(text_data[0], dict) else str(text_data[0])
                        else:
                            detected_text = str(text_data)
                    except (json.JSONDecodeError, AttributeError):
                        detected_text = str(text_results)
                else:
                    detected_text = ''
                
                # Truncar textos longos para caber na página
                detected_text = detected_text[:40] + '...' if len(detected_text) > 40 else detected_text
                
                # Formatar datas
                created_at = row.get('created_at')
                created_at = created_at.strftime('%d/%m/%y %H:%M') if created_at else 'N/A'
                
                last_used = row.get('last_used')
                last_used = last_used.strftime('%d/%m/%y %H:%M') if last_used else 'N/A'
                
                # Formatar confiança
                confidence = f"{row.get('confidence', 0):.2f}" if row.get('confidence') is not None else 'N/A'
                
                pdf_row = [
                    str(index + 1),  # Coluna Row
                    str(row.get('id', '')),
                    detected_text,
                    str(row.get('source_lang', '')),
                    confidence,
                    created_at,
                    last_used,
                    str(row.get('used_count', 0))
                ]
                rows_data.append(pdf_row)
            
            # Dividir dados em páginas (20 linhas por página para garantir que caiba com cabeçalho)
            rows_per_page = 20
            col_widths = [0.5*inch, 0.6*inch, 3.2*inch, 0.9*inch, 0.9*inch, 1.1*inch, 1.1*inch, 0.7*inch]
            
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
            
            logger.info("[DEBUG] Arquivo PDF criado com sucesso: %s", filepath)
            self.show_export_dialog("Sucesso", f"Arquivo PDF exportado com sucesso!\nLocal: {filepath}")
            
        except Exception as e:
            logger.error("[ERROR] Erro ao exportar PDF: %s", str(e))
            traceback.print_exc()
            self.show_export_dialog("Erro", f"Erro ao exportar PDF: {str(e)}")
    
    def show_export_dialog(self, title, message):
        """Mostra diálogo de resultado da exportação com logs"""
        logger.debug("[DEBUG] Exibindo diálogo de exportação: %s - %s", title, message)
        
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
# views/statistics_view.py
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from kivy.clock import Clock
from kivy_garden.graph import Graph, MeshLinePlot, SmoothLinePlot, BarPlot
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image

class StatisticsView(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)
        self.app = MDApp.get_running_app()
        self.days = 30  # Padrão: últimos 30 dias
        
        # Criar a interface
        self._create_ui()
        
        # Carregar dados iniciais
        Clock.schedule_once(lambda dt: self.load_data(), 0.5)
    
    def _create_ui(self):
        # Área de controles
        self.controls_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        # Seletor de período
        self.days_button = MDRaisedButton(
            text="Últimos 30 dias",
            size_hint_x=0.3,
            on_release=self.show_days_menu
        )
        
        # Botão de atualização
        self.refresh_button = MDRaisedButton(
            text="Atualizar",
            size_hint_x=0.2,
            on_release=lambda x: self.load_data()
        )
        
        # Adicionar widgets ao layout de controles
        self.controls_layout.add_widget(self.days_button)
        self.controls_layout.add_widget(self.refresh_button)
        
        # Adicionar layout de controles à view
        self.add_widget(self.controls_layout)
        
        # Layout para estatísticas gerais
        self.stats_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(100),
            spacing=dp(10),
            padding=dp(10)
        )
        
        # Campos de estatísticas gerais
        self.total_translations = MDTextField(
            text="Total de Traduções: 0",
            readonly=True,
            size_hint_x=0.25
        )
        
        self.total_ocr_results = MDTextField(
            text="Total de Resultados OCR: 0",
            readonly=True,
            size_hint_x=0.25
        )
        
        self.avg_translation_confidence = MDTextField(
            text="Confiança Média (Traduções): 0%",
            readonly=True,
            size_hint_x=0.25
        )
        
        self.avg_ocr_confidence = MDTextField(
            text="Confiança Média (OCR): 0%",
            readonly=True,
            size_hint_x=0.25
        )
        
        # Adicionar campos ao layout de estatísticas
        self.stats_layout.add_widget(self.total_translations)
        self.stats_layout.add_widget(self.total_ocr_results)
        self.stats_layout.add_widget(self.avg_translation_confidence)
        self.stats_layout.add_widget(self.avg_ocr_confidence)
        
        # Adicionar layout de estatísticas à view
        self.add_widget(self.stats_layout)
        
        # Layout para gráficos
        self.graphs_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10)
        )
        
        # Criar gráficos
        self.requests_graph = Graph(
            xlabel='Data',
            ylabel='Requisições',
            x_ticks_minor=5,
            x_ticks_major=10,
            y_ticks_major=10,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=30,
            ymin=0,
            ymax=100,
            size_hint_y=0.4
        )
        
        self.cache_hits_graph = Graph(
            xlabel='Data',
            ylabel='Acertos de Cache (%)',
            x_ticks_minor=5,
            x_ticks_major=10,
            y_ticks_major=10,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=30,
            ymin=0,
            ymax=100,
            size_hint_y=0.4
        )
        
        self.processing_time_graph = Graph(
            xlabel='Data',
            ylabel='Tempo Médio (ms)',
            x_ticks_minor=5,
            x_ticks_major=10,
            y_ticks_major=100,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=30,
            ymin=0,
            ymax=1000,
            size_hint_y=0.4
        )
        
        # Adicionar gráficos ao layout
        self.graphs_layout.add_widget(self.requests_graph)
        self.graphs_layout.add_widget(self.cache_hits_graph)
        self.graphs_layout.add_widget(self.processing_time_graph)
        
        # Adicionar layout de gráficos à view
        self.add_widget(self.graphs_layout)
    
    def show_days_menu(self, button):
        from kivymd.uix.menu import MDDropdownMenu
        
        # Criar menu de seleção de período
        days_options = [7, 15, 30, 60, 90]
        menu_items = []
        
        for days in days_options:
            menu_items.append({
                "text": f"Últimos {days} dias",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=days: self.set_days(x),
            })
        
        self.days_menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4
        )
        
        self.days_menu.open()
    
    def set_days(self, days):
        # Definir período selecionado
        self.days = days
        self.days_button.text = f"Últimos {days} dias"
        self.days_menu.dismiss()
        self.load_data()
    
    def load_data(self):
        try:
            # Verificar se a conexão com o banco de dados está ativa
            if not self.app.db_manager.connection or not self.app.db_manager.connection.is_connected():
                print("Aviso: Conexão com o banco de dados não está ativa")
                # Definir valores padrão
                general_stats = {
                    'total_translations': 0,
                    'total_ocr_results': 0,
                    'avg_translation_confidence': 0.0,
                    'avg_ocr_confidence': 0.0
                }
                daily_stats = []
            else:
                # Obter estatísticas gerais
                general_stats = self.app.db_manager.get_general_statistics()
                
                # Obter estatísticas diárias
                daily_stats = self.app.db_manager.get_daily_statistics(self.days)
            
            # Atualizar campos de estatísticas gerais
            self.total_translations.text = f"Total de Traduções: {general_stats['total_translations']}"
            self.total_ocr_results.text = f"Total de Resultados OCR: {general_stats['total_ocr_results']}"
            self.avg_translation_confidence.text = f"Confiança Média (Traduções): {general_stats['avg_translation_confidence']:.2f}%"
            self.avg_ocr_confidence.text = f"Confiança Média (OCR): {general_stats['avg_ocr_confidence']:.2f}%"
            
            # Atualizar gráficos
            self._update_graphs(daily_stats)
        except Exception as e:
            print(f"Erro ao carregar estatísticas: {e}")
            # Definir valores padrão em caso de erro
            self.total_translations.text = "Total de Traduções: 0"
            self.total_ocr_results.text = "Total de Resultados OCR: 0"
            self.avg_translation_confidence.text = "Confiança Média (Traduções): 0.00%"
            self.avg_ocr_confidence.text = "Confiança Média (OCR): 0.00%"
    
    def _update_graphs(self, daily_stats):
        # Limpar gráficos anteriores
        # Remover todos os plots existentes
        if hasattr(self.requests_graph, 'plots') and self.requests_graph.plots:
            for plot in list(self.requests_graph.plots):
                self.requests_graph.remove_plot(plot)
                
        if hasattr(self.cache_hits_graph, 'plots') and self.cache_hits_graph.plots:
            for plot in list(self.cache_hits_graph.plots):
                self.cache_hits_graph.remove_plot(plot)
                
        if hasattr(self.processing_time_graph, 'plots') and self.processing_time_graph.plots:
            for plot in list(self.processing_time_graph.plots):
                self.processing_time_graph.remove_plot(plot)
        
        # Configurar limites dos gráficos
        num_days = max(1, len(daily_stats))  # Garantir que num_days seja pelo menos 1
        
        # Definir limites mínimos e máximos para evitar divisão por zero
        self.requests_graph.xmin = 0
        self.requests_graph.xmax = max(1, num_days)  # Garantir que xmax > xmin
        
        self.cache_hits_graph.xmin = 0
        self.cache_hits_graph.xmax = max(1, num_days)  # Garantir que xmax > xmin
        
        self.processing_time_graph.xmin = 0
        self.processing_time_graph.xmax = max(1, num_days)  # Garantir que xmax > xmin
        
        # Encontrar valores máximos para escala dos gráficos
        max_requests = max([stat.get('total_requests', 0) for stat in daily_stats]) if daily_stats else 10
        max_processing_time = max([stat.get('avg_processing_time', 0) for stat in daily_stats]) if daily_stats else 100
        
        # Ajustar escala dos gráficos
        self.requests_graph.ymin = 0
        self.requests_graph.ymax = max(10, max_requests * 1.2)
        
        self.cache_hits_graph.ymin = 0
        self.cache_hits_graph.ymax = 100  # Porcentagem sempre vai de 0 a 100
        
        self.processing_time_graph.ymin = 0
        self.processing_time_graph.ymax = max(100, max_processing_time * 1.2)
        
        # Se não houver dados, adicionar dados fictícios para evitar erros
        if not daily_stats:
            # Adicionar um ponto fictício para cada gráfico para evitar erros
            dummy_plot1 = SmoothLinePlot(color=[0, 0, 1, 1])
            dummy_plot1.points = [(0, 0), (1, 0)]  # Dois pontos para formar uma linha
            
            dummy_plot2 = SmoothLinePlot(color=[1, 0, 0, 1])
            dummy_plot2.points = [(0, 0), (1, 0)]
            
            dummy_plot3 = SmoothLinePlot(color=[0, 1, 0, 1])
            dummy_plot3.points = [(0, 0), (1, 0)]
            
            dummy_plot4 = SmoothLinePlot(color=[1, 0.5, 0, 1])
            dummy_plot4.points = [(0, 0), (1, 0)]
            
            # Adicionar plots fictícios aos gráficos
            self.requests_graph.add_plot(dummy_plot1)
            self.cache_hits_graph.add_plot(dummy_plot2)
            self.cache_hits_graph.add_plot(dummy_plot3)
            self.processing_time_graph.add_plot(dummy_plot4)
            
            return  # Sair da função, não há mais nada a fazer
        
        # Criar plots para dados reais
        requests_plot = SmoothLinePlot(color=[0, 0, 1, 1])
        ocr_cache_plot = SmoothLinePlot(color=[1, 0, 0, 1])
        translation_cache_plot = SmoothLinePlot(color=[0, 1, 0, 1])
        processing_time_plot = SmoothLinePlot(color=[1, 0.5, 0, 1])
        
        # Preparar dados para os plots
        requests_data = []
        ocr_cache_data = []
        translation_cache_data = []
        processing_time_data = []
        
        # Garantir que temos pelo menos dois pontos para cada plot
        # para evitar problemas com a biblioteca de gráficos
        if len(daily_stats) == 1:
            # Adicionar um ponto zero no início para ter pelo menos dois pontos
            requests_data.append((0, 0))
            ocr_cache_data.append((0, 0))
            translation_cache_data.append((0, 0))
            processing_time_data.append((0, 0))
        
        for i, stat in enumerate(daily_stats):
            x = i + 1  # Posição no eixo X (dias)
            
            # Dados de requisições
            total_requests = stat.get('total_requests', 0)
            requests_data.append((x, total_requests))
            
            # Dados de acertos de cache
            if total_requests > 0:
                ocr_cache_rate = (stat.get('ocr_cache_hits', 0) / total_requests) * 100
                translation_cache_rate = (stat.get('translation_cache_hits', 0) / total_requests) * 100
            else:
                ocr_cache_rate = 0
                translation_cache_rate = 0
            
            ocr_cache_data.append((x, ocr_cache_rate))
            translation_cache_data.append((x, translation_cache_rate))
            
            # Dados de tempo de processamento
            processing_time_data.append((x, stat.get('avg_processing_time', 0)))
        
        # Atribuir dados aos plots
        requests_plot.points = requests_data
        ocr_cache_plot.points = ocr_cache_data
        translation_cache_plot.points = translation_cache_data
        processing_time_plot.points = processing_time_data
        
        # Adicionar plots aos gráficos
        self.requests_graph.add_plot(requests_plot)
        self.cache_hits_graph.add_plot(ocr_cache_plot)
        self.cache_hits_graph.add_plot(translation_cache_plot)
        self.processing_time_graph.add_plot(processing_time_plot)
        
        # Adicionar legendas
        # Nota: Kivy Graph não suporta legendas nativamente, então podemos adicionar labels
        # ou criar uma legenda personalizada
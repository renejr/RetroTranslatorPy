# views/main_screen.py
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout

class Tab(MDFloatLayout, MDTabsBase):
    """Classe para as abas da interface"""
    pass

class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.current_tab = None
        
    def on_enter(self):
        # Inicializar as views quando a tela principal é exibida
        from views.translations_view import TranslationsView
        from views.ocr_results_view import OCRResultsView
        from views.statistics_view import StatisticsView
        
        self.translations_view = TranslationsView()
        self.ocr_results_view = OCRResultsView()
        self.statistics_view = StatisticsView()
        
        # Adicionar as views às abas
        self.ids.tab_translations.add_widget(self.translations_view)
        self.ids.tab_ocr_results.add_widget(self.ocr_results_view)
        self.ids.tab_statistics.add_widget(self.statistics_view)
        
        # Definir a aba atual
        self.current_tab = "Traduções"
    
    def on_tab_switch(self, tab_text):
        # Atualizar a aba atual
        self.current_tab = tab_text
    
    def refresh_current_tab(self):
        # Atualizar os dados da aba atual
        if self.current_tab == "Traduções":
            self.translations_view.load_data()
        elif self.current_tab == "Resultados OCR":
            self.ocr_results_view.load_data()
        elif self.current_tab == "Estatísticas":
            self.statistics_view.load_data()
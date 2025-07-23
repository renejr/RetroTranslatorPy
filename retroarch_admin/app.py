# app.py
# Configurações do Kivy
from kivy.config import Config
# Configuração para iniciar a janela maximizada
Config.set('graphics', 'window_state', 'maximized')
# Configuração para desabilitar os pontos vermelhos do multitouch
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.core.window import Window

# Importar gerenciador de banco de dados
from database_manager import DatabaseManager

class RetroArchAdminApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "RetroArch AI Service - Admin Interface"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        self.db_manager = DatabaseManager()
        
    def build(self):
        # Carregar arquivos KV
        self.load_kv_files()
        
        # Conectar ao banco de dados primeiro
        connection_success = self.db_manager.connect()
        if not connection_success:
            print("Erro: Não foi possível conectar ao banco de dados. Verifique as configurações.")
        
        # Criar gerenciador de telas
        self.screen_manager = MDScreenManager()
        
        # Adicionar telas
        from views.main_screen import MainScreen
        self.main_screen = MainScreen(name="main")
        self.screen_manager.add_widget(self.main_screen)
        
        return self.screen_manager
    
    def load_kv_files(self):
        # Carregar arquivos KV
        Builder.load_file("kv/main.kv")
        Builder.load_file("kv/translations.kv")
        Builder.load_file("kv/ocr_results.kv")
        Builder.load_file("kv/statistics.kv")
    
    def on_stop(self):
        # Fechar conexão com o banco de dados ao sair
        self.db_manager.disconnect()
    
    def open_menu(self, instance):
        # Função para abrir o menu lateral com opções
        from kivymd.uix.menu import MDDropdownMenu
        
        menu_items = [
            {
                "text": "Atualizar dados",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=1: self.refresh_data(None),
            },
            {
                "text": "Sobre",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=2: self.show_about(),
            },
            {
                "text": "Sair",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=3: self.exit_app(),
            },
        ]
        
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=3,
            position="auto",
            radius=[20, 7, 20, 7],
        )
        
        self.menu.caller = instance
        self.menu.open()
    
    def refresh_data(self, instance):
        # Função para atualizar os dados exibidos
        if hasattr(self.main_screen, 'refresh_current_tab'):
            self.main_screen.refresh_current_tab()
    
    def show_about(self):
        # Exibir informações sobre o aplicativo
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        
        self.about_dialog = MDDialog(
            title="Sobre RetroArch Admin",
            text="RetroArch AI Service - Interface de Administração\n\n"
                 "Versão: 1.0.0\n"
                 "Desenvolvido para gerenciar o serviço de IA do RetroArch.",
            buttons=[
                MDFlatButton(
                    text="FECHAR",
                    on_release=lambda x: self.about_dialog.dismiss()
                )
            ],
        )
        self.about_dialog.open()
    
    def exit_app(self):
        """Função para fechar a aplicação"""
        # Fechar o menu se estiver aberto
        if hasattr(self, 'menu'):
            self.menu.dismiss()
        
        # Fechar a aplicação
        self.stop()
    
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        # Função chamada quando o usuário muda de aba
        if hasattr(self.main_screen, 'on_tab_switch'):
            self.main_screen.on_tab_switch(tab_text)
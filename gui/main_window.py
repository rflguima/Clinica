import customtkinter as ctk
from database import DatabaseManager
from .login_window import LoginWindow
from .main_interface import MainInterface

class ClinicaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão de Clínica")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        self.root.attributes('-fullscreen', True)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.db = DatabaseManager()
        self.profissional_logado = None
        
        self.container = ctk.CTkFrame(root, fg_color="white")
        self.container.pack(fill="both", expand=True)
        
        self.criar_tela_login()
    
    def _limpar_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def criar_tela_login(self):
        self._limpar_container()
        self.login_window = LoginWindow(self.container, self.db, self.on_login_success)
        self.login_window.pack(fill="both", expand=True)

    def on_login_success(self, profissional):
        self.profissional_logado = profissional
        self.criar_interface_principal()
    
    def criar_interface_principal(self):
        self._limpar_container()
        self.main_interface = MainInterface(self.container, self.db, self.profissional_logado, self.fazer_logout)
        self.main_interface.pack(fill="both", expand=True)
    
    def fazer_logout(self):
        self.profissional_logado = None
        self.criar_tela_login()
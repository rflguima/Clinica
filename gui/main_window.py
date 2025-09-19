import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from database import DatabaseManager
from models import Profissional
from services import AuthService
from .login_window import LoginWindow
from .main_interface import MainInterface

class ClinicaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão de Clínica")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        self.setup_styles()
        self.db = DatabaseManager()
        self.profissional_logado = None
        
        self.criar_tela_login()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Custom.Treeview', font=('Arial', 10), rowheight=25)
        style.configure('Custom.Treeview.Heading', font=('Arial', 10, 'bold'))
        style.configure('CalendarDay.TButton', font=('Arial', 10), padding=5)
        style.configure('Today.TButton', font=('Arial', 10, 'bold'), foreground='blue', padding=5)

    def criar_tela_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.login_window = LoginWindow(self.root, self.db, self.on_login_success, self.on_cadastrar_profissional)
    
    def on_login_success(self, profissional):
        self.profissional_logado = profissional
        self.criar_interface_principal()
    
    def on_cadastrar_profissional(self):
        # Callback para quando um novo profissional é cadastrado
        self.login_window.carregar_profissionais()
    
    def criar_interface_principal(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.main_interface = MainInterface(self.root, self.db, self.profissional_logado, self.fazer_logout)
    
    def fazer_logout(self):
        self.profissional_logado = None
        self.criar_tela_login()
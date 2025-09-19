import tkinter as tk
from tkinter import ttk
from datetime import datetime, date
from .tabs.calendario_tab import CalendarioTab
from .tabs.agendamentos_tab import AgendamentosTab
from .tabs.pacientes_tab import PacientesTab
from .tabs.profissionais_tab import ProfissionaisTab
from .tabs.procedimentos_tab import ProcedimentosTab

class MainInterface:
    def __init__(self, root, db, profissional_logado, logout_callback):
        self.root = root
        self.db = db
        self.profissional_logado = profissional_logado
        self.logout_callback = logout_callback
        
        self.criar_interface()
    
    def criar_interface(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(header_frame, text=f"Usuário: {self.profissional_logado.nome} - {self.profissional_logado.especialidade}", style='Heading.TLabel').pack(side='left')
        ttk.Button(header_frame, text="Logout", command=self.logout_callback).pack(side='right')
        
        # Notebook com abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Criar abas
        self.calendario_tab = CalendarioTab(self.notebook, self.db, self.profissional_logado)
        self.agendamentos_tab = AgendamentosTab(self.notebook, self.db, self.profissional_logado)
        self.pacientes_tab = PacientesTab(self.notebook, self.db, self.profissional_logado)
        self.profissionais_tab = ProfissionaisTab(self.notebook, self.db, self.profissional_logado)
        self.procedimentos_tab = ProcedimentosTab(self.notebook, self.db, self.profissional_logado)
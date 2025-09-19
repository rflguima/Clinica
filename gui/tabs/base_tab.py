from tkinter import ttk

class BaseTab:
    def __init__(self, notebook, db, profissional_logado, tab_name):
        self.notebook = notebook
        self.db = db
        self.profissional_logado = profissional_logado
        
        self.frame = ttk.Frame(notebook)
        self.notebook.add(self.frame, text=tab_name)
        
        self.criar_interface()
    
    def criar_interface(self):
        """Método a ser implementado pelas classes filhas"""
        pass
import tkinter as tk
from tkinter import ttk, messagebox
from models import Profissional
from services import AuthService
from .dialogs.profissional_dialog import ProfissionalDialog

class LoginWindow:
    def __init__(self, root, db, login_callback, cadastro_callback):
        self.root = root
        self.db = db
        self.login_callback = login_callback
        self.cadastro_callback = cadastro_callback
        
        self.criar_interface()
        self.carregar_profissionais()
    
    def criar_interface(self):
        login_frame = ttk.Frame(self.root)
        login_frame.pack(expand=True, fill='both', padx=50, pady=50)
        
        ttk.Label(login_frame, text="Sistema de Gestão de Clínica", style='Title.TLabel').pack(pady=30)
        ttk.Label(login_frame, text="Selecione seu perfil profissional", font=('Arial', 12)).pack(pady=10)
        
        select_frame = ttk.Frame(login_frame)
        select_frame.pack(pady=30)
        
        ttk.Label(select_frame, text="Profissional:", font=('Arial', 11)).pack(anchor='w')
        self.profissional_var = tk.StringVar()
        self.profissional_combo = ttk.Combobox(select_frame, textvariable=self.profissional_var, width=40, font=('Arial', 11), state='readonly')
        self.profissional_combo.pack(pady=5)
        
        # Campo para código de acesso
        ttk.Label(select_frame, text="Código de Acesso (6 dígitos):", font=('Arial', 11)).pack(anchor='w', pady=(20, 0))
        self.codigo_var = tk.StringVar()
        self.codigo_entry = ttk.Entry(select_frame, textvariable=self.codigo_var, width=40, font=('Arial', 11), show='*')
        self.codigo_entry.pack(pady=5)
        
        btn_frame = ttk.Frame(login_frame)
        btn_frame.pack(pady=30)
        ttk.Button(btn_frame, text="Entrar", command=self.fazer_login, width=15).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Cadastrar Novo Profissional", command=self.cadastrar_profissional_inicial, width=25).pack(side='left', padx=10)
        
        # Bind Enter key
        self.codigo_entry.bind('<Return>', lambda e: self.fazer_login())
    
    def carregar_profissionais(self):
        profissionais = self.db.get_profissionais()
        valores = [f"{prof[1]} - {prof[2]} (CRM: {prof[3]})" for prof in profissionais]
        self.profissional_combo['values'] = valores
        if valores:
            self.profissional_combo.current(0)
    
    def cadastrar_profissional_inicial(self):
        dialog = ProfissionalDialog(self.root, self.db)
        if dialog.result:
            self.carregar_profissionais()
            self.cadastro_callback()
    
    def fazer_login(self):
        if not self.profissional_var.get():
            messagebox.showwarning("Aviso", "Selecione um profissional!")
            return
        
        if not self.codigo_var.get():
            messagebox.showwarning("Aviso", "Digite o código de acesso!")
            return
        
        codigo_digitado = self.codigo_var.get().strip()
        if not AuthService.validar_codigo_acesso(codigo_digitado):
            messagebox.showerror("Erro", "O código de acesso deve ter exatamente 6 dígitos!")
            return
        
        texto_selecionado = self.profissional_var.get()
        profissionais = self.db.get_profissionais()
        
        profissional_encontrado = None
        for prof in profissionais:
            if f"{prof[1]} - {prof[2]} (CRM: {prof[3]})" == texto_selecionado:
                profissional_encontrado = prof
                break
        
        if profissional_encontrado:
            # Verificar código de acesso
            if self.db.verificar_codigo_acesso(profissional_encontrado[0], codigo_digitado):
                profissional = Profissional.from_tuple(profissional_encontrado)
                self.login_callback(profissional)
            else:
                messagebox.showerror("Erro", "Código de acesso incorreto!")
                self.codigo_var.set("")  # Limpar campo
        else:
            messagebox.showerror("Erro", "Profissional não encontrado!")
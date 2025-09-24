import customtkinter as ctk
from tkinter import messagebox
from models import Profissional
from services import AuthService
from .dialogs.profissional_dialog import ProfissionalDialog 

class LoginWindow(ctk.CTkFrame):
    def __init__(self, parent, db, login_callback):
        super().__init__(parent, fg_color="#3786c2")
        self.db = db
        self.login_callback = login_callback
        
        self.criar_interface()
        self.carregar_profissionais()
    
    def criar_interface(self):
        login_frame = ctk.CTkFrame(self, width=450, height=550, fg_color="white", border_width=1, border_color="#dbdbdb")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        content_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8)

        ctk.CTkLabel(content_frame, text="Gestão de Clínica", font=ctk.CTkFont(size=28, weight="bold"), text_color="#333").pack(pady=(20, 25))
        
        ctk.CTkLabel(content_frame, text="Selecione seu perfil:", anchor='w', font=ctk.CTkFont(size=14)).pack(fill='x')
        self.profissional_var = ctk.StringVar()
        self.profissional_combo = ctk.CTkComboBox(content_frame, variable=self.profissional_var, state='readonly', height=35)
        self.profissional_combo.pack(pady=(5, 20), fill='x')
        
        ctk.CTkLabel(content_frame, text="Código de Acesso:", anchor='w', font=ctk.CTkFont(size=14)).pack(fill='x')
        self.codigo_var = ctk.StringVar()
        self.codigo_entry = ctk.CTkEntry(content_frame, textvariable=self.codigo_var, show='*', height=35)
        self.codigo_entry.pack(pady=5, fill='x')
        self.codigo_entry.bind('<Return>', lambda e: self.fazer_login())

        ctk.CTkButton(content_frame, text="Entrar", command=self.fazer_login, height=40).pack(pady=20, fill='x')
        
        ctk.CTkButton(content_frame, text="Cadastrar Novo Profissional", fg_color="transparent", border_width=1, text_color="#555", hover_color="#f0f0f0", height=40, command=self.cadastrar_profissional).pack(pady=(0, 10), fill='x')

        # ALTERAÇÃO AQUI: Botão "Sair" movido para dentro do card
        ctk.CTkButton(
            content_frame, text="Sair", 
            fg_color="#df4e4e", 
            border_width=1,
            text_color="#fdfdfd",
            border_color="#c94444",
            hover_color="#df4646", 
            height=40, 
            command=self.fechar_programa
        ).pack(pady=(0, 20), fill='x')

    def fechar_programa(self):
        self.winfo_toplevel().destroy()

    def cadastrar_profissional(self):
        dialog = ProfissionalDialog(self, self.db)
        if hasattr(dialog, 'result') and dialog.result:
            self.carregar_profissionais()

    def carregar_profissionais(self):
        profissionais = self.db.get_profissionais()
        if profissionais:
            valores = [f"{prof[1]} - {prof[2]}" for prof in profissionais]
            self.profissional_combo.configure(values=valores)
            if valores:
                self.profissional_combo.set(valores[0])
    
    def fazer_login(self):
        if not self.profissional_var.get() or not self.codigo_var.get():
            messagebox.showwarning("Aviso", "Selecione um profissional e digite o código de acesso.")
            return
        
        codigo_digitado = self.codigo_var.get().strip()
        if not AuthService.validar_codigo_acesso(codigo_digitado):
            messagebox.showerror("Erro", "O código de acesso deve ter exatamente 6 dígitos.")
            return
        
        texto_selecionado = self.profissional_var.get()
        profissionais = self.db.get_profissionais()
        
        profissional_encontrado = None
        for prof in profissionais:
            if f"{prof[1]} - {prof[2]}" == texto_selecionado:
                profissional_encontrado = prof
                break
        
        if profissional_encontrado:
            if self.db.verificar_codigo_acesso(profissional_encontrado[0], codigo_digitado):
                profissional = Profissional.from_tuple(profissional_encontrado)
                self.login_callback(profissional)
            else:
                messagebox.showerror("Erro", "Código de acesso incorreto.")
        else:
            messagebox.showerror("Erro", "Profissional não encontrado.")
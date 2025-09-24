import customtkinter as ctk
from tkinter import messagebox
from models import Profissional
from services import AuthService

class ProfissionalDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, profissional=None):
        super().__init__(parent)
        self.db = db
        self.profissional = profissional
        self.result = None

        self.title("Cadastro de Profissional" if not profissional else "Editar Profissional")
        self.geometry("500x520")
        self.resizable(False, False)
        
        # Faz com que a janela de diálogo fique na frente e bloqueie a janela principal
        self.transient(parent)
        self.grab_set()

        self.criar_interface()

        if self.profissional:
            self.carregar_dados()
        
        self.nome_entry.focus()
        
    def carregar_dados(self):
        self.nome_var.set(self.profissional.nome)
        self.especialidade_var.set(self.profissional.especialidade)
        self.crm_var.set(self.profissional.crm_registro)
        self.telefone_var.set(self.profissional.telefone)
        self.email_var.set(self.profissional.email)
        # O código de acesso não é exibido na edição
        self.codigo_frame.pack_forget()

    def criar_interface(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Nome:").pack(anchor='w')
        self.nome_var = ctk.StringVar()
        self.nome_entry = ctk.CTkEntry(main_frame, textvariable=self.nome_var)
        self.nome_entry.pack(fill='x', pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Especialidade:").pack(anchor='w')
        self.especialidade_var = ctk.StringVar()
        ctk.CTkEntry(main_frame, textvariable=self.especialidade_var).pack(fill='x', pady=(0, 10))

        ctk.CTkLabel(main_frame, text="CRM/Registro:").pack(anchor='w')
        self.crm_var = ctk.StringVar()
        ctk.CTkEntry(main_frame, textvariable=self.crm_var).pack(fill='x', pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Telefone:").pack(anchor='w')
        self.telefone_var = ctk.StringVar()
        ctk.CTkEntry(main_frame, textvariable=self.telefone_var).pack(fill='x', pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Email:").pack(anchor='w')
        self.email_var = ctk.StringVar()
        ctk.CTkEntry(main_frame, textvariable=self.email_var).pack(fill='x', pady=(0, 10))

        # Código de Acesso (visível apenas para novos)
        self.codigo_gerado = AuthService.gerar_codigo_acesso()
        self.codigo_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.codigo_frame.pack(fill='x', pady=(10, 0))
        ctk.CTkLabel(self.codigo_frame, text="Código de Acesso Gerado:", font=ctk.CTkFont(weight="bold")).pack()
        ctk.CTkLabel(self.codigo_frame, text=self.codigo_gerado, font=ctk.CTkFont(size=20, weight="bold"), text_color="#347083").pack()

        # Botões
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill='x', pady=(20, 0))
        ctk.CTkButton(btn_frame, text="Salvar", command=self.salvar).pack(side='right')
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, fg_color="gray").pack(side='right', padx=10)

    def salvar(self):
        if not self.nome_var.get() or not self.especialidade_var.get() or not self.crm_var.get():
            messagebox.showerror("Erro", "Nome, Especialidade e CRM são obrigatórios.", parent=self)
            return
        try:
            if self.profissional:
                self.db.update_profissional(self.profissional.id, self.nome_var.get(), self.especialidade_var.get(), self.crm_var.get(), self.telefone_var.get(), self.email_var.get())
            else:
                self.db.insert_profissional(self.nome_var.get(), self.especialidade_var.get(), self.crm_var.get(), self.telefone_var.get(), self.email_var.get(), self.codigo_gerado)
            
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível salvar:\n{e}", parent=self)
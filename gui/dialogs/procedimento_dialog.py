import customtkinter as ctk
from tkinter import messagebox
from models import Procedimento

class ProcedimentoDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, procedimento=None):
        super().__init__(parent)
        self.db = db
        self.procedimento = procedimento
        self.result = None

        self.title("Novo Procedimento" if not procedimento else "Editar Procedimento")
        self.geometry("400x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.criar_interface()

        if self.procedimento:
            self.carregar_dados()

        self.nome_entry.focus()
        
    def carregar_dados(self):
        self.nome_var.set(self.procedimento.nome)
        self.duracao_var.set(str(self.procedimento.duracao))
        self.valor_var.set(f"{self.procedimento.valor:.2f}".replace('.', ','))

    def criar_interface(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Nome do Procedimento:").pack(anchor='w')
        self.nome_var = ctk.StringVar()
        self.nome_entry = ctk.CTkEntry(main_frame, textvariable=self.nome_var, height=35)
        self.nome_entry.pack(fill='x', pady=(0, 15))

        ctk.CTkLabel(main_frame, text="Duração (em minutos):").pack(anchor='w')
        self.duracao_var = ctk.StringVar()
        ctk.CTkEntry(main_frame, textvariable=self.duracao_var, height=35).pack(fill='x', pady=(0, 15))

        ctk.CTkLabel(main_frame, text="Valor (R$):").pack(anchor='w')
        self.valor_var = ctk.StringVar()
        ctk.CTkEntry(main_frame, textvariable=self.valor_var, height=35).pack(fill='x', pady=(0, 15))

        # ALTERAÇÃO AQUI: O frame dos botões agora é um filho do main_frame
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill='x', side='bottom')

        ctk.CTkButton(btn_frame, text="Salvar", command=self.salvar, height=35).pack(side='right')
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, fg_color="gray", height=35).pack(side='right', padx=10)

    def salvar(self):
        nome = self.nome_var.get().strip()
        duracao_str = self.duracao_var.get().strip()
        valor_str = self.valor_var.get().strip().replace(',', '.')

        if not all([nome, duracao_str, valor_str]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios.", parent=self)
            return

        try:
            duracao = int(duracao_str)
            valor = float(valor_str)
        except ValueError:
            messagebox.showerror("Erro de Formato", "Duração deve ser um número inteiro e Valor deve ser um número.", parent=self)
            return

        try:
            if self.procedimento:
                self.db.update_procedimento(self.procedimento.id, nome, duracao, valor)
            else:
                self.db.insert_procedimento(nome, duracao, valor)
            
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível salvar o procedimento:\n{e}", parent=self)
import customtkinter as ctk
from tkinter import ttk, messagebox
from gui.dialogs.profissional_dialog import ProfissionalDialog
from models import Profissional

class ProfissionaisTab(ctk.CTkFrame):
    def __init__(self, parent, db, profissional_logado):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.profissional_logado = profissional_logado
        self.criar_interface()
        self.carregar_profissionais()

    def criar_interface(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill='x', pady=(0,10))
        ctk.CTkButton(top_frame, text="Adicionar Profissional", command=self.adicionar_profissional).pack(side='left')
        ctk.CTkButton(top_frame, text="Editar Profissional", command=self.editar_profissional).pack(side='left', padx=5)
        ctk.CTkButton(top_frame, text="Excluir Profissional", command=self.excluir_profissional).pack(side='left')

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=25, borderwidth=0)
        style.map('Treeview', background=[('selected', '#347083')])
        style.configure("Treeview.Heading", font=('CTkFont', 12, 'bold'))

        # --- ALTERAÇÃO AQUI: Removendo a coluna 'ID' ---
        self.tree = ttk.Treeview(self, columns=('Nome', 'Especialidade', 'CRM', 'Telefone', 'Email'), show='headings')
        self.tree.tag_configure("white_row", background="white")

        self.tree.heading('Nome', text='Nome')
        self.tree.heading('Especialidade', text='Especialidade')
        self.tree.heading('CRM', text='CRM/Registro')
        self.tree.heading('Telefone', text='Telefone')
        self.tree.heading('Email', text='Email')

        self.tree.column('Nome', width=250)
        self.tree.column('Especialidade', width=200)
        self.tree.column('CRM', width=120, anchor='center')
        self.tree.column('Telefone', width=120, anchor='center')
        self.tree.column('Email', width=250)
        
        self.tree.pack(expand=True, fill='both')

    def carregar_profissionais(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        profissionais = self.db.get_profissionais()
        if profissionais:
            for prof in profissionais:
                # --- ALTERAÇÃO AQUI: Inserindo os valores sem o ID e usando o iid ---
                self.tree.insert('', 'end', values=prof[1:6], iid=prof[0], tags=('white_row',))

    def adicionar_profissional(self):
        dialog = ProfissionalDialog(self, self.db)
        if hasattr(dialog, 'result') and dialog.result:
            self.carregar_profissionais()

    def editar_profissional(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um profissional para editar.")
            return
        
        # --- ALTERAÇÃO AQUI: Pegando o ID do iid ---
        profissional_id = selected_item[0]
        profissional_data = self.db.get_profissional_by_id(profissional_id)

        if profissional_data:
            profissional = Profissional.from_tuple(profissional_data)
            dialog = ProfissionalDialog(self, self.db, profissional=profissional)
            if hasattr(dialog, 'result') and dialog.result:
                self.carregar_profissionais()

    def excluir_profissional(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um profissional para excluir.")
            return

        # --- ALTERAÇÃO AQUI: Pegando o ID do iid ---
        profissional_id = int(selected_item[0])
        
        if profissional_id == self.profissional_logado.id:
            messagebox.showerror("Ação Proibida", "Você não pode excluir o seu próprio perfil de usuário logado.")
            return

        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir o profissional selecionado?"):
            self.db.delete_profissional(profissional_id)
            self.carregar_profissionais()
import customtkinter as ctk
from tkinter import ttk, messagebox
from gui.dialogs.procedimento_dialog import ProcedimentoDialog
from models import Procedimento

class ProcedimentosTab(ctk.CTkFrame):
    def __init__(self, parent, db, profissional_logado):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.profissional_logado = profissional_logado
        self.criar_interface()
        self.carregar_procedimentos()

    def criar_interface(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill='x', pady=(0,10))
        ctk.CTkButton(top_frame, text="Adicionar Procedimento", command=self.adicionar_procedimento).pack(side='left')
        ctk.CTkButton(top_frame, text="Editar Procedimento", command=self.editar_procedimento).pack(side='left', padx=5)
        ctk.CTkButton(top_frame, text="Excluir Procedimento", command=self.excluir_procedimento).pack(side='left')

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=25, borderwidth=0)
        style.map('Treeview', background=[('selected', '#347083')])
        style.configure("Treeview.Heading", font=('CTkFont', 12, 'bold'))

        # --- ALTERAÇÃO AQUI: Removendo a coluna 'ID' ---
        self.tree = ttk.Treeview(self, columns=('Nome', 'Duração', 'Valor'), show='headings')
        self.tree.tag_configure("white_row", background="white")

        self.tree.heading('Nome', text='Nome do Procedimento')
        self.tree.heading('Duração', text='Duração')
        self.tree.heading('Valor', text='Valor (R$)')

        self.tree.column('Nome', width=350)
        self.tree.column('Duração', width=150, anchor='center')
        self.tree.column('Valor', width=150, anchor='e')
        
        self.tree.pack(expand=True, fill='both')

    def carregar_procedimentos(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        procedimentos = self.db.get_procedimentos()
        if procedimentos:
            for proc in procedimentos:
                duracao_formatada = f"{proc[2]} min"
                valor_formatado = f"R$ {proc[3]:.2f}".replace('.', ',')
                # --- ALTERAÇÃO AQUI: Inserindo os valores sem o ID e usando o iid ---
                self.tree.insert('', 'end', values=(proc[1], duracao_formatada, valor_formatado), iid=proc[0], tags=('white_row',))

    def adicionar_procedimento(self):
        dialog = ProcedimentoDialog(self, self.db)
        if hasattr(dialog, 'result') and dialog.result:
            self.carregar_procedimentos()

    def editar_procedimento(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um procedimento para editar.")
            return
        
        # --- ALTERAÇÃO AQUI: Pegando o ID do iid ---
        procedimento_id = selected_item[0]
        procedimento_data = next((p for p in self.db.get_procedimentos() if p[0] == int(procedimento_id)), None)

        if procedimento_data:
            procedimento = Procedimento.from_tuple(procedimento_data)
            dialog = ProcedimentoDialog(self, self.db, procedimento=procedimento)
            if hasattr(dialog, 'result') and dialog.result:
                self.carregar_procedimentos()

    def excluir_procedimento(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um procedimento para excluir.")
            return

        # --- ALTERAÇÃO AQUI: Pegando o ID do iid ---
        procedimento_id = selected_item[0]
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir o procedimento selecionado?"):
            self.db.delete_procedimento(procedimento_id)
            self.carregar_procedimentos()
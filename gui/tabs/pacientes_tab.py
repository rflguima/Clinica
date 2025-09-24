import customtkinter as ctk
from tkinter import ttk, messagebox
from gui.dialogs.paciente_dialog import PacienteDialog
from models import Paciente

class PacientesTab(ctk.CTkFrame):
    def __init__(self, parent, db, profissional_logado):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.profissional_logado = profissional_logado
        self.criar_interface()
        self.carregar_pacientes()

    def criar_interface(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill='x', pady=(0,10))

        ctk.CTkButton(top_frame, text="Adicionar Paciente", command=self.adicionar_paciente).pack(side='left')
        ctk.CTkButton(top_frame, text="Editar Paciente", command=self.editar_paciente).pack(side='left', padx=5)
        ctk.CTkButton(top_frame, text="Excluir Paciente", command=self.excluir_paciente).pack(side='left')

        busca_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        busca_frame.pack(side='right')

        self.busca_var = ctk.StringVar()
        busca_entry = ctk.CTkEntry(busca_frame, textvariable=self.busca_var, placeholder_text="Buscar por nome ou CPF...")
        busca_entry.pack(side='left', fill='x', expand=True, padx=(10, 5))
        busca_entry.bind("<Return>", self.buscar_pacientes)
        ctk.CTkButton(busca_frame, text="Buscar", width=100, command=self.buscar_pacientes).pack(side='left')

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=25, borderwidth=0)
        style.map('Treeview', background=[('selected', '#347083')])
        style.configure("Treeview.Heading", font=('CTkFont', 12, 'bold'))

        # --- ALTERAÇÃO AQUI: Removendo a coluna 'ID' ---
        self.tree = ttk.Treeview(self, columns=('Nome', 'CPF', 'Telefone', 'Cidade'), show='headings')
        self.tree.tag_configure("white_row", background="white")
        
        self.tree.heading('Nome', text='Nome')
        self.tree.heading('CPF', text='CPF')
        self.tree.heading('Telefone', text='Telefone')
        self.tree.heading('Cidade', text='Cidade')

        self.tree.column('Nome', width=300)
        self.tree.column('CPF', width=120, anchor='center')
        self.tree.column('Telefone', width=120, anchor='center')
        self.tree.column('Cidade', width=150)
        
        self.tree.pack(expand=True, fill='both')

    def carregar_pacientes(self, lista_pacientes=None):
        for i in self.tree.get_children(): self.tree.delete(i)
        pacientes = lista_pacientes if lista_pacientes is not None else self.db.get_pacientes()
        if pacientes:
            for p in pacientes:
                # --- ALTERAÇÃO AQUI: Inserindo os valores sem o ID e usando o iid para guardar o ID ---
                self.tree.insert('', 'end', values=(p[1], p[3], p[2], p[5]), tags=('white_row',), iid=p[0])

    def buscar_pacientes(self, event=None):
        termo = self.busca_var.get().strip()
        if termo:
            resultados = self.db.search_pacientes(termo)
            self.carregar_pacientes(resultados)
        else:
            self.carregar_pacientes()

    def adicionar_paciente(self):
        dialog = PacienteDialog(self, self.db)
        if hasattr(dialog, 'result') and dialog.result:
            self.carregar_pacientes()

    def editar_paciente(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um paciente para editar.")
            return
        # --- ALTERAÇÃO AQUI: Pegando o ID do iid do item selecionado ---
        paciente_id = selected_item[0]
        paciente_data = self.db.get_paciente_by_id(paciente_id)
        if paciente_data:
            paciente = Paciente.from_tuple(paciente_data)
            dialog = PacienteDialog(self, self.db, paciente=paciente)
            if hasattr(dialog, 'result') and dialog.result:
                self.carregar_pacientes()

    def excluir_paciente(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um paciente para excluir.")
            return
        # --- ALTERAÇÃO AQUI: Pegando o ID do iid e o nome dos valores ---
        paciente_id = selected_item[0]
        paciente_nome = self.tree.item(selected_item[0])['values'][0]
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o paciente {paciente_nome}?"):
            self.db.delete_paciente(paciente_id)
            self.carregar_pacientes()
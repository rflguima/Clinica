import customtkinter as ctk
from tkinter import messagebox
from models import Agendamento, StatusAgendamento
from datetime import datetime

class AgendamentoDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, profissional_logado, agendamento=None):
        super().__init__(parent)
        self.db = db
        self.profissional_logado = profissional_logado
        self.agendamento = agendamento
        self.result = None

        self.title("Novo Agendamento" if not agendamento else "Editar Agendamento")
        
        # Aumenta a altura SE for secretária, para caber o novo campo
        altura_janela = 500 if self.profissional_logado.role == 'secretaria' else 450
        self.geometry(f"500x{altura_janela}")

        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.configure(fg_color="white")
        
        self.pacientes_map = {}
        self.procedimentos_map = {}
        self.profissionais_map = {} # Adicionado para a secretária

        self.criar_interface()
        self.carregar_combos()

        if self.agendamento:
            self.carregar_dados()

        self.wait_window()

    def _formatar_data(self, *args):
        texto_atual = self.data_var.get()
        texto_limpo = "".join(filter(str.isdigit, texto_atual))
        novo_texto = ""
        
        if len(texto_limpo) > 0: novo_texto = texto_limpo[:2]
        if len(texto_limpo) > 2: novo_texto += "/" + texto_limpo[2:4]
        if len(texto_limpo) > 4: novo_texto += "/" + texto_limpo[4:8]
        
        if self.data_var.get() != novo_texto:
            self.data_var.set(novo_texto)
            self.after_idle(lambda: self.data_entry.icursor(len(novo_texto)))

    def criar_interface(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- ALTERAÇÃO AQUI: Campo de Profissional para Secretária ---
        if self.profissional_logado.role == 'secretaria':
            ctk.CTkLabel(main_frame, text="Profissional Responsável:").pack(anchor='w')
            self.profissional_var = ctk.StringVar()
            self.profissional_combo = ctk.CTkComboBox(main_frame, variable=self.profissional_var, state='readonly', height=35)
            self.profissional_combo.pack(fill='x', pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Paciente:").pack(anchor='w')
        self.paciente_var = ctk.StringVar()
        self.paciente_combo = ctk.CTkComboBox(main_frame, variable=self.paciente_var, state='readonly', height=35)
        self.paciente_combo.pack(fill='x', pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Procedimento:").pack(anchor='w')
        self.procedimento_var = ctk.StringVar()
        self.procedimento_combo = ctk.CTkComboBox(main_frame, variable=self.procedimento_var, state='readonly', height=35)
        self.procedimento_combo.pack(fill='x', pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Data (DD/MM/AAAA):").pack(anchor='w')
        self.data_var = ctk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        self.data_var.trace_add("write", self._formatar_data)
        self.data_entry = ctk.CTkEntry(main_frame, textvariable=self.data_var, height=35)
        self.data_entry.pack(fill='x', pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Hora (HH:MM):").pack(anchor='w')
        self.hora_var = ctk.StringVar(value="09:00")
        ctk.CTkEntry(main_frame, textvariable=self.hora_var, height=35).pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Status:").pack(anchor='w')
        self.status_var = ctk.StringVar()
        self.status_combo = ctk.CTkComboBox(main_frame, variable=self.status_var, values=StatusAgendamento.get_opcoes(), state='readonly', height=35)
        self.status_combo.pack(fill='x', pady=(0, 10))

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill='x', pady=(20, 0), side="bottom")
        ctk.CTkButton(btn_frame, text="Salvar", command=self.salvar, height=35).pack(side='right')
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, fg_color="gray", height=35).pack(side='right', padx=10)

    def carregar_combos(self):
        # --- ALTERAÇÃO AQUI: Carregar lista de profissionais para a secretária ---
        if self.profissional_logado.role == 'secretaria':
            profissionais = self.db.get_profissionais()
            if profissionais:
                profissionais_nomes = [p[1] for p in profissionais]
                self.profissional_combo.configure(values=profissionais_nomes)
                self.profissionais_map = {p[1]: p[0] for p in profissionais}

        pacientes = self.db.get_pacientes()
        if pacientes:
            pacientes_nomes = [p[1] for p in pacientes]
            self.paciente_combo.configure(values=pacientes_nomes)
            self.pacientes_map = {p[1]: p[0] for p in pacientes}

        procedimentos = self.db.get_procedimentos()
        if procedimentos:
            procedimentos_nomes = [p[1] for p in procedimentos]
            self.procedimento_combo.configure(values=procedimentos_nomes)
            self.procedimentos_map = {p[1]: p[0] for p in procedimentos}
        
        self.status_combo.set(StatusAgendamento.AGENDADO)

    def carregar_dados(self):
        dt_obj = datetime.strptime(self.agendamento.data_hora, "%Y-%m-%d %H:%M:%S")
        self.data_var.set(dt_obj.strftime('%d/%m/%Y'))
        self.hora_var.set(dt_obj.strftime('%H:%M'))
        
        paciente = self.db.get_paciente_by_id(self.agendamento.paciente_id)
        if paciente: self.paciente_var.set(paciente[1])
        
        for nome, pid in self.procedimentos_map.items():
            if pid == self.agendamento.procedimento_id:
                self.procedimento_var.set(nome)
                break
        
        self.status_var.set(self.agendamento.status)

        # --- ALTERAÇÃO AQUI: Carregar profissional correto na edição ---
        if self.profissional_logado.role == 'secretaria' and self.agendamento:
            agendamentos = self.db.get_agendamentos(self.profissional_logado)
            ag_data = next((ag for ag in agendamentos if ag[0] == self.agendamento.id), None)
            if ag_data:
                self.profissional_var.set(ag_data[3]) # Índice 3 é o nome do profissional

    def salvar(self):
        paciente_nome = self.paciente_var.get()
        procedimento_nome = self.procedimento_var.get()
        data_str_br = self.data_var.get()
        hora = self.hora_var.get()
        
        if not all([paciente_nome, procedimento_nome, data_str_br, hora]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios.", parent=self)
            return

        # --- ALTERAÇÃO AQUI: Determinar o ID do profissional a ser salvo ---
        if self.profissional_logado.role == 'secretaria':
            profissional_nome = self.profissional_var.get()
            if not profissional_nome:
                messagebox.showerror("Erro", "É necessário selecionar um profissional.", parent=self)
                return
            profissional_id = self.profissionais_map.get(profissional_nome)
        else:
            profissional_id = self.profissional_logado.id

        try:
            data_obj = datetime.strptime(data_str_br, "%d/%m/%Y")
            data_db = data_obj.strftime("%Y-%m-%d")
            data_hora_str = f"{data_db} {hora}:00"
            datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("Erro de Formato", "Formato de data ou hora inválido.", parent=self)
            return

        paciente_id = self.pacientes_map.get(paciente_nome)
        procedimento_id = self.procedimentos_map.get(procedimento_nome)
        status = self.status_var.get()
        
        try:
            if self.agendamento:
                self.db.update_agendamento(self.agendamento.id, paciente_id, procedimento_id, profissional_id, data_hora_str, status, "")
            else:
                self.db.insert_agendamento(paciente_id, procedimento_id, profissional_id, data_hora_str, status, "")
            
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível salvar o agendamento:\n{e}", parent=self)
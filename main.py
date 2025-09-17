import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font
from datetime import datetime, date, timedelta
import calendar
import re
from database import DatabaseManager
from models import Profissional, Paciente, Procedimento, Agendamento, StatusAgendamento

class ClinicaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão de Clínica")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        self.setup_styles()
        self.db = DatabaseManager()
        self.profissional_logado = None
        
        self.cal_year = datetime.now().year
        self.cal_month = datetime.now().month
        self.data_selecionada_calendario = date.today()

        self.criar_tela_login()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Custom.Treeview', font=('Arial', 10), rowheight=25)
        style.configure('Custom.Treeview.Heading', font=('Arial', 10, 'bold'))
        style.configure('CalendarDay.TButton', font=('Arial', 10), padding=5)
        style.configure('Today.TButton', font=('Arial', 10, 'bold'), foreground='blue', padding=5)

    def criar_tela_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
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
        self.carregar_profissionais_login()
        
        btn_frame = ttk.Frame(login_frame)
        btn_frame.pack(pady=30)
        ttk.Button(btn_frame, text="Entrar", command=self.fazer_login, width=15).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Cadastrar Novo Profissional", command=self.cadastrar_profissional_inicial, width=25).pack(side='left', padx=10)
    
    def carregar_profissionais_login(self):
        profissionais = self.db.get_profissionais()
        valores = [f"{prof[1]} - {prof[2]} (CRM: {prof[3]})" for prof in profissionais]
        self.profissional_combo['values'] = valores
        if valores:
            self.profissional_combo.current(0)
    
    def cadastrar_profissional_inicial(self):
        self.abrir_janela_profissional()
        self.carregar_profissionais_login()
    
    def fazer_login(self):
        if not self.profissional_var.get():
            messagebox.showwarning("Aviso", "Selecione um profissional!")
            return
        
        texto_selecionado = self.profissional_var.get()
        profissionais = self.db.get_profissionais()
        
        for prof in profissionais:
            if f"{prof[1]} - {prof[2]} (CRM: {prof[3]})" == texto_selecionado:
                self.profissional_logado = Profissional.from_tuple(prof)
                break
        
        if self.profissional_logado:
            self.criar_interface_principal()
        else:
            messagebox.showerror("Erro", "Profissional não encontrado!")
    
    def criar_interface_principal(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(header_frame, text=f"Usuário: {self.profissional_logado.nome} - {self.profissional_logado.especialidade}", style='Heading.TLabel').pack(side='left')
        ttk.Button(header_frame, text="Logout", command=self.fazer_logout).pack(side='right')
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        self.criar_aba_calendario()
        self.criar_aba_agendamentos()
        self.criar_aba_pacientes()
        self.criar_aba_profissionais()
        self.criar_aba_procedimentos()

    def fazer_logout(self):
        self.profissional_logado = None
        self.criar_tela_login()

    # --- MÉTODOS DA ABA DE CALENDÁRIO ---
    def criar_aba_calendario(self):
        self.cal_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cal_frame, text="Calendário")

        top_frame = ttk.Frame(self.cal_frame)
        top_frame.pack(fill='x', padx=10, pady=5)
        bottom_frame = ttk.Frame(self.cal_frame)
        bottom_frame.pack(expand=True, fill='both', padx=10, pady=5)

        self.cal_container = ttk.Frame(top_frame)
        self.cal_container.pack(pady=10)
        self.label_dia_selecionado = ttk.Label(bottom_frame, text="", style='Heading.TLabel')
        self.label_dia_selecionado.pack(anchor='w', pady=(5, 10))

        columns = ('Horário', 'Paciente', 'Procedimento', 'Status')
        self.tree_consultas_dia = ttk.Treeview(bottom_frame, columns=columns, show='headings', style='Custom.Treeview')
        for col in columns: self.tree_consultas_dia.heading(col, text=col)
        self.tree_consultas_dia.column('Horário', width=80, anchor='center')
        self.tree_consultas_dia.column('Paciente', width=250)
        self.tree_consultas_dia.column('Procedimento', width=250)
        self.tree_consultas_dia.column('Status', width=100, anchor='center')
        self.tree_consultas_dia.pack(expand=True, fill='both')
        
        self.desenhar_calendario()
        self.selecionar_dia(date.today())
        
    def desenhar_calendario(self):
        for widget in self.cal_container.winfo_children():
            widget.destroy()

        header_frame = ttk.Frame(self.cal_container)
        header_frame.pack(pady=10)
        ttk.Button(header_frame, text="<", command=self.mes_anterior, width=3).pack(side='left', padx=10)
        self.cal_label = ttk.Label(header_frame, text=f"{calendar.month_name[self.cal_month].capitalize()} {self.cal_year}", style='Title.TLabel', width=20, anchor='center')
        self.cal_label.pack(side='left')
        ttk.Button(header_frame, text=">", command=self.proximo_mes, width=3).pack(side='left', padx=10)

        days_frame = ttk.Frame(self.cal_container)
        days_frame.pack()
        days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        for i, day in enumerate(days):
            ttk.Label(days_frame, text=day, width=6, anchor='center', font=('Arial', 10, 'bold')).grid(row=0, column=i, padx=5, pady=5)

        dates_frame = ttk.Frame(self.cal_container)
        dates_frame.pack(pady=5)
        cal = calendar.monthcalendar(self.cal_year, self.cal_month)
        hoje = date.today()

        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0: continue
                
                data_atual = date(self.cal_year, self.cal_month, day)
                btn_style = 'Today.TButton' if data_atual == hoje else 'CalendarDay.TButton'
                btn = ttk.Button(dates_frame, text=str(day), style=btn_style, command=lambda d=data_atual: self.selecionar_dia(d))
                btn.grid(row=week_num, column=day_num, sticky="nsew", padx=2, pady=2)
    
    def mes_anterior(self):
        self.cal_month -= 1
        if self.cal_month == 0:
            self.cal_month = 12
            self.cal_year -= 1
        self.desenhar_calendario()
        
    def proximo_mes(self):
        self.cal_month += 1
        if self.cal_month == 13:
            self.cal_month = 1
            self.cal_year += 1
        self.desenhar_calendario()

    def selecionar_dia(self, data):
        self.data_selecionada_calendario = data
        self.label_dia_selecionado.config(text=f"Consultas para {data.strftime('%d/%m/%Y')}")
        self.atualizar_lista_consultas_dia()

    def atualizar_lista_consultas_dia(self):
        for item in self.tree_consultas_dia.get_children():
            self.tree_consultas_dia.delete(item)
        data_str = self.data_selecionada_calendario.strftime('%Y-%m-%d')
        consultas = self.db.get_agendamentos_por_data(data_str, self.profissional_logado.id)
        if consultas:
            for consulta in sorted(consultas, key=lambda x: x[4]):
                hora = datetime.strptime(consulta[4], "%Y-%m-%d %H:%M:%S").strftime('%H:%M')
                self.tree_consultas_dia.insert('', 'end', values=(hora, consulta[1], consulta[2], consulta[5].capitalize()))

    # --- PRONTUÁRIO DO PACIENTE ---
    def abrir_prontuario_paciente(self, paciente_id):
        paciente_data = self.db.get_paciente_by_id(paciente_id)
        if not paciente_data:
            messagebox.showerror("Erro", "Paciente não encontrado!")
            return
            
        paciente = Paciente.from_tuple(paciente_data)
        janela = tk.Toplevel(self.root)
        janela.title(f"Prontuário - {paciente.nome}")
        janela.geometry("800x600")
        janela.transient(self.root)
        janela.grab_set()

        notebook = ttk.Notebook(janela)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Aba de Dados Básicos
        frame_dados = ttk.Frame(notebook, padding="10")
        notebook.add(frame_dados, text="Dados Básicos")

        def add_readonly_info(parent, row, label, text):
            ttk.Label(parent, text=label, font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', padx=5, pady=2)
            ttk.Label(parent, text=text if text else "Não informado", wraplength=500).grid(row=row, column=1, sticky='w', padx=5, pady=2)

        add_readonly_info(frame_dados, 0, "Nome Completo:", paciente.nome)
        add_readonly_info(frame_dados, 1, "Data de Nascimento:", datetime.strptime(paciente.data_nascimento, "%Y-%m-%d").strftime("%d/%m/%Y") if paciente.data_nascimento else "")
        add_readonly_info(frame_dados, 2, "Idade:", f"{paciente.calcular_idade()} anos" if paciente.data_nascimento else "N/A")
        add_readonly_info(frame_dados, 3, "CPF:", paciente.cpf)
        add_readonly_info(frame_dados, 4, "Estado Civil:", paciente.estado_civil)
        add_readonly_info(frame_dados, 5, "Profissão:", paciente.profissao)
        add_readonly_info(frame_dados, 6, "Telefone:", paciente.telefone)
        add_readonly_info(frame_dados, 7, "Email:", paciente.email)
        endereco = f"{paciente.rua}, {paciente.numero} - {paciente.bairro}, {paciente.cidade}/{paciente.estado} - CEP: {paciente.cep}"
        add_readonly_info(frame_dados, 8, "Endereço:", endereco)
        
        # Aba de Anamnese
        frame_anamnese = ttk.Frame(notebook, padding="10")
        notebook.add(frame_anamnese, text="Anamnese")
        
        def add_readonly_text(parent, label, text):
            ttk.Label(parent, text=label, font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10,2))
            text_widget = tk.Text(parent, height=3, wrap='word', bg='#f0f0f0', relief='flat', font=('Arial', 10))
            text_widget.insert('1.0', text if text else "Não informado")
            text_widget.config(state='disabled')
            text_widget.pack(fill='x', expand=True)

        add_readonly_text(frame_anamnese, "Queixa Principal:", paciente.queixa_principal)
        add_readonly_text(frame_anamnese, "Histórico da Doença Atual:", paciente.historico_doenca_atual)
        add_readonly_text(frame_anamnese, "Antecedentes Pessoais:", paciente.antecedentes_pessoais)
        add_readonly_text(frame_anamnese, "Antecedentes Familiares:", paciente.antecedentes_familiares)
        add_readonly_text(frame_anamnese, "Hábitos de Vida:", paciente.habitos_vida)
        add_readonly_text(frame_anamnese, "Medicamentos em Uso:", paciente.medicamentos_em_uso)

        # Aba de Histórico de Consultas
        frame_historico = ttk.Frame(notebook)
        notebook.add(frame_historico, text="Histórico de Consultas")
        columns_hist = ('Procedimento', 'Profissional', 'Data/Hora', 'Status', 'Observações')
        tree_historico = ttk.Treeview(frame_historico, columns=columns_hist, show='headings')
        for col in columns_hist: tree_historico.heading(col, text=col)
        tree_historico.pack(expand=True, fill='both', pady=10)
        historico = self.db.get_historico_paciente(paciente_id)
        for item in historico:
            valores = list(item)
            try: valores[2] = datetime.strptime(valores[2], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
            except: pass
            tree_historico.insert('', 'end', values=valores)
            
        ttk.Button(janela, text="Fechar", command=janela.destroy).pack(padx=10, pady=5)

    # --- MÉTODOS DE GERENCIAMENTO DAS ABAS ---
    def criar_aba_profissionais(self):
        prof_frame = ttk.Frame(self.notebook)
        self.notebook.add(prof_frame, text="Profissionais")
        btn_frame = ttk.Frame(prof_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(btn_frame, text="Novo Profissional", command=self.abrir_janela_profissional).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.editar_profissional).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Remover", command=self.remover_profissional).pack(side='left', padx=5)
        
        columns = ('ID', 'Nome', 'Especialidade', 'CRM', 'Telefone', 'Email')
        self.tree_profissionais = ttk.Treeview(prof_frame, columns=columns, show='headings', style='Custom.Treeview')
        for col in columns: self.tree_profissionais.heading(col, text=col)
        self.tree_profissionais.pack(expand=True, fill='both', padx=10, pady=5)
        self.carregar_profissionais()

    def criar_aba_pacientes(self):
        pac_frame = ttk.Frame(self.notebook)
        self.notebook.add(pac_frame, text="Pacientes")
        top_frame = ttk.Frame(pac_frame)
        top_frame.pack(fill='x', padx=10, pady=5)
        
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side='left')
        ttk.Button(btn_frame, text="Novo Paciente", command=self.abrir_janela_paciente).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.editar_paciente).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Remover", command=self.remover_paciente).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Prontuário", command=self.ver_prontuario_paciente_da_lista).pack(side='left', padx=5)
        
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side='right')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.buscar_pacientes)
        
        columns = ('ID', 'Nome', 'Telefone', 'CPF', 'Cidade', 'Idade')
        self.tree_pacientes = ttk.Treeview(pac_frame, columns=columns, show='headings', style='Custom.Treeview')
        for col in columns: self.tree_pacientes.heading(col, text=col)
        self.tree_pacientes.column('ID', width=50)
        self.tree_pacientes.column('Nome', width=250)
        self.tree_pacientes.pack(expand=True, fill='both', padx=10, pady=5)
        self.carregar_pacientes()

    def criar_aba_procedimentos(self):
        proc_frame = ttk.Frame(self.notebook)
        self.notebook.add(proc_frame, text="Procedimentos")
        btn_frame = ttk.Frame(proc_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(btn_frame, text="Novo Procedimento", command=self.abrir_janela_procedimento).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.editar_procedimento).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Remover", command=self.remover_procedimento).pack(side='left', padx=5)
        
        columns = ('ID', 'Nome', 'Duração (min)', 'Valor (R$)')
        self.tree_procedimentos = ttk.Treeview(proc_frame, columns=columns, show='headings', style='Custom.Treeview')
        for col in columns: self.tree_procedimentos.heading(col, text=col)
        self.tree_procedimentos.pack(expand=True, fill='both', padx=10, pady=5)
        self.carregar_procedimentos()

    def criar_aba_agendamentos(self):
        agend_frame = ttk.Frame(self.notebook)
        self.notebook.add(agend_frame, text="Lista de Agendamentos")
        top_frame = ttk.Frame(agend_frame)
        top_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(top_frame, text="Novo Agendamento", command=self.abrir_janela_agendamento).pack(side='left', padx=5)
        
        columns = ('ID', 'Paciente', 'Procedimento', 'Profissional', 'Data/Hora', 'Status')
        self.tree_agendamentos = ttk.Treeview(agend_frame, columns=columns, show='headings', style='Custom.Treeview')
        for col in columns: self.tree_agendamentos.heading(col, text=col)
        self.tree_agendamentos.column('ID', width=40)
        self.tree_agendamentos.pack(expand=True, fill='both', padx=10, pady=5)
        self.carregar_agendamentos()
    
    # --- MÉTODOS PARA CARREGAR DADOS ---
    def carregar_profissionais(self):
        if not hasattr(self, 'tree_profissionais'): return
        for item in self.tree_profissionais.get_children(): self.tree_profissionais.delete(item)
        for prof in self.db.get_profissionais() or []: self.tree_profissionais.insert('', 'end', values=prof)
    
    def carregar_pacientes(self, pacientes_data=None):
        if not hasattr(self, 'tree_pacientes'): return
        for item in self.tree_pacientes.get_children(): self.tree_pacientes.delete(item)
        
        pacientes = pacientes_data if pacientes_data is not None else self.db.get_pacientes()
        if pacientes:
            for pac in pacientes:
                idade = ""
                if pac[4]: # data_nascimento
                    try:
                        nasc = datetime.strptime(pac[4], "%Y-%m-%d").date()
                        hoje = date.today()
                        idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
                    except: pass
                valores = (pac[0], pac[1], pac[2], pac[3], pac[5], idade) # id, nome, tel, cpf, cidade, idade
                self.tree_pacientes.insert('', 'end', values=valores)
    
    def carregar_procedimentos(self):
        if not hasattr(self, 'tree_procedimentos'): return
        for item in self.tree_procedimentos.get_children(): self.tree_procedimentos.delete(item)
        for proc in self.db.get_procedimentos() or []:
            valores = list(proc); valores[3] = f"R$ {valores[3]:.2f}"; self.tree_procedimentos.insert('', 'end', values=valores)
    
    def carregar_agendamentos(self):
        if not hasattr(self, 'tree_agendamentos'): return
        for item in self.tree_agendamentos.get_children(): self.tree_agendamentos.delete(item)
        for agend in self.db.get_agendamentos() or []:
            valores = list(agend)
            try: valores[4] = datetime.strptime(valores[4], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
            except: pass
            self.tree_agendamentos.insert('', 'end', values=(valores[0], valores[1], valores[2], valores[3], valores[4], valores[5]))

    def buscar_pacientes(self, event=None):
        termo = self.search_var.get().strip()
        pacientes_encontrados = self.db.search_pacientes(termo) if termo else None
        self.carregar_pacientes(pacientes_encontrados)
    
    # --- JANELAS DE CADASTRO/EDIÇÃO ---
    def abrir_janela_profissional(self, profissional=None):
        janela = tk.Toplevel(self.root)
        janela.title("Cadastro de Profissional" if not profissional else "Editar Profissional")
        janela.geometry("500x400")
        janela.resizable(False, False)
        janela.transient(self.root)
        janela.grab_set()
        
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - (janela.winfo_width() // 2)
        y = (janela.winfo_screenheight() // 2) - (janela.winfo_height() // 2)
        janela.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(janela, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        titulo = ttk.Label(main_frame, text="Cadastro de Profissional" if not profissional else "Editar Profissional", style='Title.TLabel')
        titulo.pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="Nome:").pack(anchor='w')
        nome_var = tk.StringVar(value=profissional.nome if profissional else "")
        nome_entry = ttk.Entry(main_frame, textvariable=nome_var, width=50)
        nome_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="Especialidade:").pack(anchor='w')
        especialidade_var = tk.StringVar(value=profissional.especialidade if profissional else "")
        especialidade_entry = ttk.Entry(main_frame, textvariable=especialidade_var, width=50)
        especialidade_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="CRM/Registro:").pack(anchor='w')
        crm_var = tk.StringVar(value=profissional.crm_registro if profissional else "")
        crm_entry = ttk.Entry(main_frame, textvariable=crm_var, width=50)
        crm_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="Telefone:").pack(anchor='w')
        telefone_var = tk.StringVar(value=profissional.telefone if profissional else "")
        telefone_entry = ttk.Entry(main_frame, textvariable=telefone_var, width=50)
        telefone_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="Email:").pack(anchor='w')
        email_var = tk.StringVar(value=profissional.email if profissional else "")
        email_entry = ttk.Entry(main_frame, textvariable=email_var, width=50)
        email_entry.pack(pady=(0, 20), fill='x')
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        def salvar():
            if not nome_var.get().strip() or not especialidade_var.get().strip() or not crm_var.get().strip():
                messagebox.showerror("Erro", "Nome, Especialidade e CRM/Registro são obrigatórios!")
                return
            
            try:
                if profissional:
                    self.db.update_profissional(profissional.id, nome_var.get().strip(), especialidade_var.get().strip(), crm_var.get().strip(), telefone_var.get().strip(), email_var.get().strip())
                    messagebox.showinfo("Sucesso", "Profissional atualizado com sucesso!")
                else:
                    self.db.insert_profissional(nome_var.get().strip(), especialidade_var.get().strip(), crm_var.get().strip(), telefone_var.get().strip(), email_var.get().strip())
                    messagebox.showinfo("Sucesso", "Profissional cadastrado com sucesso!")
                
                janela.destroy()
                if hasattr(self, 'profissional_combo'): self.carregar_profissionais_login()
                if hasattr(self, 'tree_profissionais'): self.carregar_profissionais()
                
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    messagebox.showerror("Erro", "Este CRM/Registro já está cadastrado!")
                else:
                    messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        
        ttk.Button(btn_frame, text="Salvar", command=salvar).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=janela.destroy).pack(side='right')
        nome_entry.focus()

    def abrir_janela_paciente(self, paciente=None):
        janela = tk.Toplevel(self.root)
        janela.title("Cadastro de Paciente" if not paciente else "Editar Paciente")
        janela.geometry("800x800")
        janela.transient(self.root)
        janela.grab_set()

        canvas = tk.Canvas(janela)
        scrollbar = ttk.Scrollbar(janela, orient="vertical", command=canvas.yview)
        main_frame = ttk.Frame(canvas, padding="20")
        
        main_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- Seção de Dados Pessoais ---
        frame_pessoal = ttk.LabelFrame(main_frame, text="Dados Pessoais", padding="10")
        frame_pessoal.pack(fill='x', expand=True, pady=5)
        frame_pessoal.columnconfigure(1, weight=1)
        
        vars_pessoais = {
            "Nome": tk.StringVar(value=paciente.nome if paciente else ""),
            "Data de Nascimento (AAAA-MM-DD)": tk.StringVar(value=paciente.data_nascimento if paciente else ""),
            "CPF": tk.StringVar(value=paciente.cpf if paciente else ""),
            "Estado Civil": tk.StringVar(value=paciente.estado_civil if paciente else ""),
            "Profissão": tk.StringVar(value=paciente.profissao if paciente else "")
        }
        for i, (label, var) in enumerate(vars_pessoais.items()):
            ttk.Label(frame_pessoal, text=f"{label}:").grid(row=i, column=0, sticky='w', pady=3, padx=5)
            ttk.Entry(frame_pessoal, textvariable=var, width=50).grid(row=i, column=1, sticky='ew', pady=3, padx=5)

        # --- Seção de Contato e Endereço ---
        frame_contato = ttk.LabelFrame(main_frame, text="Contato e Endereço", padding="10")
        frame_contato.pack(fill='x', expand=True, pady=5)
        frame_contato.columnconfigure(1, weight=1)
        frame_contato.columnconfigure(3, weight=1)

        vars_contato = {
            "Telefone": tk.StringVar(value=paciente.telefone if paciente else ""),
            "Email": tk.StringVar(value=paciente.email if paciente else ""),
            "Rua": tk.StringVar(value=paciente.rua if paciente else ""),
            "Número": tk.StringVar(value=paciente.numero if paciente else ""),
            "Bairro": tk.StringVar(value=paciente.bairro if paciente else ""),
            "Cidade": tk.StringVar(value=paciente.cidade if paciente else ""),
            "Estado": tk.StringVar(value=paciente.estado if paciente else ""),
            "CEP": tk.StringVar(value=paciente.cep if paciente else "")
        }
        
        ttk.Label(frame_contato, text="Telefone:").grid(row=0, column=0, sticky='w', pady=3, padx=5)
        ttk.Entry(frame_contato, textvariable=vars_contato["Telefone"]).grid(row=0, column=1, columnspan=3, sticky='ew', pady=3, padx=5)
        ttk.Label(frame_contato, text="Email:").grid(row=1, column=0, sticky='w', pady=3, padx=5)
        ttk.Entry(frame_contato, textvariable=vars_contato["Email"]).grid(row=1, column=1, columnspan=3, sticky='ew', pady=3, padx=5)
        ttk.Label(frame_contato, text="Rua:").grid(row=2, column=0, sticky='w', pady=3, padx=5)
        ttk.Entry(frame_contato, textvariable=vars_contato["Rua"]).grid(row=2, column=1, columnspan=3, sticky='ew', pady=3, padx=5)
        
        ttk.Label(frame_contato, text="Número:").grid(row=3, column=0, sticky='w', pady=3, padx=5)
        ttk.Entry(frame_contato, textvariable=vars_contato["Número"]).grid(row=3, column=1, sticky='ew', pady=3, padx=5)
        ttk.Label(frame_contato, text="Bairro:").grid(row=3, column=2, sticky='w', pady=3, padx=5)
        ttk.Entry(frame_contato, textvariable=vars_contato["Bairro"]).grid(row=3, column=3, sticky='ew', pady=3, padx=5)

        ttk.Label(frame_contato, text="Cidade:").grid(row=4, column=0, sticky='w', pady=3, padx=5)
        ttk.Entry(frame_contato, textvariable=vars_contato["Cidade"]).grid(row=4, column=1, sticky='ew', pady=3, padx=5)
        ttk.Label(frame_contato, text="Estado:").grid(row=4, column=2, sticky='w', pady=3, padx=5)
        ttk.Entry(frame_contato, textvariable=vars_contato["Estado"]).grid(row=4, column=3, sticky='ew', pady=3, padx=5)
        
        ttk.Label(frame_contato, text="CEP:").grid(row=5, column=0, sticky='w', pady=3, padx=5)
        ttk.Entry(frame_contato, textvariable=vars_contato["CEP"]).grid(row=5, column=1, sticky='ew', pady=3, padx=5)

        # --- Seção de Anamnese ---
        frame_anamnese = ttk.LabelFrame(main_frame, text="Anamnese", padding="10")
        frame_anamnese.pack(fill='x', expand=True, pady=5)
        frame_anamnese.columnconfigure(1, weight=1)
        
        def create_text_field(parent, label, row, text_value=""):
            ttk.Label(parent, text=f"{label}:").grid(row=row, column=0, sticky='nw', pady=5, padx=5)
            text_widget = tk.Text(parent, height=3, width=60, wrap='word', font=('Arial', 10))
            text_widget.grid(row=row, column=1, sticky='ew', pady=5, padx=5)
            if text_value: text_widget.insert('1.0', text_value)
            return text_widget

        anamnese_texts = {
            "queixa": create_text_field(frame_anamnese, "Queixa Principal", 0, paciente.queixa_principal if paciente else ""),
            "historico": create_text_field(frame_anamnese, "Histórico da Doença Atual", 1, paciente.historico_doenca_atual if paciente else ""),
            "ant_pessoais": create_text_field(frame_anamnese, "Antecedentes Pessoais", 2, paciente.antecedentes_pessoais if paciente else ""),
            "ant_familiares": create_text_field(frame_anamnese, "Antecedentes Familiares", 3, paciente.antecedentes_familiares if paciente else ""),
            "habitos": create_text_field(frame_anamnese, "Hábitos de Vida", 4, paciente.habitos_vida if paciente else ""),
            "medicamentos": create_text_field(frame_anamnese, "Medicamentos em Uso", 5, paciente.medicamentos_em_uso if paciente else "")
        }
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=20)

        def salvar():
            try:
                dados = {var_name.split(' ')[0]: var.get().strip() for var_name, var in (list(vars_pessoais.items()) + list(vars_contato.items()))}
                dados_anamnese = {text_name: text_widget.get("1.0", tk.END).strip() for text_name, text_widget in anamnese_texts.items()}
                
                if not dados["Nome"]:
                    messagebox.showerror("Erro", "O nome do paciente é obrigatório.")
                    return
                if dados["Data"] and not re.match(r'^\d{4}-\d{2}-\d{2}$', dados["Data"]):
                    messagebox.showerror("Erro", "Formato da data de nascimento inválido. Use AAAA-MM-DD.")
                    return

                params = (
                    dados["Nome"], dados["Data"], dados["CPF"], dados["Estado"], dados["Profissão"],
                    dados["Telefone"], dados["Email"], dados["Rua"], dados["Número"], dados["Bairro"], dados["Cidade"],
                    vars_contato["Estado"].get(), dados["CEP"], dados_anamnese["queixa"], dados_anamnese["historico"],
                    dados_anamnese["ant_pessoais"], dados_anamnese["ant_familiares"], dados_anamnese["habitos"],
                    dados_anamnese["medicamentos"]
                )

                if paciente:
                    self.db.update_paciente(paciente.id, *params)
                else:
                    self.db.insert_paciente(*params)
                
                messagebox.showinfo("Sucesso", "Paciente salvo com sucesso!")
                janela.destroy()
                self.carregar_pacientes()
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    messagebox.showerror("Erro", "Este CPF já está cadastrado!")
                else:
                    messagebox.showerror("Erro", f"Ocorreu um erro ao salvar: {e}")

        ttk.Button(btn_frame, text="Salvar", command=salvar).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=janela.destroy).pack(side='right')

    def abrir_janela_procedimento(self, procedimento=None):
        janela = tk.Toplevel(self.root)
        janela.title("Cadastro de Procedimento" if not procedimento else "Editar Procedimento")
        janela.geometry("450x350")
        janela.resizable(False, False)
        janela.transient(self.root)
        janela.grab_set()
        
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - (janela.winfo_width() // 2)
        y = (janela.winfo_screenheight() // 2) - (janela.winfo_height() // 2)
        janela.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(janela, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        titulo = ttk.Label(main_frame, text="Cadastro de Procedimento" if not procedimento else "Editar Procedimento", style='Title.TLabel')
        titulo.pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="Nome do Procedimento:").pack(anchor='w')
        nome_var = tk.StringVar(value=procedimento.nome if procedimento else "")
        nome_entry = ttk.Entry(main_frame, textvariable=nome_var, width=50)
        nome_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="Duração (minutos):").pack(anchor='w')
        duracao_var = tk.StringVar(value=str(procedimento.duracao) if procedimento else "")
        duracao_entry = ttk.Entry(main_frame, textvariable=duracao_var, width=50)
        duracao_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="Valor (R$):").pack(anchor='w')
        valor_var = tk.StringVar(value=str(procedimento.valor) if procedimento else "")
        valor_entry = ttk.Entry(main_frame, textvariable=valor_var, width=50)
        valor_entry.pack(pady=(0, 20), fill='x')
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        def salvar():
            if not nome_var.get().strip():
                messagebox.showerror("Erro", "Nome do procedimento é obrigatório!")
                return
            try:
                duracao = int(duracao_var.get().strip())
                if duracao <= 0: raise ValueError()
            except ValueError:
                messagebox.showerror("Erro", "Duração deve ser um número inteiro positivo!")
                return
            try:
                valor = float(valor_var.get().strip().replace(',', '.'))
                if valor < 0: raise ValueError()
            except ValueError:
                messagebox.showerror("Erro", "Valor deve ser um número positivo!")
                return
            
            try:
                if procedimento:
                    self.db.update_procedimento(procedimento.id, nome_var.get().strip(), duracao, valor)
                    messagebox.showinfo("Sucesso", "Procedimento atualizado com sucesso!")
                else:
                    self.db.insert_procedimento(nome_var.get().strip(), duracao, valor)
                    messagebox.showinfo("Sucesso", "Procedimento cadastrado com sucesso!")
                
                janela.destroy()
                if hasattr(self, 'tree_procedimentos'): self.carregar_procedimentos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        
        ttk.Button(btn_frame, text="Salvar", command=salvar).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=janela.destroy).pack(side='right')
        nome_entry.focus()

    def abrir_janela_agendamento(self, agendamento=None, data_hora_preenchida=None):
        janela = tk.Toplevel(self.root)
        janela.title("Novo Agendamento")
        janela.geometry("500x600")
        janela.resizable(False, False)
        janela.transient(self.root)
        janela.grab_set()
        
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - (janela.winfo_width() // 2)
        y = (janela.winfo_screenheight() // 2) - (janela.winfo_height() // 2)
        janela.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(janela, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        titulo = ttk.Label(main_frame, text="Novo Agendamento", style='Title.TLabel')
        titulo.pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="Paciente:").pack(anchor='w')
        paciente_var = tk.StringVar()
        paciente_combo = ttk.Combobox(main_frame, textvariable=paciente_var, width=47, state='readonly')
        paciente_combo.pack(pady=(0, 10), fill='x')
        pacientes = self.db.get_pacientes() or []
        pacientes_valores = [f"{pac[1]} - CPF: {pac[3]}" for pac in pacientes]
        pacientes_dict = {f"{pac[1]} - CPF: {pac[3]}": pac[0] for pac in pacientes}
        paciente_combo['values'] = pacientes_valores
        
        ttk.Label(main_frame, text="Procedimento:").pack(anchor='w')
        procedimento_var = tk.StringVar()
        procedimento_combo = ttk.Combobox(main_frame, textvariable=procedimento_var, width=47, state='readonly')
        procedimento_combo.pack(pady=(0, 10), fill='x')
        procedimentos = self.db.get_procedimentos() or []
        procedimentos_valores = [f"{proc[1]} - {proc[2]}min - R$ {proc[3]:.2f}" for proc in procedimentos]
        procedimentos_dict = {f"{proc[1]} - {proc[2]}min - R$ {proc[3]:.2f}": proc[0] for proc in procedimentos}
        procedimento_combo['values'] = procedimentos_valores
        
        ttk.Label(main_frame, text="Profissional:").pack(anchor='w')
        profissional_var = tk.StringVar()
        profissional_combo = ttk.Combobox(main_frame, textvariable=profissional_var, width=47, state='readonly')
        profissional_combo.pack(pady=(0, 10), fill='x')
        profissionais = self.db.get_profissionais() or []
        profissionais_valores = [f"{prof[1]} - {prof[2]}" for prof in profissionais]
        profissionais_dict = {f"{prof[1]} - {prof[2]}": prof[0] for prof in profissionais}
        profissional_combo['values'] = profissionais_valores
        prof_logado_texto = f"{self.profissional_logado.nome} - {self.profissional_logado.especialidade}"
        if prof_logado_texto in profissionais_valores:
            profissional_var.set(prof_logado_texto)
        
        data_var = tk.StringVar()
        hora_var = tk.StringVar()
        if data_hora_preenchida:
            try:
                dt = datetime.strptime(data_hora_preenchida, "%Y-%m-%d %H:%M")
                data_var.set(dt.strftime("%Y-%m-%d")); hora_var.set(dt.strftime("%H:%M"))
            except ValueError:
                data_var.set(datetime.now().strftime("%Y-%m-%d")); hora_var.set("09:00")
        else:
            data_var.set(datetime.now().strftime("%Y-%m-%d")); hora_var.set("09:00")
        
        ttk.Label(main_frame, text="Data (AAAA-MM-DD):").pack(anchor='w')
        ttk.Entry(main_frame, textvariable=data_var, width=50).pack(pady=(0, 10), fill='x')
        ttk.Label(main_frame, text="Hora (HH:MM):").pack(anchor='w')
        ttk.Entry(main_frame, textvariable=hora_var, width=50).pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="Status:").pack(anchor='w')
        status_var = tk.StringVar(value="agendado")
        status_combo = ttk.Combobox(main_frame, textvariable=status_var, width=47, state='readonly', values=["agendado", "concluido", "cancelado"])
        status_combo.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="Observações:").pack(anchor='w')
        obs_text = tk.Text(main_frame, height=4, width=50)
        obs_text.pack(pady=(0, 20), fill='x')
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        def salvar():
            if not all([paciente_var.get(), procedimento_var.get(), profissional_var.get()]):
                messagebox.showerror("Erro", "Paciente, Procedimento e Profissional são obrigatórios!")
                return
            try:
                data_hora_str = f"{data_var.get().strip()} {hora_var.get().strip()}:00"
                datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("Erro", "Formato de data (AAAA-MM-DD) ou hora (HH:MM) inválido!")
                return
            
            try:
                self.db.insert_agendamento(pacientes_dict[paciente_var.get()], procedimentos_dict[procedimento_var.get()], 
                                           profissionais_dict[profissional_var.get()], data_hora_str, status_var.get(), 
                                           obs_text.get("1.0", tk.END).strip())
                messagebox.showinfo("Sucesso", "Agendamento cadastrado com sucesso!")
                janela.destroy()
                if hasattr(self, 'tree_agendamentos'): self.carregar_agendamentos()
                if hasattr(self, 'tree_consultas_dia'): self.atualizar_lista_consultas_dia()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        
        ttk.Button(btn_frame, text="Salvar", command=salvar).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=janela.destroy).pack(side='right')
        paciente_combo.focus()

    # --- MÉTODOS DE EDIÇÃO E REMOÇÃO ---
    def editar_profissional(self):
        if not hasattr(self, 'tree_profissionais'): return
        selection = self.tree_profissionais.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um profissional para editar!")
            return
        
        profissional = Profissional.from_tuple(self.tree_profissionais.item(selection[0])['values'])
        self.abrir_janela_profissional(profissional)
    
    def editar_paciente(self):
        if not hasattr(self, 'tree_pacientes'): return
        selection = self.tree_pacientes.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um paciente para editar!")
            return
        
        paciente_id = self.tree_pacientes.item(selection[0])['values'][0]
        paciente_data = self.db.get_paciente_by_id(paciente_id)
        
        if paciente_data:
            paciente = Paciente.from_tuple(paciente_data)
            self.abrir_janela_paciente(paciente)
        else:
            messagebox.showerror("Erro", "Não foi possível carregar os dados completos do paciente.")
    
    def editar_procedimento(self):
        if not hasattr(self, 'tree_procedimentos'): return
        selection = self.tree_procedimentos.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um procedimento para editar!")
            return
        
        valores = self.tree_procedimentos.item(selection[0])['values']
        valores_proc = list(valores)
        try:
            valores_proc[3] = float(str(valores_proc[3]).replace('R$ ', '').replace(',', '.'))
        except (ValueError, IndexError):
            messagebox.showerror("Erro", "Valor do procedimento inválido.")
            return
        
        procedimento = Procedimento.from_tuple(valores_proc)
        self.abrir_janela_procedimento(procedimento)
    
    def editar_agendamento(self):
        messagebox.showinfo("Informação", "Para editar um agendamento, por favor, remova o antigo e crie um novo com os dados corrigidos.")
        
    def remover_profissional(self):
        if not hasattr(self, 'tree_profissionais'): return
        selection = self.tree_profissionais.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um profissional para remover!")
            return
        
        item = self.tree_profissionais.item(selection[0])
        profissional_id, nome = item['values'][0], item['values'][1]
        
        if messagebox.askyesno("Confirmação", f"Deseja realmente remover o profissional '{nome}'?"):
            try:
                self.db.delete_profissional(profissional_id)
                messagebox.showinfo("Sucesso", "Profissional removido com sucesso!")
                self.carregar_profissionais()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover: {str(e)}.\nVerifique se há agendamentos vinculados.")

    def remover_paciente(self):
        if not hasattr(self, 'tree_pacientes'): return
        selection = self.tree_pacientes.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um paciente para remover!")
            return
        
        item = self.tree_pacientes.item(selection[0])
        paciente_id, nome = item['values'][0], item['values'][1]
        
        if messagebox.askyesno("Confirmação", f"Deseja realmente remover o paciente '{nome}'?"):
            try:
                self.db.delete_paciente(paciente_id)
                messagebox.showinfo("Sucesso", "Paciente removido com sucesso!")
                self.carregar_pacientes()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover: {str(e)}.\nVerifique se há agendamentos vinculados.")

    def remover_procedimento(self):
        if not hasattr(self, 'tree_procedimentos'): return
        selection = self.tree_procedimentos.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um procedimento para remover!")
            return
        
        item = self.tree_procedimentos.item(selection[0])
        procedimento_id, nome = item['values'][0], item['values'][1]
        
        if messagebox.askyesno("Confirmação", f"Deseja realmente remover o procedimento '{nome}'?"):
            try:
                self.db.delete_procedimento(procedimento_id)
                messagebox.showinfo("Sucesso", "Procedimento removido com sucesso!")
                self.carregar_procedimentos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover: {str(e)}.\nVerifique se há agendamentos vinculados.")

    def ver_prontuario_paciente_da_lista(self):
        if not hasattr(self, 'tree_pacientes'): return
        selection = self.tree_pacientes.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um paciente para ver o prontuário!")
            return
        paciente_id = self.tree_pacientes.item(selection[0])['values'][0]
        self.abrir_prontuario_paciente(paciente_id)

def main():
    root = tk.Tk()
    app = ClinicaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
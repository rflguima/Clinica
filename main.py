import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import font
from datetime import datetime, date
import re
from database import DatabaseManager
from models import Profissional, Paciente, Procedimento, Agendamento, StatusAgendamento

class ClinicaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão de Clínica")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Configurar estilo
        self.setup_styles()
        
        # Inicializar banco de dados
        self.db = DatabaseManager()
        
        # Variável para armazenar o profissional logado
        self.profissional_logado = None
        
        # Criar interface de login
        self.criar_tela_login()
    
    def setup_styles(self):
        """Configura estilos da interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Custom.Treeview', font=('Arial', 10))
        style.configure('Custom.Treeview.Heading', font=('Arial', 10, 'bold'))
    
    def criar_tela_login(self):
        """Cria a tela de login/seleção de profissional"""
        # Limpar a janela
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal do login
        login_frame = ttk.Frame(self.root)
        login_frame.pack(expand=True, fill='both', padx=50, pady=50)
        
        # Título
        titulo = ttk.Label(login_frame, text="Sistema de Gestão de Clínica", style='Title.TLabel')
        titulo.pack(pady=30)
        
        # Subtítulo
        subtitulo = ttk.Label(login_frame, text="Selecione seu perfil profissional", font=('Arial', 12))
        subtitulo.pack(pady=10)
        
        # Frame para seleção de profissional
        select_frame = ttk.Frame(login_frame)
        select_frame.pack(pady=30)
        
        ttk.Label(select_frame, text="Profissional:", font=('Arial', 11)).pack(anchor='w')
        
        self.profissional_var = tk.StringVar()
        self.profissional_combo = ttk.Combobox(select_frame, textvariable=self.profissional_var, 
                                              width=40, font=('Arial', 11))
        self.profissional_combo.pack(pady=5)
        
        # Carregar profissionais
        self.carregar_profissionais_login()
        
        # Botões
        btn_frame = ttk.Frame(login_frame)
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="Entrar", command=self.fazer_login, 
                  width=15).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Cadastrar Novo Profissional", 
                  command=self.cadastrar_profissional_inicial, width=25).pack(side='left', padx=10)
    
    def carregar_profissionais_login(self):
        """Carrega profissionais para o combo de login"""
        profissionais = self.db.get_profissionais()
        valores = []
        
        for prof in profissionais:
            valores.append(f"{prof[1]} - {prof[2]} (CRM: {prof[3]})")
        
        self.profissional_combo['values'] = valores
        
        if valores:
            self.profissional_combo.current(0)
    
    def cadastrar_profissional_inicial(self):
        """Abre janela para cadastrar o primeiro profissional"""
        self.abrir_janela_profissional()
        # Recarregar a lista após o cadastro
        self.carregar_profissionais_login()
    
    def fazer_login(self):
        """Realiza o login do profissional selecionado"""
        if not self.profissional_var.get():
            messagebox.showwarning("Aviso", "Selecione um profissional!")
            return
        
        # Extrair ID do profissional selecionado
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
        """Cria a interface principal do sistema"""
        # Limpar a janela
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame superior com informações do usuário
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(header_frame, text=f"Usuário: {self.profissional_logado.nome} - {self.profissional_logado.especialidade}", 
                 style='Heading.TLabel').pack(side='left')
        
        ttk.Button(header_frame, text="Logout", command=self.fazer_logout).pack(side='right')
        
        # Notebook para as abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Criar abas
        self.criar_aba_profissionais()
        self.criar_aba_pacientes()
        self.criar_aba_procedimentos()
        self.criar_aba_agendamentos()
    
    def fazer_logout(self):
        """Faz logout e retorna à tela de login"""
        self.profissional_logado = None
        self.criar_tela_login()
    
    def criar_aba_profissionais(self):
        """Cria a aba de gerenciamento de profissionais"""
        # Frame da aba
        prof_frame = ttk.Frame(self.notebook)
        self.notebook.add(prof_frame, text="Profissionais")
        
        # Frame superior com botões
        btn_frame = ttk.Frame(prof_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Novo Profissional", 
                  command=self.abrir_janela_profissional).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Editar", 
                  command=self.editar_profissional).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Remover", 
                  command=self.remover_profissional).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Atualizar", 
                  command=self.carregar_profissionais).pack(side='left', padx=5)
        
        # Treeview para lista de profissionais
        columns = ('ID', 'Nome', 'Especialidade', 'CRM', 'Telefone', 'Email')
        self.tree_profissionais = ttk.Treeview(prof_frame, columns=columns, show='headings', style='Custom.Treeview')
        
        # Configurar colunas
        self.tree_profissionais.heading('ID', text='ID')
        self.tree_profissionais.heading('Nome', text='Nome')
        self.tree_profissionais.heading('Especialidade', text='Especialidade')
        self.tree_profissionais.heading('CRM', text='CRM/Registro')
        self.tree_profissionais.heading('Telefone', text='Telefone')
        self.tree_profissionais.heading('Email', text='Email')
        
        self.tree_profissionais.column('ID', width=50)
        self.tree_profissionais.column('Nome', width=200)
        self.tree_profissionais.column('Especialidade', width=150)
        self.tree_profissionais.column('CRM', width=120)
        self.tree_profissionais.column('Telefone', width=120)
        self.tree_profissionais.column('Email', width=200)
        
        # Scrollbar
        scrollbar_prof = ttk.Scrollbar(prof_frame, orient='vertical', command=self.tree_profissionais.yview)
        self.tree_profissionais.configure(yscrollcommand=scrollbar_prof.set)
        
        # Pack treeview e scrollbar
        self.tree_profissionais.pack(side='left', expand=True, fill='both', padx=(10, 0), pady=5)
        scrollbar_prof.pack(side='right', fill='y', padx=(0, 10), pady=5)
        
        # Carregar dados
        self.carregar_profissionais()
    
    def criar_aba_pacientes(self):
        """Cria a aba de gerenciamento de pacientes"""
        # Frame da aba
        pac_frame = ttk.Frame(self.notebook)
        self.notebook.add(pac_frame, text="Pacientes")
        
        # Frame superior com botões e busca
        top_frame = ttk.Frame(pac_frame)
        top_frame.pack(fill='x', padx=10, pady=5)
        
        # Botões
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side='left')
        
        ttk.Button(btn_frame, text="Novo Paciente", 
                  command=self.abrir_janela_paciente).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Editar", 
                  command=self.editar_paciente).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Remover", 
                  command=self.remover_paciente).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Histórico", 
                  command=self.ver_historico_paciente).pack(side='left', padx=5)
        
        # Frame de busca
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side='right')
        
        ttk.Label(search_frame, text="Buscar:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.buscar_pacientes)
        
        ttk.Button(search_frame, text="Limpar", 
                  command=self.limpar_busca_pacientes).pack(side='left', padx=5)
        
        # Treeview para lista de pacientes
        columns = ('ID', 'Nome', 'Telefone', 'CPF', 'Endereço', 'Data Nascimento', 'Idade')
        self.tree_pacientes = ttk.Treeview(pac_frame, columns=columns, show='headings', style='Custom.Treeview')
        
        # Configurar colunas
        self.tree_pacientes.heading('ID', text='ID')
        self.tree_pacientes.heading('Nome', text='Nome')
        self.tree_pacientes.heading('Telefone', text='Telefone')
        self.tree_pacientes.heading('CPF', text='CPF')
        self.tree_pacientes.heading('Endereço', text='Endereço')
        self.tree_pacientes.heading('Data Nascimento', text='Nascimento')
        self.tree_pacientes.heading('Idade', text='Idade')
        
        self.tree_pacientes.column('ID', width=50)
        self.tree_pacientes.column('Nome', width=200)
        self.tree_pacientes.column('Telefone', width=120)
        self.tree_pacientes.column('CPF', width=120)
        self.tree_pacientes.column('Endereço', width=200)
        self.tree_pacientes.column('Data Nascimento', width=100)
        self.tree_pacientes.column('Idade', width=60)
        
        # Scrollbar
        scrollbar_pac = ttk.Scrollbar(pac_frame, orient='vertical', command=self.tree_pacientes.yview)
        self.tree_pacientes.configure(yscrollcommand=scrollbar_pac.set)
        
        # Pack treeview e scrollbar
        self.tree_pacientes.pack(side='left', expand=True, fill='both', padx=(10, 0), pady=5)
        scrollbar_pac.pack(side='right', fill='y', padx=(0, 10), pady=5)
        
        # Carregar dados
        self.carregar_pacientes()
    
    def criar_aba_procedimentos(self):
        """Cria a aba de gerenciamento de procedimentos"""
        # Frame da aba
        proc_frame = ttk.Frame(self.notebook)
        self.notebook.add(proc_frame, text="Procedimentos")
        
        # Frame superior com botões
        btn_frame = ttk.Frame(proc_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Novo Procedimento", 
                  command=self.abrir_janela_procedimento).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Editar", 
                  command=self.editar_procedimento).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Remover", 
                  command=self.remover_procedimento).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Atualizar", 
                  command=self.carregar_procedimentos).pack(side='left', padx=5)
        
        # Treeview para lista de procedimentos
        columns = ('ID', 'Nome', 'Duração (min)', 'Valor (R$)')
        self.tree_procedimentos = ttk.Treeview(proc_frame, columns=columns, show='headings', style='Custom.Treeview')
        
        # Configurar colunas
        self.tree_procedimentos.heading('ID', text='ID')
        self.tree_procedimentos.heading('Nome', text='Nome do Procedimento')
        self.tree_procedimentos.heading('Duração (min)', text='Duração (min)')
        self.tree_procedimentos.heading('Valor (R$)', text='Valor (R$)')
        
        self.tree_procedimentos.column('ID', width=50)
        self.tree_procedimentos.column('Nome', width=300)
        self.tree_procedimentos.column('Duração (min)', width=120)
        self.tree_procedimentos.column('Valor (R$)', width=120)
        
        # Scrollbar
        scrollbar_proc = ttk.Scrollbar(proc_frame, orient='vertical', command=self.tree_procedimentos.yview)
        self.tree_procedimentos.configure(yscrollcommand=scrollbar_proc.set)
        
        # Pack treeview e scrollbar
        self.tree_procedimentos.pack(side='left', expand=True, fill='both', padx=(10, 0), pady=5)
        scrollbar_proc.pack(side='right', fill='y', padx=(0, 10), pady=5)
        
        # Carregar dados
        self.carregar_procedimentos()
    
    def criar_aba_agendamentos(self):
        """Cria a aba de gerenciamento de agendamentos"""
        # Frame da aba
        agend_frame = ttk.Frame(self.notebook)
        self.notebook.add(agend_frame, text="Agendamentos")
        
        # Frame superior com botões e filtros
        top_frame = ttk.Frame(agend_frame)
        top_frame.pack(fill='x', padx=10, pady=5)
        
        # Botões
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side='left')
        
        ttk.Button(btn_frame, text="Novo Agendamento", 
                  command=self.abrir_janela_agendamento).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Editar", 
                  command=self.editar_agendamento).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Remover", 
                  command=self.remover_agendamento).pack(side='left', padx=5)
        
        # Frame de filtros
        filter_frame = ttk.Frame(top_frame)
        filter_frame.pack(side='right')
        
        ttk.Label(filter_frame, text="Data:").pack(side='left', padx=5)
        self.data_filter_var = tk.StringVar()
        self.data_filter_var.set(datetime.now().strftime("%Y-%m-%d"))
        data_entry = ttk.Entry(filter_frame, textvariable=self.data_filter_var, width=12)
        data_entry.pack(side='left', padx=5)
        
        ttk.Button(filter_frame, text="Filtrar por Data", 
                  command=self.filtrar_agendamentos_data).pack(side='left', padx=5)
        ttk.Button(filter_frame, text="Todos", 
                  command=self.carregar_agendamentos).pack(side='left', padx=5)
        
        # Checkbox para mostrar apenas agendamentos do profissional logado
        self.apenas_meus_var = tk.BooleanVar()
        self.apenas_meus_var.set(True)
        ttk.Checkbutton(filter_frame, text="Apenas meus agendamentos", 
                       variable=self.apenas_meus_var, 
                       command=self.carregar_agendamentos).pack(side='left', padx=5)
        
        # Treeview para lista de agendamentos
        columns = ('ID', 'Paciente', 'Procedimento', 'Profissional', 'Data/Hora', 'Status', 'Observações')
        self.tree_agendamentos = ttk.Treeview(agend_frame, columns=columns, show='headings', style='Custom.Treeview')
        
        # Configurar colunas
        self.tree_agendamentos.heading('ID', text='ID')
        self.tree_agendamentos.heading('Paciente', text='Paciente')
        self.tree_agendamentos.heading('Procedimento', text='Procedimento')
        self.tree_agendamentos.heading('Profissional', text='Profissional')
        self.tree_agendamentos.heading('Data/Hora', text='Data/Hora')
        self.tree_agendamentos.heading('Status', text='Status')
        self.tree_agendamentos.heading('Observações', text='Observações')
        
        self.tree_agendamentos.column('ID', width=50)
        self.tree_agendamentos.column('Paciente', width=150)
        self.tree_agendamentos.column('Procedimento', width=150)
        self.tree_agendamentos.column('Profissional', width=120)
        self.tree_agendamentos.column('Data/Hora', width=130)
        self.tree_agendamentos.column('Status', width=100)
        self.tree_agendamentos.column('Observações', width=200)
        
        # Scrollbar
        scrollbar_agend = ttk.Scrollbar(agend_frame, orient='vertical', command=self.tree_agendamentos.yview)
        self.tree_agendamentos.configure(yscrollcommand=scrollbar_agend.set)
        
        # Pack treeview e scrollbar
        self.tree_agendamentos.pack(side='left', expand=True, fill='both', padx=(10, 0), pady=5)
        scrollbar_agend.pack(side='right', fill='y', padx=(0, 10), pady=5)
        
        # Carregar dados
        self.carregar_agendamentos()
    
    # Métodos para carregar dados nas listas
    def carregar_profissionais(self):
        """Carrega profissionais na treeview"""
        # Limpar dados existentes
        for item in self.tree_profissionais.get_children():
            self.tree_profissionais.delete(item)
        
        # Carregar novos dados
        profissionais = self.db.get_profissionais()
        for prof in profissionais:
            self.tree_profissionais.insert('', 'end', values=prof)
    
    def carregar_pacientes(self):
        """Carrega pacientes na treeview"""
        # Limpar dados existentes
        for item in self.tree_pacientes.get_children():
            self.tree_pacientes.delete(item)
        
        # Carregar novos dados
        pacientes = self.db.get_pacientes()
        for pac in pacientes:
            # Calcular idade
            idade = ""
            if pac[5]:  # data_nascimento
                try:
                    nascimento = datetime.strptime(pac[5], "%Y-%m-%d")
                    hoje = datetime.now()
                    idade = hoje.year - nascimento.year
                    if hoje.month < nascimento.month or (hoje.month == nascimento.month and hoje.day < nascimento.day):
                        idade -= 1
                except:
                    idade = ""
            
            # Inserir com idade calculada
            valores = list(pac) + [idade]
            self.tree_pacientes.insert('', 'end', values=valores)
    
    def carregar_procedimentos(self):
        """Carrega procedimentos na treeview"""
        # Limpar dados existentes
        for item in self.tree_procedimentos.get_children():
            self.tree_procedimentos.delete(item)
        
        # Carregar novos dados
        procedimentos = self.db.get_procedimentos()
        for proc in procedimentos:
            # Formatar valor
            valores = list(proc)
            valores[3] = f"R$ {valores[3]:.2f}"
            self.tree_procedimentos.insert('', 'end', values=valores)
    
    def carregar_agendamentos(self):
        """Carrega agendamentos na treeview"""
        # Limpar dados existentes
        for item in self.tree_agendamentos.get_children():
            self.tree_agendamentos.delete(item)
        
        # Carregar novos dados
        profissional_id = self.profissional_logado.id if self.apenas_meus_var.get() else None
        agendamentos = self.db.get_agendamentos(profissional_id)
        
        for agend in agendamentos:
            # Formatar data/hora
            valores = list(agend)
            try:
                dt = datetime.strptime(valores[4], "%Y-%m-%d %H:%M:%S")
                valores[4] = dt.strftime("%d/%m/%Y %H:%M")
            except:
                pass
            
            self.tree_agendamentos.insert('', 'end', values=valores)
    
    # Métodos para janelas de cadastro/edição
    def abrir_janela_profissional(self, profissional=None):
        """Abre janela para cadastro/edição de profissional"""
        janela = tk.Toplevel(self.root)
        janela.title("Cadastro de Profissional" if not profissional else "Editar Profissional")
        janela.geometry("500x400")
        janela.resizable(False, False)
        janela.transient(self.root)
        janela.grab_set()
        
        # Centralizar janela
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - (janela.winfo_width() // 2)
        y = (janela.winfo_screenheight() // 2) - (janela.winfo_height() // 2)
        janela.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(janela, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="Cadastro de Profissional" if not profissional else "Editar Profissional", 
                          style='Title.TLabel')
        titulo.pack(pady=(0, 20))
        
        # Campos
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
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        def salvar():
            # Validações
            if not nome_var.get().strip():
                messagebox.showerror("Erro", "Nome é obrigatório!")
                return
            
            if not especialidade_var.get().strip():
                messagebox.showerror("Erro", "Especialidade é obrigatória!")
                return
            
            if not crm_var.get().strip():
                messagebox.showerror("Erro", "CRM/Registro é obrigatório!")
                return
            
            try:
                if profissional:  # Edição
                    self.db.update_profissional(
                        profissional.id,
                        nome_var.get().strip(),
                        especialidade_var.get().strip(),
                        crm_var.get().strip(),
                        telefone_var.get().strip(),
                        email_var.get().strip()
                    )
                    messagebox.showinfo("Sucesso", "Profissional atualizado com sucesso!")
                else:  # Novo cadastro
                    self.db.insert_profissional(
                        nome_var.get().strip(),
                        especialidade_var.get().strip(),
                        crm_var.get().strip(),
                        telefone_var.get().strip(),
                        email_var.get().strip()
                    )
                    messagebox.showinfo("Sucesso", "Profissional cadastrado com sucesso!")
                
                janela.destroy()
                if hasattr(self, 'tree_profissionais'):
                    self.carregar_profissionais()
                
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    messagebox.showerror("Erro", "Este CRM/Registro já está cadastrado!")
                else:
                    messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        
        ttk.Button(btn_frame, text="Salvar", command=salvar).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=janela.destroy).pack(side='right')
        
        # Focar no primeiro campo
        nome_entry.focus()
    
    def abrir_janela_paciente(self, paciente=None):
        """Abre janela para cadastro/edição de paciente"""
        janela = tk.Toplevel(self.root)
        janela.title("Cadastro de Paciente" if not paciente else "Editar Paciente")
        janela.geometry("500x500")
        janela.resizable(False, False)
        janela.transient(self.root)
        janela.grab_set()
        
        # Centralizar janela
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - (janela.winfo_width() // 2)
        y = (janela.winfo_screenheight() // 2) - (janela.winfo_height() // 2)
        janela.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(janela, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="Cadastro de Paciente" if not paciente else "Editar Paciente", 
                          style='Title.TLabel')
        titulo.pack(pady=(0, 20))
        
        # Campos
        ttk.Label(main_frame, text="Nome:").pack(anchor='w')
        nome_var = tk.StringVar(value=paciente.nome if paciente else "")
        nome_entry = ttk.Entry(main_frame, textvariable=nome_var, width=50)
        nome_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="Telefone:").pack(anchor='w')
        telefone_var = tk.StringVar(value=paciente.telefone if paciente else "")
        telefone_entry = ttk.Entry(main_frame, textvariable=telefone_var, width=50)
        telefone_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="CPF:").pack(anchor='w')
        cpf_var = tk.StringVar(value=paciente.cpf if paciente else "")
        cpf_entry = ttk.Entry(main_frame, textvariable=cpf_var, width=50)
        cpf_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="Endereço:").pack(anchor='w')
        endereco_var = tk.StringVar(value=paciente.endereco if paciente else "")
        endereco_entry = ttk.Entry(main_frame, textvariable=endereco_var, width=50)
        endereco_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="Data de Nascimento (AAAA-MM-DD):").pack(anchor='w')
        data_nasc_var = tk.StringVar(value=paciente.data_nascimento if paciente else "")
        data_nasc_entry = ttk.Entry(main_frame, textvariable=data_nasc_var, width=50)
        data_nasc_entry.pack(pady=(0, 20), fill='x')
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        def salvar():
            # Validações
            if not nome_var.get().strip():
                messagebox.showerror("Erro", "Nome é obrigatório!")
                return
            
            # Validar formato da data
            if data_nasc_var.get().strip():
                try:
                    datetime.strptime(data_nasc_var.get().strip(), "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Erro", "Data de nascimento deve estar no formato AAAA-MM-DD!")
                    return
            
            try:
                if paciente:  # Edição
                    self.db.update_paciente(
                        paciente.id,
                        nome_var.get().strip(),
                        telefone_var.get().strip(),
                        cpf_var.get().strip(),
                        endereco_var.get().strip(),
                        data_nasc_var.get().strip()
                    )
                    messagebox.showinfo("Sucesso", "Paciente atualizado com sucesso!")
                else:  # Novo cadastro
                    self.db.insert_paciente(
                        nome_var.get().strip(),
                        telefone_var.get().strip(),
                        cpf_var.get().strip(),
                        endereco_var.get().strip(),
                        data_nasc_var.get().strip()
                    )
                    messagebox.showinfo("Sucesso", "Paciente cadastrado com sucesso!")
                
                janela.destroy()
                if hasattr(self, 'tree_pacientes'):
                    self.carregar_pacientes()
                
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    messagebox.showerror("Erro", "Este CPF já está cadastrado!")
                else:
                    messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        
        ttk.Button(btn_frame, text="Salvar", command=salvar).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=janela.destroy).pack(side='right')
        
        # Focar no primeiro campo
        nome_entry.focus()
    
    def abrir_janela_procedimento(self, procedimento=None):
        """Abre janela para cadastro/edição de procedimento"""
        janela = tk.Toplevel(self.root)
        janela.title("Cadastro de Procedimento" if not procedimento else "Editar Procedimento")
        janela.geometry("450x350")
        janela.resizable(False, False)
        janela.transient(self.root)
        janela.grab_set()
        
        # Centralizar janela
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - (janela.winfo_width() // 2)
        y = (janela.winfo_screenheight() // 2) - (janela.winfo_height() // 2)
        janela.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(janela, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="Cadastro de Procedimento" if not procedimento else "Editar Procedimento", 
                          style='Title.TLabel')
        titulo.pack(pady=(0, 20))
        
        # Campos
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
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        def salvar():
            # Validações
            if not nome_var.get().strip():
                messagebox.showerror("Erro", "Nome do procedimento é obrigatório!")
                return
            
            try:
                duracao = int(duracao_var.get().strip())
                if duracao <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Erro", "Duração deve ser um número inteiro positivo!")
                return
            
            try:
                valor = float(valor_var.get().strip().replace(',', '.'))
                if valor < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Erro", "Valor deve ser um número positivo!")
                return
            
            try:
                if procedimento:  # Edição
                    self.db.update_procedimento(
                        procedimento.id,
                        nome_var.get().strip(),
                        duracao,
                        valor
                    )
                    messagebox.showinfo("Sucesso", "Procedimento atualizado com sucesso!")
                else:  # Novo cadastro
                    self.db.insert_procedimento(
                        nome_var.get().strip(),
                        duracao,
                        valor
                    )
                    messagebox.showinfo("Sucesso", "Procedimento cadastrado com sucesso!")
                
                janela.destroy()
                if hasattr(self, 'tree_procedimentos'):
                    self.carregar_procedimentos()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        
        ttk.Button(btn_frame, text="Salvar", command=salvar).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=janela.destroy).pack(side='right')
        
        # Focar no primeiro campo
        nome_entry.focus()
    
    def abrir_janela_agendamento(self, agendamento=None):
        """Abre janela para cadastro/edição de agendamento"""
        janela = tk.Toplevel(self.root)
        janela.title("Novo Agendamento" if not agendamento else "Editar Agendamento")
        janela.geometry("500x600")
        janela.resizable(False, False)
        janela.transient(self.root)
        janela.grab_set()
        
        # Centralizar janela
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - (janela.winfo_width() // 2)
        y = (janela.winfo_screenheight() // 2) - (janela.winfo_height() // 2)
        janela.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(janela, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="Novo Agendamento" if not agendamento else "Editar Agendamento", 
                          style='Title.TLabel')
        titulo.pack(pady=(0, 20))
        
        # Paciente
        ttk.Label(main_frame, text="Paciente:").pack(anchor='w')
        paciente_var = tk.StringVar()
        paciente_combo = ttk.Combobox(main_frame, textvariable=paciente_var, width=47)
        paciente_combo.pack(pady=(0, 10), fill='x')
        
        # Carregar pacientes
        pacientes = self.db.get_pacientes()
        pacientes_valores = []
        pacientes_dict = {}
        
        for pac in pacientes:
            texto = f"{pac[1]} - CPF: {pac[3]}"
            pacientes_valores.append(texto)
            pacientes_dict[texto] = pac[0]
        
        paciente_combo['values'] = pacientes_valores
        
        # Procedimento
        ttk.Label(main_frame, text="Procedimento:").pack(anchor='w')
        procedimento_var = tk.StringVar()
        procedimento_combo = ttk.Combobox(main_frame, textvariable=procedimento_var, width=47)
        procedimento_combo.pack(pady=(0, 10), fill='x')
        
        # Carregar procedimentos
        procedimentos = self.db.get_procedimentos()
        procedimentos_valores = []
        procedimentos_dict = {}
        
        for proc in procedimentos:
            texto = f"{proc[1]} - {proc[2]}min - R$ {proc[3]:.2f}"
            procedimentos_valores.append(texto)
            procedimentos_dict[texto] = proc[0]
        
        procedimento_combo['values'] = procedimentos_valores
        
        # Profissional
        ttk.Label(main_frame, text="Profissional:").pack(anchor='w')
        profissional_var = tk.StringVar()
        profissional_combo = ttk.Combobox(main_frame, textvariable=profissional_var, width=47)
        profissional_combo.pack(pady=(0, 10), fill='x')
        
        # Carregar profissionais
        profissionais = self.db.get_profissionais()
        profissionais_valores = []
        profissionais_dict = {}
        
        for prof in profissionais:
            texto = f"{prof[1]} - {prof[2]}"
            profissionais_valores.append(texto)
            profissionais_dict[texto] = prof[0]
        
        profissional_combo['values'] = profissionais_valores
        
        # Definir profissional logado como padrão
        prof_logado_texto = f"{self.profissional_logado.nome} - {self.profissional_logado.especialidade}"
        if prof_logado_texto in profissionais_valores:
            profissional_var.set(prof_logado_texto)
        
        # Data
        ttk.Label(main_frame, text="Data (AAAA-MM-DD):").pack(anchor='w')
        data_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        data_entry = ttk.Entry(main_frame, textvariable=data_var, width=50)
        data_entry.pack(pady=(0, 10), fill='x')
        
        # Hora
        ttk.Label(main_frame, text="Hora (HH:MM):").pack(anchor='w')
        hora_var = tk.StringVar(value="09:00")
        hora_entry = ttk.Entry(main_frame, textvariable=hora_var, width=50)
        hora_entry.pack(pady=(0, 10), fill='x')
        
        # Status
        ttk.Label(main_frame, text="Status:").pack(anchor='w')
        status_var = tk.StringVar(value="agendado")
        status_combo = ttk.Combobox(main_frame, textvariable=status_var, width=47)
        status_combo['values'] = ["agendado", "concluido", "cancelado"]
        status_combo.pack(pady=(0, 10), fill='x')
        
        # Observações
        ttk.Label(main_frame, text="Observações:").pack(anchor='w')
        obs_text = tk.Text(main_frame, height=4, width=50)
        obs_text.pack(pady=(0, 20), fill='x')
        
        # Se for edição, preencher campos
        if agendamento:
            # Aqui você precisaria carregar os dados do agendamento
            # Por simplicidade, vou deixar os campos vazios
            pass
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        def salvar():
            # Validações
            if not paciente_var.get():
                messagebox.showerror("Erro", "Selecione um paciente!")
                return
            
            if not procedimento_var.get():
                messagebox.showerror("Erro", "Selecione um procedimento!")
                return
            
            if not profissional_var.get():
                messagebox.showerror("Erro", "Selecione um profissional!")
                return
            
            # Validar data e hora
            try:
                data_hora_str = f"{data_var.get()} {hora_var.get()}:00"
                datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("Erro", "Data ou hora inválida!")
                return
            
            try:
                paciente_id = pacientes_dict[paciente_var.get()]
                procedimento_id = procedimentos_dict[procedimento_var.get()]
                profissional_id = profissionais_dict[profissional_var.get()]
                observacoes = obs_text.get("1.0", tk.END).strip()
                
                if agendamento:  # Edição
                    self.db.update_agendamento(
                        agendamento.id,
                        paciente_id,
                        procedimento_id,
                        profissional_id,
                        data_hora_str,
                        status_var.get(),
                        observacoes
                    )
                    messagebox.showinfo("Sucesso", "Agendamento atualizado com sucesso!")
                else:  # Novo cadastro
                    self.db.insert_agendamento(
                        paciente_id,
                        procedimento_id,
                        profissional_id,
                        data_hora_str,
                        status_var.get(),
                        observacoes
                    )
                    messagebox.showinfo("Sucesso", "Agendamento cadastrado com sucesso!")
                
                janela.destroy()
                if hasattr(self, 'tree_agendamentos'):
                    self.carregar_agendamentos()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        
        ttk.Button(btn_frame, text="Salvar", command=salvar).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=janela.destroy).pack(side='right')
        
        # Focar no primeiro campo
        paciente_combo.focus()
    
    # Métodos para edição
    def editar_profissional(self):
        """Edita o profissional selecionado"""
        selection = self.tree_profissionais.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um profissional para editar!")
            return
        
        item = self.tree_profissionais.item(selection[0])
        valores = item['values']
        
        profissional = Profissional.from_tuple(valores)
        self.abrir_janela_profissional(profissional)
    
    def editar_paciente(self):
        """Edita o paciente selecionado"""
        selection = self.tree_pacientes.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um paciente para editar!")
            return
        
        item = self.tree_pacientes.item(selection[0])
        valores = item['values']
        
        # Remover a coluna de idade que foi adicionada na exibição
        valores_paciente = valores[:6]
        paciente = Paciente.from_tuple(valores_paciente)
        self.abrir_janela_paciente(paciente)
    
    def editar_procedimento(self):
        """Edita o procedimento selecionado"""
        selection = self.tree_procedimentos.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um procedimento para editar!")
            return
        
        item = self.tree_procedimentos.item(selection[0])
        valores = item['values']
        
        # Converter valor de volta para float
        valores_proc = list(valores)
        valores_proc[3] = float(valores_proc[3].replace('R$ ', '').replace(',', '.'))
        
        procedimento = Procedimento.from_tuple(valores_proc)
        self.abrir_janela_procedimento(procedimento)
    
    def editar_agendamento(self):
        """Edita o agendamento selecionado"""
        selection = self.tree_agendamentos.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um agendamento para editar!")
            return
        
        item = self.tree_agendamentos.item(selection[0])
        valores = item['values']
        
        # Por simplicidade, vou abrir a janela de novo agendamento
        # Em uma implementação completa, você carregaria os dados do agendamento
        self.abrir_janela_agendamento()
    
    # Métodos para remoção
    def remover_profissional(self):
        """Remove o profissional selecionado"""
        selection = self.tree_profissionais.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um profissional para remover!")
            return
        
        item = self.tree_profissionais.item(selection[0])
        profissional_id = item['values'][0]
        nome = item['values'][1]
        
        if messagebox.askyesno("Confirmação", f"Deseja realmente remover o profissional '{nome}'?"):
            try:
                self.db.delete_profissional(profissional_id)
                messagebox.showinfo("Sucesso", "Profissional removido com sucesso!")
                self.carregar_profissionais()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover: {str(e)}")
    
    def remover_paciente(self):
        """Remove o paciente selecionado"""
        selection = self.tree_pacientes.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um paciente para remover!")
            return
        
        item = self.tree_pacientes.item(selection[0])
        paciente_id = item['values'][0]
        nome = item['values'][1]
        
        if messagebox.askyesno("Confirmação", f"Deseja realmente remover o paciente '{nome}'?"):
            try:
                self.db.delete_paciente(paciente_id)
                messagebox.showinfo("Sucesso", "Paciente removido com sucesso!")
                self.carregar_pacientes()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover: {str(e)}")
    
    def remover_procedimento(self):
        """Remove o procedimento selecionado"""
        selection = self.tree_procedimentos.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um procedimento para remover!")
            return
        
        item = self.tree_procedimentos.item(selection[0])
        procedimento_id = item['values'][0]
        nome = item['values'][1]
        
        if messagebox.askyesno("Confirmação", f"Deseja realmente remover o procedimento '{nome}'?"):
            try:
                self.db.delete_procedimento(procedimento_id)
                messagebox.showinfo("Sucesso", "Procedimento removido com sucesso!")
                self.carregar_procedimentos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover: {str(e)}")
    
    def remover_agendamento(self):
        """Remove o agendamento selecionado"""
        selection = self.tree_agendamentos.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um agendamento para remover!")
            return
        
        item = self.tree_agendamentos.item(selection[0])
        agendamento_id = item['values'][0]
        paciente = item['values'][1]
        data_hora = item['values'][4]
        
        if messagebox.askyesno("Confirmação", f"Deseja realmente remover o agendamento de '{paciente}' em '{data_hora}'?"):
            try:
                self.db.delete_agendamento(agendamento_id)
                messagebox.showinfo("Sucesso", "Agendamento removido com sucesso!")
                self.carregar_agendamentos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover: {str(e)}")
    
    # Métodos para busca e filtros
    def buscar_pacientes(self, event=None):
        """Busca pacientes por nome ou CPF"""
        termo = self.search_var.get().strip()
        
        # Limpar dados existentes
        for item in self.tree_pacientes.get_children():
            self.tree_pacientes.delete(item)
        
        if termo:
            pacientes = self.db.search_pacientes(termo)
        else:
            pacientes = self.db.get_pacientes()
        
        for pac in pacientes:
            # Calcular idade
            idade = ""
            if pac[5]:  # data_nascimento
                try:
                    nascimento = datetime.strptime(pac[5], "%Y-%m-%d")
                    hoje = datetime.now()
                    idade = hoje.year - nascimento.year
                    if hoje.month < nascimento.month or (hoje.month == nascimento.month and hoje.day < nascimento.day):
                        idade -= 1
                except:
                    idade = ""
            
            # Inserir com idade calculada
            valores = list(pac) + [idade]
            self.tree_pacientes.insert('', 'end', values=valores)
    
    def limpar_busca_pacientes(self):
        """Limpa a busca de pacientes"""
        self.search_var.set("")
        self.carregar_pacientes()
    
    def filtrar_agendamentos_data(self):
        """Filtra agendamentos por data"""
        data = self.data_filter_var.get().strip()
        
        if not data:
            messagebox.showwarning("Aviso", "Digite uma data para filtrar!")
            return
        
        try:
            # Validar formato da data
            datetime.strptime(data, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Data deve estar no formato AAAA-MM-DD!")
            return
        
        # Limpar dados existentes
        for item in self.tree_agendamentos.get_children():
            self.tree_agendamentos.delete(item)
        
        # Carregar agendamentos da data
        profissional_id = self.profissional_logado.id if self.apenas_meus_var.get() else None
        agendamentos = self.db.get_agendamentos_por_data(data, profissional_id)
        
        for agend in agendamentos:
            # Formatar data/hora
            valores = list(agend)
            try:
                dt = datetime.strptime(valores[4], "%Y-%m-%d %H:%M:%S")
                valores[4] = dt.strftime("%d/%m/%Y %H:%M")
            except:
                pass
            
            self.tree_agendamentos.insert('', 'end', values=valores)
    
    def ver_historico_paciente(self):
        """Mostra o histórico de procedimentos do paciente selecionado"""
        selection = self.tree_pacientes.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um paciente para ver o histórico!")
            return
        
        item = self.tree_pacientes.item(selection[0])
        paciente_id = item['values'][0]
        nome_paciente = item['values'][1]
        
        # Criar janela de histórico
        janela = tk.Toplevel(self.root)
        janela.title(f"Histórico de {nome_paciente}")
        janela.geometry("800x400")
        janela.transient(self.root)
        
        # Frame principal
        main_frame = ttk.Frame(janela, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(main_frame, text=f"Histórico de Procedimentos - {nome_paciente}", 
                 style='Title.TLabel').pack(pady=(0, 10))
        
        # Treeview para histórico
        columns = ('Procedimento', 'Profissional', 'Data/Hora', 'Status', 'Observações')
        tree_historico = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        # Configurar colunas
        tree_historico.heading('Procedimento', text='Procedimento')
        tree_historico.heading('Profissional', text='Profissional')
        tree_historico.heading('Data/Hora', text='Data/Hora')
        tree_historico.heading('Status', text='Status')
        tree_historico.heading('Observações', text='Observações')
        
        tree_historico.column('Procedimento', width=150)
        tree_historico.column('Profissional', width=120)
        tree_historico.column('Data/Hora', width=130)
        tree_historico.column('Status', width=100)
        tree_historico.column('Observações', width=200)
        
        # Scrollbar
        scrollbar_hist = ttk.Scrollbar(main_frame, orient='vertical', command=tree_historico.yview)
        tree_historico.configure(yscrollcommand=scrollbar_hist.set)
        
        # Pack treeview e scrollbar
        tree_historico.pack(side='left', expand=True, fill='both')
        scrollbar_hist.pack(side='right', fill='y')
        
        # Carregar histórico
        historico = self.db.get_historico_paciente(paciente_id)
        for item in historico:
            # Formatar data/hora
            valores = list(item)
            try:
                dt = datetime.strptime(valores[2], "%Y-%m-%d %H:%M:%S")
                valores[2] = dt.strftime("%d/%m/%Y %H:%M")
            except:
                pass
            
            tree_historico.insert('', 'end', values=valores)
        
        # Botão fechar
        ttk.Button(main_frame, text="Fechar", command=janela.destroy).pack(pady=10)

def main():
    """Função principal para executar o aplicativo"""
    root = tk.Tk()
    app = ClinicaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
import customtkinter as ctk
from tkinter import messagebox
from models import Paciente

class PacienteDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, paciente=None):
        super().__init__(parent)
        self.db = db
        self.paciente = paciente
        self.result = None
        
        self.title("Cadastro de Paciente" if not paciente else "Editar Paciente")
        self.geometry("850x700")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        self.criar_interface()
        
        if self.paciente:
            self.carregar_dados()
        
        self.nome_entry.focus()
        
    def _formatar_data(self, *args):
        texto_atual = self.data_nasc_var.get()
        texto_limpo = "".join(filter(str.isdigit, texto_atual))
        novo_texto = ""
        if len(texto_limpo) > 0: novo_texto = texto_limpo[:2]
        if len(texto_limpo) > 2: novo_texto += "/" + texto_limpo[2:4]
        if len(texto_limpo) > 4: novo_texto += "/" + texto_limpo[4:8]
        if self.data_nasc_var.get() != novo_texto:
            self.data_nasc_var.set(novo_texto)
            self.after_idle(lambda: self.data_nasc_entry.icursor(len(novo_texto)))

    def _formatar_cpf(self, *args):
        texto_atual = self.cpf_var.get()
        texto_limpo = "".join(filter(str.isdigit, texto_atual))
        novo_texto = ""
        if len(texto_limpo) > 0: novo_texto = texto_limpo[:3]
        if len(texto_limpo) > 3: novo_texto += "." + texto_limpo[3:6]
        if len(texto_limpo) > 6: novo_texto += "." + texto_limpo[6:9]
        if len(texto_limpo) > 9: novo_texto += "-" + texto_limpo[9:11]
        if self.cpf_var.get() != novo_texto:
            self.cpf_var.set(novo_texto)
            self.after_idle(lambda: self.cpf_entry.icursor(len(novo_texto)))

    def criar_interface(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ALTERAÇÃO: Trocando 'tab_view' para 'self.tab_view'
        self.tab_view = ctk.CTkTabview(main_frame)
        self.tab_view.pack(fill="both", expand=True)
        
        tab_dados = self.tab_view.add("Dados Pessoais e Contato")
        tab_anamnese = self.tab_view.add("Anamnese")
        
        # ... (O restante do método criar_interface continua igual)
        aba_dados_frame = ctk.CTkScrollableFrame(tab_dados, fg_color="transparent")
        aba_dados_frame.pack(fill="both", expand=True)
        dados_pessoais_lf = ctk.CTkFrame(aba_dados_frame, fg_color="transparent")
        dados_pessoais_lf.pack(fill='x', expand=True, pady=5, padx=5)
        ctk.CTkLabel(dados_pessoais_lf, text="Dados Pessoais", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0,5))
        ctk.CTkLabel(dados_pessoais_lf, text="Nome:").grid(row=1, column=0, sticky='w', pady=2)
        self.nome_var = ctk.StringVar()
        self.nome_entry = ctk.CTkEntry(dados_pessoais_lf, textvariable=self.nome_var)
        self.nome_entry.grid(row=1, column=1, columnspan=3, sticky='we', pady=2)
        ctk.CTkLabel(dados_pessoais_lf, text="Data de Nasc.:").grid(row=2, column=0, sticky='w', pady=2)
        self.data_nasc_var = ctk.StringVar()
        self.data_nasc_var.trace_add("write", self._formatar_data)
        self.data_nasc_entry = ctk.CTkEntry(dados_pessoais_lf, textvariable=self.data_nasc_var)
        self.data_nasc_entry.grid(row=2, column=1, sticky='we', pady=2)
        ctk.CTkLabel(dados_pessoais_lf, text="CPF:").grid(row=2, column=2, sticky='w', pady=2, padx=(10,0))
        self.cpf_var = ctk.StringVar()
        self.cpf_var.trace_add("write", self._formatar_cpf)
        self.cpf_entry = ctk.CTkEntry(dados_pessoais_lf, textvariable=self.cpf_var)
        self.cpf_entry.grid(row=2, column=3, sticky='we', pady=2)
        ctk.CTkLabel(dados_pessoais_lf, text="Estado Civil:").grid(row=3, column=0, sticky='w', pady=2)
        self.est_civil_var = ctk.StringVar()
        opcoes_est_civil = ["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "Separado(a) Judicialmente"]
        self.est_civil_combo = ctk.CTkComboBox(dados_pessoais_lf, variable=self.est_civil_var, values=opcoes_est_civil, state='readonly')
        self.est_civil_combo.grid(row=3, column=1, sticky='we', pady=2)
        ctk.CTkLabel(dados_pessoais_lf, text="Profissão:").grid(row=3, column=2, sticky='w', pady=2, padx=(10,0))
        self.profissao_var = ctk.StringVar()
        ctk.CTkEntry(dados_pessoais_lf, textvariable=self.profissao_var).grid(row=3, column=3, sticky='we', pady=2)
        dados_pessoais_lf.columnconfigure((1, 3), weight=1)
        contato_lf = ctk.CTkFrame(aba_dados_frame, fg_color="transparent")
        contato_lf.pack(fill='x', expand=True, pady=5, padx=5)
        ctk.CTkLabel(contato_lf, text="Contato", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(10,5))
        ctk.CTkLabel(contato_lf, text="Telefone:").grid(row=1, column=0, sticky='w', pady=2)
        self.telefone_var = ctk.StringVar()
        ctk.CTkEntry(contato_lf, textvariable=self.telefone_var).grid(row=1, column=1, sticky='we', pady=2)
        ctk.CTkLabel(contato_lf, text="Email:").grid(row=1, column=2, sticky='w', pady=2, padx=(10,0))
        self.email_var = ctk.StringVar()
        ctk.CTkEntry(contato_lf, textvariable=self.email_var).grid(row=1, column=3, sticky='we', pady=2)
        contato_lf.columnconfigure((1, 3), weight=1)
        endereco_lf = ctk.CTkFrame(aba_dados_frame, fg_color="transparent")
        endereco_lf.pack(fill='x', expand=True, pady=5, padx=5)
        ctk.CTkLabel(endereco_lf, text="Endereço", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(10,5))
        ctk.CTkLabel(endereco_lf, text="Rua:").grid(row=1, column=0, sticky='w', pady=2)
        self.rua_var = ctk.StringVar()
        ctk.CTkEntry(endereco_lf, textvariable=self.rua_var).grid(row=1, column=1, columnspan=3, sticky='we', pady=2)
        ctk.CTkLabel(endereco_lf, text="Número:").grid(row=2, column=0, sticky='w', pady=2)
        self.numero_var = ctk.StringVar()
        ctk.CTkEntry(endereco_lf, textvariable=self.numero_var).grid(row=2, column=1, sticky='we', pady=2)
        ctk.CTkLabel(endereco_lf, text="Bairro:").grid(row=2, column=2, sticky='w', pady=2, padx=(10,0))
        self.bairro_var = ctk.StringVar()
        ctk.CTkEntry(endereco_lf, textvariable=self.bairro_var).grid(row=2, column=3, sticky='we', pady=2)
        ctk.CTkLabel(endereco_lf, text="Cidade:").grid(row=3, column=0, sticky='w', pady=2)
        self.cidade_var = ctk.StringVar()
        ctk.CTkEntry(endereco_lf, textvariable=self.cidade_var).grid(row=3, column=1, sticky='we', pady=2)
        ctk.CTkLabel(endereco_lf, text="Estado:").grid(row=3, column=2, sticky='w', pady=2, padx=(10,0))
        self.estado_var = ctk.StringVar()
        ctk.CTkEntry(endereco_lf, textvariable=self.estado_var).grid(row=3, column=3, sticky='we', pady=2)
        ctk.CTkLabel(endereco_lf, text="CEP:").grid(row=4, column=0, sticky='w', pady=2)
        self.cep_var = ctk.StringVar()
        ctk.CTkEntry(endereco_lf, textvariable=self.cep_var).grid(row=4, column=1, sticky='we', pady=2)
        endereco_lf.columnconfigure((1, 3), weight=1)
        anamnese_scroll_frame = ctk.CTkScrollableFrame(tab_anamnese, fg_color="transparent")
        anamnese_scroll_frame.pack(fill='both', expand=True)
        self.queixa_text = self.create_text_field(anamnese_scroll_frame, "Queixa Principal:")
        self.historico_text = self.create_text_field(anamnese_scroll_frame, "Histórico da Doença Atual:")
        self.ant_pessoais_text = self.create_text_field(anamnese_scroll_frame, "Antecedentes Pessoais:")
        self.ant_familiares_text = self.create_text_field(anamnese_scroll_frame, "Antecedentes Familiares:")
        self.habitos_text = self.create_text_field(anamnese_scroll_frame, "Hábitos de Vida:")
        self.medicamentos_text = self.create_text_field(anamnese_scroll_frame, "Medicamentos em Uso:")
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill='x', padx=10, pady=10, side='bottom')
        ctk.CTkButton(btn_frame, text="Salvar", command=self.salvar).pack(side='right')
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, fg_color="gray").pack(side='right', padx=10)

    def create_text_field(self, parent, label_text):
        ctk.CTkLabel(parent, text=label_text).pack(anchor='w', pady=(10,2), padx=10)
        text_widget = ctk.CTkTextbox(parent, height=80, wrap='word', border_width=1)
        text_widget.pack(fill='x', expand=True, padx=10)
        return text_widget

    def carregar_dados(self):
        if not self.paciente: return
        p = self.paciente
        self.nome_var.set(p.nome)
        self.data_nasc_var.set(p.data_nascimento)
        self.cpf_var.set(p.cpf)
        self.est_civil_var.set(p.estado_civil)
        self.profissao_var.set(p.profissao)
        self.telefone_var.set(p.telefone)
        self.email_var.set(p.email)
        self.rua_var.set(p.rua)
        self.numero_var.set(p.numero)
        self.bairro_var.set(p.bairro)
        self.cidade_var.set(p.cidade)
        self.estado_var.set(p.estado)
        self.cep_var.set(p.cep)
        
        self.queixa_text.insert('1.0', p.queixa_principal or "")
        self.historico_text.insert('1.0', p.historico_doenca_atual or "")
        self.ant_pessoais_text.insert('1.0', p.antecedentes_pessoais or "")
        self.ant_familiares_text.insert('1.0', p.antecedentes_familiares or "")
        self.habitos_text.insert('1.0', p.habitos_vida or "")
        self.medicamentos_text.insert('1.0', p.medicamentos_em_uso or "")

    def salvar(self):
        if not self.nome_var.get().strip():
            messagebox.showerror("Erro", "O nome do paciente é obrigatório!", parent=self)
            return
        try:
            dados_paciente = (
                self.nome_var.get(), self.data_nasc_var.get(), self.cpf_var.get(),
                self.est_civil_var.get(), self.profissao_var.get(), self.telefone_var.get(),
                self.email_var.get(), self.rua_var.get(), self.numero_var.get(),
                self.bairro_var.get(), self.cidade_var.get(), self.estado_var.get(),
                self.cep_var.get(), self.queixa_text.get('1.0', 'end-1c'),
                self.historico_text.get('1.0', 'end-1c'), self.ant_pessoais_text.get('1.0', 'end-1c'),
                self.ant_familiares_text.get('1.0', 'end-1c'), self.habitos_text.get('1.0', 'end-1c'),
                self.medicamentos_text.get('1.0', 'end-1c')
            )
            if self.paciente:
                self.db.update_paciente(self.paciente.id, *dados_paciente)
            else:
                self.db.insert_paciente(*dados_paciente)
            
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar o paciente:\n{e}", parent=self)
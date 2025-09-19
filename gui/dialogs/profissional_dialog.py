import tkinter as tk
from tkinter import ttk, messagebox
from models import Profissional
from services import AuthService

class ProfissionalDialog:
    def __init__(self, parent, db, profissional=None):
        self.db = db
        self.profissional = profissional
        self.result = None
        
        self.janela = tk.Toplevel(parent)
        self.janela.title("Cadastro de Profissional" if not profissional else "Editar Profissional")
        self.janela.geometry("500x450")
        self.janela.resizable(False, False)
        self.janela.transient(parent)
        self.janela.grab_set()
        
        self.centralizar_janela()
        self.criar_interface()
        
        # Focar no primeiro campo
        self.nome_entry.focus()
        
        # Aguardar fechamento da janela
        self.janela.wait_window()
    
    def centralizar_janela(self):
        self.janela.update_idletasks()
        x = (self.janela.winfo_screenwidth() // 2) - (self.janela.winfo_width() // 2)
        y = (self.janela.winfo_screenheight() // 2) - (self.janela.winfo_height() // 2)
        self.janela.geometry(f"+{x}+{y}")
    
    def criar_interface(self):
        main_frame = ttk.Frame(self.janela, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        titulo = ttk.Label(main_frame, text="Cadastro de Profissional" if not self.profissional else "Editar Profissional", style='Title.TLabel')
        titulo.pack(pady=(0, 20))
        
        # Campos do formulário
        ttk.Label(main_frame, text="Nome:").pack(anchor='w')
        self.nome_var = tk.StringVar(value=self.profissional.nome if self.profissional else "")
        self.nome_entry = ttk.Entry(main_frame, textvariable=self.nome_var, width=50)
        self.nome_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="Especialidade:").pack(anchor='w')
        self.especialidade_var = tk.StringVar(value=self.profissional.especialidade if self.profissional else "")
        especialidade_entry = ttk.Entry(main_frame, textvariable=self.especialidade_var, width=50)
        especialidade_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="CRM/Registro:").pack(anchor='w')
        self.crm_var = tk.StringVar(value=self.profissional.crm_registro if self.profissional else "")
        crm_entry = ttk.Entry(main_frame, textvariable=self.crm_var, width=50)
        crm_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="Telefone:").pack(anchor='w')
        self.telefone_var = tk.StringVar(value=self.profissional.telefone if self.profissional else "")
        telefone_entry = ttk.Entry(main_frame, textvariable=self.telefone_var, width=50)
        telefone_entry.pack(pady=(0, 10), fill='x')
        
        ttk.Label(main_frame, text="Email:").pack(anchor='w')
        self.email_var = tk.StringVar(value=self.profissional.email if self.profissional else "")
        email_entry = ttk.Entry(main_frame, textvariable=self.email_var, width=50)
        email_entry.pack(pady=(0, 10), fill='x')
        
        # Mostrar código de acesso apenas para novos profissionais
        if not self.profissional:
            self.codigo_gerado = AuthService.gerar_codigo_acesso()
            
            codigo_frame = ttk.LabelFrame(main_frame, text="Código de Acesso Gerado", padding="10")
            codigo_frame.pack(fill='x', pady=(10, 0))
            
            ttk.Label(codigo_frame, text="IMPORTANTE: Anote este código, ele será necessário para fazer login:", 
                     font=('Arial', 10, 'bold'), foreground='red').pack(anchor='w')
            
            codigo_label = ttk.Label(codigo_frame, text=self.codigo_gerado, 
                                   font=('Arial', 16, 'bold'), foreground='blue')
            codigo_label.pack(pady=5)
            
            ttk.Label(codigo_frame, text="Este código não será exibido novamente após o cadastro.", 
                     font=('Arial', 9), foreground='gray').pack(anchor='w')
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(btn_frame, text="Salvar", command=self.salvar).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.janela.destroy).pack(side='right')
    
    def salvar(self):
        if not self.nome_var.get().strip() or not self.especialidade_var.get().strip() or not self.crm_var.get().strip():
            messagebox.showerror("Erro", "Nome, Especialidade e CRM/Registro são obrigatórios!")
            return
        
        try:
            if self.profissional:
                # Edição - não alteramos o código de acesso
                self.db.update_profissional(
                    self.profissional.id, 
                    self.nome_var.get().strip(), 
                    self.especialidade_var.get().strip(), 
                    self.crm_var.get().strip(), 
                    self.telefone_var.get().strip(), 
                    self.email_var.get().strip()
                )
                messagebox.showinfo("Sucesso", "Profissional atualizado com sucesso!")
            else:
                # Novo cadastro - incluir código de acesso
                self.db.insert_profissional(
                    self.nome_var.get().strip(), 
                    self.especialidade_var.get().strip(), 
                    self.crm_var.get().strip(), 
                    self.telefone_var.get().strip(), 
                    self.email_var.get().strip(),
                    self.codigo_gerado
                )
                messagebox.showinfo("Sucesso", f"Profissional cadastrado com sucesso!\n\nCódigo de acesso: {self.codigo_gerado}\n\nAnote este código, ele será necessário para fazer login!")
            
            self.result = True
            self.janela.destroy()
            
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Erro", "Este CRM/Registro já está cadastrado!")
            else:
                messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
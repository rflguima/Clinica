import customtkinter as ctk
from PIL import Image # IMPORTAÇÃO ADICIONADA
from .tabs.pacientes_tab import PacientesTab
from .tabs.inicio_tab import InicioTab
from .tabs.procedimentos_tab import ProcedimentosTab
from .tabs.profissionais_tab import ProfissionaisTab
from .tabs.agenda_tab import AgendaTab

class MainInterface(ctk.CTkFrame):
    def __init__(self, parent, db, profissional_logado, logout_callback):
        super().__init__(parent, fg_color="white")
        self.db = db
        self.profissional_logado = profissional_logado
        self.logout_callback = logout_callback

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Carregar Ícones ---
        try:
            self.icon_inicio = ctk.CTkImage(Image.open("icons/home.png"))
            self.icon_pacientes = ctk.CTkImage(Image.open("icons/pacientes.png"))
            self.icon_agenda = ctk.CTkImage(Image.open("icons/agenda.png"))
            self.icon_profissionais = ctk.CTkImage(Image.open("icons/profissionais.png"))
            self.icon_procedimentos = ctk.CTkImage(Image.open("icons/procedimentos.png"))
        except FileNotFoundError as e:
            print(f"Erro ao carregar ícones: {e}. Verifique se a pasta 'icons' e as imagens existem.")
            # Define ícones vazios para não quebrar o programa
            self.icon_inicio = self.icon_pacientes = self.icon_agenda = self.icon_profissionais = self.icon_procedimentos = None


        # --- Barra de Navegação Lateral ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#3786c2")
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="Consultório Live", text_color="white", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        nav_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        nav_frame.pack(fill="x")

        self.nav_buttons = {}
        nav_items = {
            "Início": self.icon_inicio,
            "Pacientes": self.icon_pacientes,
            "Agenda": self.icon_agenda,
            "Profissionais": self.icon_profissionais,
            "Procedimentos": self.icon_procedimentos
        }

        for item_text, item_icon in nav_items.items():
            button = ctk.CTkButton(
                nav_frame, 
                text=item_text,
                image=item_icon,
                compound="left",
                anchor="w", 
                fg_color="transparent", 
                text_color="white", 
                font=ctk.CTkFont(weight="bold"),
                hover_color="#2a6a9e", 
                command=lambda i=item_text: self.show_frame(i)
            )
            button.pack(fill="x", padx=20, pady=5)
            self.nav_buttons[item_text] = button

        sair_button = ctk.CTkButton(
            self.sidebar_frame, text="Sair", anchor="w", fg_color="#c94444", 
            hover_color="#a13636", command=self.fechar_programa
        )
        sair_button.pack(fill="x", padx=0.1, pady=0.1, side="bottom")

        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="white")
        self.header_frame.grid(row=0, column=1, sticky="new")
        ctk.CTkLabel(self.header_frame, text=f"Dr(a). {profissional_logado.nome}", anchor='w').pack(side="left", padx=20)
        ctk.CTkButton(self.header_frame, text="Logout", width=100, fg_color="#df4e4e", hover_color="#b23e3e", command=self.logout_callback).pack(side="right", padx=20, pady=10)
        ctk.CTkFrame(self, height=1, fg_color="#dbdbdb").grid(row=0, column=1, sticky="sew", pady=(55,0))

        # --- Área de Conteúdo Principal ---
        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)

        self.frames = {}
        
        self.frames["Início"] = InicioTab(self.main_content_frame, self.db, self.profissional_logado)
        self.frames["Pacientes"] = PacientesTab(self.main_content_frame, self.db, self.profissional_logado)
        self.frames["Procedimentos"] = ProcedimentosTab(self.main_content_frame, self.db, self.profissional_logado)
        self.frames["Profissionais"] = ProfissionaisTab(self.main_content_frame, self.db, self.profissional_logado)
        self.frames["Agenda"] = AgendaTab(self.main_content_frame, self.db, self.profissional_logado)
        
        self.show_frame("Início")

    def fechar_programa(self):
        self.winfo_toplevel().destroy()

    def show_frame(self, frame_name):
        if frame_name not in self.frames:
            # print(f"Frame '{frame_name}' ainda não implementado.")
            return

        for frame in self.frames.values():
            frame.pack_forget()
        
        frame = self.frames.get(frame_name)
        if frame:
            frame.pack(fill="both", expand=True)
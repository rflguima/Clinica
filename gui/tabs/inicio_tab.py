import customtkinter as ctk
from datetime import datetime

class InicioTab(ctk.CTkFrame):
    def __init__(self, parent, db, profissional_logado):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.profissional_logado = profissional_logado
        
        # --- Configuração do Grid ---
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1)

        # --- Criar os Cards ---
        self.card_pacientes_cadastrados()
        self.card_agendamentos_hoje()
        self.card_sala_de_espera()
        self.card_pacientes_recentes()

    def _criar_card_base(self, row, column, title, rowspan=1, columnspan=1):
        """Função auxiliar para criar a estrutura base de um card."""
        card = ctk.CTkFrame(self, fg_color="#F0F0F0", corner_radius=8)
        card.grid(row=row, column=column, padx=10, pady=10, sticky="nsew", rowspan=rowspan, columnspan=columnspan)
        
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(padx=20, pady=(20, 10), anchor="w")
        
        return card

    def card_pacientes_cadastrados(self):
        card = self._criar_card_base(row=0, column=0, title="Pacientes Cadastrados")
        
        try:
            total_pacientes = len(self.db.get_pacientes() or [])
        except Exception:
            total_pacientes = "Erro"

        value_label = ctk.CTkLabel(card, text=str(total_pacientes), font=ctk.CTkFont(size=48, weight="bold"), text_color="#3786c2")
        value_label.pack(expand=True)

    def card_agendamentos_hoje(self):
        card = self._criar_card_base(row=0, column=1, title="Agendamentos Hoje")
        
        try:
            hoje_str = datetime.now().strftime('%Y-%m-%d')
            # --- CORREÇÃO AQUI: Usando a função correta e passando o objeto profissional ---
            agendamentos_hoje = len(self.db.get_agendamentos_detalhados_por_data(hoje_str, self.profissional_logado) or [])
        except Exception:
            agendamentos_hoje = "Erro"
            
        value_label = ctk.CTkLabel(card, text=str(agendamentos_hoje), font=ctk.CTkFont(size=48, weight="bold"), text_color="#3786c2")
        value_label.pack(expand=True)

    def card_sala_de_espera(self):
        card = self._criar_card_base(row=0, column=2, title="Sala de Espera")
        
        try:
            hoje_str = datetime.now().strftime('%Y-%m-%d')
            # Usaremos a mesma função, mas precisaremos ajustar a lógica no DB Manager para a secretária
            # Por enquanto, esta lógica funciona para o profissional logado
            pacientes_esperando = self.db.get_agendamentos_em_espera(hoje_str, self.profissional_logado.id)
        except Exception:
            pacientes_esperando = "Erro"
            
        value_label = ctk.CTkLabel(card, text=str(pacientes_esperando), font=ctk.CTkFont(size=48, weight="bold"), text_color="#3786c2")
        value_label.pack(expand=True)
        
        ctk.CTkLabel(card, text="pacientes aguardando", text_color="gray").pack(pady=(0, 10))

    def card_pacientes_recentes(self):
        card = self._criar_card_base(row=1, column=0, title="Pacientes Recentes", columnspan=3)

        try:
            pacientes_recentes = self.db.get_pacientes_recentes(limit=5)
            if not pacientes_recentes:
                ctk.CTkLabel(card, text="Nenhum paciente cadastrado.", text_color="gray").pack(padx=20, pady=10, anchor="w")
                return

            for paciente in pacientes_recentes:
                ctk.CTkLabel(card, text=f"• {paciente[0]}", font=ctk.CTkFont(size=14)).pack(padx=20, pady=2, anchor="w")

        except Exception as e:
            ctk.CTkLabel(card, text=f"Erro ao carregar pacientes: {e}", text_color="red").pack(padx=20, pady=10, anchor="w")
import customtkinter as ctk
from tkinter import messagebox, Menu
import calendar
from datetime import datetime, time, timedelta
from gui.dialogs.agendamento_dialog import AgendamentoDialog
from gui.dialogs.paciente_dialog import PacienteDialog
from models import Agendamento, Paciente, StatusAgendamento

class AgendaTab(ctk.CTkFrame):
    def __init__(self, parent, db, profissional_logado):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.profissional_logado = profissional_logado
        
        self.hoje = datetime.now()
        self.cal_ano = self.hoje.year
        self.cal_mes = self.hoje.month
        self.data_selecionada = self.hoje.date()
        self.agendamento_selecionado_id = None
        self.frame_selecionado = None

        # --- Variáveis para o Drag-and-Drop ---
        self.drag_item = None
        self.drag_start_y = 0
        self.drag_ghost_window = None

        self.criar_interface()
        self.criar_menu_status()
        self.desenhar_calendario()
        self.selecionar_dia(self.data_selecionada)

    def criar_interface(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        cal_frame = ctk.CTkFrame(self)
        cal_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        header_frame = ctk.CTkFrame(cal_frame, fg_color="transparent")
        header_frame.pack(pady=10)
        
        ctk.CTkButton(header_frame, text="<", width=30, command=self.mes_anterior).pack(side="left", padx=10)
        self.cal_label = ctk.CTkLabel(header_frame, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.cal_label.pack(side="left")
        ctk.CTkButton(header_frame, text=">", width=30, command=self.proximo_mes).pack(side="left", padx=10)

        self.cal_container = ctk.CTkFrame(cal_frame, fg_color="transparent")
        self.cal_container.pack(fill="x", expand=True, padx=10, pady=(0, 10))

        consultas_frame = ctk.CTkFrame(self, fg_color="white")
        consultas_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        consultas_frame.grid_columnconfigure(0, weight=1)
        consultas_frame.grid_rowconfigure(1, weight=1)

        botoes_agenda_frame = ctk.CTkFrame(consultas_frame, fg_color="transparent")
        botoes_agenda_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(botoes_agenda_frame, text="Novo Agendamento", command=self.novo_agendamento, fg_color="#46a842").pack(side="left")
        self.btn_editar = ctk.CTkButton(botoes_agenda_frame, text="Editar Agendamento", state="disabled", command=self.editar_agendamento)
        self.btn_editar.pack(side="left", padx=5)
        self.btn_excluir = ctk.CTkButton(botoes_agenda_frame, text="Excluir Agendamento", state="disabled", command=self.excluir_agendamento)
        self.btn_excluir.pack(side="left")

        self.agenda_scroll_frame = ctk.CTkScrollableFrame(consultas_frame, fg_color="white", border_width=1, border_color="#dbdbdb")
        self.agenda_scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def criar_menu_status(self):
        self.menu_status = Menu(self, tearoff=0)
        self.menu_status.add_command(label="Marcar como Concluído", command=lambda: self.mudar_status(StatusAgendamento.CONCLUIDO))
        self.menu_status.add_command(label="Marcar como Agendado", command=lambda: self.mudar_status(StatusAgendamento.AGENDADO))
        self.menu_status.add_command(label="Cancelar Agendamento", command=lambda: self.mudar_status(StatusAgendamento.CANCELADO))

    def mostrar_menu_status(self, event, agendamento_id):
        self.agendamento_para_mudar_status = agendamento_id
        self.menu_status.tk_popup(event.x_root, event.y_root)

    def mudar_status(self, novo_status):
        if hasattr(self, 'agendamento_para_mudar_status') and self.agendamento_para_mudar_status:
            self.db.update_agendamento_status(self.agendamento_para_mudar_status, novo_status)
            self.selecionar_dia(self.data_selecionada)

    def desenhar_calendario(self):
        for widget in self.cal_container.winfo_children(): widget.destroy()
        mes_nome = calendar.month_name[self.cal_mes].capitalize()
        self.cal_label.configure(text=f"{mes_nome} {self.cal_ano}")
        dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        for i, dia in enumerate(dias_semana):
            ctk.CTkLabel(self.cal_container, text=dia, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, padx=5, pady=5, sticky="ew")
        cal = calendar.monthcalendar(self.cal_ano, self.cal_mes)
        for semana_num, semana in enumerate(cal):
            for dia_num, dia in enumerate(semana):
                if dia == 0: continue
                data_atual = datetime(self.cal_ano, self.cal_mes, dia).date()
                btn_dia = ctk.CTkButton(self.cal_container, text=str(dia), command=lambda d=data_atual: self.selecionar_dia(d))
                if data_atual == self.hoje.date():
                    btn_dia.configure(fg_color="#2a6a9e", text_color="white", border_width=2, border_color="#3786c2")
                btn_dia.grid(row=semana_num + 1, column=dia_num, padx=2, pady=2, sticky="nsew")
        self.cal_container.grid_columnconfigure(list(range(7)), weight=1)

    def selecionar_dia(self, data):
        self.data_selecionada = data
        self.desmarcar_agendamento()
        self.desenhar_grade_horarios()

    def desenhar_grade_horarios(self):
        for widget in self.agenda_scroll_frame.winfo_children(): widget.destroy()
        
        hora_inicio, hora_fim, intervalo = time(7, 0), time(19, 0), timedelta(minutes=30)
        self.slot_height = 50 
        
        agendamentos_data = self.db.get_agendamentos_detalhados_por_data(self.data_selecionada.strftime('%Y-%m-%d'), self.profissional_logado) or []
        agendamentos_map = {}
        for ag in agendamentos_data:
            hora_agendamento = datetime.strptime(ag[3], "%Y-%m-%d %H:%M:%S").time()
            if hora_agendamento not in agendamentos_map: agendamentos_map[hora_agendamento] = []
            agendamentos_map[hora_agendamento].append(ag)

        hora_atual, row_num = hora_inicio, 0
        while hora_atual <= hora_fim:
            ctk.CTkLabel(self.agenda_scroll_frame, text=hora_atual.strftime("%H:%M"), width=50, height=self.slot_height).grid(row=row_num, column=0, padx=5)
            ctk.CTkFrame(self.agenda_scroll_frame, height=1, fg_color="#dbdbdb").grid(row=row_num, column=1, sticky="sew")

            if hora_atual in agendamentos_map:
                agendamentos_concorrentes = agendamentos_map[hora_atual]
                if self.profissional_logado.role == 'secretaria' and len(agendamentos_concorrentes) > 1:
                    slot_container = ctk.CTkFrame(self.agenda_scroll_frame, fg_color="transparent")
                    slot_container.grid(row=row_num, column=1, sticky="nsew")
                    for i, ag_data in enumerate(agendamentos_concorrentes):
                        slot_container.grid_columnconfigure(i, weight=1)
                        self.criar_frame_agendamento(parent=slot_container, ag_data=ag_data, grid_row=0, grid_col=i)
                else:
                    self.criar_frame_agendamento(parent=self.agenda_scroll_frame, ag_data=agendamentos_concorrentes[0], grid_row=row_num, grid_col=1)
            
            row_num += 1
            hora_atual = (datetime.combine(self.data_selecionada, hora_atual) + intervalo).time()

        self.agenda_scroll_frame.grid_columnconfigure(1, weight=1)

    def criar_frame_agendamento(self, parent, ag_data, grid_row, grid_col):
        ag_id, pac_nome, proc_nome, _, duracao, status, pac_id, prof_nome = ag_data
        slots = duracao // 30 if duracao > 0 else 1
        
        cores_status = {
            StatusAgendamento.AGENDADO: ("#eaf4ff", "#3786c2"),
            StatusAgendamento.CONCLUIDO: ("#e1f5e1", "#4caf50"),
            StatusAgendamento.CANCELADO: ("#ffebee", "#f44336"),
        }
        bg_color, border_color = cores_status.get(status, ("#eeeeee", "#e0e0e0"))

        frame = ctk.CTkFrame(parent, fg_color=bg_color, border_width=1, border_color=border_color, corner_radius=8)
        frame.grid(row=grid_row, column=grid_col, rowspan=slots, sticky="nsew", padx=5, pady=2)
        
        ctk.CTkLabel(frame, text=pac_nome, font=ctk.CTkFont(weight="bold")).pack(padx=10, pady=(5,0), anchor="w")
        ctk.CTkLabel(frame, text=f"{proc_nome} ({duracao} min)", text_color="gray50").pack(padx=10, pady=(0,5), anchor="w")
        if self.profissional_logado.role == 'secretaria':
             ctk.CTkLabel(frame, text=f"Dr(a). {prof_nome.split()[0]}", text_color=border_color, font=ctk.CTkFont(size=10)).pack(padx=10, pady=(0,5), anchor="w")
        
        elementos_clicaveis = [frame] + frame.winfo_children()
        for elemento in elementos_clicaveis:
            elemento.bind("<Button-1>", lambda e, id=ag_id, f=frame: self.selecionar_agendamento(id, f))
            elemento.bind("<Double-Button-1>", lambda e, id=pac_id: self.abrir_anamnese(id))
            elemento.bind("<Button-3>", lambda e, id=ag_id: self.mostrar_menu_status(e, id))
            # Binds para o Drag-and-Drop
            elemento.bind("<ButtonPress-1>", lambda e, id=ag_id, f=frame: self.on_drag_start(e, id, f))
            elemento.bind("<B1-Motion>", self.on_drag_motion)
            elemento.bind("<ButtonRelease-1>", self.on_drag_release)

    def on_drag_start(self, event, agendamento_id, frame):
        self.drag_item = {'id': agendamento_id, 'frame': frame}
        self.drag_start_y = event.y_root
        
        self.drag_ghost_window = ctk.CTkToplevel(self)
        self.drag_ghost_window.overrideredirect(True)
        self.drag_ghost_window.geometry(f"{frame.winfo_width()}x{frame.winfo_height()}+{event.x_root}+{event.y_root}")
        ctk.CTkLabel(self.drag_ghost_window, text=frame.winfo_children()[0].cget("text"), fg_color="#3786c2", text_color="white").pack(fill="both", expand=True)
        self.drag_ghost_window.attributes("-alpha", 0.7)

    def on_drag_motion(self, event):
        if self.drag_ghost_window:
            self.drag_ghost_window.geometry(f"+{event.x_root}+{event.y_root}")

    def on_drag_release(self, event):
        if self.drag_item:
            y_deslocamento = event.y_root - self.drag_start_y
            slots_movidos = round(y_deslocamento / self.slot_height)
            
            if slots_movidos != 0:
                agendamentos = self.db.get_agendamentos(self.profissional_logado)
                ag_data = next((ag for ag in agendamentos if ag[0] == self.drag_item['id']), None)
                
                if ag_data:
                    agendamento = Agendamento.from_tuple(ag_data)
                    data_hora_antiga = datetime.strptime(agendamento.data_hora, "%Y-%m-%d %H:%M:%S")
                    nova_data_hora = data_hora_antiga + timedelta(minutes=30 * slots_movidos)
                    
                    self.db.update_agendamento_horario(self.drag_item['id'], nova_data_hora.strftime("%Y-%m-%d %H:%M:%S"))
                    self.selecionar_dia(self.data_selecionada)
            
        if self.drag_ghost_window:
            self.drag_ghost_window.destroy()
        self.drag_item = None
        self.drag_ghost_window = None

    def selecionar_agendamento(self, agendamento_id, frame_clicado):
        self.desmarcar_agendamento()
        self.agendamento_selecionado_id = agendamento_id
        self.frame_selecionado = frame_clicado
        self.frame_selecionado.configure(border_color="red")
        self.btn_editar.configure(state="normal")
        self.btn_excluir.configure(state="normal")

    def desmarcar_agendamento(self):
        if self.frame_selecionado:
            status_query = self.db.execute_query("SELECT status FROM agendamentos WHERE id = ?", (self.agendamento_selecionado_id,))
            status = status_query[0][0] if status_query else StatusAgendamento.AGENDADO
            cores_status = { StatusAgendamento.CONCLUIDO: "#4caf50", StatusAgendamento.CANCELADO: "#f44336" }
            border_color = cores_status.get(status, "#3786c2")
            self.frame_selecionado.configure(border_color=border_color)

        self.agendamento_selecionado_id = None
        self.frame_selecionado = None
        self.btn_editar.configure(state="disabled")
        self.btn_excluir.configure(state="disabled")

    def novo_agendamento(self):
        dialog = AgendamentoDialog(self, self.db, self.profissional_logado)
        if hasattr(dialog, 'result') and dialog.result:
            self.selecionar_dia(self.data_selecionada)

    def editar_agendamento(self):
        if not self.agendamento_selecionado_id: return
        agendamentos = self.db.get_agendamentos(self.profissional_logado)
        ag_data = next((ag for ag in agendamentos if ag[0] == self.agendamento_selecionado_id), None)
        if ag_data:
            agendamento = Agendamento.from_tuple(ag_data)
            dialog = AgendamentoDialog(self, self.db, self.profissional_logado, agendamento=agendamento)
            if hasattr(dialog, 'result') and dialog.result:
                self.selecionar_dia(self.data_selecionada)

    def excluir_agendamento(self):
        if not self.agendamento_selecionado_id: return
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este agendamento?"):
            self.db.delete_agendamento(self.agendamento_selecionado_id)
            self.selecionar_dia(self.data_selecionada)

    def abrir_anamnese(self, paciente_id):
        paciente_data = self.db.get_paciente_by_id(paciente_id)
        if paciente_data:
            paciente = Paciente.from_tuple(paciente_data)
            dialog = PacienteDialog(self, self.db, paciente=paciente)
            if hasattr(dialog, 'tab_view'):
                dialog.tab_view.set("Anamnese")

    def mes_anterior(self):
        self.cal_mes -= 1
        if self.cal_mes == 0: self.cal_mes = 12; self.cal_ano -= 1
        self.desenhar_calendario()

    def proximo_mes(self):
        self.cal_mes += 1
        if self.cal_mes == 13: self.cal_mes = 1; self.cal_ano += 1
        self.desenhar_calendario()
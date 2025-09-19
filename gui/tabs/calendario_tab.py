import tkinter as tk
from tkinter import ttk
from datetime import datetime, date, timedelta
import calendar
from .base_tab import BaseTab

class CalendarioTab(BaseTab):
    def __init__(self, notebook, db, profissional_logado):
        self.cal_year = datetime.now().year
        self.cal_month = datetime.now().month
        self.data_selecionada_calendario = date.today()
        
        super().__init__(notebook, db, profissional_logado, "Calendário")
    
    def criar_interface(self):
        top_frame = ttk.Frame(self.frame)
        top_frame.pack(fill='x', padx=10, pady=5)
        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.pack(expand=True, fill='both', padx=10, pady=5)

        self.cal_container = ttk.Frame(top_frame)
        self.cal_container.pack(pady=10)
        self.label_dia_selecionado = ttk.Label(bottom_frame, text="", style='Heading.TLabel')
        self.label_dia_selecionado.pack(anchor='w', pady=(5, 10))

        columns = ('Horário', 'Paciente', 'Procedimento', 'Status')
        self.tree_consultas_dia = ttk.Treeview(bottom_frame, columns=columns, show='headings', style='Custom.Treeview')
        for col in columns: 
            self.tree_consultas_dia.heading(col, text=col)
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
                if day == 0: 
                    continue
                
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
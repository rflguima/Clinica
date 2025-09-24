from datetime import datetime

class Agendamento:
    def __init__(self, id=None, paciente_id=None, procedimento_id=None, profissional_id=None, 
                 data_hora="", status="agendado", observacoes=""):
        self.id = id
        self.paciente_id = paciente_id
        self.procedimento_id = procedimento_id
        self.profissional_id = profissional_id
        self.data_hora = data_hora
        self.status = status
        self.observacoes = observacoes
    
    def __str__(self):
        return f"Agendamento {self.id} - {self.data_hora} - {self.status}"
    
    def to_dict(self):
        return {
            'id': self.id, 'paciente_id': self.paciente_id, 'procedimento_id': self.procedimento_id,
            'profissional_id': self.profissional_id, 'data_hora': self.data_hora, 'status': self.status,
            'observacoes': self.observacoes
        }
    
    @classmethod
    def from_tuple(cls, data):
        if data and len(data) >= 7:
            paciente_id_original = data[1] if isinstance(data[1], int) else (data[7] if len(data) > 7 else None)
            return cls(id=data[0], paciente_id=paciente_id_original, procedimento_id=data[2], 
                       profissional_id=data[3], data_hora=data[4], status=data[5], observacoes=data[6])
        return cls()
    
    def get_data_formatada(self):
        try:
            if isinstance(self.data_hora, str):
                dt = datetime.strptime(self.data_hora, "%Y-%m-%d %H:%M:%S")
            else: dt = self.data_hora
            return dt.strftime("%d/%m/%Y %H:%M")
        except: return str(self.data_hora)
    
    def get_status_cor(self):
        cores = { 'agendado': '#4CAF50', 'concluido': '#2196F3', 'cancelado': '#F44336' }
        return cores.get(self.status.lower(), '#757575')

class StatusAgendamento:
    AGENDADO = "agendado"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"
    
    @classmethod
    def get_opcoes(cls):
        return [cls.AGENDADO, cls.CONCLUIDO, cls.CANCELADO]
    
    @classmethod
    def get_opcoes_formatadas(cls):
        return { cls.AGENDADO: "Agendado", cls.CONCLUIDO: "Concluído", cls.CANCELADO: "Cancelado" }
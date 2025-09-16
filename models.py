from datetime import datetime

class Profissional:
    def __init__(self, id=None, nome="", especialidade="", crm_registro="", telefone="", email=""):
        self.id = id
        self.nome = nome
        self.especialidade = especialidade
        self.crm_registro = crm_registro
        self.telefone = telefone
        self.email = email
    
    def __str__(self):
        return f"{self.nome} - {self.especialidade}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'especialidade': self.especialidade,
            'crm_registro': self.crm_registro,
            'telefone': self.telefone,
            'email': self.email
        }
    
    @classmethod
    def from_tuple(cls, data):
        if data and len(data) >= 6:
            return cls(data[0], data[1], data[2], data[3], data[4], data[5])
        return cls()

class Paciente:
    def __init__(self, id=None, nome="", telefone="", cpf="", endereco="", data_nascimento=""):
        self.id = id
        self.nome = nome
        self.telefone = telefone
        self.cpf = cpf
        self.endereco = endereco
        self.data_nascimento = data_nascimento
    
    def __str__(self):
        return f"{self.nome} - CPF: {self.cpf}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'cpf': self.cpf,
            'endereco': self.endereco,
            'data_nascimento': self.data_nascimento
        }
    
    @classmethod
    def from_tuple(cls, data):
        if data and len(data) >= 6:
            return cls(data[0], data[1], data[2], data[3], data[4], data[5])
        return cls()
    
    def calcular_idade(self):
        """Calcula a idade do paciente"""
        if self.data_nascimento:
            try:
                nascimento = datetime.strptime(self.data_nascimento, "%Y-%m-%d")
                hoje = datetime.now()
                idade = hoje.year - nascimento.year
                if hoje.month < nascimento.month or (hoje.month == nascimento.month and hoje.day < nascimento.day):
                    idade -= 1
                return idade
            except:
                return 0
        return 0

class Procedimento:
    def __init__(self, id=None, nome="", duracao=0, valor=0.0):
        self.id = id
        self.nome = nome
        self.duracao = duracao  # em minutos
        self.valor = valor
    
    def __str__(self):
        return f"{self.nome} - {self.duracao}min - R$ {self.valor:.2f}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'duracao': self.duracao,
            'valor': self.valor
        }
    
    @classmethod
    def from_tuple(cls, data):
        if data and len(data) >= 4:
            return cls(data[0], data[1], data[2], data[3])
        return cls()
    
    def get_duracao_formatada(self):
        """Retorna a duração formatada em horas e minutos"""
        horas = self.duracao // 60
        minutos = self.duracao % 60
        
        if horas > 0:
            return f"{horas}h {minutos}min" if minutos > 0 else f"{horas}h"
        else:
            return f"{minutos}min"

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
            'id': self.id,
            'paciente_id': self.paciente_id,
            'procedimento_id': self.procedimento_id,
            'profissional_id': self.profissional_id,
            'data_hora': self.data_hora,
            'status': self.status,
            'observacoes': self.observacoes
        }
    
    @classmethod
    def from_tuple(cls, data):
        if data and len(data) >= 7:
            return cls(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
        return cls()
    
    def get_data_formatada(self):
        """Retorna a data formatada para exibição"""
        try:
            if isinstance(self.data_hora, str):
                dt = datetime.strptime(self.data_hora, "%Y-%m-%d %H:%M:%S")
            else:
                dt = self.data_hora
            return dt.strftime("%d/%m/%Y %H:%M")
        except:
            return str(self.data_hora)
    
    def get_status_cor(self):
        """Retorna uma cor baseada no status do agendamento"""
        cores = {
            'agendado': '#4CAF50',    # Verde
            'concluido': '#2196F3',   # Azul
            'cancelado': '#F44336'    # Vermelho
        }
        return cores.get(self.status.lower(), '#757575')  # Cinza padrão

# Enums para status de agendamento
class StatusAgendamento:
    AGENDADO = "agendado"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"
    
    @classmethod
    def get_opcoes(cls):
        return [cls.AGENDADO, cls.CONCLUIDO, cls.CANCELADO]
    
    @classmethod
    def get_opcoes_formatadas(cls):
        return {
            cls.AGENDADO: "Agendado",
            cls.CONCLUIDO: "Concluído",
            cls.CANCELADO: "Cancelado"
        }
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
    # --- CLASSE MODIFICADA ---
    def __init__(self, id=None, nome="", data_nascimento="", cpf="", estado_civil="", profissao="",
                 telefone="", email="", rua="", numero="", bairro="", cidade="", estado="", cep="",
                 queixa_principal="", historico_doenca_atual="", antecedentes_pessoais="",
                 antecedentes_familiares="", habitos_vida="", medicamentos_em_uso=""):
        # Dados Pessoais
        self.id = id
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
        self.estado_civil = estado_civil
        self.profissao = profissao
        # Contato
        self.telefone = telefone
        self.email = email
        # Endereço
        self.rua = rua
        self.numero = numero
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.cep = cep
        # Anamnese
        self.queixa_principal = queixa_principal
        self.historico_doenca_atual = historico_doenca_atual
        self.antecedentes_pessoais = antecedentes_pessoais
        self.antecedentes_familiares = antecedentes_familiares
        self.habitos_vida = habitos_vida
        self.medicamentos_em_uso = medicamentos_em_uso
    
    def __str__(self):
        return f"{self.nome} - CPF: {self.cpf}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'data_nascimento': self.data_nascimento,
            'cpf': self.cpf,
            'estado_civil': self.estado_civil,
            'profissao': self.profissao,
            'telefone': self.telefone,
            'email': self.email,
            'rua': self.rua,
            'numero': self.numero,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado,
            'cep': self.cep,
            'queixa_principal': self.queixa_principal,
            'historico_doenca_atual': self.historico_doenca_atual,
            'antecedentes_pessoais': self.antecedentes_pessoais,
            'antecedentes_familiares': self.antecedentes_familiares,
            'habitos_vida': self.habitos_vida,
            'medicamentos_em_uso': self.medicamentos_em_uso
        }
    
    @classmethod
    def from_tuple(cls, data):
        # Para carregar o paciente completo (20 colunas)
        if data and len(data) >= 20:
            return cls(id=data[0], nome=data[1], data_nascimento=data[2], cpf=data[3], estado_civil=data[4],
                       profissao=data[5], telefone=data[6], email=data[7], rua=data[8], numero=data[9],
                       bairro=data[10], cidade=data[11], estado=data[12], cep=data[13], queixa_principal=data[14],
                       historico_doenca_atual=data[15], antecedentes_pessoais=data[16],
                       antecedentes_familiares=data[17], habitos_vida=data[18], medicamentos_em_uso=data[19])
        # Para compatibilidade com a lista de pacientes (6 colunas)
        elif data and len(data) >= 6:
             return cls(id=data[0], nome=data[1], telefone=data[2], cpf=data[3], data_nascimento=data[4], cidade=data[5])
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
        return { 'id': self.id, 'nome': self.nome, 'duracao': self.duracao, 'valor': self.valor }
    
    @classmethod
    def from_tuple(cls, data):
        if data and len(data) >= 4:
            return cls(data[0], data[1], data[2], data[3])
        return cls()
    
    def get_duracao_formatada(self):
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
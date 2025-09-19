from datetime import datetime

class Paciente:
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
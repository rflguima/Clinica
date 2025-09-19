class Profissional:
    def __init__(self, id=None, nome="", especialidade="", crm_registro="", telefone="", email="", codigo_acesso=""):
        self.id = id
        self.nome = nome
        self.especialidade = especialidade
        self.crm_registro = crm_registro
        self.telefone = telefone
        self.email = email
        self.codigo_acesso = codigo_acesso  # Novo campo para código de 6 dígitos
    
    def __str__(self):
        return f"{self.nome} - {self.especialidade}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'especialidade': self.especialidade,
            'crm_registro': self.crm_registro,
            'telefone': self.telefone,
            'email': self.email,
            'codigo_acesso': self.codigo_acesso
        }
    
    @classmethod
    def from_tuple(cls, data):
        if data and len(data) >= 7:  # Agora com 7 campos incluindo codigo_acesso
            return cls(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
        elif data and len(data) >= 6:  # Compatibilidade com versão antiga
            return cls(data[0], data[1], data[2], data[3], data[4], data[5], "")
        return cls()
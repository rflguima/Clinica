class Profissional:
    def __init__(self, id=None, nome="", especialidade="", crm_registro="", telefone="", email="", codigo_acesso="", role="profissional"):
        self.id = id
        self.nome = nome
        self.especialidade = especialidade
        self.crm_registro = crm_registro
        self.telefone = telefone
        self.email = email
        self.codigo_acesso = codigo_acesso
        # --- CAMPO NOVO ---
        self.role = role
    
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
            'codigo_acesso': self.codigo_acesso,
            'role': self.role
        }
    
    @classmethod
    def from_tuple(cls, data):
        # Agora com 8 campos incluindo role
        if data and len(data) >= 8:
            return cls(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])
        # Compatibilidade com versão antiga
        elif data and len(data) >= 7:
            return cls(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
        return cls()
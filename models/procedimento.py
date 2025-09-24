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
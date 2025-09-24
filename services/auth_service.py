import random
import string

class AuthService:
    @staticmethod
    def gerar_codigo_acesso():
        """Gera um código aleatório de 6 dígitos"""
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def validar_codigo_acesso(codigo):
        """Valida se o código tem o formato correto (6 dígitos)"""
        return len(codigo) == 6 and codigo.isdigit()
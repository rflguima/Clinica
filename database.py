import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="clinica.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Retorna uma conexão com o banco de dados"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Tabela profissionais
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profissionais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    especialidade TEXT NOT NULL,
                    crm_registro TEXT UNIQUE NOT NULL,
                    telefone TEXT,
                    email TEXT
                )
            ''')
            
            # Tabela pacientes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pacientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    telefone TEXT,
                    cpf TEXT UNIQUE,
                    endereco TEXT,
                    data_nascimento DATE
                )
            ''')
            
            # Tabela procedimentos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS procedimentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    duracao INTEGER NOT NULL,
                    valor REAL NOT NULL
                )
            ''')
            
            # Tabela agendamentos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agendamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER NOT NULL,
                    procedimento_id INTEGER NOT NULL,
                    profissional_id INTEGER NOT NULL,
                    data_hora DATETIME NOT NULL,
                    status TEXT DEFAULT 'agendado',
                    observacoes TEXT,
                    FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
                    FOREIGN KEY (procedimento_id) REFERENCES procedimentos (id),
                    FOREIGN KEY (profissional_id) REFERENCES profissionais (id)
                )
            ''')
            
            conn.commit()
            print("Banco de dados inicializado com sucesso!")
            
        except sqlite3.Error as e:
            print(f"Erro ao inicializar banco de dados: {e}")
        finally:
            conn.close()
    
    def execute_query(self, query, params=None):
        """Executa uma query e retorna os resultados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                return results
            else:
                conn.commit()
                return cursor.lastrowid
                
        except sqlite3.Error as e:
            print(f"Erro na execução da query: {e}")
            return None
        finally:
            conn.close()
    
    def insert_profissional(self, nome, especialidade, crm_registro, telefone, email):
        """Insere um novo profissional"""
        query = '''
            INSERT INTO profissionais (nome, especialidade, crm_registro, telefone, email)
            VALUES (?, ?, ?, ?, ?)
        '''
        return self.execute_query(query, (nome, especialidade, crm_registro, telefone, email))
    
    def get_profissionais(self):
        """Retorna todos os profissionais"""
        query = "SELECT * FROM profissionais ORDER BY nome"
        return self.execute_query(query)
    
    def update_profissional(self, id, nome, especialidade, crm_registro, telefone, email):
        """Atualiza um profissional"""
        query = '''
            UPDATE profissionais 
            SET nome=?, especialidade=?, crm_registro=?, telefone=?, email=?
            WHERE id=?
        '''
        return self.execute_query(query, (nome, especialidade, crm_registro, telefone, email, id))
    
    def delete_profissional(self, id):
        """Remove um profissional"""
        query = "DELETE FROM profissionais WHERE id=?"
        return self.execute_query(query, (id,))
    
    def insert_paciente(self, nome, telefone, cpf, endereco, data_nascimento):
        """Insere um novo paciente"""
        query = '''
            INSERT INTO pacientes (nome, telefone, cpf, endereco, data_nascimento)
            VALUES (?, ?, ?, ?, ?)
        '''
        return self.execute_query(query, (nome, telefone, cpf, endereco, data_nascimento))
    
    def get_pacientes(self):
        """Retorna todos os pacientes"""
        query = "SELECT * FROM pacientes ORDER BY nome"
        return self.execute_query(query)
    
    def search_pacientes(self, termo):
        """Busca pacientes por nome ou CPF"""
        query = "SELECT * FROM pacientes WHERE nome LIKE ? OR cpf LIKE ? ORDER BY nome"
        termo = f"%{termo}%"
        return self.execute_query(query, (termo, termo))
    
    def update_paciente(self, id, nome, telefone, cpf, endereco, data_nascimento):
        """Atualiza um paciente"""
        query = '''
            UPDATE pacientes 
            SET nome=?, telefone=?, cpf=?, endereco=?, data_nascimento=?
            WHERE id=?
        '''
        return self.execute_query(query, (nome, telefone, cpf, endereco, data_nascimento, id))
    
    def delete_paciente(self, id):
        """Remove um paciente"""
        query = "DELETE FROM pacientes WHERE id=?"
        return self.execute_query(query, (id,))
    
    def insert_procedimento(self, nome, duracao, valor):
        """Insere um novo procedimento"""
        query = '''
            INSERT INTO procedimentos (nome, duracao, valor)
            VALUES (?, ?, ?)
        '''
        return self.execute_query(query, (nome, duracao, valor))
    
    def get_procedimentos(self):
        """Retorna todos os procedimentos"""
        query = "SELECT * FROM procedimentos ORDER BY nome"
        return self.execute_query(query)
    
    def update_procedimento(self, id, nome, duracao, valor):
        """Atualiza um procedimento"""
        query = '''
            UPDATE procedimentos 
            SET nome=?, duracao=?, valor=?
            WHERE id=?
        '''
        return self.execute_query(query, (nome, duracao, valor, id))
    
    def delete_procedimento(self, id):
        """Remove um procedimento"""
        query = "DELETE FROM procedimentos WHERE id=?"
        return self.execute_query(query, (id,))
    
    def insert_agendamento(self, paciente_id, procedimento_id, profissional_id, data_hora, status, observacoes):
        """Insere um novo agendamento"""
        query = '''
            INSERT INTO agendamentos (paciente_id, procedimento_id, profissional_id, data_hora, status, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        return self.execute_query(query, (paciente_id, procedimento_id, profissional_id, data_hora, status, observacoes))
    
    def get_agendamentos(self, profissional_id=None):
        """Retorna agendamentos, opcionalmente filtrados por profissional"""
        if profissional_id:
            query = '''
                SELECT a.id, p.nome as paciente, pr.nome as procedimento, 
                       prof.nome as profissional, a.data_hora, a.status, a.observacoes
                FROM agendamentos a
                JOIN pacientes p ON a.paciente_id = p.id
                JOIN procedimentos pr ON a.procedimento_id = pr.id
                JOIN profissionais prof ON a.profissional_id = prof.id
                WHERE a.profissional_id = ?
                ORDER BY a.data_hora
            '''
            return self.execute_query(query, (profissional_id,))
        else:
            query = '''
                SELECT a.id, p.nome as paciente, pr.nome as procedimento, 
                       prof.nome as profissional, a.data_hora, a.status, a.observacoes
                FROM agendamentos a
                JOIN pacientes p ON a.paciente_id = p.id
                JOIN procedimentos pr ON a.procedimento_id = pr.id
                JOIN profissionais prof ON a.profissional_id = prof.id
                ORDER BY a.data_hora
            '''
            return self.execute_query(query)
    
    def get_agendamentos_por_data(self, data, profissional_id=None):
        """Retorna agendamentos de uma data específica"""
        if profissional_id:
            query = '''
                SELECT a.id, p.nome as paciente, pr.nome as procedimento, 
                       prof.nome as profissional, a.data_hora, a.status, a.observacoes
                FROM agendamentos a
                JOIN pacientes p ON a.paciente_id = p.id
                JOIN procedimentos pr ON a.procedimento_id = pr.id
                JOIN profissionais prof ON a.profissional_id = prof.id
                WHERE DATE(a.data_hora) = ? AND a.profissional_id = ?
                ORDER BY a.data_hora
            '''
            return self.execute_query(query, (data, profissional_id))
        else:
            query = '''
                SELECT a.id, p.nome as paciente, pr.nome as procedimento, 
                       prof.nome as profissional, a.data_hora, a.status, a.observacoes
                FROM agendamentos a
                JOIN pacientes p ON a.paciente_id = p.id
                JOIN procedimentos pr ON a.procedimento_id = pr.id
                JOIN profissionais prof ON a.profissional_id = prof.id
                WHERE DATE(a.data_hora) = ?
                ORDER BY a.data_hora
            '''
            return self.execute_query(query, (data,))
    
    def update_agendamento(self, id, paciente_id, procedimento_id, profissional_id, data_hora, status, observacoes):
        """Atualiza um agendamento"""
        query = '''
            UPDATE agendamentos 
            SET paciente_id=?, procedimento_id=?, profissional_id=?, data_hora=?, status=?, observacoes=?
            WHERE id=?
        '''
        return self.execute_query(query, (paciente_id, procedimento_id, profissional_id, data_hora, status, observacoes, id))
    
    def delete_agendamento(self, id):
        """Remove um agendamento"""
        query = "DELETE FROM agendamentos WHERE id=?"
        return self.execute_query(query, (id,))
    
    def get_historico_paciente(self, paciente_id):
        """Retorna o histórico de procedimentos de um paciente"""
        query = '''
            SELECT pr.nome as procedimento, prof.nome as profissional, 
                   a.data_hora, a.status, a.observacoes
            FROM agendamentos a
            JOIN procedimentos pr ON a.procedimento_id = pr.id
            JOIN profissionais prof ON a.profissional_id = prof.id
            WHERE a.paciente_id = ?
            ORDER BY a.data_hora DESC
        '''
        return self.execute_query(query, (paciente_id,))
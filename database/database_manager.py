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
            # Tabela profissionais - MODIFICADA COM ROLE
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profissionais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    especialidade TEXT NOT NULL,
                    crm_registro TEXT UNIQUE NOT NULL,
                    telefone TEXT,
                    email TEXT,
                    codigo_acesso TEXT NOT NULL,
                    role TEXT DEFAULT 'profissional' NOT NULL
                )
            ''')

            cursor.execute("PRAGMA table_info(profissionais)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'role' not in columns:
                cursor.execute("ALTER TABLE profissionais ADD COLUMN role TEXT DEFAULT 'profissional' NOT NULL")
            
            # Tabela pacientes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pacientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    data_nascimento DATE,
                    cpf TEXT UNIQUE,
                    estado_civil TEXT,
                    profissao TEXT,
                    telefone TEXT,
                    email TEXT,
                    rua TEXT,
                    numero TEXT,
                    bairro TEXT,
                    cidade TEXT,
                    estado TEXT,
                    cep TEXT,
                    queixa_principal TEXT,
                    historico_doenca_atual TEXT,
                    antecedentes_pessoais TEXT,
                    antecedentes_familiares TEXT,
                    habitos_vida TEXT,
                    medicamentos_em_uso TEXT
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
    
    # --- MÉTODOS DE PROFISSIONAIS ---
    def insert_profissional(self, nome, especialidade, crm_registro, telefone, email, codigo_acesso):
        query = '''
            INSERT INTO profissionais (nome, especialidade, crm_registro, telefone, email, codigo_acesso)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        return self.execute_query(query, (nome, especialidade, crm_registro, telefone, email, codigo_acesso))
    
    def get_profissionais(self):
        query = "SELECT * FROM profissionais ORDER BY nome"
        return self.execute_query(query)
    
    def get_profissional_by_id(self, profissional_id):
        query = "SELECT * FROM profissionais WHERE id = ?"
        result = self.execute_query(query, (profissional_id,))
        return result[0] if result else None
    
    def verificar_codigo_acesso(self, profissional_id, codigo):
        query = "SELECT codigo_acesso FROM profissionais WHERE id = ?"
        result = self.execute_query(query, (profissional_id,))
        if result:
            return result[0][0] == codigo
        return False
    
    def update_profissional(self, id, nome, especialidade, crm_registro, telefone, email):
        query = '''
            UPDATE profissionais 
            SET nome=?, especialidade=?, crm_registro=?, telefone=?, email=?
            WHERE id=?
        '''
        return self.execute_query(query, (nome, especialidade, crm_registro, telefone, email, id))
    
    def delete_profissional(self, id):
        query = "DELETE FROM profissionais WHERE id=?"
        return self.execute_query(query, (id,))
    
    # --- MÉTODOS DE PACIENTES ---
    def insert_paciente(self, nome, data_nascimento, cpf, estado_civil, profissao, telefone, email,
                        rua, numero, bairro, cidade, estado, cep, queixa, historico, ant_pessoais,
                        ant_familiares, habitos, medicamentos):
        query = '''
            INSERT INTO pacientes (nome, data_nascimento, cpf, estado_civil, profissao, telefone, email,
                                   rua, numero, bairro, cidade, estado, cep, queixa_principal,
                                   historico_doenca_atual, antecedentes_pessoais, antecedentes_familiares,
                                   habitos_vida, medicamentos_em_uso)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (nome, data_nascimento, cpf, estado_civil, profissao, telefone, email, rua, numero,
                  bairro, cidade, estado, cep, queixa, historico, ant_pessoais, ant_familiares,
                  habitos, medicamentos)
        return self.execute_query(query, params)
    
    def get_pacientes(self):
        query = "SELECT id, nome, telefone, cpf, data_nascimento, cidade FROM pacientes ORDER BY nome"
        return self.execute_query(query)

    def get_pacientes_recentes(self, limit=5):
        query = "SELECT nome FROM pacientes ORDER BY id DESC LIMIT ?"
        return self.execute_query(query, (limit,))

    def get_paciente_by_id(self, paciente_id):
        query = "SELECT * FROM pacientes WHERE id = ?"
        result = self.execute_query(query, (paciente_id,))
        return result[0] if result else None
    
    def search_pacientes(self, termo):
        query = "SELECT id, nome, telefone, cpf, data_nascimento, cidade FROM pacientes WHERE nome LIKE ? OR cpf LIKE ? ORDER BY nome"
        termo = f"%{termo}%"
        return self.execute_query(query, (termo, termo))
    
    def update_paciente(self, id, nome, data_nascimento, cpf, estado_civil, profissao, telefone, email,
                        rua, numero, bairro, cidade, estado, cep, queixa, historico, ant_pessoais,
                        ant_familiares, habitos, medicamentos):
        query = '''
            UPDATE pacientes 
            SET nome=?, data_nascimento=?, cpf=?, estado_civil=?, profissao=?, telefone=?, email=?,
                rua=?, numero=?, bairro=?, cidade=?, estado=?, cep=?, queixa_principal=?,
                historico_doenca_atual=?, antecedentes_pessoais=?, antecedentes_familiares=?,
                habitos_vida=?, medicamentos_em_uso=?
            WHERE id=?
        '''
        params = (nome, data_nascimento, cpf, estado_civil, profissao, telefone, email, rua, numero,
                  bairro, cidade, estado, cep, queixa, historico, ant_pessoais, ant_familiares,
                  habitos, medicamentos, id)
        return self.execute_query(query, params)
    
    def delete_paciente(self, id):
        query = "DELETE FROM pacientes WHERE id=?"
        return self.execute_query(query, (id,))
    
    # --- MÉTODOS DE PROCEDIMENTOS ---
    def insert_procedimento(self, nome, duracao, valor):
        query = '''
            INSERT INTO procedimentos (nome, duracao, valor)
            VALUES (?, ?, ?)
        '''
        return self.execute_query(query, (nome, duracao, valor))
    
    def get_procedimentos(self):
        query = "SELECT * FROM procedimentos ORDER BY nome"
        return self.execute_query(query)
    
    def update_procedimento(self, id, nome, duracao, valor):
        query = '''
            UPDATE procedimentos 
            SET nome=?, duracao=?, valor=?
            WHERE id=?
        '''
        return self.execute_query(query, (nome, duracao, valor, id))
    
    def delete_procedimento(self, id):
        query = "DELETE FROM procedimentos WHERE id=?"
        return self.execute_query(query, (id,))
    
    # --- MÉTODOS DE AGENDAMENTOS ---
    def insert_agendamento(self, paciente_id, procedimento_id, profissional_id, data_hora, status, observacoes):
        query = '''
            INSERT INTO agendamentos (paciente_id, procedimento_id, profissional_id, data_hora, status, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        return self.execute_query(query, (paciente_id, procedimento_id, profissional_id, data_hora, status, observacoes))
    
    def get_agendamentos(self, profissional_logado):
        if profissional_logado.role == 'secretaria':
            query = '''
                SELECT a.id, p.nome as paciente, pr.nome as procedimento, 
                       prof.nome as profissional, a.data_hora, a.status, a.observacoes,
                       p.id as paciente_id
                FROM agendamentos a
                JOIN pacientes p ON a.paciente_id = p.id
                JOIN procedimentos pr ON a.procedimento_id = pr.id
                JOIN profissionais prof ON a.profissional_id = prof.id
                ORDER BY a.data_hora
            '''
            return self.execute_query(query)
        else:
            query = '''
                SELECT a.id, p.nome as paciente, pr.nome as procedimento, 
                       prof.nome as profissional, a.data_hora, a.status, a.observacoes,
                       p.id as paciente_id
                FROM agendamentos a
                JOIN pacientes p ON a.paciente_id = p.id
                JOIN procedimentos pr ON a.procedimento_id = pr.id
                JOIN profissionais prof ON a.profissional_id = prof.id
                WHERE a.profissional_id = ?
                ORDER BY a.data_hora
            '''
            return self.execute_query(query, (profissional_logado.id,))

    def get_agendamentos_detalhados_por_data(self, data, profissional_logado):
        """
        Retorna detalhes dos agendamentos para a agenda visual,
        incluindo a duração e o nome do profissional.
        """
        query_base = """
            SELECT
                a.id,
                p.nome as paciente_nome,
                pr.nome as procedimento_nome,
                a.data_hora,
                pr.duracao,
                a.status,
                p.id as paciente_id,
                prof.nome as profissional_nome 
            FROM agendamentos a
            JOIN pacientes p ON a.paciente_id = p.id
            JOIN procedimentos pr ON a.procedimento_id = pr.id
            JOIN profissionais prof ON a.profissional_id = prof.id
        """
        if profissional_logado.role == 'secretaria':
            query = query_base + " WHERE DATE(a.data_hora) = ? ORDER BY a.data_hora"
            return self.execute_query(query, (data,))
        else:
            query = query_base + " WHERE DATE(a.data_hora) = ? AND a.profissional_id = ? ORDER BY a.data_hora"
            return self.execute_query(query, (data, profissional_logado.id))
    
    def get_agendamentos_em_espera(self, data, profissional_id):
        """Conta os agendamentos para uma data específica que ainda estão com status 'agendado'."""
        query = "SELECT COUNT(*) FROM agendamentos WHERE DATE(data_hora) = ? AND profissional_id = ? AND status = 'agendado'"
        result = self.execute_query(query, (data, profissional_id))
        return result[0][0] if result else 0

    def update_agendamento(self, id, paciente_id, procedimento_id, profissional_id, data_hora, status, observacoes):
        query = '''
            UPDATE agendamentos 
            SET paciente_id=?, procedimento_id=?, profissional_id=?, data_hora=?, status=?, observacoes=?
            WHERE id=?
        '''
        return self.execute_query(query, (paciente_id, procedimento_id, profissional_id, data_hora, status, observacoes, id))
    
    def delete_agendamento(self, id):
        query = "DELETE FROM agendamentos WHERE id=?"
        return self.execute_query(query, (id,))
    
    def get_historico_paciente(self, paciente_id):
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
    
    def update_agendamento_status(self, agendamento_id, novo_status):
        """Atualiza apenas o status de um agendamento específico."""
        query = "UPDATE agendamentos SET status = ? WHERE id = ?"
        return self.execute_query(query, (novo_status, agendamento_id))

    def update_agendamento_horario(self, agendamento_id, nova_data_hora):
        """Atualiza apenas a data e a hora de um agendamento específico."""
        query = "UPDATE agendamentos SET data_hora = ? WHERE id = ?"
        return self.execute_query(query, (nova_data_hora, agendamento_id))
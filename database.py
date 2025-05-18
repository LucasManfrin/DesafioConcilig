import sqlite3
import os

   # Classe para gerenciar conexões com o banco de dados SQLite
class Database:
    _db_file = "contratos.db"
    
    @classmethod
    def initialize(cls, db_file=None):
        # Inicializa o banco de dados
        if db_file:
            cls._db_file = db_file
        
        # Verifica se há um diretório no caminho do arquivo
        db_dir = os.path.dirname(cls._db_file)
        if db_dir:  # Se houver um diretório no caminho
            os.makedirs(db_dir, exist_ok=True)
        
        print(f"Banco de dados inicializado: {cls._db_file}")
    
    @classmethod
    def get_connection(cls):
        # Conexão com o banco de dados
        conn = sqlite3.connect(cls._db_file)
        conn.row_factory = sqlite3.Row  # Para acessar colunas pelo nome
        return conn
    
    @classmethod
    def execute_query(cls, query, params=None, fetchone=False, commit=False):
        # Consulta SQL e retorna o resultado
        conn = cls.get_connection()
        cursor = conn.cursor()
        result = None
        
        try:
            print(f"Executando query: {query}")
            if params:
                print(f"Com parâmetros: {params}")
            
            cursor.execute(query, params or ())
            
            if fetchone:
                result = cursor.fetchone()
                print(f"Resultado fetchone: {result}")
            else:
                result = cursor.fetchall()
                print(f"Resultado fetchall: {len(result)} linhas")
                
            if commit:
                print("Realizando commit...")
                conn.commit()
                print("Commit realizado com sucesso!")
                
            return result
        except Exception as e:
            print(f"ERRO na execução da query: {str(e)}")
            if commit:
                print("Realizando rollback...")
                conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            print("Conexão fechada.")
    
    @classmethod
    def execute_script(cls, script):
        """Executa um script SQL"""
        conn = cls.get_connection()
        
        try:
            print(f"Executando script SQL...")
            conn.executescript(script)
            print("Realizando commit do script...")
            conn.commit()
            print("Script executado com sucesso!")
        except Exception as e:
            print(f"ERRO na execução do script: {str(e)}")
            conn.rollback()
            raise e
        finally:
            conn.close()
            print("Conexão fechada.")
"""
Script para limpeza e reinicialização completa do banco de dados.

Este script:
1. Exclui completamente as tabelas 'contratos' e 'arquivos_importados'
2. Recria as tabelas com a estrutura correta e limpa 
3. Configura as restrições e valores padrão apropriados para cada coluna

Estrutura das tabelas criadas:
- arquivos_importados:
  * id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
  * nome_arquivo (TEXT, NOT NULL)
  * data_importacao (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
  * usuario_id (INTEGER, NOT NULL)

- contratos:
  * id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
  * numero_contrato (TEXT, NOT NULL, UNIQUE)
  * cliente (TEXT, NOT NULL)
  * valor (REAL, NOT NULL)
  * data_inicio (TEXT, NOT NULL)
  * data_vencimento (TEXT, NOT NULL)
  * descricao (TEXT)
  * status (TEXT, DEFAULT 'Ativo')
  * arquivo_id (INTEGER)
  * data_criacao (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
  * atraso (INTEGER, DEFAULT 0)


Este script apaga todos os dados existentes nas tabelas.
"""

# Adiciona o diretório pai ao path do Python para encontrar o módulo database
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Agora podemos importar o Database
from database import Database

def limpar_banco():
    """Limpa e reinicializa o banco de dados"""
    print("=== LIMPANDO BANCO DE DADOS ===")
    
    # Inicializa o banco de dados
    Database.initialize()
    
    try:
        # Exclui as tabelas se existirem
        Database.execute_query("DROP TABLE IF EXISTS contratos", commit=True)
        print("Tabela contratos excluída.")
        
        Database.execute_query("DROP TABLE IF EXISTS arquivos_importados", commit=True)
        print("Tabela arquivos_importados excluída.")
        
        # Recria as tabelas
        create_arquivos = """
        CREATE TABLE arquivos_importados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_arquivo TEXT NOT NULL,
            data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER NOT NULL
        )
        """
        Database.execute_query(create_arquivos, commit=True)
        print("Tabela arquivos_importados recriada.")
        
        create_contratos = """
        CREATE TABLE contratos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_contrato TEXT NOT NULL UNIQUE,
            cliente TEXT NOT NULL,
            valor REAL NOT NULL,
            data_inicio TEXT NOT NULL,
            data_vencimento TEXT NOT NULL,
            descricao TEXT,
            status TEXT DEFAULT 'ativo',
            arquivo_id INTEGER,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atraso INTEGER DEFAULT 0
        )
        """
        Database.execute_query(create_contratos, commit=True)
        print("Tabela contratos recriada.")
        
        print("\n=== BANCO DE DADOS REINICIALIZADO COM SUCESSO ===")
    except Exception as e:
        print(f"ERRO ao limpar banco de dados: {str(e)}")

if __name__ == "__main__":
    limpar_banco()
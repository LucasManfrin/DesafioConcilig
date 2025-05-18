"""
Script para atualização do banco de dados.

Este script:
1. Verifica se a coluna 'admin' existe na tabela 'usuarios'
2. Adiciona a coluna 'admin' se ela não existir
3. Garante que exista pelo menos um usuário com privilégios de administrador

"""


import sqlite3

def atualizar_banco():
    """Atualiza a estrutura do banco de dados adicionando a coluna admin à tabela usuarios"""
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect("contratos.db")
        cursor = conn.cursor()
        
        # Obtém informações sobre as colunas da tabela 'usuarios'
        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = cursor.fetchall()
        
        # Verifica se a coluna admin já existe
        coluna_admin_existe = any(coluna[1] == 'admin' for coluna in colunas)
        
        # Se a coluna admin não existir, ela é adicionada automaticamente
        if not coluna_admin_existe:
            print("Coluna 'admin' não encontrada")
            print("Adicionando coluna 'admin' à tabela 'usuarios'...")
            # Adiciona a coluna admin à tabela usuarios
            cursor.execute("ALTER TABLE usuarios ADD COLUMN admin INTEGER DEFAULT 0")
            conn.commit()
            print("Coluna 'admin' adicionada com sucesso!")
        else:
            print("\nA coluna 'admin' já existe na tabela 'usuarios'. \n")
        
        # Verifica se há algum usuário administrador
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE admin = 1")
        total_admins = cursor.fetchone()[0]
        
        # Se não houver administradores, torna o primeiro usuário administrador
        if total_admins == 0:
            cursor.execute("UPDATE usuarios SET admin = 1 WHERE id = (SELECT MIN(id) FROM usuarios)")
            conn.commit()
            print("Primeiro usuário definido como administrador.")
        else:
            # Mostra se já existe um usuário administrador e quem é o primeiro usuário
            cursor.execute("SELECT nome FROM usuarios WHERE admin = 1")
            admin_usuarios = cursor.fetchone()
            conn.commit()
            print("Usuário 'admin' já existe.")
            print(f"Nome: {admin_usuarios[0]}, está cadastrado como administrador")
        
        print("\nBanco de dados atualizado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao atualizar o banco de dados: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    atualizar_banco()

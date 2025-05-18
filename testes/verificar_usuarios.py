import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

def verificar_e_corrigir_usuarios():
    """Verifica os usuários no banco de dados e corrige problemas de autenticação"""
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect("contratos.db")
        conn.row_factory = sqlite3.Row  # Para acessar as colunas pelo nome
        cursor = conn.cursor()
        
        print("\n=== VERIFICAÇÃO DE USUÁRIOS ===\n")
        
        # Verifica se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if cursor.fetchone() is None:
            print("A tabela 'usuarios' não existe no banco de dados!")
            criar_tabela = input("Deseja criar a tabela de usuários? (s/n): ")
            if criar_tabela.lower() == 's':
                criar_tabela_usuarios(cursor, conn)
            else:
                return
        
        # Lista todos os usuários
        cursor.execute("SELECT id, nome, email, admin FROM usuarios")
        usuarios = cursor.fetchall()
        
        if not usuarios:
            print("Não há usuários cadastrados no banco de dados.")
            criar_admin = input("Deseja criar um usuário administrador? (s/n): ")
            if criar_admin.lower() == 's':
                criar_usuario_admin(cursor, conn)
            return
        
        print("Usuários cadastrados:")
        print("-" * 60)
        print(f"{'ID':<5} {'Nome':<20} {'Email':<30} {'Admin':<5}")
        print("-" * 60)
        
        for usuario in usuarios:
            admin_status = "Sim" if usuario['admin'] else "Não"
            print(f"{usuario['id']:<5} {usuario['nome']:<20} {usuario['email']:<30} {admin_status:<5}")
        
        print("-" * 60)
        
        # Verifica se há administradores
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE admin = 1")
        total_admins = cursor.fetchone()[0]
        
        if total_admins == 0:
            print("\nAtenção: Não há usuários administradores no sistema!")
            definir_admin = input("Deseja definir um usuário existente como administrador? (s/n): ")
            if definir_admin.lower() == 's':
                id_usuario = input("Digite o ID do usuário que deseja tornar administrador: ")
                cursor.execute("UPDATE usuarios SET admin = 1 WHERE id = ?", (id_usuario,))
                conn.commit()
                print(f"Usuário ID {id_usuario} definido como administrador.")
        
        # Opção para redefinir senha
        print("\nOpções:")
        print("1. Redefinir senha de um usuário")
        print("2. Criar novo usuário administrador")
        print("3. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == '1':
            id_usuario = input("Digite o ID do usuário cuja senha deseja redefinir: ")
            nova_senha = input("Digite a nova senha: ")
            
            # Verifica se o usuário existe
            cursor.execute("SELECT id FROM usuarios WHERE id = ?", (id_usuario,))
            if cursor.fetchone() is None:
                print(f"Usuário com ID {id_usuario} não encontrado.")
                return
            
            # Atualiza a senha
            senha_hash = generate_password_hash(nova_senha)
            cursor.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, id_usuario))
            conn.commit()
            print(f"Senha do usuário ID {id_usuario} redefinida com sucesso.")
            
        elif opcao == '2':
            criar_usuario_admin(cursor, conn)
            
    except Exception as e:
        print(f"Erro ao verificar usuários: {str(e)}")
    finally:
        if conn:
            conn.close()

def criar_tabela_usuarios(cursor, conn):
    """Cria a tabela de usuários"""
    try:
        cursor.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            admin INTEGER DEFAULT 0,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        print("Tabela 'usuarios' criada com sucesso!")
        
        criar_admin = input("Deseja criar um usuário administrador? (s/n): ")
        if criar_admin.lower() == 's':
            criar_usuario_admin(cursor, conn)
            
    except Exception as e:
        print(f"Erro ao criar tabela: {str(e)}")

def criar_usuario_admin(cursor, conn):
    """Cria um usuário administrador"""
    try:
        nome = input("Nome do administrador: ")
        email = input("Email do administrador: ")
        senha = input("Senha do administrador: ")
        
        senha_hash = generate_password_hash(senha)
        
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, admin, data_criacao) VALUES (?, ?, ?, ?, ?)",
            (nome, email, senha_hash, 1, datetime.now().isoformat())
        )
        conn.commit()
        
        print(f"\nUsuário administrador criado com sucesso!")
        print(f"Email: {email}")
        print(f"Senha: {senha}")
        
    except Exception as e:
        print(f"Erro ao criar usuário administrador: {str(e)}")

if __name__ == "__main__":
    verificar_e_corrigir_usuarios()

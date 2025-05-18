"""
Script para reconstrução completa da tabela de usuários.

1. Faz backup dos usuários existentes
2. Remove a tabela antiga e cria uma nova com a estrutura atualizada
3. Restaura os dados dos usuários do backup
4. Cria um usuário administrador padrão se não houver usuários
5. Se houber usuários, torna o primeiro como administrador

"""

import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def reconstruir_tabela_usuarios():
    """Reconstrói a tabela de usuários com a estrutura correta"""
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect("contratos.db")
        cursor = conn.cursor()
        
        print("Iniciando reconstrução da tabela de usuários...")
        
        # Verifica se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        tabela_existe = cursor.fetchone() is not None
        
        # Backup dos usuários existentes se a tabela existir
        usuarios_backup = []
        if tabela_existe:
            print("Fazendo backup dos usuários existentes...")
            try:
                cursor.execute("SELECT nome, email, senha FROM usuarios")
                usuarios_backup = cursor.fetchall()
                print(f"Backup de {len(usuarios_backup)} usuários realizado.")
            except sqlite3.OperationalError as e:
                print(f"Erro ao fazer backup: {str(e)}")
                print("Continuando sem backup...")
        
        # Renomeia a tabela antiga se existir
        if tabela_existe:
            print("Renomeando tabela antiga...")
            cursor.execute("ALTER TABLE usuarios RENAME TO usuarios_old")
            conn.commit()
        
        # Cria a nova tabela com a estrutura correta
        print("Criando nova tabela de usuários...")
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
        
        # Restaura os usuários do backup
        if usuarios_backup:
            print("Restaurando usuários do backup...")
            for usuario in usuarios_backup:
                nome, email, senha = usuario
                # Adiciona o campo admin como 0 (não admin)
                cursor.execute(
                    "INSERT INTO usuarios (nome, email, senha, admin, data_criacao) VALUES (?, ?, ?, ?, ?)",
                    (nome, email, senha, 0, datetime.now().isoformat())
                )
            conn.commit()
            print(f"{len(usuarios_backup)} usuários restaurados.")
        
        # Cria um usuário administrador padrão se não houver usuários
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_usuarios = cursor.fetchone()[0]
        
        if total_usuarios == 0:
            print("Criando usuário administrador padrão...")
            admin_nome = "Administrador"
            admin_email = "admin@exemplo.com"
            admin_senha = "1234"
            admin_senha_hash = generate_password_hash(admin_senha)
            
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha, admin, data_criacao) VALUES (?, ?, ?, ?, ?)",
                (admin_nome, admin_email, admin_senha_hash, 1, datetime.now().isoformat())
            )
            conn.commit()
            print(f"Usuário administrador criado com sucesso!")
            print(f"Email: {admin_email}")
            print(f"Senha: {admin_senha}")
        
        # Verifica se há algum usuário administrador
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE admin = 1")
        total_admins = cursor.fetchone()[0]
        
        if total_admins == 0 and total_usuarios > 0:
            # Se não houver administradores mas houver usuários, torna o primeiro usuário administrador
            cursor.execute("UPDATE usuarios SET admin = 1 WHERE id = (SELECT MIN(id) FROM usuarios)")
            conn.commit()
            print("Primeiro usuário definido como administrador.")
        
        # Remove a tabela antiga se existir
        if tabela_existe:
            print("Removendo tabela antiga...")
            cursor.execute("DROP TABLE IF EXISTS usuarios_old")
            conn.commit()
        
        print("Reconstrução da tabela de usuários concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro ao reconstruir a tabela de usuários: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    reconstruir_tabela_usuarios()

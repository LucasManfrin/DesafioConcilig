import os
from werkzeug.security import generate_password_hash
from database import Database

# Nome do arquivo do banco de dados
db_file = "contratos.db"

def inicializar_banco():
    """Cria as tabelas no banco de dados"""
    # Inicializa o banco de dados
    Database.initialize(db_file)
    
    # Script SQL para criar as tabelas
    script = """
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        admin INTEGER DEFAULT 0,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS arquivos_importados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_arquivo TEXT NOT NULL,
        data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        usuario_id INTEGER,
        status TEXT DEFAULT 'processado',
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    );
    
    CREATE TABLE IF NOT EXISTS contratos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_contrato TEXT UNIQUE NOT NULL,
        cliente TEXT NOT NULL,
        valor REAL NOT NULL,
        data_inicio DATE NOT NULL,
        data_vencimento DATE NOT NULL,
        status TEXT DEFAULT 'ativo',
        descricao TEXT,
        atraso INTEGER DEFAULT 0,
        arquivo_id INTEGER,
        usuario_id INTEGER,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (arquivo_id) REFERENCES arquivos_importados (id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    );
    
    CREATE INDEX IF NOT EXISTS idx_contratos_cliente ON contratos(cliente);
    CREATE INDEX IF NOT EXISTS idx_contratos_vencimento ON contratos(data_vencimento);
    CREATE INDEX IF NOT EXISTS idx_arquivos_usuario ON arquivos_importados(usuario_id);
    """

    # Executa o script
    Database.execute_script(script)
    print("Tabelas criadas com sucesso.")
    
    # Verifica se já existe um usuário admin
    query = "SELECT id FROM usuarios WHERE email = ?"
    usuario = Database.execute_query(query, ("admin@exemplo.com",), fetchone=True)
    
    if not usuario:
        # Cria um usuário admin
        senha_hash = generate_password_hash("admin123")
        query = "INSERT INTO usuarios (nome, email, senha, admin) VALUES (?, ?, ?, ?)"
        Database.execute_query(
            query, 
            ("Administrador", "admin@exemplo.com", senha_hash, 1), 
            commit=True
        )
        print("Usuário admin criado com sucesso.")
    else:
        print("Usuário admin já existe.")

if __name__ == "__main__":
    print("Inicializando o banco de dados...")
    inicializar_banco()
    print("Banco de dados inicializado com sucesso!")
    print(f"Arquivo do banco de dados: {os.path.abspath(db_file)}")

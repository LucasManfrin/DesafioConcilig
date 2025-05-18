import tkinter as tk
from tkinter import messagebox
from werkzeug.security import generate_password_hash

from database import Database

class TelaCadastro:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        
        # Widgets da tela
        self.frame_cadastro = None
        self.nome_entry = None
        self.email_entry = None
        self.senha_entry = None
    
    def mostrar(self, **kwargs):
        """Mostra a tela de cadastro"""
        # Frame de cadastro
        self.frame_cadastro = tk.Frame(self.master, padx=20, pady=20)
        self.frame_cadastro.pack(expand=True)
        
        # Título
        tk.Label(self.frame_cadastro, text="Sistema de Importação de Contratos", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.frame_cadastro, text="Cadastro", font=("Arial", 12)).pack(pady=10)
        
        # Campos de cadastro
        tk.Label(self.frame_cadastro, text="Nome:").pack(anchor="w")
        self.nome_entry = tk.Entry(self.frame_cadastro, width=30)
        self.nome_entry.pack(fill="x", pady=5)
        
        tk.Label(self.frame_cadastro, text="Email:").pack(anchor="w")
        self.email_entry = tk.Entry(self.frame_cadastro, width=30)
        self.email_entry.pack(fill="x", pady=5)
        
        tk.Label(self.frame_cadastro, text="Senha:").pack(anchor="w")
        self.senha_entry = tk.Entry(self.frame_cadastro, width=30, show="*")
        self.senha_entry.pack(fill="x", pady=5)
        
        # Botão de cadastro
        tk.Button(
            self.frame_cadastro, 
            text="Cadastrar", 
            command=self.processar_cadastro
        ).pack(pady=10)
        
        # Link para login
        tk.Button(
            self.frame_cadastro, 
            text="Já tem uma conta? Faça login", 
            command=lambda: self.app.mostrar_tela("login"),
            relief=tk.FLAT,
            fg="blue"
        ).pack()
    
    def processar_cadastro(self):
        """Processa o cadastro do usuário"""
        nome = self.nome_entry.get()
        email = self.email_entry.get()
        senha = self.senha_entry.get()
        
        if not nome or not email or not senha:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos")
            return
        
        try:
            # Verifica se o email já existe
            query = "SELECT id FROM usuarios WHERE email = ?"
            usuario_existente = Database.execute_query(query, (email,), fetchone=True)
            
            if usuario_existente:
                messagebox.showerror("Erro", "Este email já está cadastrado")
                return
            
            # Hash da senha
            senha_hash = generate_password_hash(senha)
            
            # Insere o novo usuário
            query = "INSERT INTO usuarios (nome, email, senha, admin) VALUES (?, ?, ?, ?)"
            Database.execute_query(query, (nome, email, senha_hash, 0), commit=True)
            
            # Obtém o ID do usuário inserido
            query = "SELECT last_insert_rowid()"
            result = Database.execute_query(query, fetchone=True)
            
            # Login automático
            usuario_id = result[0]
            usuario_admin = False
            
            messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso!")
            self.app.fazer_login(usuario_id, nome, usuario_admin)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {str(e)}")

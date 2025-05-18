import tkinter as tk
from tkinter import messagebox
from werkzeug.security import check_password_hash

from database import Database

class TelaLogin:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        
        # Widgets da tela
        self.frame_login = None
        self.email_entry = None
        self.senha_entry = None
    
    def mostrar(self, **kwargs):
        """Mostra a tela de login"""
        # Frame de login
        self.frame_login = tk.Frame(self.master, padx=20, pady=20)
        self.frame_login.pack(expand=True)
        
        # Título
        tk.Label(self.frame_login, text="Sistema de Importação de Contratos", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.frame_login, text="Login", font=("Arial", 12)).pack(pady=10)
        
        # Campos de login
        tk.Label(self.frame_login, text="Email:").pack(anchor="w")
        self.email_entry = tk.Entry(self.frame_login, width=30)
        self.email_entry.pack(fill="x", pady=5)
        
        tk.Label(self.frame_login, text="Senha:").pack(anchor="w")
        self.senha_entry = tk.Entry(self.frame_login, width=30, show="*")
        self.senha_entry.pack(fill="x", pady=5)
        
        # Botão de login
        tk.Button(
            self.frame_login, 
            text="Entrar", 
            command=self.processar_login
        ).pack(pady=10)
        
        # Link para cadastro
        tk.Button(
            self.frame_login, 
            text="Não tem uma conta? Cadastre-se", 
            command=lambda: self.app.mostrar_tela("cadastro"),
            relief=tk.FLAT,
            fg="blue"
        ).pack()
    
    def processar_login(self):
        """Processa o login do usuário"""
        email = self.email_entry.get()
        senha = self.senha_entry.get()
        
        if not email or not senha:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos")
            return
        
        try:
            # Busca o usuário no banco de dados
            query = "SELECT id, nome, senha, admin FROM usuarios WHERE email = ?"
            usuario = Database.execute_query(query, (email,), fetchone=True)
            
            if usuario and check_password_hash(usuario['senha'], senha):
                # Login bem-sucedido
                usuario_id = usuario['id']
                usuario_nome = usuario['nome']
                # Verifica se a coluna admin existe e obtém seu valor
                try:
                    usuario_admin = bool(usuario['admin'])
                except (IndexError, KeyError):
                    usuario_admin = False
                
                messagebox.showinfo("Sucesso", f"Bem-vindo, {usuario_nome}!")
                self.app.fazer_login(usuario_id, usuario_nome, usuario_admin)
            else:
                messagebox.showerror("Erro", "Email ou senha incorretos")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao fazer login: {str(e)}")

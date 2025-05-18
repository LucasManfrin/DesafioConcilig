import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from werkzeug.security import generate_password_hash
from componentes.menu import Menu
from database import Database

class TelaUsuarios:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        
        # Widgets da tela
        self.frame_usuarios = None
        self.treeview = None
    
    def mostrar(self, **kwargs):
        """Mostra a tela de gerenciamento de usuários"""
        # Verifica se o usuário é administrador
        if not self.app.usuario_admin:
            messagebox.showerror("Erro", "Você não tem permissão para acessar esta funcionalidade")
            self.app.mostrar_tela("dashboard")
            return
        
        # Cria o menu
        Menu(self.app).criar_menu()
        
        # Frame de usuários
        self.frame_usuarios = tk.Frame(self.master, padx=20, pady=20)
        self.frame_usuarios.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(self.frame_usuarios, text="Gerenciar Usuários", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Tabela de usuários
        frame_tabela = tk.Frame(self.frame_usuarios)
        frame_tabela.pack(fill="both", expand=True, pady=10)
        
        # Cria a tabela
        colunas = ("id", "nome", "email", "admin", "data_criacao")
        self.treeview = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        
        # Define os cabeçalhos
        self.treeview.heading("id", text="ID")
        self.treeview.heading("nome", text="Nome")
        self.treeview.heading("email", text="Email")
        self.treeview.heading("admin", text="Admin")
        self.treeview.heading("data_criacao", text="Data de Criação")
        
        # Define as larguras das colunas
        self.treeview.column("id", width=50)
        self.treeview.column("nome", width=200)
        self.treeview.column("email", width=200)
        self.treeview.column("admin", width=100)
        self.treeview.column("data_criacao", width=150)
        
        # Adiciona barras de rolagem
        scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.treeview.yview)
        scrollbar_x = ttk.Scrollbar(frame_tabela, orient="horizontal", command=self.treeview.xview)
        self.treeview.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Posiciona os widgets
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.treeview.pack(side="left", fill="both", expand=True)
        
        # Carrega os usuários
        self.carregar_usuarios()
        
        # Adiciona menu de contexto para gerenciar usuários
        self.adicionar_menu_contexto_usuarios()
        
        # Botões de ação
        frame_acoes = tk.Frame(self.frame_usuarios)
        frame_acoes.pack(fill="x", pady=10)
        
        tk.Button(
            frame_acoes, 
            text="Adicionar Usuário", 
            command=self.adicionar_usuario,
            padx=10, pady=5,
            bg="#4dabf7", fg="white"
        ).pack(side="left", padx=5)
        
        tk.Button(
            frame_acoes, 
            text="Editar Usuário Selecionado", 
            command=self.editar_usuario_selecionado,
            padx=10, pady=5
        ).pack(side="left", padx=5)
        
        tk.Button(
            frame_acoes, 
            text="Excluir Usuário Selecionado", 
            command=self.excluir_usuario_selecionado,
            padx=10, pady=5,
            bg="#ff6b6b", fg="white"
        ).pack(side="left", padx=5)
    
    def carregar_usuarios(self):
        """Carrega os usuários na tabela"""
        # Limpa a tabela
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        # Carrega os usuários
        query = "SELECT id, nome, email, admin, data_criacao FROM usuarios ORDER BY id"
        usuarios = Database.execute_query(query)
        
        # Adiciona os usuários à tabela
        for usuario in usuarios:
            # Formata a data de criação
            try:
                data_criacao = datetime.fromisoformat(usuario[4].replace('Z', '+00:00'))
                data_criacao_formatada = data_criacao.strftime("%d/%m/%Y %H:%M")
            except:
                data_criacao_formatada = "N/A"
            
            # Formata o status de admin
            admin = "Sim" if usuario[3] else "Não"
            
            # Adiciona à tabela
            self.treeview.insert(
                "", "end", 
                values=(
                    usuario[0], 
                    usuario[1], 
                    usuario[2], 
                    admin, 
                    data_criacao_formatada
                )
            )
    
    def adicionar_menu_contexto_usuarios(self):
        """Adiciona um menu de contexto à tabela de usuários"""
        menu_contexto = tk.Menu(self.app, tearoff=0)
        menu_contexto.add_command(label="Editar", command=self.editar_usuario_selecionado)
        menu_contexto.add_command(label="Excluir", command=self.excluir_usuario_selecionado)
        menu_contexto.add_separator()
        menu_contexto.add_command(label="Tornar Admin", command=lambda: self.tornar_admin_usuario_selecionado(True))
        menu_contexto.add_command(label="Remover Admin", command=lambda: self.tornar_admin_usuario_selecionado(False))
        
        def mostrar_menu_contexto(event):
            # Verifica se há um item selecionado
            if self.treeview.selection():
                menu_contexto.post(event.x_root, event.y_root)
        
        # Vincula o menu de contexto ao botão direito do mouse
        self.treeview.bind("<Button-3>", mostrar_menu_contexto)
    
    def adicionar_usuario(self):
        """Adiciona um novo usuário"""
        # Cria uma janela para adicionar usuário
        janela_adicionar = tk.Toplevel(self.app)
        janela_adicionar.title("Adicionar Usuário")
        janela_adicionar.geometry("400x300")
        janela_adicionar.transient(self.app)
        janela_adicionar.grab_set()
        
        # Frame principal
        frame_form = tk.Frame(janela_adicionar, padx=20, pady=20)
        frame_form.pack(fill="both", expand=True)
        
        # Campos do formulário
        tk.Label(frame_form, text="Nome:").grid(row=0, column=0, sticky="w", pady=5)
        nome_entry = tk.Entry(frame_form, width=30)
        nome_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(frame_form, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
        email_entry = tk.Entry(frame_form, width=30)
        email_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(frame_form, text="Senha:").grid(row=2, column=0, sticky="w", pady=5)
        senha_entry = tk.Entry(frame_form, width=30, show="*")
        senha_entry.grid(row=2, column=1, pady=5)
        
        # Checkbox para admin
        admin_var = tk.BooleanVar(value=False)
        admin_check = tk.Checkbutton(frame_form, text="Administrador", variable=admin_var)
        admin_check.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        
        # Botões de ação
        frame_botoes = tk.Frame(frame_form)
        frame_botoes.grid(row=4, column=0, columnspan=2, pady=20)
        
        tk.Button(
            frame_botoes,
            text="Salvar",
            command=lambda: self.salvar_novo_usuario(
                nome_entry.get(),
                email_entry.get(),
                senha_entry.get(),
                admin_var.get(),
                janela_adicionar
            ),
            padx=10, pady=5,
            bg="#4dabf7", fg="white"
        ).pack(side="left", padx=5)
        
        tk.Button(
            frame_botoes,
            text="Cancelar",
            command=janela_adicionar.destroy,
            padx=10, pady=5
        ).pack(side="left", padx=5)
    
    def salvar_novo_usuario(self, nome, email, senha, admin, janela):
        """Salva um novo usuário"""
        try:
            # Valida os campos obrigatórios
            if not nome or not email or not senha:
                messagebox.showerror("Erro", "Todos os campos são obrigatórios")
                return
            
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
            Database.execute_query(query, (nome, email, senha_hash, 1 if admin else 0), commit=True)
            
            # Fecha a janela
            janela.destroy()
            
            # Atualiza a tabela
            messagebox.showinfo("Sucesso", "Usuário adicionado com sucesso!")
            
            # Recarrega a tela de gerenciamento de usuários
            self.carregar_usuarios()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar usuário: {str(e)}")
    
    def editar_usuario_selecionado(self):
        """Edita o usuário selecionado"""
        # Verifica se há um item selecionado
        selecao = self.treeview.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Nenhum usuário selecionado")
            return
        
        # Obtém o ID do usuário selecionado
        item = self.treeview.item(selecao[0])
        usuario_id = item['values'][0]
        
        # Não permite editar o próprio usuário
        if usuario_id == self.app.usuario_id:
            messagebox.showwarning("Aviso", "Você não pode editar seu próprio usuário")
            return
        
        try:
            # Busca os dados completos do usuário
            query = "SELECT id, nome, email, admin FROM usuarios WHERE id = ?"
            usuario = Database.execute_query(query, (usuario_id,), fetchone=True)
            
            if not usuario:
                messagebox.showerror("Erro", "Usuário não encontrado")
                return
            
            # Cria uma janela para edição
            janela_edicao = tk.Toplevel(self.app)
            janela_edicao.title(f"Editar Usuário #{usuario[0]}")
            janela_edicao.geometry("400x300")
            janela_edicao.transient(self.app)
            janela_edicao.grab_set()
            
            # Frame principal
            frame_form = tk.Frame(janela_edicao, padx=20, pady=20)
            frame_form.pack(fill="both", expand=True)
            
            # Campos do formulário
            tk.Label(frame_form, text="Nome:").grid(row=0, column=0, sticky="w", pady=5)
            nome_entry = tk.Entry(frame_form, width=30)
            nome_entry.insert(0, usuario[1])
            nome_entry.grid(row=0, column=1, pady=5)
            
            tk.Label(frame_form, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
            email_entry = tk.Entry(frame_form, width=30)
            email_entry.insert(0, usuario[2])
            email_entry.grid(row=1, column=1, pady=5)
            
            tk.Label(frame_form, text="Nova Senha:").grid(row=2, column=0, sticky="w", pady=5)
            senha_entry = tk.Entry(frame_form, width=30, show="*")
            senha_entry.grid(row=2, column=1, pady=5)
            tk.Label(frame_form, text="(Deixe em branco para manter a senha atual)").grid(row=3, column=0, columnspan=2, sticky="w", pady=0)
            
            # Checkbox para admin
            admin_var = tk.BooleanVar(value=bool(usuario[3]))
            admin_check = tk.Checkbutton(frame_form, text="Administrador", variable=admin_var)
            admin_check.grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
            
            # Botões de ação
            frame_botoes = tk.Frame(frame_form)
            frame_botoes.grid(row=5, column=0, columnspan=2, pady=20)
            
            tk.Button(
                frame_botoes,
                text="Salvar",
                command=lambda: self.salvar_edicao_usuario(
                    usuario[0],
                    nome_entry.get(),
                    email_entry.get(),
                    senha_entry.get(),
                    admin_var.get(),
                    janela_edicao
                ),
                padx=10, pady=5,
                bg="#4dabf7", fg="white"
            ).pack(side="left", padx=5)
            
            tk.Button(
                frame_botoes,
                text="Cancelar",
                command=janela_edicao.destroy,
                padx=10, pady=5
            ).pack(side="left", padx=5)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados do usuário: {str(e)}")
    
    def salvar_edicao_usuario(self, usuario_id, nome, email, senha, admin, janela):
        """Salva as alterações em um usuário"""
        try:
            # Valida os campos obrigatórios
            if not nome or not email:
                messagebox.showerror("Erro", "Nome e email são obrigatórios")
                return
            
            # Verifica se o email já existe (exceto para o próprio usuário)
            query = "SELECT id FROM usuarios WHERE email = ? AND id != ?"
            usuario_existente = Database.execute_query(query, (email, usuario_id), fetchone=True)
            
            if usuario_existente:
                messagebox.showerror("Erro", "Este email já está cadastrado para outro usuário")
                return
            
            # Se a senha foi fornecida, atualiza a senha
            if senha:
                senha_hash = generate_password_hash(senha)
                query = "UPDATE usuarios SET nome = ?, email = ?, senha = ?, admin = ? WHERE id = ?"
                Database.execute_query(query, (nome, email, senha_hash, 1 if admin else 0, usuario_id), commit=True)
            else:
                # Se a senha não foi fornecida, mantém a senha atual
                query = "UPDATE usuarios SET nome = ?, email = ?, admin = ? WHERE id = ?"
                Database.execute_query(query, (nome, email, 1 if admin else 0, usuario_id), commit=True)
            
            # Fecha a janela
            janela.destroy()
            
            # Atualiza a tabela
            messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
            
            # Recarrega a tela de gerenciamento de usuários
            self.carregar_usuarios()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar usuário: {str(e)}")
    
    def excluir_usuario_selecionado(self):
        """Exclui o usuário selecionado"""
        # Verifica se há um item selecionado
        selecao = self.treeview.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Nenhum usuário selecionado")
            return
        
        # Obtém o ID do usuário selecionado
        item = self.treeview.item(selecao[0])
        usuario_id = item['values'][0]
        usuario_nome = item['values'][1]
        
        # Não permite excluir o próprio usuário
        if usuario_id == self.app.usuario_id:
            messagebox.showwarning("Aviso", "Você não pode excluir seu próprio usuário")
            return
        
        # Confirma a exclusão
        if not messagebox.askyesno("Confirmar", f"Deseja realmente excluir o usuário {usuario_nome}?"):
            return
        
        try:
            # Exclui o usuário do banco de dados
            query = "DELETE FROM usuarios WHERE id = ?"
            Database.execute_query(query, (usuario_id,), commit=True)
            
            # Remove o item da tabela
            self.treeview.delete(selecao[0])
            
            messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir usuário: {str(e)}")
    
    def tornar_admin_usuario_selecionado(self, admin):
        """Torna o usuário selecionado administrador ou remove privilégios de administrador"""
        # Verifica se há um item selecionado
        selecao = self.treeview.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Nenhum usuário selecionado")
            return
        
        # Obtém o ID do usuário selecionado
        item = self.treeview.item(selecao[0])
        usuario_id = item['values'][0]
        usuario_nome = item['values'][1]
        
        # Não permite alterar o próprio usuário
        if usuario_id == self.app.usuario_id:
            messagebox.showwarning("Aviso", "Você não pode alterar seus próprios privilégios")
            return
        
        # Confirma a alteração
        acao = "tornar administrador" if admin else "remover privilégios de administrador"
        if not messagebox.askyesno("Confirmar", f"Deseja realmente {acao} o usuário {usuario_nome}?"):
            return
        
        try:
            # Atualiza o status de admin do usuário
            query = "UPDATE usuarios SET admin = ? WHERE id = ?"
            Database.execute_query(query, (1 if admin else 0, usuario_id), commit=True)
            
            # Atualiza a tabela
            messagebox.showinfo("Sucesso", f"Privilégios do usuário alterados com sucesso!")
            
            # Recarrega a tela de gerenciamento de usuários
            self.carregar_usuarios()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao alterar privilégios do usuário: {str(e)}")

import tkinter as tk

class Menu:
    def __init__(self, app):
        self.app = app
    
    def criar_menu(self):
        # Cria o menu principal
        menu_bar = tk.Menu(self.app)
        
        # Menu Sistema
        menu_sistema = tk.Menu(menu_bar, tearoff=0)
        menu_sistema.add_command(label="Dashboard", command=lambda: self.app.mostrar_tela("dashboard"))
        menu_sistema.add_separator()
        menu_sistema.add_command(label="Sair", command=self.app.fazer_logout)
        menu_bar.add_cascade(label="Sistema", menu=menu_sistema)
        
        # Menu Contratos
        menu_contratos = tk.Menu(menu_bar, tearoff=0)
        menu_contratos.add_command(label="Importar Contratos", command=lambda: self.app.mostrar_tela("importar"))
        menu_contratos.add_command(label="Ver Contratos", command=lambda: self.app.mostrar_tela("contratos"))
        menu_bar.add_cascade(label="Contratos", menu=menu_contratos)
        
        # Menu Relatórios
        menu_relatorios = tk.Menu(menu_bar, tearoff=0)
        menu_relatorios.add_command(label="Relatório por Cliente", command=lambda: self.app.mostrar_tela("relatorio"))
        menu_bar.add_cascade(label="Relatórios", menu=menu_relatorios)
        
        # Menu Usuários (apenas para administradores)
        if self.app.usuario_admin:
            menu_usuarios = tk.Menu(menu_bar, tearoff=0)
            menu_usuarios.add_command(label="Gerenciar Usuários", command=lambda: self.app.mostrar_tela("usuarios"))
            menu_bar.add_cascade(label="Usuários", menu=menu_usuarios)
        
        self.app.config(menu=menu_bar)
        return menu_bar

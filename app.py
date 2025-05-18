import tkinter as tk
from tkinter import messagebox
import os
import sys

def main():
    # Adiciona o diretório atual ao PATH para garantir que os módulos sejam encontrados
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Verifica se o banco de dados existe, se não existir, ele é iniciado
    if not os.path.exists("contratos.db"):
        print("Banco de dados não encontrado. Inicializando...")
        from inicializar_banco import inicializar_banco
        inicializar_banco()
    
    # Importa as telas
    try:
        from telas.login import TelaLogin
        from telas.cadastro import TelaCadastro
        from telas.dashboard import TelaDashboard
        from telas.importar import TelaImportar
        from telas.contratos import TelaContratos
        from telas.relatorio import TelaRelatorio
        from telas.usuarios import TelaUsuarios
    except ImportError as e:
        messagebox.showerror("Erro de Importação", f"Erro ao importar módulos: {str(e)}\n\nVerifique se as pastas 'telas' e 'componentes' existem e contêm os arquivos necessários.")
        return
    
    # Importa o banco de dados
    from database import Database
    
    class App(tk.Tk):
        def __init__(self):
            super().__init__()
            
            # Configurações da janela principal
            self.title("Sistema de Importação de Contratos")
            self.geometry("1000x600")
            self.minsize(800, 500)
            
            # Variáveis de sessão
            self.usuario_id = None
            self.usuario_nome = None
            self.usuario_admin = False
            
            # Inicializa o banco de dados
            Database.initialize("contratos.db")
            
            # Cria o frame principal
            self.frame_principal = tk.Frame(self)
            self.frame_principal.pack(fill=tk.BOTH, expand=True)
            
            # Cada tela é armazenada nesse dicionário, evitando recriar toda vez.
            self.telas = {}
            
            # Mostra a tela de login
            self.mostrar_tela("login")
        
        def limpar_frame(self):
            # Limpa todos os widgets do frame principal
            for widget in self.frame_principal.winfo_children():
                widget.destroy()
        
        def mostrar_tela(self, nome_tela, **kwargs):
            # Mostra uma tela específica
            self.limpar_frame()
            
            # Cria a tela se ela não existir
            if nome_tela not in self.telas:
                if nome_tela == "login":
                    self.telas[nome_tela] = TelaLogin(self.frame_principal, self)
                elif nome_tela == "cadastro":
                    self.telas[nome_tela] = TelaCadastro(self.frame_principal, self)
                elif nome_tela == "dashboard":
                    self.telas[nome_tela] = TelaDashboard(self.frame_principal, self)
                elif nome_tela == "importar":
                    self.telas[nome_tela] = TelaImportar(self.frame_principal, self)
                elif nome_tela == "contratos":
                    self.telas[nome_tela] = TelaContratos(self.frame_principal, self)
                elif nome_tela == "relatorio":
                    self.telas[nome_tela] = TelaRelatorio(self.frame_principal, self)
                elif nome_tela == "usuarios":
                    self.telas[nome_tela] = TelaUsuarios(self.frame_principal, self)
            
            # Mostra a tela
            self.telas[nome_tela].mostrar(**kwargs)
        
        def fazer_login(self, usuario_id, usuario_nome, usuario_admin):
            # Registra o login do usuário
            self.usuario_id = usuario_id
            self.usuario_nome = usuario_nome
            self.usuario_admin = usuario_admin
            self.mostrar_tela("dashboard")
        
        def fazer_logout(self):
            # Realiza o logout do usuário
            self.usuario_id = None
            self.usuario_nome = None
            self.usuario_admin = False
            self.config(menu=tk.Menu(self))  # Remove o menu
            self.mostrar_tela("login")
    
    app = App()
    app.mainloop()

if __name__ == "__main__":
    print("Iniciando aplicação...")
    main()

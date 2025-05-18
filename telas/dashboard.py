import tkinter as tk
from componentes.menu import Menu
from database import Database

class TelaDashboard:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        
        # Widgets da tela
        self.frame_dashboard = None
    
    def mostrar(self, **kwargs):
        """Mostra o dashboard principal"""
        # Cria o menu
        Menu(self.app).criar_menu()
        
        # Frame do dashboard
        self.frame_dashboard = tk.Frame(self.master, padx=20, pady=20)
        self.frame_dashboard.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(self.frame_dashboard, text=f"Bem-vindo, {self.app.usuario_nome}", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Estatísticas
        frame_stats = tk.Frame(self.frame_dashboard)
        frame_stats.pack(fill="x", pady=10)
        
        # Total de contratos por usuário
        total_contratos = Database.execute_query(
            """
            SELECT COUNT(*) 
            FROM contratos
            JOIN arquivos_importados ON contratos.arquivo_id = arquivos_importados.id
            WHERE arquivos_importados.usuario_id = ?
            """,
            (self.app.usuario_id,),
            fetchone=True
        )
        total_contratos = total_contratos[0] if total_contratos else 0

        # Total de arquivos importados por usuário
        total_arquivos = Database.execute_query(
            """
            SELECT COUNT(*) 
            FROM arquivos_importados 
            WHERE usuario_id = ?
            """,
            (self.app.usuario_id,),
            fetchone=True
        )
        total_arquivos = total_arquivos[0] if total_arquivos else 0

        # Valor total dos contratos do usuário
        valor_total_result = Database.execute_query(
            """
            SELECT SUM(contratos.valor) 
            FROM contratos
            JOIN arquivos_importados ON contratos.arquivo_id = arquivos_importados.id
            WHERE arquivos_importados.usuario_id = ?
            """,
            (self.app.usuario_id,),
            fetchone=True
        )
        valor_total = valor_total_result[0] if valor_total_result and valor_total_result[0] else 0.0
        valor_total_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")




        
        # Cria frames para as estatísticas
        stats = [
            {"texto": "Total de Contratos", "valor": total_contratos},
            {"texto": "Arquivos Importados", "valor": total_arquivos},
            {"texto": "Valor Total", "valor": f"{valor_total_formatado}"}
        ]
        
        for i, stat in enumerate(stats):
            frame_stat = tk.Frame(frame_stats, bd=1, relief=tk.RAISED, padx=10, pady=10)
            frame_stat.grid(row=0, column=i, padx=10, sticky="nsew")
            
            tk.Label(frame_stat, text=stat["texto"], font=("Arial", 12)).pack()
            tk.Label(frame_stat, text=str(stat["valor"]), font=("Arial", 16, "bold")).pack()
        
        frame_stats.grid_columnconfigure(0, weight=1)
        frame_stats.grid_columnconfigure(1, weight=1)
        frame_stats.grid_columnconfigure(2, weight=1)
        
        # Botões de ação
        frame_acoes = tk.Frame(self.frame_dashboard)
        frame_acoes.pack(fill="x", pady=20)
        
        tk.Button(
            frame_acoes, 
            text="Importar Contratos", 
            command=lambda: self.app.mostrar_tela("importar"),
            padx=10, pady=5
        ).grid(row=0, column=0, padx=10, pady=10)
        
        tk.Button(
            frame_acoes, 
            text="Ver Contratos", 
            command=lambda: self.app.mostrar_tela("contratos"),
            padx=10, pady=5
        ).grid(row=0, column=1, padx=10, pady=10)
        
        tk.Button(
            frame_acoes, 
            text="Relatório por Cliente", 
            command=lambda: self.app.mostrar_tela("relatorio"),
            padx=10, pady=5
        ).grid(row=0, column=2, padx=10, pady=10)
        
        frame_acoes.grid_columnconfigure(0, weight=1)
        frame_acoes.grid_columnconfigure(1, weight=1)
        frame_acoes.grid_columnconfigure(2, weight=1)

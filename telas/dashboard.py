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
        
        # Obtém estatísticas
        total_contratos = Database.execute_query("SELECT COUNT(*) FROM contratos", fetchone=True)[0]
        total_arquivos = Database.execute_query(
            "SELECT COUNT(*) FROM arquivos_importados WHERE usuario_id = ?", 
            (self.app.usuario_id,), 
            fetchone=True
        )[0]
        valor_total_result = Database.execute_query(
            """
            SELECT COALESCE(SUM(valor), 0) FROM contratos c
            JOIN arquivos_importados a ON c.arquivo_id = a.id
            WHERE a.usuario_id = ?
            """, 
            (self.app.usuario_id,), 
            fetchone=True
        )
        valor_total = valor_total_result[0] if valor_total_result[0] is not None else 0
        
        # Cria frames para as estatísticas
        stats = [
            {"texto": "Total de Contratos", "valor": total_contratos},
            {"texto": "Arquivos Importados", "valor": total_arquivos},
            {"texto": f"Valor Total: R$ {valor_total:.2f}", "valor": ""}
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

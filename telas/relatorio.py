import tkinter as tk
from tkinter import ttk
from datetime import datetime
from componentes.menu import Menu
from database import Database

class TelaRelatorio:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        
        # Widgets da tela
        self.frame_relatorio = None
        self.treeview = None
    
    def mostrar(self, **kwargs):
        """Mostra o relatório por cliente"""
        # Cria o menu
        Menu(self.app).criar_menu()
        
        # Frame do relatório
        self.frame_relatorio = tk.Frame(self.master, padx=20, pady=20)
        self.frame_relatorio.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(self.frame_relatorio, text="Relatório por Cliente", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Tabela de relatório
        frame_tabela = tk.Frame(self.frame_relatorio)
        frame_tabela.pack(fill="both", expand=True, pady=10)
        
        # Cria a tabela
        colunas = ("cliente", "valor_total", "maior_atraso", "status")
        self.treeview = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        
        # Define os cabeçalhos
        self.treeview.heading("cliente", text="Cliente")
        self.treeview.heading("valor_total", text="Valor Total")
        self.treeview.heading("maior_atraso", text="Maior Atraso (dias)")
        self.treeview.heading("status", text="Status")
        
        # Define as larguras das colunas
        self.treeview.column("cliente", width=200)
        self.treeview.column("valor_total", width=100)
        self.treeview.column("maior_atraso", width=100)
        self.treeview.column("status", width=100)
        
        # Adiciona barras de rolagem
        scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.treeview.yview)
        scrollbar_x = ttk.Scrollbar(frame_tabela, orient="horizontal", command=self.treeview.xview)
        self.treeview.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Posiciona os widgets
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.treeview.pack(side="left", fill="both", expand=True)
        
        # Carrega os dados do relatório
        self.carregar_relatorio()
        
        # Resumo
        frame_resumo = tk.LabelFrame(self.frame_relatorio, text="Resumo", padx=10, pady=10)
        frame_resumo.pack(fill="x", pady=10)
        
        # Calcula os valores do resumo
        self.mostrar_resumo(frame_resumo)
    
    def carregar_relatorio(self):
        """Carrega os dados do relatório"""
        query = """
            SELECT 
                c.cliente,
                SUM(c.valor) as valor_total,
                MAX(
                    CASE 
                        WHEN date(c.data_vencimento) < date('now') 
                        THEN julianday('now') - julianday(c.data_vencimento) 
                        ELSE 0 
                    END
                ) as maior_atraso
            FROM contratos c
            GROUP BY c.cliente
            ORDER BY valor_total DESC
        """
        
        relatorio = Database.execute_query(query)
        
        # Adiciona os dados à tabela
        for cliente in relatorio:
            # Formata os valores
            valor_formatado = f"R$ {cliente[1]:.2f}"
            maior_atraso = int(cliente[2])
            
            # Define o status
            if maior_atraso == 0:
                status = "Em dia"
                tag = "em_dia"
            elif maior_atraso <= 30:
                status = "Atraso leve"
                tag = "atraso_leve"
            elif maior_atraso <= 90:
                status = "Atraso moderado"
                tag = "atraso_moderado"
            else:
                status = "Atraso crítico"
                tag = "atraso_critico"
            
            # Adiciona à tabela
            self.treeview.insert(
                "", "end", 
                values=(
                    cliente[0], 
                    valor_formatado, 
                    maior_atraso, 
                    status
                ),
                tags=(tag,)
            )
        
        # Configura cores para os status
        self.treeview.tag_configure("em_dia", background="#ccffcc")
        self.treeview.tag_configure("atraso_leve", background="#ffffcc")
        self.treeview.tag_configure("atraso_moderado", background="#ffcccc")
        self.treeview.tag_configure("atraso_critico", background="#ffaaaa")
    
    def mostrar_resumo(self, frame_resumo):
        """Mostra o resumo do relatório"""
        # Obtém os dados para o resumo
        query = """
            SELECT 
                COUNT(DISTINCT cliente) as total_clientes,
                SUM(valor) as valor_total,
                MAX(
                    CASE 
                        WHEN date(data_vencimento) < date('now') 
                        THEN julianday('now') - julianday(data_vencimento) 
                        ELSE 0 
                    END
                ) as maior_atraso
            FROM contratos
        """
        
        resumo = Database.execute_query(query, fetchone=True)
        
        # Extrai os valores
        total_clientes = resumo[0] or 0
        valor_total = resumo[1] or 0
        maior_atraso = int(resumo[2] or 0)
        
        # Cria o resumo
        frame_stats = tk.Frame(frame_resumo)
        frame_stats.pack(fill="x")
        
        stats = [
            {"texto": "Total de Clientes", "valor": total_clientes},
            {"texto": f"Valor Total", "valor": f"R$ {valor_total:.2f}"},
            {"texto": "Maior Atraso", "valor": f"{maior_atraso} dias"}
        ]
        
        for i, stat in enumerate(stats):
            frame_stat = tk.Frame(frame_stats, bd=1, relief=tk.RAISED, padx=10, pady=10)
            frame_stat.grid(row=0, column=i, padx=10, sticky="nsew")
            
            tk.Label(frame_stat, text=stat["texto"], font=("Arial", 12)).pack()
            tk.Label(frame_stat, text=str(stat["valor"]), font=("Arial", 16, "bold")).pack()
        
        frame_stats.grid_columnconfigure(0, weight=1)
        frame_stats.grid_columnconfigure(1, weight=1)
        frame_stats.grid_columnconfigure(2, weight=1)

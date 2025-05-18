import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
from componentes.menu import Menu
from importador import ImportadorContratos

class TelaImportar:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        
        # Widgets da tela
        self.frame_importar = None
    
    def mostrar(self, **kwargs):
        """Mostra a tela de importação de contratos"""
        # Cria o menu
        Menu(self.app).criar_menu()
        
        # Frame de importação
        self.frame_importar = tk.Frame(self.master, padx=20, pady=20)
        self.frame_importar.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(self.frame_importar, text="Importar Contratos", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Frame para opções de importação
        frame_opcoes = tk.Frame(self.frame_importar)
        frame_opcoes.pack(fill="x", pady=10)
        
        # Opção: Importar de arquivo local
        frame_arquivo = tk.LabelFrame(frame_opcoes, text="Importar de arquivo local", padx=10, pady=10)
        frame_arquivo.pack(fill="x", pady=10)
        
        tk.Label(frame_arquivo, text="Selecione um arquivo CSV para importar").pack(anchor="w")
        
        tk.Button(
            frame_arquivo, 
            text="Selecionar Arquivo", 
            command=self.importar_de_arquivo,
            padx=10, pady=5
        ).pack(pady=10)
    
    def importar_de_arquivo(self):
        """Importa contratos de um arquivo local"""
        # Abre o diálogo para selecionar o arquivo
        arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo CSV",
            filetypes=[("Arquivos CSV", "*.csv")]
        )
        
        if not arquivo:
            return
        
        # Confirma a importação
        if not messagebox.askyesno("Confirmar", f"Deseja importar os contratos do arquivo {os.path.basename(arquivo)}?"):
            return
        
        # Mostra uma janela de progresso
        progress_window = tk.Toplevel(self.app)
        progress_window.title("Importando...")
        progress_window.geometry("300x100")
        progress_window.transient(self.app)
        progress_window.grab_set()
        
        tk.Label(progress_window, text="Importando contratos, aguarde...").pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, mode="indeterminate")
        progress_bar.pack(fill="x", padx=20)
        progress_bar.start()
        
        # Função para executar a importação em uma thread separada
        def executar_importacao():
            try:
                importador = ImportadorContratos(caminho_arquivo=arquivo, usuario_id=self.app.usuario_id)
                sucesso, contratos_importados, erros = importador.importar()
                
                # Atualiza a interface na thread principal
                self.app.after(0, lambda: self.finalizar_importacao(progress_window, sucesso, contratos_importados, erros))
                
            except Exception as e:
                # Atualiza a interface na thread principal
                self.app.after(0, lambda: self.mostrar_erro_importacao(progress_window, str(e)))
        
        # Inicia a thread
        threading.Thread(target=executar_importacao, daemon=True).start()
    
    def finalizar_importacao(self, progress_window, sucesso, contratos_importados, erros):
        """Finaliza o processo de importação (chamado na thread principal)"""
        # Fecha a janela de progresso
        progress_window.destroy()
        
        if sucesso:
            messagebox.showinfo("Sucesso", f"{contratos_importados} contratos importados com sucesso!")
            
            # Se houver erros, mostra em uma janela separada
            if erros:
                self.mostrar_erros_importacao(erros)
        else:
            messagebox.showerror("Erro", f"Erro ao importar contratos: {erros[0] if erros else 'Erro desconhecido'}")
    
    def mostrar_erro_importacao(self, progress_window, mensagem_erro):
        """Mostra um erro de importação (chamado na thread principal)"""
        progress_window.destroy()
        messagebox.showerror("Erro", f"Erro ao importar contratos: {mensagem_erro}")
    
    def mostrar_erros_importacao(self, erros):
        """Mostra os erros de importação em uma janela separada"""
        if not erros:
            return
        
        # Cria uma janela para mostrar os erros
        erros_window = tk.Toplevel(self.app)
        erros_window.title("Erros na Importação")
        erros_window.geometry("600x400")
        erros_window.transient(self.app)
        
        tk.Label(erros_window, text="Os seguintes erros ocorreram durante a importação:", font=("Arial", 12)).pack(pady=10)
        
        # Cria um widget de texto para mostrar os erros
        texto_erros = tk.Text(erros_window, wrap="word", height=15)
        texto_erros.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Adiciona uma barra de rolagem
        scrollbar = tk.Scrollbar(texto_erros)
        scrollbar.pack(side="right", fill="y")
        texto_erros.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=texto_erros.yview)
        
        # Insere os erros no widget de texto
        for erro in erros:
            texto_erros.insert("end", f"• {erro}\n")
        
        texto_erros.config(state="disabled")  # Torna o texto somente leitura
        
        # Botão para fechar a janela
        tk.Button(erros_window, text="Fechar", command=erros_window.destroy).pack(pady=10)

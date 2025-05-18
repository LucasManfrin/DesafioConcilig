import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from componentes.menu import Menu
from database import Database

class TelaContratos:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        
        # Widgets da tela
        self.frame_contratos = None
        self.treeview = None
    
    def mostrar(self, **kwargs):
        """Mostra a lista de contratos"""
        # Cria o menu
        Menu(self.app).criar_menu()
        
        # Frame de contratos
        self.frame_contratos = tk.Frame(self.master, padx=20, pady=20)
        self.frame_contratos.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(self.frame_contratos, text="Contratos", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Frame de filtros
        frame_filtros = tk.LabelFrame(self.frame_contratos, text="Filtros", padx=10, pady=10)
        frame_filtros.pack(fill="x", pady=10)
        
        # Filtro por cliente
        tk.Label(frame_filtros, text="Cliente:").grid(row=0, column=0, padx=5, pady=5)
        cliente_entry = tk.Entry(frame_filtros, width=30)
        cliente_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Filtro por status
        tk.Label(frame_filtros, text="Status:").grid(row=0, column=2, padx=5, pady=5)
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(frame_filtros, textvariable=status_var, width=15)
        status_combo["values"] = ["Todos", "Ativo", "Vencido", "Cancelado"]
        status_combo.current(0)
        status_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Botão de filtrar
        tk.Button(
            frame_filtros, 
            text="Filtrar", 
            command=lambda: self.filtrar_contratos(cliente_entry.get(), status_var.get()),
            padx=10
        ).grid(row=0, column=4, padx=10, pady=5)
        
        # Tabela de contratos
        frame_tabela = tk.Frame(self.frame_contratos)
        frame_tabela.pack(fill="both", expand=True, pady=10)
        
        # Cria a tabela
        colunas = ("id", "numero", "cliente", "valor", "data_inicio", "data_vencimento", "status", "atraso")
        self.treeview = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        
        # Define os cabeçalhos
        self.treeview.heading("id", text="ID")
        self.treeview.heading("numero", text="Número")
        self.treeview.heading("cliente", text="Cliente")
        self.treeview.heading("valor", text="Valor")
        self.treeview.heading("data_inicio", text="Data Início")
        self.treeview.heading("data_vencimento", text="Data Vencimento")
        self.treeview.heading("status", text="Status")
        self.treeview.heading("atraso", text="Atraso (dias)")
        
        # Define as larguras das colunas
        self.treeview.column("id", width=50)
        self.treeview.column("numero", width=100)
        self.treeview.column("cliente", width=200)
        self.treeview.column("valor", width=100)
        self.treeview.column("data_inicio", width=100)
        self.treeview.column("data_vencimento", width=100)
        self.treeview.column("status", width=100)
        self.treeview.column("atraso", width=100)
        
        # Adiciona barras de rolagem
        scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.treeview.yview)
        scrollbar_x = ttk.Scrollbar(frame_tabela, orient="horizontal", command=self.treeview.xview)
        self.treeview.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Posiciona os widgets
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.treeview.pack(side="left", fill="both", expand=True)
        
        # Adiciona menu de contexto para excluir contratos
        self.adicionar_menu_contexto_contratos()
        
        # Carrega os contratos iniciais
        self.filtrar_contratos("", "Todos")
        
        # Botões de ação
        frame_acoes = tk.Frame(self.frame_contratos)
        frame_acoes.pack(fill="x", pady=10)
        
        tk.Button(
            frame_acoes, 
            text="Excluir Contrato Selecionado", 
            command=self.excluir_contrato_selecionado,
            padx=10, pady=5,
            bg="#ff6b6b", fg="white"
        ).pack(side="left", padx=5)
        
        tk.Button(
            frame_acoes, 
            text="Editar Contrato Selecionado", 
            command=self.editar_contrato_selecionado,
            padx=10, pady=5,
            bg="#4dabf7", fg="white"
        ).pack(side="left", padx=5)
        
        # Botão para recalcular todos os atrasos
        tk.Button(
            frame_acoes, 
            text="Recalcular Todos os Atrasos", 
            command=self.recalcular_todos_atrasos,
            padx=10, pady=5,
            bg="#82c91e", fg="white"
        ).pack(side="left", padx=5)
    
    def adicionar_menu_contexto_contratos(self):
        """Adiciona um menu de contexto à tabela de contratos"""
        menu_contexto = tk.Menu(self.app, tearoff=0)
        menu_contexto.add_command(label="Excluir", command=self.excluir_contrato_selecionado)
        menu_contexto.add_command(label="Editar", command=self.editar_contrato_selecionado)
        
        def mostrar_menu_contexto(event):
            # Verifica se há um item selecionado
            if self.treeview.selection():
                menu_contexto.post(event.x_root, event.y_root)
        
        # Vincula o menu de contexto ao botão direito do mouse
        self.treeview.bind("<Button-3>", mostrar_menu_contexto)
    
    def excluir_contrato_selecionado(self):
        """Exclui o contrato selecionado"""
        # Verifica se há um item selecionado
        selecao = self.treeview.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Nenhum contrato selecionado")
            return
        
        # Obtém o ID do contrato selecionado
        item = self.treeview.item(selecao[0])
        contrato_id = item['values'][0]
        
        # Confirma a exclusão
        if not messagebox.askyesno("Confirmar", f"Deseja realmente excluir o contrato #{contrato_id}?"):
            return
        
        try:
            # Exclui o contrato do banco de dados
            query = "DELETE FROM contratos WHERE id = ?"
            Database.execute_query(query, (contrato_id,), commit=True)
            
            # Remove o item da tabela
            self.treeview.delete(selecao[0])
            
            messagebox.showinfo("Sucesso", "Contrato excluído com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir contrato: {str(e)}")
    
    def editar_contrato_selecionado(self):
        """Edita o contrato selecionado"""
        # Verifica se há um item selecionado
        selecao = self.treeview.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Nenhum contrato selecionado")
            return
        
        # Obtém os dados do contrato selecionado
        item = self.treeview.item(selecao[0])
        contrato_id = item['values'][0]
        
        try:
            # Busca os dados completos do contrato
            query = """
                SELECT id, numero_contrato, cliente, valor, data_inicio, data_vencimento, descricao, status
                FROM contratos
                WHERE id = ?
            """
            contrato = Database.execute_query(query, (contrato_id,), fetchone=True)
            
            if not contrato:
                messagebox.showerror("Erro", "Contrato não encontrado")
                return
            
            # Cria uma janela para edição
            self.mostrar_formulario_contrato(contrato)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados do contrato: {str(e)}")
    
    def mostrar_formulario_contrato(self, contrato):
        """Mostra um formulário para edição de contrato"""
        # Cria uma janela para edição
        janela_edicao = tk.Toplevel(self.app)
        janela_edicao.title(f"Editar Contrato #{contrato['id']}")
        janela_edicao.geometry("500x400")
        janela_edicao.transient(self.app)
        janela_edicao.grab_set()
        
        # Frame principal
        frame_form = tk.Frame(janela_edicao, padx=20, pady=20)
        frame_form.pack(fill="both", expand=True)
        
        # Campos do formulário
        tk.Label(frame_form, text="Número do Contrato:").grid(row=0, column=0, sticky="w", pady=5)
        numero_entry = tk.Entry(frame_form, width=30)
        numero_entry.insert(0, contrato['numero_contrato'])
        numero_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(frame_form, text="Cliente:").grid(row=1, column=0, sticky="w", pady=5)
        cliente_entry = tk.Entry(frame_form, width=30)
        cliente_entry.insert(0, contrato['cliente'])
        cliente_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(frame_form, text="Valor:").grid(row=2, column=0, sticky="w", pady=5)
        valor_entry = tk.Entry(frame_form, width=30)
        valor_entry.insert(0, str(contrato['valor']))
        valor_entry.grid(row=2, column=1, pady=5)
        
        tk.Label(frame_form, text="Data de Início (DD/MM/AAAA):").grid(row=3, column=0, sticky="w", pady=5)
        data_inicio_entry = tk.Entry(frame_form, width=30)
        data_inicio = datetime.fromisoformat(contrato['data_inicio'])
        data_inicio_entry.insert(0, data_inicio.strftime("%d/%m/%Y"))
        data_inicio_entry.grid(row=3, column=1, pady=5)
        
        tk.Label(frame_form, text="Data de Vencimento (DD/MM/AAAA):").grid(row=4, column=0, sticky="w", pady=5)
        data_vencimento_entry = tk.Entry(frame_form, width=30)
        data_vencimento = datetime.fromisoformat(contrato['data_vencimento'])
        data_vencimento_entry.insert(0, data_vencimento.strftime("%d/%m/%Y"))
        data_vencimento_entry.grid(row=4, column=1, pady=5)
        
        # Removido o campo de status manual, pois agora será calculado automaticamente
        # Mantemos apenas um label informativo
        tk.Label(frame_form, text="Status:").grid(row=5, column=0, sticky="w", pady=5)
        status_label = tk.Label(frame_form, text=contrato['status'].capitalize() if contrato['status'] else "Ativo")
        status_label.grid(row=5, column=1, sticky="w", pady=5)
        
        tk.Label(frame_form, text="Descrição:").grid(row=6, column=0, sticky="w", pady=5)
        descricao_text = tk.Text(frame_form, width=30, height=5)
        descricao_text.insert("1.0", contrato['descricao'] or "")
        descricao_text.grid(row=6, column=1, pady=5)
        
        # Botões de ação
        frame_botoes = tk.Frame(frame_form)
        frame_botoes.grid(row=7, column=0, columnspan=2, pady=20)
        
        tk.Button(
            frame_botoes,
            text="Salvar",
            command=lambda: self.salvar_contrato(
                contrato['id'],
                numero_entry.get(),
                cliente_entry.get(),
                valor_entry.get(),
                data_inicio_entry.get(),
                data_vencimento_entry.get(),
                descricao_text.get("1.0", "end-1c"),
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
    
    def salvar_contrato(self, contrato_id, numero, cliente, valor_str, data_inicio_str, data_vencimento_str, descricao, janela):
        """Salva as alterações em um contrato"""
        try:
            # Valida os campos obrigatórios
            if not numero or not cliente:
                messagebox.showerror("Erro", "Número do contrato e cliente são obrigatórios")
                return
            
            # Converte o valor para float
            try:
                valor = float(valor_str.replace(',', '.'))
            except:
                messagebox.showerror("Erro", "Valor inválido")
                return
            
            # Converte as datas
            try:
                data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y").date()
            except:
                messagebox.showerror("Erro", "Data de início inválida. Use o formato DD/MM/AAAA")
                return
            
            try:
                data_vencimento = datetime.strptime(data_vencimento_str, "%d/%m/%Y").date()
            except:
                messagebox.showerror("Erro", "Data de vencimento inválida. Use o formato DD/MM/AAAA")
                return
            
            # Calcula o atraso e determina o status
            hoje = date.today()
            atraso = (hoje - data_vencimento).days if hoje > data_vencimento else 0
            
            # Define o status com base no atraso
            status = "vencido" if atraso > 0 else "ativo"
            
            # Verifica se a coluna atraso existe e adiciona se necessário
            try:
                Database.execute_query("SELECT atraso FROM contratos LIMIT 1")
            except:
                try:
                    Database.execute_query("ALTER TABLE contratos ADD COLUMN atraso INTEGER DEFAULT 0", commit=True)
                    print("Coluna atraso adicionada com sucesso")
                except Exception as e:
                    print(f"Erro ao adicionar coluna atraso: {str(e)}")
            
            # Atualiza o contrato no banco de dados
            try:
                query = """
                    UPDATE contratos SET
                    numero_contrato = ?,
                    cliente = ?,
                    valor = ?,
                    data_inicio = ?,
                    data_vencimento = ?,
                    status = ?,
                    descricao = ?,
                    atraso = ?
                    WHERE id = ?
                """
                
                Database.execute_query(
                    query,
                    (
                        numero,
                        cliente,
                        valor,
                        data_inicio.isoformat(),
                        data_vencimento.isoformat(),
                        status,
                        descricao,
                        atraso,
                        contrato_id
                    ),
                    commit=True
                )
            except Exception as e:
                print(f"Erro ao atualizar contrato com atraso: {str(e)}")
                # Se falhar, tenta sem o campo atraso
                query = """
                    UPDATE contratos SET
                    numero_contrato = ?,
                    cliente = ?,
                    valor = ?,
                    data_inicio = ?,
                    data_vencimento = ?,
                    status = ?,
                    descricao = ?
                    WHERE id = ?
                """
                Database.execute_query(
                    query,
                    (
                        numero,
                        cliente,
                        valor,
                        data_inicio.isoformat(),
                        data_vencimento.isoformat(),
                        status,
                        descricao,
                        contrato_id
                    ),
                    commit=True
                )
            
            # Fecha a janela de edição
            janela.destroy()
            
            # Atualiza a tabela
            messagebox.showinfo("Sucesso", "Contrato atualizado com sucesso!")
            
            # Recarrega os contratos na tabela
            self.filtrar_contratos("", "Todos")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar contrato: {str(e)}")
    
    def recalcular_atraso(self, contrato_id):
        """Recalcula o atraso de um contrato específico"""
        try:
            # Busca os dados do contrato
            query = """
                SELECT data_inicio, data_vencimento 
                FROM contratos 
                WHERE id = ?
            """
            resultado = Database.execute_query(query, (contrato_id,), fetchone=True)
            
            if not resultado:
                print(f"Contrato {contrato_id} não encontrado")
                return False
            
            # Calcula o atraso
            try:
                data_vencimento = datetime.fromisoformat(resultado['data_vencimento']).date()
                hoje = date.today()
                atraso = (hoje - data_vencimento).days if hoje > data_vencimento else 0
                
                # Define o status com base no atraso
                status = "vencido" if atraso > 0 else "ativo"
                
                # Atualiza o contrato
                try:
                    # Verifica se a coluna atraso existe
                    try:
                        Database.execute_query("SELECT atraso FROM contratos LIMIT 1")
                    except:
                        Database.execute_query("ALTER TABLE contratos ADD COLUMN atraso INTEGER DEFAULT 0", commit=True)
                        print(f"Coluna atraso adicionada para contrato {contrato_id}")
                    
                    # Atualiza com o campo atraso
                    query = "UPDATE contratos SET status = ?, atraso = ? WHERE id = ?"
                    Database.execute_query(query, (status, atraso, contrato_id), commit=True)
                    print(f"Contrato {contrato_id} atualizado: status={status}, atraso={atraso}")
                except Exception as e:
                    print(f"Erro ao atualizar contrato {contrato_id} com atraso: {str(e)}")
                    # Atualiza apenas o status
                    query = "UPDATE contratos SET status = ? WHERE id = ?"
                    Database.execute_query(query, (status, contrato_id), commit=True)
                    print(f"Contrato {contrato_id} atualizado apenas com status={status}")
                
                return True
            except Exception as e:
                print(f"Erro ao calcular atraso para contrato {contrato_id}: {str(e)}")
                return False
                
        except Exception as e:
            print(f"Erro ao recalcular atraso para contrato {contrato_id}: {str(e)}")
            return False
    
    def recalcular_todos_atrasos(self):
        """Recalcula o atraso de todos os contratos"""
        try:
            # Busca todos os IDs de contratos
            query = "SELECT id FROM contratos"
            contratos = Database.execute_query(query)
            
            if not contratos:
                messagebox.showinfo("Informação", "Nenhum contrato encontrado para recalcular.")
                return
            
            atualizados = 0
            for contrato in contratos:
                contrato_id = contrato[0]
                print(f"Recalculando contrato {contrato_id}...")
                if self.recalcular_atraso(contrato_id):
                    atualizados += 1
            
            # Recarrega a tabela
            self.filtrar_contratos("", "Todos")
            
            messagebox.showinfo("Sucesso", f"{atualizados} contratos atualizados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao recalcular atrasos: {str(e)}")
    
    def filtrar_contratos(self, cliente, status):
        """Filtra os contratos de acordo com os critérios do usuário logado"""
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        query = """
            SELECT c.id, c.numero_contrato, c.cliente, c.valor, 
                c.data_inicio, c.data_vencimento, c.status
            FROM contratos c
            JOIN arquivos_importados a ON c.arquivo_id = a.id
            WHERE a.usuario_id = ?
        """
        params = [self.app.usuario_id]
        
        if cliente:
            query += " AND c.cliente LIKE ?"
            params.append(f"%{cliente}%")
        
        if status != "Todos":
            query += " AND c.status LIKE ?"
            params.append(f"%{status.lower()}%")
        
        query += " ORDER BY c.id DESC"
        
        try:
            contratos = Database.execute_query(query, params)
            hoje = date.today()
            
            for contrato in contratos:
                try:
                    data_inicio = datetime.strptime(contrato[4], '%Y-%m-%d').date()
                except Exception as e:
                    print(f"Erro ao converter data_inicio: {str(e)}")
                    data_inicio = datetime.now().date()
                    
                try:
                    data_vencimento = datetime.strptime(contrato[5], '%Y-%m-%d').date()
                except Exception as e:
                    print(f"Erro ao converter data_vencimento: {str(e)}")
                    data_vencimento = datetime.now().date()
                
                atraso = (hoje - data_vencimento).days if hoje > data_vencimento else 0
                status_correto = "Vencido" if atraso > 0 else "Ativo"
                
                if contrato[6] and contrato[6].lower() != status_correto.lower():
                    try:
                        update_query = "UPDATE contratos SET status = ? WHERE id = ?"
                        Database.execute_query(update_query, (status_correto.lower(), contrato[0]), commit=True)
                        print(f"Status do contrato {contrato[0]} atualizado para {status_correto}")
                    except Exception as e:
                        print(f"Erro ao atualizar status do contrato {contrato[0]}: {str(e)}")
                
                valor_formatado = f"R$ {contrato[3]:.2f}"
                data_inicio_formatada = data_inicio.strftime("%d/%m/%Y")
                data_vencimento_formatada = data_vencimento.strftime("%d/%m/%Y")
                tag = "atraso" if atraso > 0 else ""
                
                self.treeview.insert(
                    "", "end", 
                    values=(
                        contrato[0], 
                        contrato[1], 
                        contrato[2], 
                        valor_formatado, 
                        data_inicio_formatada, 
                        data_vencimento_formatada, 
                        status_correto,
                        atraso if atraso > 0 else "Em dia"
                    ),
                    tags=(tag,)
                )
            
            self.treeview.tag_configure("atraso", background="#ffcccc")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao filtrar contratos: {str(e)}")

import pandas as pd
import requests
import sqlite3
from io import StringIO
from datetime import datetime
from database import Database

class ImportadorContratos:
    """Classe para importar contratos do arquivo CSV"""
    
    def __init__(self, url=None, caminho_arquivo=None, usuario_id=1):
        """Inicializa o importador com a URL ou caminho do arquivo e ID do usuário"""
        self.url = url
        self.caminho_arquivo = caminho_arquivo
        self.usuario_id = usuario_id
        self.nome_arquivo = "contratos.csv" if url else (caminho_arquivo.split("/")[-1] if caminho_arquivo else "arquivo_local.csv")
    
    def carregar_dados(self):
        """Carrega os dados do arquivo ou URL e retorna um DataFrame"""
        try:
            df = None
            
            if self.url:
                print(f"Carregando dados da URL: {self.url}")
                # Carrega dados da URL
                response = requests.get(self.url)
                response.raise_for_status()
                
                # Tenta diferentes codificações
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252']
                
                for encoding in encodings:
                    try:
                        content = StringIO(response.content.decode(encoding))
                        df = pd.read_csv(content, sep=';')
                        print(f"Arquivo carregado com sucesso usando codificação {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        print(f"Erro ao processar CSV com codificação {encoding}: {str(e)}")
                
                # Se chegou aqui e df ainda é None, nenhuma codificação funcionou
                if df is None:
                    raise Exception("Não foi possível decodificar o arquivo com as codificações tentadas")
                
            elif self.caminho_arquivo:
                print(f"Carregando dados do arquivo local: {self.caminho_arquivo}")
                # Tenta diferentes codificações para o arquivo local
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252']
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(self.caminho_arquivo, sep=';', encoding=encoding)
                        print(f"Arquivo carregado com sucesso usando codificação {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        print(f"Erro ao processar CSV com codificação {encoding}: {str(e)}")
                
                # Se chegou aqui e df ainda é None, nenhuma codificação funcionou
                if df is None:
                    raise Exception("Não foi possível decodificar o arquivo com as codificações tentadas")
            else:
                raise Exception("URL ou caminho do arquivo não fornecido")
            
            # Imprime informações sobre o DataFrame para debug
            print(f"Colunas encontradas no arquivo: {df.columns.tolist()}")
            print(f"Total de linhas no arquivo: {len(df)}")
            print(f"Primeiras 5 linhas do arquivo:")
            print(df.head())
            
            return df
            
        except Exception as e:
            raise Exception(f"Erro ao carregar dados: {str(e)}")
    
    def registrar_arquivo(self):
        """Registra o arquivo importado no banco de dados"""
        try:
            data_importacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Registrando arquivo: {self.nome_arquivo}, data: {data_importacao}, usuário: {self.usuario_id}")

            query = """
                INSERT INTO arquivos_importados (nome_arquivo, data_importacao, usuario_id) 
                VALUES (?, ?, ?)
            """
            # CORREÇÃO: Ordem correta dos parâmetros para corresponder à query
            Database.execute_query(query, (self.nome_arquivo, data_importacao, self.usuario_id), commit=True)
            print("Arquivo registrado com sucesso, obtendo ID...")
            
            # Obtém o ID do arquivo inserido
            query = "SELECT last_insert_rowid()"
            result = Database.execute_query(query, fetchone=True)
            arquivo_id = result[0]
            print(f"ID do arquivo registrado: {arquivo_id}")
            return arquivo_id
        except Exception as e:
            print(f"ERRO ao registrar arquivo: {str(e)}")
            raise Exception(f"Erro ao registrar arquivo: {str(e)}")
    
    def importar_contratos(self, df, arquivo_id):
        """Importa os contratos do DataFrame para o banco de dados"""
        contratos_importados = 0
        erros = []
        
        print(f"Iniciando importação de {len(df)} contratos para o arquivo ID: {arquivo_id}")
        
        # Obtém uma conexão única para todas as operações
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        try:
            # Para cada linha no DataFrame
            for idx, row in df.iterrows():
                try:
                    # Obtém os valores das colunas específicas deste arquivo
                    numero_contrato = str(row.get('Contrato', '')).strip()
                    cliente = str(row.get('Nome', '')).strip()
                    cpf = str(row.get('CPF', '')).strip()
                    produto = str(row.get('Produto', '')).strip()
                    
                    # Converte o valor para float (formato brasileiro com vírgula)
                    valor_str = str(row.get('Valor', '0')).replace('.', '').replace(',', '.').strip()
                    try:
                        valor = float(valor_str)
                    except:
                        valor = 0.0
                    
                    # Processa a data de vencimento (formato DD/MM/YYYY)
                    data_vencimento_str = str(row.get('Vencimento', '31/12/2023'))
                    
                    try:
                        data_vencimento = datetime.strptime(data_vencimento_str, '%d/%m/%Y').date()
                    except:
                        data_vencimento = datetime.strptime('31/12/2023', '%d/%m/%Y').date()
                    
                    # Usa a data atual como data de início
                    data_inicio = datetime.now().date()
                    
                    # Cria uma descrição com o produto e CPF
                    descricao = f"Produto: {produto}, CPF: {cpf}"
                    
                    print(f"Processando contrato {idx+1}/{len(df)}: {numero_contrato}, Cliente: {cliente}, Valor: {valor}")
                    
                    # Verifica se o número do contrato e o cliente não estão vazios
                    if numero_contrato and cliente:
                        # CORREÇÃO: Primeiro tenta inserir, se falhar, então atualiza
                        try:
                            query = """
                                INSERT INTO contratos 
                                (numero_contrato, cliente, valor, data_inicio, data_vencimento, descricao, arquivo_id, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, 'Ativo')
                            """
                            cursor.execute(
                                query,
                                (
                                    numero_contrato,
                                    cliente,
                                    valor,
                                    data_inicio.isoformat(),
                                    data_vencimento.isoformat(),
                                    descricao,
                                    arquivo_id
                                )
                            )
                            contratos_importados += 1
                            print(f"Contrato {numero_contrato} importado com sucesso")
                        except sqlite3.IntegrityError:
                            # Se o contrato já existe (violação de UNIQUE), atualiza
                            query = """
                                UPDATE contratos SET
                                cliente = ?,
                                valor = ?,
                                data_inicio = ?,
                                data_vencimento = ?,
                                descricao = ?,
                                arquivo_id = ?,
                                status = 'Ativo'
                                WHERE numero_contrato = ?
                            """
                            cursor.execute(
                                query,
                                (
                                    cliente,
                                    valor,
                                    data_inicio.isoformat(),
                                    data_vencimento.isoformat(),
                                    descricao,
                                    arquivo_id,
                                    numero_contrato
                                )
                            )
                            contratos_importados += 1
                            print(f"Contrato {numero_contrato} atualizado com sucesso")
                    else:
                        print(f"Contrato ignorado: número ou cliente vazio. Número: '{numero_contrato}', Cliente: '{cliente}'")
                except Exception as e:
                    erro_msg = f"Erro na linha {idx+1}: {str(e)}"
                    print(erro_msg)
                    erros.append(erro_msg)
            
            # Commit explícito após processar todos os contratos
            conn.commit()
            print(f"Commit realizado com sucesso! {contratos_importados} contratos importados.")
            
            # Verificar se os contratos foram realmente inseridos
            cursor.execute("SELECT COUNT(*) FROM contratos")
            count = cursor.fetchone()[0]
            print(f"Total de contratos no banco após importação: {count}")
            
            return contratos_importados, erros
        except Exception as e:
            conn.rollback()
            print(f"ERRO durante importação, realizando rollback: {str(e)}")
            raise e
        finally:
            cursor.close()
            conn.close()
            print("Conexão com o banco de dados fechada.")
    
    def importar(self):
        """Executa o processo completo de importação"""
        try:
            print("\n=== INICIANDO PROCESSO DE IMPORTAÇÃO ===")
            
            # Carrega os dados
            print("\n--- Carregando dados do arquivo ---")
            df = self.carregar_dados()
            print(f"Dados carregados com sucesso: {len(df)} linhas encontradas")
            
            # Registra o arquivo
            print("\n--- Registrando arquivo no banco de dados ---")
            arquivo_id = self.registrar_arquivo()
            print(f"Arquivo registrado com ID: {arquivo_id}")
            
            # Importa os contratos
            print("\n--- Importando contratos ---")
            contratos_importados, erros = self.importar_contratos(df, arquivo_id)
            print(f"\n=== IMPORTAÇÃO CONCLUÍDA: {contratos_importados} contratos importados, {len(erros)} erros ===")
            
            # Verificar se os contratos foram realmente inseridos
            print("\n--- Verificando contratos inseridos ---")
            query = "SELECT COUNT(*) FROM contratos"
            result = Database.execute_query(query, fetchone=True)
            total_contratos = result[0] if result else 0
            print(f"Total de contratos no banco de dados: {total_contratos}")
            
            return True, contratos_importados, erros
        except Exception as e:
            print(f"\n!!! ERRO CRÍTICO NA IMPORTAÇÃO: {str(e)} !!!")
            return False, 0, [str(e)]
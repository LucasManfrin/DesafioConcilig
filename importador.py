import pandas as pd
import requests
import sqlite3
from io import StringIO
from datetime import datetime
from database import Database

class ImportadorContratos:
    def __init__(self, url=None, caminho_arquivo=None, usuario_id=1):
        self.url = url
        self.caminho_arquivo = caminho_arquivo
        self.usuario_id = usuario_id
        self.nome_arquivo = "contratos.csv" if url else (caminho_arquivo.split("/")[-1] if caminho_arquivo else "arquivo_local.csv")

    def carregar_dados(self):
        try:
            df = None
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252']

            if self.url:
                response = requests.get(self.url)
                response.raise_for_status()

                for encoding in encodings:
                    try:
                        content = StringIO(response.content.decode(encoding))
                        df = pd.read_csv(content, sep=';')
                        print(f"Arquivo carregado com codificação: {encoding}")
                        break
                    except Exception:
                        continue
            elif self.caminho_arquivo:
                for encoding in encodings:
                    try:
                        df = pd.read_csv(self.caminho_arquivo, sep=';', encoding=encoding)
                        print(f"Arquivo local carregado com codificação: {encoding}")
                        break
                    except Exception:
                        continue
            else:
                raise Exception("URL ou caminho de arquivo não informado.")

            if df is None:
                raise Exception("Não foi possível carregar o arquivo com as codificações tentadas.")

            return df

        except Exception as e:
            raise Exception(f"Erro ao carregar dados: {str(e)}")

    def registrar_arquivo(self):
        try:
            data_importacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO arquivos_importados (nome_arquivo, data_importacao, usuario_id)
                VALUES (?, ?, ?)
            """, (self.nome_arquivo, data_importacao, self.usuario_id))
            
            arquivo_id = cursor.lastrowid
            conn.commit()
            return arquivo_id
        except Exception as e:
            raise Exception(f"Erro ao registrar arquivo: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def calcular_atraso(self, data_vencimento):
        hoje = datetime.today().date()
        if data_vencimento < hoje:
            return (hoje - data_vencimento).days
        return 0

    def importar_contratos(self, df, arquivo_id):
        contratos_importados = 0
        erros = []

        conn = Database.get_connection()
        cursor = conn.cursor()

        try:
            for idx, row in df.iterrows():
                try:
                    numero_contrato = str(row.get('Contrato', '')).strip()
                    cliente = str(row.get('Nome', '')).strip()
                    cpf = str(row.get('CPF', '')).strip()
                    produto = str(row.get('Produto', '')).strip()
                    valor_str = str(row.get('Valor', '0')).replace('.', '').replace(',', '.').strip()

                    try:
                        valor = float(valor_str)
                    except:
                        valor = 0.0

                    data_vencimento_str = str(row.get('Vencimento', '31/12/2023'))
                    try:
                        data_vencimento = datetime.strptime(data_vencimento_str, '%d/%m/%Y').date()
                    except:
                        data_vencimento = datetime.strptime('31/12/2023', '%d/%m/%Y').date()

                    atraso = self.calcular_atraso(data_vencimento)
                    data_inicio = datetime.now().date()
                    descricao = f"Produto: {produto}, CPF: {cpf}"

                    if numero_contrato and cliente:
                        try:
                            cursor.execute("""
                                INSERT INTO contratos (
                                    numero_contrato, cliente, valor, data_inicio, data_vencimento,
                                    descricao, arquivo_id, usuario_id, status, atraso
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Ativo', ?)
                            """, (
                                numero_contrato, cliente, valor,
                                data_inicio.isoformat(), data_vencimento.isoformat(),
                                descricao, arquivo_id, self.usuario_id, atraso
                            ))
                            contratos_importados += 1
                        except sqlite3.IntegrityError:
                            cursor.execute("""
                                UPDATE contratos SET
                                    cliente = ?,
                                    valor = ?,
                                    data_inicio = ?,
                                    data_vencimento = ?,
                                    descricao = ?,
                                    arquivo_id = ?,
                                    usuario_id = ?,
                                    status = 'Ativo',
                                    atraso = ?
                                WHERE numero_contrato = ?
                            """, (
                                cliente, valor, data_inicio.isoformat(),
                                data_vencimento.isoformat(), descricao,
                                arquivo_id, self.usuario_id, atraso, numero_contrato
                            ))
                            contratos_importados += 1
                    else:
                        erros.append(f"Contrato ignorado na linha {idx+1}: campos obrigatórios vazios.")
                except Exception as e:
                    erros.append(f"Erro na linha {idx+1}: {str(e)}")

            conn.commit()
            return contratos_importados, erros
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro na importação: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def importar(self):
        try:
            print("=== Iniciando processo de importação ===")
            df = self.carregar_dados()
            print(f"{len(df)} contratos carregados.")
            arquivo_id = self.registrar_arquivo()
            print(f"Arquivo registrado com ID {arquivo_id}")
            contratos_importados, erros = self.importar_contratos(df, arquivo_id)
            print(f"{contratos_importados} contratos importados com sucesso.")
            if erros:
                print(f"{len(erros)} erros encontrados.")
            return True, contratos_importados, erros
        except Exception as e:
            print(f"Erro crítico: {str(e)}")
            return False, 0, [str(e)]

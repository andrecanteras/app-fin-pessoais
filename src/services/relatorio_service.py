import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from src.models.transacao import Transacao
from src.models.categoria import Categoria
from src.models.conta import Conta

class RelatorioService:
    """Serviço para geração de relatórios financeiros."""
    
    @staticmethod
    def gerar_fluxo_caixa(data_inicio, data_fim):
        """Gera um relatório de fluxo de caixa para o período especificado."""
        try:
            # Obter todas as transações do período
            filtros = {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'ordenacao': 'data_transacao ASC'
            }
            transacoes = Transacao.listar_todas(filtros)
            
            # Criar DataFrame para análise
            dados = []
            for t in transacoes:
                categoria_nome = t.categoria.nome if t.categoria else "Sem categoria"
                conta_nome = t.conta.nome if t.conta else "Sem conta"
                
                dados.append({
                    'data': t.data_transacao,
                    'descricao': t.descricao,
                    'categoria': categoria_nome,
                    'conta': conta_nome,
                    'receita': t.valor if t.tipo == 'R' else 0,
                    'despesa': t.valor if t.tipo == 'D' else 0
                })
            
            if not dados:
                return {
                    'dados': [],
                    'resumo': {
                        'total_receitas': 0,
                        'total_despesas': 0,
                        'saldo_periodo': 0
                    }
                }
            
            df = pd.DataFrame(dados)
            
            # Calcular saldo acumulado
            df['saldo_diario'] = df['receita'] - df['despesa']
            df['saldo_acumulado'] = df['saldo_diario'].cumsum()
            
            # Resumo do período
            resumo = {
                'total_receitas': df['receita'].sum(),
                'total_despesas': df['despesa'].sum(),
                'saldo_periodo': df['receita'].sum() - df['despesa'].sum()
            }
            
            # Converter para formato de lista para retorno
            resultado = df.to_dict('records')
            
            return {
                'dados': resultado,
                'resumo': resumo
            }
            
        except Exception as e:
            print(f"Erro ao gerar relatório de fluxo de caixa: {e}")
            return {
                'dados': [],
                'resumo': {
                    'total_receitas': 0,
                    'total_despesas': 0,
                    'saldo_periodo': 0
                }
            }
    
    @staticmethod
    def gerar_resumo_por_categoria(data_inicio, data_fim, tipo):
        """Gera um resumo de gastos ou receitas por categoria."""
        try:
            # Obter resumo por categoria
            resumo = Transacao.obter_resumo_por_categoria(data_inicio, data_fim, tipo)
            
            # Calcular percentuais
            total = sum(item['total'] for item in resumo)
            
            if total > 0:
                for item in resumo:
                    item['percentual'] = (item['total'] / total) * 100
            else:
                for item in resumo:
                    item['percentual'] = 0
            
            return resumo
            
        except Exception as e:
            print(f"Erro ao gerar resumo por categoria: {e}")
            return []
    
    @staticmethod
    def gerar_grafico_pizza_categorias(data_inicio, data_fim, tipo, caminho_arquivo=None):
        """Gera um gráfico de pizza com a distribuição por categorias."""
        try:
            resumo = RelatorioService.gerar_resumo_por_categoria(data_inicio, data_fim, tipo)
            
            if not resumo:
                return False
            
            # Preparar dados para o gráfico
            labels = [item['nome_categoria'] for item in resumo]
            valores = [item['total'] for item in resumo]
            
            # Criar gráfico
            plt.figure(figsize=(10, 7))
            plt.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            
            titulo = "Distribuição de Receitas por Categoria" if tipo == 'R' else "Distribuição de Despesas por Categoria"
            plt.title(titulo)
            
            # Salvar ou mostrar o gráfico
            if caminho_arquivo:
                plt.savefig(caminho_arquivo)
                plt.close()
                return True
            else:
                plt.show()
                return True
                
        except Exception as e:
            print(f"Erro ao gerar gráfico de pizza: {e}")
            return False
    
    @staticmethod
    def gerar_grafico_evolucao_saldo(data_inicio, data_fim, caminho_arquivo=None):
        """Gera um gráfico de linha mostrando a evolução do saldo no período."""
        try:
            # Obter todas as transações do período
            filtros = {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'ordenacao': 'data_transacao ASC'
            }
            transacoes = Transacao.listar_todas(filtros)
            
            if not transacoes:
                return False
            
            # Criar DataFrame para análise
            dados = []
            for t in transacoes:
                dados.append({
                    'data': t.data_transacao,
                    'valor': t.valor if t.tipo == 'R' else -t.valor  # Receitas positivas, despesas negativas
                })
            
            df = pd.DataFrame(dados)
            
            # Agrupar por data e somar valores
            df_agrupado = df.groupby('data')['valor'].sum().reset_index()
            
            # Calcular saldo acumulado
            df_agrupado['saldo_acumulado'] = df_agrupado['valor'].cumsum()
            
            # Criar gráfico
            plt.figure(figsize=(12, 6))
            plt.plot(df_agrupado['data'], df_agrupado['saldo_acumulado'], marker='o')
            plt.title('Evolução do Saldo')
            plt.xlabel('Data')
            plt.ylabel('Saldo (R$)')
            plt.grid(True)
            
            # Formatar eixo Y com valores monetários
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'R$ {x:,.2f}'))
            
            # Rotacionar datas no eixo X para melhor visualização
            plt.xticks(rotation=45)
            
            # Ajustar layout
            plt.tight_layout()
            
            # Salvar ou mostrar o gráfico
            if caminho_arquivo:
                plt.savefig(caminho_arquivo)
                plt.close()
                return True
            else:
                plt.show()
                return True
                
        except Exception as e:
            print(f"Erro ao gerar gráfico de evolução de saldo: {e}")
            return False
    
    @staticmethod
    def gerar_comparativo_mensal(ano, tipo, caminho_arquivo=None):
        """Gera um gráfico de barras comparando receitas ou despesas por mês."""
        try:
            # Preparar dados para todos os meses do ano
            meses = []
            valores = []
            
            for mes in range(1, 13):
                # Definir primeiro e último dia do mês
                if mes == 12:
                    data_inicio = datetime(ano, mes, 1)
                    data_fim = datetime(ano + 1, 1, 1) - timedelta(days=1)
                else:
                    data_inicio = datetime(ano, mes, 1)
                    data_fim = datetime(ano, mes + 1, 1) - timedelta(days=1)
                
                # Obter resumo do período
                resumo = Transacao.obter_resumo_por_periodo(data_inicio, data_fim)
                
                # Adicionar aos dados
                meses.append(data_inicio.strftime('%b'))  # Nome abreviado do mês
                if tipo == 'R':
                    valores.append(resumo['total_receitas'])
                else:
                    valores.append(resumo['total_despesas'])
            
            # Criar gráfico
            plt.figure(figsize=(12, 6))
            
            # Definir cores
            cor = 'green' if tipo == 'R' else 'red'
            
            # Criar barras
            plt.bar(meses, valores, color=cor)
            
            # Adicionar rótulos e título
            titulo = f"Receitas Mensais - {ano}" if tipo == 'R' else f"Despesas Mensais - {ano}"
            plt.title(titulo)
            plt.xlabel('Mês')
            plt.ylabel('Valor (R$)')
            
            # Formatar eixo Y com valores monetários
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'R$ {x:,.2f}'))
            
            # Adicionar valores sobre as barras
            for i, valor in enumerate(valores):
                plt.text(i, valor + (max(valores) * 0.01), f'R$ {valor:,.2f}', 
                         ha='center', va='bottom', rotation=45, fontsize=8)
            
            # Ajustar layout
            plt.tight_layout()
            
            # Salvar ou mostrar o gráfico
            if caminho_arquivo:
                plt.savefig(caminho_arquivo)
                plt.close()
                return True
            else:
                plt.show()
                return True
                
        except Exception as e:
            print(f"Erro ao gerar comparativo mensal: {e}")
            return False
from datetime import datetime
import locale

# Configurar localização para formato brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass  # Usar configuração padrão

class CashCalculations:
    def __init__(self, db_manager):
        """Inicializa calculadora de caixa"""
        self.db_manager = db_manager
    
    def calculate_partial_result(self, movimentacao_id):
        """
        Calcula resultado parcial do caixa individual
        Fórmula: (Suprimento Abertura + Vendas Sankhya + Suprimento Adicional) - (Sangria + Despesas) - Fechamento
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    suprimento_abertura,
                    sangria,
                    despesas,
                    suprimento_caixa,
                    fechamento_caixa,
                    vendas_sankhya
                FROM movimentacoes_diarias
                WHERE id = ?
            ''', (movimentacao_id,))
            
            data = cursor.fetchone()
            
            if not data:
                return 0.0, {}
            
            # Extrair valores (tratar None como 0)
            suprimento_abertura = data[0] or 0
            sangria = data[1] or 0
            despesas = data[2] or 0
            suprimento_caixa = data[3] or 0
            fechamento_caixa = data[4] or 0
            vendas_sankhya = data[5] or 0
            
            # Calcular valores esperados
            total_entradas = suprimento_abertura + vendas_sankhya + suprimento_caixa
            total_saidas = sangria + despesas
            valor_esperado = total_entradas - total_saidas
            
            # Resultado: diferença entre esperado e fechamento
            resultado = valor_esperado - fechamento_caixa
            
            # Detalhamento para relatório
            detalhes = {
                'suprimento_abertura': suprimento_abertura,
                'vendas_sankhya': vendas_sankhya,
                'suprimento_caixa': suprimento_caixa,
                'sangria': sangria,
                'despesas': despesas,
                'fechamento_caixa': fechamento_caixa,
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'valor_esperado': valor_esperado,
                'resultado': resultado
            }
            
            return resultado, detalhes
            
        except Exception as e:
            print(f"Erro ao calcular resultado parcial: {e}")
            return 0.0, {}
        finally:
            conn.close()
    
    def calculate_general_result(self, movimentacao_ids, conta_7, conta_19):
        """
        Calcula resultado do caixa geral
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar dados de todas as movimentações
            placeholders = ','.join(['?' for _ in movimentacao_ids])
            cursor.execute(f'''
                SELECT 
                    SUM(COALESCE(suprimento_abertura, 0)) as total_suprimento_abertura,
                    SUM(COALESCE(sangria, 0)) as total_sangria,
                    SUM(COALESCE(despesas, 0)) as total_despesas,
                    SUM(COALESCE(suprimento_caixa, 0)) as total_suprimento_caixa,
                    SUM(COALESCE(fechamento_caixa, 0)) as total_fechamento,
                    SUM(COALESCE(vendas_sankhya, 0)) as total_vendas,
                    COUNT(*) as total_movimentacoes
                FROM movimentacoes_diarias
                WHERE id IN ({placeholders})
            ''', movimentacao_ids)
            
            totals = cursor.fetchone()
            
            if not totals:
                return 0.0, {}
            
            # Extrair totais
            total_suprimento_abertura = totals[0] or 0
            total_sangria = totals[1] or 0
            total_despesas = totals[2] or 0
            total_suprimento_caixa = totals[3] or 0
            total_fechamento = totals[4] or 0
            total_vendas = totals[5] or 0
            total_movimentacoes = totals[6] or 0
            
            # Calcular somatório das contas
            somatorio_contas = conta_7 + conta_19
            
            # Calcular totais de entrada e saída
            total_entradas = total_suprimento_abertura + total_vendas + total_suprimento_caixa + somatorio_contas
            total_saidas = total_sangria + total_despesas + total_fechamento
            
            # Resultado geral
            resultado_geral = total_entradas - total_saidas
            
            # Detalhamento
            detalhes = {
                'total_movimentacoes': total_movimentacoes,
                'total_suprimento_abertura': total_suprimento_abertura,
                'total_vendas': total_vendas,
                'total_suprimento_caixa': total_suprimento_caixa,
                'conta_7': conta_7,
                'conta_19': conta_19,
                'somatorio_contas': somatorio_contas,
                'total_sangria': total_sangria,
                'total_despesas': total_despesas,
                'total_fechamento': total_fechamento,
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'resultado_geral': resultado_geral
            }
            
            return resultado_geral, detalhes
            
        except Exception as e:
            print(f"Erro ao calcular resultado geral: {e}")
            return 0.0, {}
        finally:
            conn.close()
    
    def get_movement_details(self, movimentacao_id):
        """Obtém detalhes completos de uma movimentação"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Dados principais da movimentação
            cursor.execute('''
                SELECT 
                    m.id,
                    c.nome as caixa_nome,
                    u.nome as operador_nome,
                    m.data_movimentacao,
                    m.suprimento_abertura,
                    m.sangria,
                    m.despesas,
                    m.suprimento_caixa,
                    m.fechamento_caixa,
                    m.vendas_sankhya,
                    m.resultado_parcial,
                    m.observacoes,
                    m.data_criacao,
                    m.data_atualizacao
                FROM movimentacoes_diarias m
                JOIN caixas c ON m.caixa_id = c.id
                JOIN usuarios u ON m.usuario_id = u.id
                WHERE m.id = ?
            ''', (movimentacao_id,))
            
            movement_data = cursor.fetchone()
            
            if not movement_data:
                return None
            
            # Buscar detalhes das despesas
            cursor.execute('''
                SELECT valor, descricao, data_lancamento
                FROM despesas_detalhes
                WHERE movimentacao_id = ?
                ORDER BY data_lancamento
            ''', (movimentacao_id,))
            
            expenses_details = cursor.fetchall()
            
            # Organizar dados
            details = {
                'id': movement_data[0],
                'caixa_nome': movement_data[1],
                'operador_nome': movement_data[2],
                'data_movimentacao': movement_data[3],
                'suprimento_abertura': movement_data[4] or 0,
                'sangria': movement_data[5] or 0,
                'despesas': movement_data[6] or 0,
                'suprimento_caixa': movement_data[7] or 0,
                'fechamento_caixa': movement_data[8] or 0,
                'vendas_sankhya': movement_data[9] or 0,
                'resultado_parcial': movement_data[10] or 0,
                'observacoes': movement_data[11],
                'data_criacao': movement_data[12],
                'data_atualizacao': movement_data[13],
                'despesas_detalhes': []
            }
            
            # Adicionar detalhes das despesas
            for expense in expenses_details:
                details['despesas_detalhes'].append({
                    'valor': expense[0],
                    'descricao': expense[1] or 'Sem descrição',
                    'data_lancamento': expense[2]
                })
            
            return details
            
        except Exception as e:
            print(f"Erro ao obter detalhes da movimentação: {e}")
            return None
        finally:
            conn.close()
    
    def get_daily_summary(self, target_date):
        """Obtém resumo do dia específico"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_movimentacoes,
                    COUNT(CASE WHEN status_fluxo = 'finalizado' THEN 1 END) as finalizadas,
                    SUM(COALESCE(suprimento_abertura, 0)) as total_suprimento,
                    SUM(COALESCE(vendas_sankhya, 0)) as total_vendas,
                    SUM(COALESCE(sangria, 0)) as total_sangria,
                    SUM(COALESCE(despesas, 0)) as total_despesas,
                    SUM(COALESCE(fechamento_caixa, 0)) as total_fechamento,
                    SUM(COALESCE(resultado_parcial, 0)) as resultado_total
                FROM movimentacoes_diarias
                WHERE data_movimentacao = ?
            ''', (target_date,))
            
            summary = cursor.fetchone()
            
            if summary:
                return {
                    'data': target_date,
                    'total_movimentacoes': summary[0] or 0,
                    'finalizadas': summary[1] or 0,
                    'pendentes': (summary[0] or 0) - (summary[1] or 0),
                    'total_suprimento_abertura': summary[2] or 0,
                    'total_vendas': summary[3] or 0,
                    'total_sangria': summary[4] or 0,
                    'total_despesas': summary[5] or 0,
                    'total_fechamento': summary[6] or 0,
                    'resultado_total': summary[7] or 0
                }
            else:
                return {
                    'data': target_date,
                    'total_movimentacoes': 0,
                    'finalizadas': 0,
                    'pendentes': 0,
                    'total_suprimento_abertura': 0,
                    'total_vendas': 0,
                    'total_sangria': 0,
                    'total_despesas': 0,
                    'total_fechamento': 0,
                    'resultado_total': 0
                }
            
        except Exception as e:
            print(f"Erro ao obter resumo diário: {e}")
            return None
        finally:
            conn.close()
    
    def format_currency(self, value):
        """Formata valor como moeda brasileira"""
        if value is None:
            value = 0
        
        try:
            return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            return "R$ 0,00"
    
    def format_result_text(self, result_value):
        """Formata texto do resultado (SOBRA/FALTA/EXATO)"""
        if result_value > 0:
            return f"SOBRA: {self.format_currency(result_value)}"
        elif result_value < 0:
            return f"FALTA: {self.format_currency(abs(result_value))}"
        else:
            return "EXATO: R$ 0,00"
    
    def validate_movement_data(self, movement_data):
        """Valida dados de movimentação"""
        errors = []
        
        # Verificar campos obrigatórios
        if not movement_data.get('suprimento_abertura') or movement_data['suprimento_abertura'] <= 0:
            errors.append("Suprimento de abertura deve ser maior que zero")
        
        if not movement_data.get('fechamento_caixa') and movement_data['fechamento_caixa'] != 0:
            errors.append("Valor de fechamento é obrigatório")
        
        if not movement_data.get('vendas_sankhya') and movement_data['vendas_sankhya'] != 0:
            errors.append("Valor de vendas Sankhya é obrigatório")
        
        # Verificar valores negativos onde não devem existir
        negative_fields = ['suprimento_abertura', 'suprimento_caixa', 'vendas_sankhya']
        for field in negative_fields:
            if movement_data.get(field) and movement_data[field] < 0:
                errors.append(f"{field.replace('_', ' ').title()} não pode ser negativo")
        
        return errors
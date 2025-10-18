from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus.flowables import HRFlowable
from datetime import datetime
import os

class PDFGenerator:
    def __init__(self):
        """Inicializa o gerador de PDF"""
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configura estilos customizados"""
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Centralizado
            textColor=colors.darkblue
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.darkblue
        ))
        
        # Estilo para texto de resultado
        self.styles.add(ParagraphStyle(
            name='ResultText',
            parent=self.styles['Normal'],
            fontSize=16,
            spaceAfter=10,
            alignment=1,  # Centralizado
            textColor=colors.darkgreen
        ))
    
    def format_currency(self, value):
        """Formata valor como moeda brasileira"""
        if value is None:
            value = 0
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def generate_cashier_report(self, movimentacao_id, db_manager):
        """Gera relatório PDF do caixa individual"""
        from utils.calculations import CashCalculations
        
        calc = CashCalculations(db_manager)
        details = calc.get_movement_details(movimentacao_id)
        
        if not details:
            raise Exception("Movimentação não encontrada")
        
        # Calcular resultado
        resultado, calc_details = calc.calculate_partial_result(movimentacao_id)
        
        # Nome do arquivo
        data_str = details['data_movimentacao']
        if isinstance(data_str, str):
            data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
        else:
            data_obj = data_str
        
        filename = f"reports/Caixa_{details['caixa_nome'].replace(' ', '_')}_{data_obj.strftime('%Y%m%d')}.pdf"
        
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Criar documento
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Cabeçalho
        story.append(Paragraph("BRUMAKE COMERCIAL E SERVIÇOS LTDA", self.styles['CustomTitle']))
        story.append(Paragraph("Relatório de Fechamento de Caixa", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 20))
        
        # Informações gerais
        info_data = [
            ['Caixa:', details['caixa_nome']],
            ['Operador:', details['operador_nome']],
            ['Data:', data_obj.strftime('%d/%m/%Y')],
            ['Gerado em:', datetime.now().strftime('%d/%m/%Y às %H:%M')]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Seção de movimentações
        story.append(Paragraph("MOVIMENTAÇÕES DO DIA", self.styles['CustomSubtitle']))
        
        # Dados das movimentações
        mov_data = [
            ['Descrição', 'Valor'],
            ['Suprimento de Abertura', self.format_currency(details['suprimento_abertura'])],
            ['Vendas em Dinheiro (Sankhya)', self.format_currency(details['vendas_sankhya'])],
            ['Suprimento Adicional', self.format_currency(details['suprimento_caixa'])],
            ['Sangria', self.format_currency(details['sangria'])],
            ['Despesas', self.format_currency(details['despesas'])],
            ['Fechamento de Caixa', self.format_currency(details['fechamento_caixa'])]
        ]
        
        mov_table = Table(mov_data, colWidths=[4*inch, 2*inch])
        mov_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
        ]))
        
        story.append(mov_table)
        story.append(Spacer(1, 20))
        
        # Detalhes das despesas se houver
        if details['despesas_detalhes']:
            story.append(Paragraph("DETALHAMENTO DAS DESPESAS", self.styles['CustomSubtitle']))
            
            expense_data = [['Item', 'Descrição', 'Valor', 'Horário']]
            
            for i, expense in enumerate(details['despesas_detalhes'], 1):
                data_lancamento = datetime.strptime(expense['data_lancamento'], '%Y-%m-%d %H:%M:%S')
                expense_data.append([
                    str(i),
                    expense['descricao'],
                    self.format_currency(expense['valor']),
                    data_lancamento.strftime('%H:%M')
                ])
            
            expense_table = Table(expense_data, colWidths=[0.5*inch, 3*inch, 1.5*inch, 1*inch])
            expense_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
            ]))
            
            story.append(expense_table)
            story.append(Spacer(1, 20))
        
        # Cálculo do resultado
        story.append(HRFlowable(width="100%", thickness=2, color=colors.black))
        story.append(Spacer(1, 10))
        story.append(Paragraph("CÁLCULO DO RESULTADO", self.styles['CustomSubtitle']))
        
        calc_data = [
            ['Cálculo', 'Valor'],
            ['Total de Entradas', self.format_currency(calc_details['total_entradas'])],
            ['(Suprimento Abertura + Vendas + Suprimento Adicional)', ''],
            ['Total de Saídas', self.format_currency(calc_details['total_saidas'])],
            ['(Sangria + Despesas)', ''],
            ['Valor Esperado no Caixa', self.format_currency(calc_details['valor_esperado'])],
            ['Valor Real no Fechamento', self.format_currency(calc_details['fechamento_caixa'])],
        ]
        
        calc_table = Table(calc_data, colWidths=[4*inch, 2*inch])
        calc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (1, 1), (1, 1), 9),
            ('FONTSIZE', (1, 3), (1, 3), 9),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
            ('FONTNAME', (0, 4), (0, 4), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (0, 5), 'Helvetica-Bold'),
        ]))
        
        story.append(calc_table)
        story.append(Spacer(1, 30))
        
        # Resultado final
        story.append(HRFlowable(width="100%", thickness=3, color=colors.darkblue))
        story.append(Spacer(1, 20))
        
        if resultado > 0:
            result_text = f"<b>RESULTADO: SOBRA DE {self.format_currency(resultado)}</b>"
            result_style = ParagraphStyle(
                name='ResultPositive',
                parent=self.styles['ResultText'],
                textColor=colors.darkgreen
            )
        elif resultado < 0:
            result_text = f"<b>RESULTADO: FALTA DE {self.format_currency(abs(resultado))}</b>"
            result_style = ParagraphStyle(
                name='ResultNegative',
                parent=self.styles['ResultText'],
                textColor=colors.darkred
            )
        else:
            result_text = f"<b>RESULTADO: CAIXA EXATO</b>"
            result_style = ParagraphStyle(
                name='ResultExact',
                parent=self.styles['ResultText'],
                textColor=colors.darkblue
            )
        
        story.append(Paragraph(result_text, result_style))
        story.append(Spacer(1, 30))
        
        # Rodapé
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Spacer(1, 10))
        
        footer_text = f"""
        <i>Relatório gerado automaticamente pelo Sistema de Fechamento de Caixa<br/>
        BRUMAKE COMERCIAL E SERVIÇOS LTDA<br/>
        Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</i>
        """
        
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Gerar PDF
        doc.build(story)
        
        return filename
    
    def generate_general_report(self, data_fechamento, movimentacao_ids, conta_7, conta_19, db_manager):
        """Gera relatório PDF do caixa geral"""
        from utils.calculations import CashCalculations
        
        calc = CashCalculations(db_manager)
        resultado, details = calc.calculate_general_result(movimentacao_ids, conta_7, conta_19)
        
        # Nome do arquivo
        if isinstance(data_fechamento, str):
            data_obj = datetime.strptime(data_fechamento, '%Y-%m-%d').date()
        else:
            data_obj = data_fechamento
        
        filename = f"reports/Caixa_Geral_{data_obj.strftime('%Y%m%d')}.pdf"
        
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Criar documento
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Cabeçalho
        story.append(Paragraph("BRUMAKE COMERCIAL E SERVIÇOS LTDA", self.styles['CustomTitle']))
        story.append(Paragraph("Relatório de Caixa Geral", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 20))
        
        # Informações gerais
        info_data = [
            ['Data do Fechamento:', data_obj.strftime('%d/%m/%Y')],
            ['Movimentações Incluídas:', str(details['total_movimentacoes'])],
            ['Gerado em:', datetime.now().strftime('%d/%m/%Y às %H:%M')]
        ]
        
        info_table = Table(info_data, colWidths=[2.5*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Seção de entradas
        story.append(Paragraph("ENTRADAS", self.styles['CustomSubtitle']))
        
        entrada_data = [
            ['Descrição', 'Valor'],
            ['Total Suprimentos de Abertura', self.format_currency(details['total_suprimento_abertura'])],
            ['Total Vendas em Dinheiro', self.format_currency(details['total_vendas'])],
            ['Total Suprimentos Adicionais', self.format_currency(details['total_suprimento_caixa'])],
            ['Conta 7', self.format_currency(details['conta_7'])],
            ['Conta 19', self.format_currency(details['conta_19'])],
            ['Somatório das Contas', self.format_currency(details['somatorio_contas'])],
            ['TOTAL ENTRADAS', self.format_currency(details['total_entradas'])]
        ]
        
        entrada_table = Table(entrada_data, colWidths=[4*inch, 2*inch])
        entrada_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue)
        ]))
        
        story.append(entrada_table)
        story.append(Spacer(1, 20))
        
        # Seção de saídas
        story.append(Paragraph("SAÍDAS", self.styles['CustomSubtitle']))
        
        saida_data = [
            ['Descrição', 'Valor'],
            ['Total Sangrias', self.format_currency(details['total_sangria'])],
            ['Total Despesas', self.format_currency(details['total_despesas'])],
            ['Total Fechamentos de Caixa', self.format_currency(details['total_fechamento'])],
            ['TOTAL SAÍDAS', self.format_currency(details['total_saidas'])]
        ]
        
        saida_table = Table(saida_data, colWidths=[4*inch, 2*inch])
        saida_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightyellow)
        ]))
        
        story.append(saida_table)
        story.append(Spacer(1, 40))
        
        # Resultado final
        story.append(HRFlowable(width="100%", thickness=3, color=colors.darkblue))
        story.append(Spacer(1, 20))
        
        # Cálculo final
        calc_final_data = [
            ['CÁLCULO FINAL', ''],
            ['Total de Entradas', self.format_currency(details['total_entradas'])],
            ['Total de Saídas', self.format_currency(details['total_saidas'])],
            ['DIFERENÇA', self.format_currency(resultado)]
        ]
        
        calc_final_table = Table(calc_final_data, colWidths=[4*inch, 2*inch])
        calc_final_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 2, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), colors.yellow)
        ]))
        
        story.append(calc_final_table)
        story.append(Spacer(1, 30))
        
        # Resultado final destacado
        if resultado > 0:
            result_text = f"<b>RESULTADO PARCIAL GERAL: SOBRA DE {self.format_currency(resultado)}</b>"
            result_style = ParagraphStyle(
                name='ResultPositive',
                parent=self.styles['ResultText'],
                textColor=colors.darkgreen,
                fontSize=18
            )
        elif resultado < 0:
            result_text = f"<b>RESULTADO PARCIAL GERAL: FALTA DE {self.format_currency(abs(resultado))}</b>"
            result_style = ParagraphStyle(
                name='ResultNegative',
                parent=self.styles['ResultText'],
                textColor=colors.darkred,
                fontSize=18
            )
        else:
            result_text = f"<b>RESULTADO PARCIAL GERAL: EXATO</b>"
            result_style = ParagraphStyle(
                name='ResultExact',
                parent=self.styles['ResultText'],
                textColor=colors.darkblue,
                fontSize=18
            )
        
        story.append(Paragraph(result_text, result_style))
        story.append(Spacer(1, 40))
        
        # Observações
        obs_text = """
        <b>OBSERVAÇÕES:</b><br/>
        • Este relatório consolida todas as movimentações de caixa selecionadas para o dia.<br/>
        • Os valores das Contas 7 e 19 foram informados manualmente pelo usuário responsável.<br/>
        • O resultado parcial geral indica a diferença entre entradas e saídas totais.<br/>
        • Em caso de divergências, verificar individualmente cada movimentação de caixa.
        """
        
        story.append(Paragraph(obs_text, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Rodapé
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Spacer(1, 10))
        
        footer_text = f"""
        <i>Relatório gerado automaticamente pelo Sistema de Fechamento de Caixa<br/>
        BRUMAKE COMERCIAL E SERVIÇOS LTDA<br/>
        Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</i>
        """
        
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Gerar PDF
        doc.build(story)
        
        return filename


if __name__ == "__main__":
    # Teste do gerador de PDF
    print("Gerador de PDF inicializado com sucesso!")
    print("Para testar, execute através do sistema principal.")
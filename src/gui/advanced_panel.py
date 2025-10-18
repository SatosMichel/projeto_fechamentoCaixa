import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from tkcalendar import DateEntry
import json

class AdvancedPanel:
    def __init__(self, auth_manager, db_manager, on_logout):
        """Inicializa painel do usuário avançado"""
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.on_logout = on_logout
        
        self.root = tk.Tk()
        self.root.title("Painel Avançado - Sistema Brumake")
        self.root.geometry("900x700")
        
        # Centralizar janela
        self.center_window()
        
        # Criar interface
        self.create_widgets()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Cria os widgets da interface"""
        # Barra superior
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        user_info = self.auth_manager.get_current_user()
        welcome_label = ttk.Label(
            top_frame, 
            text=f"Usuário Avançado: {user_info['nome']}",
            font=('Arial', 12, 'bold')
        )
        welcome_label.pack(side=tk.LEFT)
        
        ttk.Button(
            top_frame, 
            text="Logout", 
            command=self.handle_logout
        ).pack(side=tk.RIGHT)
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Aba 1: Consultar Movimentações Anteriores
        self.create_historical_tab()
        
        # Aba 2: Consultar Movimentação do Dia Atual
        self.create_current_day_tab()
        
        # Aba 3: Criar Movimentação de Caixa Geral
        self.create_general_cashbox_tab()
        
        # Atualizar dados iniciais
        self.refresh_current_day()
    
    def create_historical_tab(self):
        """Cria aba de consulta histórica"""
        historical_frame = ttk.Frame(self.notebook)
        self.notebook.add(historical_frame, text="Consultar Movimentações Anteriores")
        
        # Título
        ttk.Label(
            historical_frame, 
            text="Consultar Movimentações Anteriores", 
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Frame de filtros
        filter_frame = ttk.LabelFrame(historical_frame, text="Filtros", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Filtro por data
        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="Data:").pack(side=tk.LEFT, padx=5)
        
        try:
            self.historical_date = DateEntry(
                date_frame,
                width=12,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='dd/mm/yyyy'
            )
            self.historical_date.pack(side=tk.LEFT, padx=5)
        except:
            # Fallback se tkcalendar não estiver disponível
            self.historical_date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
            self.historical_date = ttk.Entry(date_frame, textvariable=self.historical_date_var, width=15)
            self.historical_date.pack(side=tk.LEFT, padx=5)
            ttk.Label(date_frame, text="(dd/mm/yyyy)").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            date_frame,
            text="Consultar",
            command=self.search_historical,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            date_frame,
            text="Limpar",
            command=self.clear_historical
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview para resultados
        columns = ('Caixa', 'Operador', 'Sup. Abertura', 'Sangria', 'Despesas', 'Sup. Adicional', 'Fechamento', 'Vendas', 'Resultado')
        self.historical_tree = ttk.Treeview(historical_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.historical_tree.heading(col, text=col)
            if 'Resultado' in col:
                self.historical_tree.column(col, width=100)
            else:
                self.historical_tree.column(col, width=90)
        
        # Scrollbars
        h_scrollbar = ttk.Scrollbar(historical_frame, orient=tk.HORIZONTAL, command=self.historical_tree.xview)
        v_scrollbar = ttk.Scrollbar(historical_frame, orient=tk.VERTICAL, command=self.historical_tree.yview)
        self.historical_tree.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        self.historical_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        h_scrollbar.pack(fill=tk.X, padx=10)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de ações
        actions_frame = ttk.Frame(historical_frame)
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            actions_frame,
            text="Ver Detalhes",
            command=self.view_movement_details
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            actions_frame,
            text="Gerar Relatório",
            command=self.generate_historical_report
        ).pack(side=tk.LEFT, padx=5)
    
    def create_current_day_tab(self):
        """Cria aba de consulta do dia atual"""
        current_frame = ttk.Frame(self.notebook)
        self.notebook.add(current_frame, text="Consultar Dia Atual")
        
        # Título
        title_frame = ttk.Frame(current_frame)
        title_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            title_frame, 
            text="Movimentações do Dia Atual", 
            font=('Arial', 14, 'bold')
        ).pack(side=tk.LEFT)
        
        current_date = datetime.now().strftime('%d/%m/%Y')
        ttk.Label(
            title_frame, 
            text=f"Data: {current_date}", 
            font=('Arial', 12)
        ).pack(side=tk.RIGHT)
        
        # Treeview para movimentações do dia
        columns = ('Caixa', 'Operador', 'Status', 'Sup. Abertura', 'Sangria', 'Despesas', 'Fechamento', 'Vendas', 'Último Update')
        self.current_tree = ttk.Treeview(current_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.current_tree.heading(col, text=col)
            if col == 'Status':
                self.current_tree.column(col, width=120)
            elif col == 'Último Update':
                self.current_tree.column(col, width=150)
            else:
                self.current_tree.column(col, width=90)
        
        self.current_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbars
        current_h_scrollbar = ttk.Scrollbar(current_frame, orient=tk.HORIZONTAL, command=self.current_tree.xview)
        current_v_scrollbar = ttk.Scrollbar(current_frame, orient=tk.VERTICAL, command=self.current_tree.yview)
        self.current_tree.configure(xscrollcommand=current_h_scrollbar.set, yscrollcommand=current_v_scrollbar.set)
        
        current_h_scrollbar.pack(fill=tk.X, padx=10)
        current_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de ações
        current_actions_frame = ttk.Frame(current_frame)
        current_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            current_actions_frame,
            text="Atualizar",
            command=self.refresh_current_day,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            current_actions_frame,
            text="Ver Detalhes",
            command=self.view_current_details
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame de resumo
        summary_frame = ttk.LabelFrame(current_frame, text="Resumo do Dia", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        self.summary_text = tk.Text(summary_frame, height=6, width=80, state='disabled')
        self.summary_text.pack(fill=tk.X)
    
    def create_general_cashbox_tab(self):
        """Cria aba de criação de caixa geral"""
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text="Criar Movimentação Geral")
        
        # Título
        ttk.Label(
            general_frame, 
            text="Gerar Relatório de Caixa Geral", 
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Frame de seleção de movimentações
        selection_frame = ttk.LabelFrame(general_frame, text="1. Selecionar Movimentações Finalizadas", padding=10)
        selection_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Lista de movimentações disponíveis
        columns = ('Selecionar', 'Caixa', 'Operador', 'Abertura', 'Vendas', 'Fechamento', 'Resultado')
        self.available_tree = ttk.Treeview(selection_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.available_tree.heading(col, text=col)
            if col == 'Selecionar':
                self.available_tree.column(col, width=80)
            else:
                self.available_tree.column(col, width=100)
        
        self.available_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Botões de seleção
        selection_btn_frame = ttk.Frame(selection_frame)
        selection_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            selection_btn_frame,
            text="Selecionar Todos",
            command=self.select_all_movements
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            selection_btn_frame,
            text="Desmarcar Todos",
            command=self.deselect_all_movements
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            selection_btn_frame,
            text="Atualizar Lista",
            command=self.refresh_available_movements,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        # Frame de valores adicionais
        values_frame = ttk.LabelFrame(general_frame, text="2. Informações Adicionais", padding=10)
        values_frame.pack(fill=tk.X, padx=10, pady=5)
        
        values_grid = ttk.Frame(values_frame)
        values_grid.pack(fill=tk.X)
        
        # Conta 7
        ttk.Label(values_grid, text="Valor da Conta 7:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.conta_7_var = tk.StringVar()
        self.conta_7_entry = ttk.Entry(values_grid, textvariable=self.conta_7_var, width=20, justify='right')
        self.conta_7_entry.grid(row=0, column=1, padx=5, pady=5)
        self.conta_7_entry.bind('<KeyRelease>', self.format_currency)
        
        # Conta 19
        ttk.Label(values_grid, text="Valor da Conta 19:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.conta_19_var = tk.StringVar()
        self.conta_19_entry = ttk.Entry(values_grid, textvariable=self.conta_19_var, width=20, justify='right')
        self.conta_19_entry.grid(row=1, column=1, padx=5, pady=5)
        self.conta_19_entry.bind('<KeyRelease>', self.format_currency)
        
        # Botão gerar relatório
        ttk.Button(
            general_frame,
            text="3. Gerar Relatório de Caixa Geral",
            command=self.generate_general_report,
            style="Accent.TButton"
        ).pack(pady=20)
        
        # Carregar movimentações disponíveis
        self.refresh_available_movements()
    
    def search_historical(self):
        """Busca movimentações históricas"""
        try:
            # Obter data selecionada
            if hasattr(self.historical_date, 'get_date'):
                selected_date = self.historical_date.get_date()
            else:
                date_str = self.historical_date_var.get()
                selected_date = datetime.strptime(date_str, '%d/%m/%Y').date()
            
            # Limpar árvore
            for item in self.historical_tree.get_children():
                self.historical_tree.delete(item)
            
            # Buscar dados
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    c.nome as caixa_nome,
                    u.nome as operador_nome,
                    m.suprimento_abertura,
                    m.sangria,
                    m.despesas,
                    m.suprimento_caixa,
                    m.fechamento_caixa,
                    m.vendas_sankhya,
                    m.resultado_parcial,
                    m.status_fluxo
                FROM movimentacoes_diarias m
                JOIN caixas c ON m.caixa_id = c.id
                JOIN usuarios u ON m.usuario_id = u.id
                WHERE m.data_movimentacao = ?
                ORDER BY c.id
            ''', (selected_date,))
            
            movements = cursor.fetchall()
            
            for movement in movements:
                # Formatar valores monetários
                values = []
                for i, value in enumerate(movement):
                    if i >= 2 and i <= 8 and value is not None:  # Valores monetários
                        formatted = f"R$ {value:,.2f}".replace('.', ',').replace(',', '.', 1)
                        values.append(formatted)
                    elif i >= 2 and i <= 8:  # Valores nulos
                        values.append("R$ 0,00")
                    else:
                        values.append(value)
                
                # Determinar cor baseada no resultado
                if movement[8] is not None:
                    if movement[8] > 0:
                        tags = ('positive',)
                    elif movement[8] < 0:
                        tags = ('negative',)
                    else:
                        tags = ('neutral',)
                else:
                    tags = ()
                
                self.historical_tree.insert('', tk.END, values=values[:9], tags=tags)
            
            # Configurar cores das tags
            self.historical_tree.tag_configure('positive', foreground='green')
            self.historical_tree.tag_configure('negative', foreground='red')
            self.historical_tree.tag_configure('neutral', foreground='blue')
            
            if not movements:
                messagebox.showinfo("Resultado", "Nenhuma movimentação encontrada para esta data.")
        
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use o formato dd/mm/yyyy.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar movimentações: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def clear_historical(self):
        """Limpa consulta histórica"""
        for item in self.historical_tree.get_children():
            self.historical_tree.delete(item)
    
    def refresh_current_day(self):
        """Atualiza movimentações do dia atual"""
        # Limpar árvore
        for item in self.current_tree.get_children():
            self.current_tree.delete(item)
        
        today = date.today()
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    c.nome as caixa_nome,
                    u.nome as operador_nome,
                    m.status_fluxo,
                    m.suprimento_abertura,
                    m.sangria,
                    m.despesas,
                    m.fechamento_caixa,
                    m.vendas_sankhya,
                    m.data_atualizacao,
                    m.resultado_parcial
                FROM movimentacoes_diarias m
                JOIN caixas c ON m.caixa_id = c.id
                JOIN usuarios u ON m.usuario_id = u.id
                WHERE m.data_movimentacao = ?
                ORDER BY c.id
            ''', (today,))
            
            movements = cursor.fetchall()
            
            # Contadores para resumo
            total_movements = len(movements)
            completed_movements = 0
            total_opening = 0
            total_sales = 0
            total_closing = 0
            total_result = 0
            
            for movement in movements:
                status = movement[2]
                if status == 'finalizado':
                    completed_movements += 1
                
                # Traduzir status
                status_translations = {
                    'iniciado': 'Iniciado',
                    'suprimento_abertura': 'Suprimento Abertura',
                    'sangria': 'Sangria',
                    'despesas': 'Despesas',
                    'suprimento_caixa': 'Suprimento Adicional',
                    'fechamento': 'Fechamento',
                    'vendas_sankhya': 'Vendas Sankhya',
                    'finalizado': 'Finalizado'
                }
                
                status_display = status_translations.get(status, status)
                
                # Formatar valores
                values = [movement[0], movement[1], status_display]  # Caixa, Operador, Status
                
                for i in range(3, 8):  # Valores monetários
                    if movement[i] is not None:
                        formatted = f"R$ {movement[i]:,.2f}".replace('.', ',').replace(',', '.', 1)
                        values.append(formatted)
                        
                        # Somar para resumo
                        if i == 3:  # Suprimento abertura
                            total_opening += movement[i]
                        elif i == 7:  # Vendas
                            total_sales += movement[i]
                        elif i == 6:  # Fechamento
                            total_closing += movement[i]
                    else:
                        values.append("R$ 0,00")
                
                # Data atualização
                if movement[8]:
                    update_time = datetime.strptime(movement[8], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
                    values.append(update_time)
                else:
                    values.append("Não informado")
                
                # Cor baseada no status
                if status == 'finalizado':
                    tags = ('completed',)
                elif status in ['iniciado', 'suprimento_abertura']:
                    tags = ('started',)
                else:
                    tags = ('progress',)
                
                self.current_tree.insert('', tk.END, values=values, tags=tags)
                
                # Somar resultado
                if movement[9] is not None:
                    total_result += movement[9]
            
            # Configurar cores
            self.current_tree.tag_configure('completed', background='lightgreen')
            self.current_tree.tag_configure('started', background='lightyellow')
            self.current_tree.tag_configure('progress', background='lightblue')
            
            # Atualizar resumo
            self.update_day_summary(total_movements, completed_movements, total_opening, total_sales, total_closing, total_result)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar movimentações do dia: {e}")
        finally:
            conn.close()
    
    def update_day_summary(self, total, completed, opening, sales, closing, result):
        """Atualiza resumo do dia"""
        self.summary_text.config(state='normal')
        self.summary_text.delete(1.0, tk.END)
        
        summary = f"""RESUMO DO DIA - {datetime.now().strftime('%d/%m/%Y')}

Total de Movimentações: {total}
Movimentações Concluídas: {completed}
Movimentações Pendentes: {total - completed}

VALORES TOTAIS:
Total Suprimentos de Abertura: R$ {opening:,.2f}
Total Vendas em Dinheiro: R$ {sales:,.2f}
Total Fechamentos: R$ {closing:,.2f}
Resultado Geral: R$ {result:,.2f}""".replace('.', ',').replace(',', '.', 2)
        
        self.summary_text.insert(1.0, summary)
        self.summary_text.config(state='disabled')
    
    def refresh_available_movements(self):
        """Atualiza lista de movimentações disponíveis para relatório geral"""
        # Limpar árvore
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)
        
        today = date.today()
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    m.id,
                    c.nome as caixa_nome,
                    u.nome as operador_nome,
                    m.suprimento_abertura,
                    m.vendas_sankhya,
                    m.fechamento_caixa,
                    m.resultado_parcial
                FROM movimentacoes_diarias m
                JOIN caixas c ON m.caixa_id = c.id
                JOIN usuarios u ON m.usuario_id = u.id
                WHERE m.data_movimentacao = ? AND m.status_fluxo = 'finalizado'
                ORDER BY c.id
            ''', (today,))
            
            movements = cursor.fetchall()
            
            for movement in movements:
                mov_id = movement[0]
                
                # Formatar valores
                values = ["☐"]  # Checkbox não selecionado
                
                for i in range(1, len(movement)):
                    if i >= 3 and movement[i] is not None:  # Valores monetários
                        formatted = f"R$ {movement[i]:,.2f}".replace('.', ',').replace(',', '.', 1)
                        values.append(formatted)
                    elif i >= 3:
                        values.append("R$ 0,00")
                    else:
                        values.append(movement[i])
                
                item_id = self.available_tree.insert('', tk.END, values=values)
                # Guardar ID da movimentação no item
                self.available_tree.set(item_id, 'id', mov_id)
            
            if not movements:
                messagebox.showinfo("Informação", "Nenhuma movimentação finalizada encontrada para hoje.")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar movimentações disponíveis: {e}")
        finally:
            conn.close()
        
        # Bind para seleção/deseleção
        self.available_tree.bind('<Button-1>', self.toggle_movement_selection)
        
        # Armazenar seleções
        self.selected_movements = set()
    
    def toggle_movement_selection(self, event):
        """Alterna seleção de movimentação"""
        item = self.available_tree.identify('item', event.x, event.y)
        column = self.available_tree.identify('column', event.x, event.y)
        
        if item and column == '#1':  # Clique na coluna de seleção
            current_values = list(self.available_tree.item(item, 'values'))
            mov_id = self.available_tree.set(item, 'id')
            
            if current_values[0] == "☐":
                current_values[0] = "☑"
                self.selected_movements.add(mov_id)
            else:
                current_values[0] = "☐"
                self.selected_movements.discard(mov_id)
            
            self.available_tree.item(item, values=current_values)
    
    def select_all_movements(self):
        """Seleciona todas as movimentações"""
        for item in self.available_tree.get_children():
            current_values = list(self.available_tree.item(item, 'values'))
            current_values[0] = "☑"
            self.available_tree.item(item, values=current_values)
            
            mov_id = self.available_tree.set(item, 'id')
            self.selected_movements.add(mov_id)
    
    def deselect_all_movements(self):
        """Desmarca todas as movimentações"""
        for item in self.available_tree.get_children():
            current_values = list(self.available_tree.item(item, 'values'))
            current_values[0] = "☐"
            self.available_tree.item(item, values=current_values)
        
        self.selected_movements.clear()
    
    def format_currency(self, event=None):
        """Formata entrada como moeda brasileira"""
        widget = event.widget
        value = widget.get()
        
        # Remove tudo que não é dígito
        import re
        digits = re.sub(r'\D', '', value)
        
        if not digits:
            return
        
        # Converte para float (centavos)
        amount = float(digits) / 100
        
        # Formata como moeda
        formatted = f"R$ {amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        # Atualiza o campo
        current_pos = widget.index(tk.INSERT)
        widget.delete(0, tk.END)
        widget.insert(0, formatted)
        
        # Ajusta posição do cursor
        new_pos = min(current_pos, len(formatted))
        widget.icursor(new_pos)
    
    def currency_to_float(self, currency_str):
        """Converte string de moeda para float"""
        if not currency_str:
            return 0.0
        
        # Remove R$, espaços e pontos de milhares
        clean_str = currency_str.replace('R$', '').replace(' ', '').replace('.', '')
        # Troca vírgula por ponto decimal
        clean_str = clean_str.replace(',', '.')
        
        try:
            return float(clean_str)
        except ValueError:
            return 0.0
    
    def generate_general_report(self):
        """Gera relatório de caixa geral"""
        if not self.selected_movements:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma movimentação para gerar o relatório.")
            return
        
        conta_7_str = self.conta_7_var.get()
        conta_19_str = self.conta_19_var.get()
        
        if not conta_7_str or not conta_19_str:
            messagebox.showwarning("Aviso", "Por favor, informe os valores das contas 7 e 19.")
            return
        
        conta_7 = self.currency_to_float(conta_7_str)
        conta_19 = self.currency_to_float(conta_19_str)
        
        if conta_7 <= 0 or conta_19 <= 0:
            messagebox.showwarning("Aviso", "Os valores das contas devem ser maiores que zero.")
            return
        
        try:
            # Calcular somatório
            somatorio_contas = conta_7 + conta_19
            
            # Salvar no banco
            user_id = self.auth_manager.get_current_user()['id']
            today = date.today()
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Calcular totais das movimentações selecionadas
            placeholders = ','.join(['?' for _ in self.selected_movements])
            cursor.execute(f'''
                SELECT 
                    SUM(suprimento_abertura + COALESCE(suprimento_caixa, 0)) as total_suprimentos,
                    SUM(vendas_sankhya) as total_vendas,
                    SUM(sangria + despesas) as total_saidas,
                    SUM(fechamento_caixa) as total_fechamentos,
                    SUM(resultado_parcial) as resultado_parcial_total
                FROM movimentacoes_diarias
                WHERE id IN ({placeholders})
            ''', list(self.selected_movements))
            
            totals = cursor.fetchone()
            
            # Calcular resultado parcial geral
            # Fórmula: (Total Suprimentos + Total Vendas + Somatório Contas) - (Total Saídas + Total Fechamentos)
            total_entradas = (totals[0] or 0) + (totals[1] or 0) + somatorio_contas
            total_saidas = (totals[2] or 0) + (totals[3] or 0)
            resultado_parcial_geral = total_entradas - total_saidas
            
            # Salvar registro
            cursor.execute('''
                INSERT INTO caixa_geral (
                    data_fechamento, usuario_responsavel, conta_7, conta_19, 
                    somatorio_contas, resultado_parcial_geral, movimentacoes_utilizadas
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                today, user_id, conta_7, conta_19, somatorio_contas,
                resultado_parcial_geral, json.dumps(list(self.selected_movements))
            ))
            
            conn.commit()
            
            # Mostrar resultado
            self.show_general_report_result(
                totals[0] or 0, totals[1] or 0, totals[2] or 0, totals[3] or 0,
                conta_7, conta_19, somatorio_contas, resultado_parcial_geral
            )
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório geral: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def show_general_report_result(self, suprimentos, vendas, saidas, fechamentos, conta_7, conta_19, somatorio, resultado):
        """Mostra resultado do relatório geral"""
        result_window = tk.Toplevel(self.root)
        result_window.title("Relatório de Caixa Geral")
        result_window.geometry("500x600")
        result_window.transient(self.root)
        result_window.grab_set()
        
        # Título
        ttk.Label(
            result_window,
            text="RELATÓRIO DE CAIXA GERAL",
            font=('Arial', 16, 'bold')
        ).pack(pady=20)
        
        ttk.Label(
            result_window,
            text=f"Data: {datetime.now().strftime('%d/%m/%Y')}",
            font=('Arial', 12)
        ).pack()
        
        # Frame principal
        main_frame = ttk.Frame(result_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Seção de entradas
        ttk.Label(main_frame, text="ENTRADAS:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        entries = [
            ("Total Suprimentos de Caixa:", suprimentos),
            ("Total Vendas em Dinheiro:", vendas),
            ("Conta 7:", conta_7),
            ("Conta 19:", conta_19),
            ("Somatório das Contas:", somatorio)
        ]
        
        total_entradas = suprimentos + vendas + somatorio
        
        for label, value in entries:
            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=label, width=25).pack(side=tk.LEFT)
            value_text = f"R$ {value:,.2f}".replace('.', ',').replace(',', '.', 1)
            ttk.Label(frame, text=value_text, font=('Arial', 10, 'bold')).pack(side=tk.RIGHT)
        
        # Total entradas
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        frame = ttk.Frame(main_frame)
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="TOTAL ENTRADAS:", font=('Arial', 12, 'bold'), width=25).pack(side=tk.LEFT)
        value_text = f"R$ {total_entradas:,.2f}".replace('.', ',').replace(',', '.', 1)
        ttk.Label(frame, text=value_text, font=('Arial', 12, 'bold')).pack(side=tk.RIGHT)
        
        # Seção de saídas
        ttk.Label(main_frame, text="SAÍDAS:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(20, 5))
        
        exits = [
            ("Total Sangrias e Despesas:", saidas),
            ("Total Fechamentos de Caixa:", fechamentos)
        ]
        
        total_saidas = saidas + fechamentos
        
        for label, value in exits:
            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=label, width=25).pack(side=tk.LEFT)
            value_text = f"R$ {value:,.2f}".replace('.', ',').replace(',', '.', 1)
            ttk.Label(frame, text=value_text, font=('Arial', 10, 'bold')).pack(side=tk.RIGHT)
        
        # Total saídas
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        frame = ttk.Frame(main_frame)
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="TOTAL SAÍDAS:", font=('Arial', 12, 'bold'), width=25).pack(side=tk.LEFT)
        value_text = f"R$ {total_saidas:,.2f}".replace('.', ',').replace(',', '.', 1)
        ttk.Label(frame, text=value_text, font=('Arial', 12, 'bold')).pack(side=tk.RIGHT)
        
        # Resultado final
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=20)
        
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(result_frame, text="RESULTADO PARCIAL GERAL:", font=('Arial', 14, 'bold'), width=25).pack(side=tk.LEFT)
        
        if resultado > 0:
            result_text = f"SOBRA: R$ {resultado:,.2f}".replace('.', ',').replace(',', '.', 1)
            color = 'green'
        elif resultado < 0:
            result_text = f"FALTA: R$ {abs(resultado):,.2f}".replace('.', ',').replace(',', '.', 1)
            color = 'red'
        else:
            result_text = "EXATO: R$ 0,00"
            color = 'blue'
        
        result_label = tk.Label(result_frame, text=result_text, font=('Arial', 14, 'bold'), fg=color)
        result_label.pack(side=tk.RIGHT)
        
        # Botões
        btn_frame = ttk.Frame(result_window)
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="Gerar PDF",
            command=lambda: self.generate_general_pdf(result_window),
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame,
            text="Fechar",
            command=result_window.destroy
        ).pack(side=tk.LEFT, padx=10)
    
    def generate_general_pdf(self, parent_window):
        """Gera PDF do relatório geral"""
        try:
            # Placeholder para geração de PDF
            messagebox.showinfo("PDF", "Funcionalidade de geração de PDF será implementada em breve.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}")
    
    def view_movement_details(self):
        """Visualiza detalhes de movimentação histórica"""
        selected = self.historical_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma movimentação para ver os detalhes.")
            return
        
        # Placeholder para visualização de detalhes
        messagebox.showinfo("Detalhes", "Funcionalidade de visualização de detalhes será implementada em breve.")
    
    def view_current_details(self):
        """Visualiza detalhes de movimentação atual"""
        selected = self.current_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma movimentação para ver os detalhes.")
            return
        
        # Placeholder para visualização de detalhes
        messagebox.showinfo("Detalhes", "Funcionalidade de visualização de detalhes será implementada em breve.")
    
    def generate_historical_report(self):
        """Gera relatório histórico"""
        # Placeholder para relatório histórico
        messagebox.showinfo("Relatório", "Funcionalidade de geração de relatório histórico será implementada em breve.")
    
    def handle_logout(self):
        """Processa logout"""
        if messagebox.askyesno("Logout", "Deseja realmente sair do sistema?"):
            self.auth_manager.logout()
            self.root.destroy()
            self.on_logout()
    
    def run(self):
        """Executa a interface"""
        self.root.mainloop()


if __name__ == "__main__":
    # Teste do painel avançado
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from database_manager import DatabaseManager
    from auth_manager import AuthManager
    
    db = DatabaseManager()
    auth = AuthManager(db)
    
    # Login como admin para teste
    if auth.login("admin", "admin123"):
        def on_logout():
            print("Logout realizado")
        
        panel = AdvancedPanel(auth, db, on_logout)
        panel.run()
    else:
        print("Erro no login")
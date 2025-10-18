import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import locale
import re

# Configurar localização para formato brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass  # Usar configuração padrão

class CashierFlow:
    def __init__(self, auth_manager, db_manager, on_logout):
        """Inicializa fluxo do usuário caixa"""
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.on_logout = on_logout
        
        self.current_movimentacao_id = None
        self.current_step = 0
        self.steps = [
            'selecao_caixa',
            'suprimento_abertura', 
            'sangria',
            'despesas',
            'suprimento_caixa',
            'fechamento',
            'vendas_sankhya',
            'finalizado'
        ]
        
        self.root = tk.Tk()
        self.root.title("Sistema de Caixa - Brumake")
        self.root.geometry("600x500")
        
        # Centralizar janela
        self.center_window()
        
        # Verificar se já existe movimentação em andamento
        self.check_existing_movement()
        
        # Criar interface
        self.create_widgets()
        
        # Mostrar tela apropriada
        self.show_current_step()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def check_existing_movement(self):
        """Verifica se existe movimentação em andamento para hoje"""
        user_id = self.auth_manager.get_current_user()['id']
        today = date.today()
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, caixa_id, status_fluxo
                FROM movimentacoes_diarias
                WHERE usuario_id = ? AND data_movimentacao = ?
            ''', (user_id, today))
            
            result = cursor.fetchone()
            
            if result:
                self.current_movimentacao_id = result[0]
                self.selected_cashbox = result[1]
                current_status = result[2]
                
                # Determinar step atual baseado no status
                if current_status in self.steps:
                    self.current_step = self.steps.index(current_status)
                else:
                    self.current_step = 0
            else:
                self.current_step = 0
                
        except Exception as e:
            print(f"Erro ao verificar movimentação existente: {e}")
            self.current_step = 0
        finally:
            conn.close()
    
    def create_widgets(self):
        """Cria os widgets da interface"""
        # Barra superior
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        user_info = self.auth_manager.get_current_user()
        welcome_label = ttk.Label(
            top_frame, 
            text=f"Operador: {user_info['nome']}",
            font=('Arial', 12, 'bold')
        )
        welcome_label.pack(side=tk.LEFT)
        
        ttk.Button(
            top_frame, 
            text="Logout", 
            command=self.handle_logout
        ).pack(side=tk.RIGHT)
        
        # Barra de progresso
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(progress_frame, text="Progresso do Fluxo:").pack(anchor=tk.W)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            maximum=len(self.steps)-1
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Frame principal (será recriado para cada step)
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def show_current_step(self):
        """Mostra a tela do step atual"""
        # Atualizar barra de progresso
        self.progress_var.set(self.current_step)
        
        # Limpar frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Mostrar tela apropriada
        step_name = self.steps[self.current_step]
        
        if step_name == 'selecao_caixa':
            self.show_cashbox_selection()
        elif step_name == 'suprimento_abertura':
            self.show_opening_supply()
        elif step_name == 'sangria':
            self.show_bloodletting()
        elif step_name == 'despesas':
            self.show_expenses()
        elif step_name == 'suprimento_caixa':
            self.show_cashbox_supply()
        elif step_name == 'fechamento':
            self.show_closing()
        elif step_name == 'vendas_sankhya':
            self.show_sankhya_sales()
        elif step_name == 'finalizado':
            self.show_completion()
    
    def show_cashbox_selection(self):
        """Mostra tela de seleção de caixa"""
        ttk.Label(
            self.main_frame, 
            text="Seleção de Caixa", 
            font=('Arial', 16, 'bold')
        ).pack(pady=20)
        
        ttk.Label(
            self.main_frame, 
            text="Escolha o seu caixa para o dia de hoje:", 
            font=('Arial', 12)
        ).pack(pady=10)
        
        # Buscar caixas ativas
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id, nome FROM caixas WHERE ativo = 1 ORDER BY id')
            cashboxes = cursor.fetchall()
            
            self.selected_cashbox_var = tk.IntVar()
            
            for cashbox in cashboxes:
                ttk.Radiobutton(
                    self.main_frame,
                    text=cashbox[1],
                    variable=self.selected_cashbox_var,
                    value=cashbox[0]
                ).pack(pady=5, anchor=tk.W, padx=50)
            
            # Se já havia caixa selecionado, marcar
            if hasattr(self, 'selected_cashbox'):
                self.selected_cashbox_var.set(self.selected_cashbox)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar caixas: {e}")
        finally:
            conn.close()
        
        ttk.Button(
            self.main_frame,
            text="Avançar",
            command=self.process_cashbox_selection,
            style="Accent.TButton"
        ).pack(pady=30)
    
    def show_opening_supply(self):
        """Mostra tela de suprimento de abertura"""
        ttk.Label(
            self.main_frame, 
            text="Suprimento de Abertura", 
            font=('Arial', 16, 'bold')
        ).pack(pady=20)
        
        ttk.Label(
            self.main_frame, 
            text=f"Caixa selecionado: Caixa {self.selected_cashbox}", 
            font=('Arial', 10, 'italic')
        ).pack()
        
        ttk.Label(
            self.main_frame, 
            text=f"Data: {datetime.now().strftime('%d/%m/%Y')}", 
            font=('Arial', 10, 'italic')
        ).pack(pady=(0, 20))
        
        ttk.Label(
            self.main_frame, 
            text="Informe o suprimento de caixa do dia de hoje:", 
            font=('Arial', 12)
        ).pack(pady=10)
        
        # Campo com máscara de moeda
        self.opening_supply_var = tk.StringVar()
        self.opening_supply_entry = ttk.Entry(
            self.main_frame, 
            textvariable=self.opening_supply_var,
            font=('Arial', 14),
            width=20,
            justify='right'
        )
        self.opening_supply_entry.pack(pady=10)
        self.opening_supply_entry.bind('<KeyRelease>', self.format_currency)
        self.opening_supply_entry.focus()
        
        ttk.Label(
            self.main_frame, 
            text="(Digite apenas números. Ex: 10050 = R$ 100,50)", 
            font=('Arial', 9, 'italic')
        ).pack()
        
        ttk.Button(
            self.main_frame,
            text="Avançar",
            command=self.process_opening_supply,
            style="Accent.TButton"
        ).pack(pady=30)
    
    def show_bloodletting(self):
        """Mostra tela de sangria"""
        ttk.Label(
            self.main_frame, 
            text="Sangria", 
            font=('Arial', 16, 'bold')
        ).pack(pady=20)
        
        ttk.Label(
            self.main_frame, 
            text="Deseja efetuar uma sangria?", 
            font=('Arial', 12)
        ).pack(pady=20)
        
        self.bloodletting_choice = tk.StringVar(value="nao")
        
        ttk.Radiobutton(
            self.main_frame,
            text="Não",
            variable=self.bloodletting_choice,
            value="nao",
            command=self.toggle_bloodletting_entry
        ).pack(pady=5)
        
        ttk.Radiobutton(
            self.main_frame,
            text="Sim",
            variable=self.bloodletting_choice,
            value="sim",
            command=self.toggle_bloodletting_entry
        ).pack(pady=5)
        
        # Frame para valor (inicialmente oculto)
        self.bloodletting_frame = ttk.Frame(self.main_frame)
        self.bloodletting_frame.pack(pady=20)
        
        ttk.Label(self.bloodletting_frame, text="Valor da sangria:").pack()
        
        self.bloodletting_var = tk.StringVar()
        self.bloodletting_entry = ttk.Entry(
            self.bloodletting_frame,
            textvariable=self.bloodletting_var,
            font=('Arial', 12),
            width=20,
            justify='right',
            state='disabled'
        )
        self.bloodletting_entry.pack(pady=5)
        self.bloodletting_entry.bind('<KeyRelease>', self.format_currency)
        
        ttk.Button(
            self.main_frame,
            text="Avançar",
            command=self.process_bloodletting,
            style="Accent.TButton"
        ).pack(pady=30)
    
    def show_expenses(self):
        """Mostra tela de despesas"""
        ttk.Label(
            self.main_frame, 
            text="Despesas", 
            font=('Arial', 16, 'bold')
        ).pack(pady=20)
        
        # Lista de despesas já cadastradas
        self.expenses_frame = ttk.LabelFrame(self.main_frame, text="Despesas cadastradas")
        self.expenses_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollable frame para despesas
        canvas = tk.Canvas(self.expenses_frame, height=150)
        scrollbar = ttk.Scrollbar(self.expenses_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Carregar despesas existentes
        self.load_existing_expenses()
        
        # Pergunta sobre nova despesa
        question_frame = ttk.Frame(self.main_frame)
        question_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(question_frame, text="Deseja lançar uma despesa?", font=('Arial', 12)).pack()
        
        self.expense_choice = tk.StringVar(value="nao")
        
        choice_frame = ttk.Frame(question_frame)
        choice_frame.pack(pady=10)
        
        ttk.Radiobutton(
            choice_frame,
            text="Não",
            variable=self.expense_choice,
            value="nao",
            command=self.toggle_expense_entry
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(
            choice_frame,
            text="Sim",
            variable=self.expense_choice,
            value="sim",
            command=self.toggle_expense_entry
        ).pack(side=tk.LEFT, padx=10)
        
        # Frame para nova despesa (inicialmente oculto)
        self.new_expense_frame = ttk.Frame(self.main_frame)
        self.new_expense_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(self.new_expense_frame, text="Valor da despesa:").pack()
        
        self.expense_var = tk.StringVar()
        self.expense_entry = ttk.Entry(
            self.new_expense_frame,
            textvariable=self.expense_var,
            font=('Arial', 12),
            width=20,
            justify='right',
            state='disabled'
        )
        self.expense_entry.pack(pady=5)
        self.expense_entry.bind('<KeyRelease>', self.format_currency)
        
        ttk.Label(self.new_expense_frame, text="Descrição (opcional):").pack()
        
        self.expense_desc_var = tk.StringVar()
        self.expense_desc_entry = ttk.Entry(
            self.new_expense_frame,
            textvariable=self.expense_desc_var,
            font=('Arial', 10),
            width=30,
            state='disabled'
        )
        self.expense_desc_entry.pack(pady=5)
        
        btn_frame = ttk.Frame(self.new_expense_frame)
        btn_frame.pack(pady=10)
        
        self.add_expense_btn = ttk.Button(
            btn_frame,
            text="Adicionar Despesa",
            command=self.add_expense,
            state='disabled'
        )
        self.add_expense_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            self.main_frame,
            text="Avançar",
            command=self.process_expenses,
            style="Accent.TButton"
        ).pack(pady=20)
    
    def show_cashbox_supply(self):
        """Mostra tela de suprimento adicional de caixa"""
        ttk.Label(
            self.main_frame, 
            text="Suprimento Adicional", 
            font=('Arial', 16, 'bold')
        ).pack(pady=20)
        
        ttk.Label(
            self.main_frame, 
            text="Houve suprimento adicional de caixa durante o dia?", 
            font=('Arial', 12)
        ).pack(pady=20)
        
        self.supply_choice = tk.StringVar(value="nao")
        
        ttk.Radiobutton(
            self.main_frame,
            text="Não",
            variable=self.supply_choice,
            value="nao",
            command=self.toggle_supply_entry
        ).pack(pady=5)
        
        ttk.Radiobutton(
            self.main_frame,
            text="Sim",
            variable=self.supply_choice,
            value="sim",
            command=self.toggle_supply_entry
        ).pack(pady=5)
        
        # Frame para valor (inicialmente oculto)
        self.supply_frame = ttk.Frame(self.main_frame)
        self.supply_frame.pack(pady=20)
        
        ttk.Label(self.supply_frame, text="Valor do suprimento adicional:").pack()
        
        self.supply_var = tk.StringVar()
        self.supply_entry = ttk.Entry(
            self.supply_frame,
            textvariable=self.supply_var,
            font=('Arial', 12),
            width=20,
            justify='right',
            state='disabled'
        )
        self.supply_entry.pack(pady=5)
        self.supply_entry.bind('<KeyRelease>', self.format_currency)
        
        ttk.Button(
            self.main_frame,
            text="Avançar",
            command=self.process_cashbox_supply,
            style="Accent.TButton"
        ).pack(pady=30)
    
    def show_closing(self):
        """Mostra tela de fechamento"""
        ttk.Label(
            self.main_frame, 
            text="Fechamento de Caixa", 
            font=('Arial', 16, 'bold')
        ).pack(pady=20)
        
        ttk.Label(
            self.main_frame, 
            text="Qual o valor do seu fechamento de caixa?", 
            font=('Arial', 12)
        ).pack(pady=20)
        
        ttk.Label(
            self.main_frame, 
            text="(Valor total que sobrou no caixa para retirada)", 
            font=('Arial', 10, 'italic')
        ).pack()
        
        self.closing_var = tk.StringVar()
        self.closing_entry = ttk.Entry(
            self.main_frame,
            textvariable=self.closing_var,
            font=('Arial', 14),
            width=20,
            justify='right'
        )
        self.closing_entry.pack(pady=20)
        self.closing_entry.bind('<KeyRelease>', self.format_currency)
        self.closing_entry.focus()
        
        ttk.Button(
            self.main_frame,
            text="Avançar",
            command=self.process_closing,
            style="Accent.TButton"
        ).pack(pady=30)
    
    def show_sankhya_sales(self):
        """Mostra tela de vendas Sankhya"""
        ttk.Label(
            self.main_frame, 
            text="Vendas no Sistema Sankhya", 
            font=('Arial', 16, 'bold')
        ).pack(pady=20)
        
        ttk.Label(
            self.main_frame, 
            text="Digite o valor total de suas vendas em dinheiro no sistema Sankhya:", 
            font=('Arial', 12)
        ).pack(pady=20)
        
        self.sankhya_var = tk.StringVar()
        self.sankhya_entry = ttk.Entry(
            self.main_frame,
            textvariable=self.sankhya_var,
            font=('Arial', 14),
            width=20,
            justify='right'
        )
        self.sankhya_entry.pack(pady=20)
        self.sankhya_entry.bind('<KeyRelease>', self.format_currency)
        self.sankhya_entry.focus()
        
        ttk.Button(
            self.main_frame,
            text="Finalizar",
            command=self.process_sankhya_sales,
            style="Accent.TButton"
        ).pack(pady=30)
    
    def show_completion(self):
        """Mostra tela de finalização"""
        ttk.Label(
            self.main_frame, 
            text="Processo Finalizado!", 
            font=('Arial', 18, 'bold'),
            foreground='green'
        ).pack(pady=30)
        
        ttk.Label(
            self.main_frame, 
            text="Seu relatório de caixa foi gerado com sucesso.", 
            font=('Arial', 12)
        ).pack(pady=10)
        
        # Mostrar resumo
        self.show_summary()
        
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=30)
        
        ttk.Button(
            btn_frame,
            text="Imprimir PDF",
            command=self.generate_pdf,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame,
            text="Sair",
            command=self.handle_logout
        ).pack(side=tk.LEFT, padx=10)
    
    def format_currency(self, event=None):
        """Formata entrada como moeda brasileira"""
        widget = event.widget
        value = widget.get()
        
        # Remove tudo que não é dígito
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
    
    def process_cashbox_selection(self):
        """Processa seleção de caixa"""
        selected = self.selected_cashbox_var.get()
        
        if not selected:
            messagebox.showwarning("Aviso", "Por favor, selecione um caixa.")
            return
        
        self.selected_cashbox = selected
        
        # Criar nova movimentação se não existir
        if not self.current_movimentacao_id:
            user_id = self.auth_manager.get_current_user()['id']
            today = date.today()
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO movimentacoes_diarias (usuario_id, caixa_id, data_movimentacao, status_fluxo)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, selected, today, 'suprimento_abertura'))
                
                self.current_movimentacao_id = cursor.lastrowid
                conn.commit()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao criar movimentação: {e}")
                return
            finally:
                conn.close()
        
        self.current_step += 1
        self.show_current_step()
    
    def process_opening_supply(self):
        """Processa suprimento de abertura"""
        value_str = self.opening_supply_var.get()
        
        if not value_str:
            messagebox.showwarning("Aviso", "Por favor, informe o valor do suprimento.")
            return
        
        value = self.currency_to_float(value_str)
        
        if value <= 0:
            messagebox.showwarning("Aviso", "O valor deve ser maior que zero.")
            return
        
        # Salvar no banco
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE movimentacoes_diarias 
                SET suprimento_abertura = ?, status_fluxo = ?, data_atualizacao = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (value, 'sangria', self.current_movimentacao_id))
            
            conn.commit()
            
            self.current_step += 1
            self.show_current_step()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar suprimento: {e}")
        finally:
            conn.close()
    
    def process_bloodletting(self):
        """Processa sangria"""
        choice = self.bloodletting_choice.get()
        value = 0.0
        
        if choice == "sim":
            value_str = self.bloodletting_var.get()
            if not value_str:
                messagebox.showwarning("Aviso", "Por favor, informe o valor da sangria.")
                return
            
            value = self.currency_to_float(value_str)
            
            if value <= 0:
                messagebox.showwarning("Aviso", "O valor da sangria deve ser maior que zero.")
                return
        
        # Salvar no banco
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE movimentacoes_diarias 
                SET sangria = ?, status_fluxo = ?, data_atualizacao = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (value, 'despesas', self.current_movimentacao_id))
            
            conn.commit()
            
            self.current_step += 1
            self.show_current_step()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar sangria: {e}")
        finally:
            conn.close()
    
    def toggle_bloodletting_entry(self):
        """Ativa/desativa campo de sangria"""
        if self.bloodletting_choice.get() == "sim":
            self.bloodletting_entry.config(state='normal')
            self.bloodletting_entry.focus()
        else:
            self.bloodletting_entry.config(state='disabled')
            self.bloodletting_var.set("")
    
    def toggle_expense_entry(self):
        """Ativa/desativa campos de despesa"""
        if self.expense_choice.get() == "sim":
            self.expense_entry.config(state='normal')
            self.expense_desc_entry.config(state='normal')
            self.add_expense_btn.config(state='normal')
            self.expense_entry.focus()
        else:
            self.expense_entry.config(state='disabled')
            self.expense_desc_entry.config(state='disabled')
            self.add_expense_btn.config(state='disabled')
            self.expense_var.set("")
            self.expense_desc_var.set("")
    
    def toggle_supply_entry(self):
        """Ativa/desativa campo de suprimento"""
        if self.supply_choice.get() == "sim":
            self.supply_entry.config(state='normal')
            self.supply_entry.focus()
        else:
            self.supply_entry.config(state='disabled')
            self.supply_var.set("")
    
    def load_existing_expenses(self):
        """Carrega despesas já cadastradas"""
        # Limpar frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.current_movimentacao_id:
            return
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT valor, descricao, data_lancamento
                FROM despesas_detalhes
                WHERE movimentacao_id = ?
                ORDER BY data_lancamento
            ''', (self.current_movimentacao_id,))
            
            expenses = cursor.fetchall()
            
            if not expenses:
                ttk.Label(self.scrollable_frame, text="Nenhuma despesa cadastrada ainda.").pack(pady=10)
            else:
                total = 0
                for i, expense in enumerate(expenses, 1):
                    valor = expense[0]
                    descricao = expense[1] or "Sem descrição"
                    data = datetime.strptime(expense[2], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
                    
                    expense_text = f"{i}. R$ {valor:,.2f}".replace('.', ',').replace(',', '.', 1) + f" - {descricao} ({data})"
                    ttk.Label(self.scrollable_frame, text=expense_text).pack(anchor=tk.W, padx=10, pady=2)
                    total += valor
                
                ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=5)
                total_text = f"Total: R$ {total:,.2f}".replace('.', ',').replace(',', '.', 1)
                ttk.Label(self.scrollable_frame, text=total_text, font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=10)
        
        except Exception as e:
            ttk.Label(self.scrollable_frame, text=f"Erro ao carregar despesas: {e}").pack(pady=10)
        finally:
            conn.close()
    
    def add_expense(self):
        """Adiciona nova despesa"""
        value_str = self.expense_var.get()
        description = self.expense_desc_var.get().strip()
        
        if not value_str:
            messagebox.showwarning("Aviso", "Por favor, informe o valor da despesa.")
            return
        
        value = self.currency_to_float(value_str)
        
        if value <= 0:
            messagebox.showwarning("Aviso", "O valor da despesa deve ser maior que zero.")
            return
        
        # Salvar despesa
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO despesas_detalhes (movimentacao_id, valor, descricao)
                VALUES (?, ?, ?)
            ''', (self.current_movimentacao_id, value, description if description else None))
            
            conn.commit()
            
            # Limpar campos
            self.expense_var.set("")
            self.expense_desc_var.set("")
            
            # Recarregar lista
            self.load_existing_expenses()
            
            messagebox.showinfo("Sucesso", "Despesa adicionada com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar despesa: {e}")
        finally:
            conn.close()
    
    def process_expenses(self):
        """Processa etapa de despesas"""
        # Calcular total de despesas
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT COALESCE(SUM(valor), 0)
                FROM despesas_detalhes
                WHERE movimentacao_id = ?
            ''', (self.current_movimentacao_id,))
            
            total_expenses = cursor.fetchone()[0]
            
            # Atualizar movimentação
            cursor.execute('''
                UPDATE movimentacoes_diarias 
                SET despesas = ?, status_fluxo = ?, data_atualizacao = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (total_expenses, 'suprimento_caixa', self.current_movimentacao_id))
            
            conn.commit()
            
            self.current_step += 1
            self.show_current_step()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar despesas: {e}")
        finally:
            conn.close()
    
    def process_cashbox_supply(self):
        """Processa suprimento adicional"""
        choice = self.supply_choice.get()
        value = 0.0
        
        if choice == "sim":
            value_str = self.supply_var.get()
            if not value_str:
                messagebox.showwarning("Aviso", "Por favor, informe o valor do suprimento.")
                return
            
            value = self.currency_to_float(value_str)
            
            if value <= 0:
                messagebox.showwarning("Aviso", "O valor do suprimento deve ser maior que zero.")
                return
        
        # Salvar no banco
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE movimentacoes_diarias 
                SET suprimento_caixa = ?, status_fluxo = ?, data_atualizacao = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (value, 'fechamento', self.current_movimentacao_id))
            
            conn.commit()
            
            self.current_step += 1
            self.show_current_step()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar suprimento: {e}")
        finally:
            conn.close()
    
    def process_closing(self):
        """Processa fechamento"""
        value_str = self.closing_var.get()
        
        if not value_str:
            messagebox.showwarning("Aviso", "Por favor, informe o valor de fechamento.")
            return
        
        value = self.currency_to_float(value_str)
        
        if value < 0:
            messagebox.showwarning("Aviso", "O valor de fechamento não pode ser negativo.")
            return
        
        # Salvar no banco
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE movimentacoes_diarias 
                SET fechamento_caixa = ?, status_fluxo = ?, data_atualizacao = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (value, 'vendas_sankhya', self.current_movimentacao_id))
            
            conn.commit()
            
            self.current_step += 1
            self.show_current_step()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar fechamento: {e}")
        finally:
            conn.close()
    
    def process_sankhya_sales(self):
        """Processa vendas Sankhya e finaliza"""
        value_str = self.sankhya_var.get()
        
        if not value_str:
            messagebox.showwarning("Aviso", "Por favor, informe o valor das vendas.")
            return
        
        value = self.currency_to_float(value_str)
        
        if value < 0:
            messagebox.showwarning("Aviso", "O valor das vendas não pode ser negativo.")
            return
        
        # Calcular resultado parcial
        resultado_parcial = self.calculate_partial_result(value)
        
        # Salvar no banco
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE movimentacoes_diarias 
                SET vendas_sankhya = ?, resultado_parcial = ?, status_fluxo = ?, data_atualizacao = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (value, resultado_parcial, 'finalizado', self.current_movimentacao_id))
            
            conn.commit()
            
            self.current_step += 1
            self.show_current_step()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao finalizar processo: {e}")
        finally:
            conn.close()
    
    def calculate_partial_result(self, vendas_sankhya):
        """Calcula resultado parcial do caixa"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT suprimento_abertura, sangria, despesas, suprimento_caixa, fechamento_caixa
                FROM movimentacoes_diarias
                WHERE id = ?
            ''', (self.current_movimentacao_id,))
            
            data = cursor.fetchone()
            
            if data:
                suprimento_abertura = data[0] or 0
                sangria = data[1] or 0
                despesas = data[2] or 0
                suprimento_caixa = data[3] or 0
                fechamento_caixa = data[4] or 0
                
                # Fórmula: (Suprimento Abertura + Vendas Sankhya + Suprimento Caixa) - (Sangria + Despesas) - Fechamento
                esperado = (suprimento_abertura + vendas_sankhya + suprimento_caixa) - (sangria + despesas)
                resultado = esperado - fechamento_caixa
                
                return resultado
            
            return 0.0
            
        except Exception as e:
            print(f"Erro ao calcular resultado: {e}")
            return 0.0
        finally:
            conn.close()
    
    def show_summary(self):
        """Mostra resumo da movimentação"""
        if not self.current_movimentacao_id:
            return
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT suprimento_abertura, sangria, despesas, suprimento_caixa, 
                       fechamento_caixa, vendas_sankhya, resultado_parcial
                FROM movimentacoes_diarias
                WHERE id = ?
            ''', (self.current_movimentacao_id,))
            
            data = cursor.fetchone()
            
            if data:
                summary_frame = ttk.LabelFrame(self.main_frame, text="Resumo do Caixa", padding=10)
                summary_frame.pack(fill=tk.X, pady=20)
                
                # Dados
                suprimento_abertura = data[0] or 0
                sangria = data[1] or 0
                despesas = data[2] or 0
                suprimento_caixa = data[3] or 0
                fechamento_caixa = data[4] or 0
                vendas_sankhya = data[5] or 0
                resultado_parcial = data[6] or 0
                
                # Mostrar valores
                values = [
                    ("Suprimento de Abertura:", suprimento_abertura),
                    ("Vendas em Dinheiro (Sankhya):", vendas_sankhya),
                    ("Suprimento Adicional:", suprimento_caixa),
                    ("Sangria:", sangria),
                    ("Despesas:", despesas),
                    ("Fechamento de Caixa:", fechamento_caixa)
                ]
                
                for label, value in values:
                    row_frame = ttk.Frame(summary_frame)
                    row_frame.pack(fill=tk.X, pady=2)
                    
                    ttk.Label(row_frame, text=label, width=25).pack(side=tk.LEFT)
                    value_text = f"R$ {value:,.2f}".replace('.', ',').replace(',', '.', 1)
                    ttk.Label(row_frame, text=value_text, font=('Arial', 10, 'bold')).pack(side=tk.RIGHT)
                
                # Separador
                ttk.Separator(summary_frame, orient='horizontal').pack(fill=tk.X, pady=10)
                
                # Resultado
                result_frame = ttk.Frame(summary_frame)
                result_frame.pack(fill=tk.X, pady=5)
                
                ttk.Label(result_frame, text="Resultado:", font=('Arial', 12, 'bold'), width=25).pack(side=tk.LEFT)
                
                if resultado_parcial > 0:
                    result_text = f"SOBRA: R$ {resultado_parcial:,.2f}".replace('.', ',').replace(',', '.', 1)
                    color = 'green'
                elif resultado_parcial < 0:
                    result_text = f"FALTA: R$ {abs(resultado_parcial):,.2f}".replace('.', ',').replace(',', '.', 1)
                    color = 'red'
                else:
                    result_text = "EXATO: R$ 0,00"
                    color = 'blue'
                
                result_label = tk.Label(result_frame, text=result_text, font=('Arial', 12, 'bold'), fg=color)
                result_label.pack(side=tk.RIGHT)
        
        except Exception as e:
            print(f"Erro ao mostrar resumo: {e}")
        finally:
            conn.close()
    
    def generate_pdf(self):
        """Gera relatório PDF"""
        try:
            from utils.pdf_generator import PDFGenerator
            
            pdf_gen = PDFGenerator()
            filename = pdf_gen.generate_cashier_report(self.current_movimentacao_id, self.db_manager)
            
            messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\nArquivo: {filename}")
            
        except ImportError:
            messagebox.showwarning("Aviso", "Módulo de geração de PDF não disponível ainda.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}")
    
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
    # Teste do fluxo do caixa
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from database_manager import DatabaseManager
    from auth_manager import AuthManager
    
    db = DatabaseManager()
    auth = AuthManager(db)
    
    # Criar usuário de teste
    db.db_manager.create_access_request("Operador Teste", "caixa1", "123456", "caixa")
    
    if auth.login("caixa1", "123456"):
        def on_logout():
            print("Logout realizado")
        
        flow = CashierFlow(auth, db, on_logout)
        flow.run()
    else:
        print("Erro no login")
// Sistema de Fechamento de Caixa - Brumake
// JavaScript Principal

$(document).ready(function() {
    // Inicializações
    initializeApp();
    
    // Event listeners globais
    setupGlobalEventListeners();
    
    // Máscaras de entrada
    setupCurrencyMasks();
    
    // Validações de formulário
    setupFormValidations();
    
    // Auto-save functionality
    setupAutoSave();
});

// Inicialização da aplicação
function initializeApp() {
    // Adicionar classe fade-in aos elementos principais
    $('.container-fluid, .card').addClass('fade-in');
    
    // Configurar tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Configurar popovers do Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Verificar conectividade
    checkConnectivity();
    
    console.log('Sistema Brumake inicializado com sucesso!');
}

// Event listeners globais
function setupGlobalEventListeners() {
    // Confirmação para ações perigosas
    $(document).on('click', '[data-confirm]', function(e) {
        var message = $(this).data('confirm');
        if (!confirm(message)) {
            e.preventDefault();
            return false;
        }
    });
    
    // Loading state para formulários
    $(document).on('submit', 'form', function() {
        var $form = $(this);
        var $submitBtn = $form.find('button[type="submit"]');
        
        if (!$submitBtn.hasClass('no-loading')) {
            $submitBtn.prop('disabled', true);
            $submitBtn.html('<i class="fas fa-spinner fa-spin me-2"></i>Processando...');
        }
    });
    
    // Auto-dismiss para alerts
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Navegação com teclas de atalho
    $(document).on('keydown', function(e) {
        // Ctrl + Enter para submeter formulários
        if (e.ctrlKey && e.keyCode === 13) {
            $('form:visible').first().submit();
        }
        
        // ESC para fechar modals
        if (e.keyCode === 27) {
            $('.modal.show').modal('hide');
        }
    });
}

// Configurar máscaras de moeda
function setupCurrencyMasks() {
    // Máscara para campos de moeda
    $(document).on('input', '.currency-input, input[type="currency"]', function() {
        formatCurrencyInput(this);
    });
    
    // Aplicar formatação inicial
    $('.currency-input, input[type="currency"]').each(function() {
        if ($(this).val()) {
            formatCurrencyInput(this);
        }
    });
}

// Formatar entrada de moeda
function formatCurrencyInput(input) {
    var $input = $(input);
    var value = $input.val();
    
    // Remove tudo que não é dígito
    var digits = value.replace(/\D/g, '');
    
    if (!digits) {
        $input.val('');
        return;
    }
    
    // Converte para float (centavos)
    var amount = parseFloat(digits) / 100;
    
    // Formata como moeda brasileira
    var formatted = formatCurrency(amount);
    
    // Atualiza o campo
    var cursorPos = $input[0].selectionStart;
    $input.val(formatted);
    
    // Ajusta posição do cursor
    var newPos = Math.min(cursorPos, formatted.length);
    $input[0].setSelectionRange(newPos, newPos);
}

// Formatar valor como moeda brasileira
function formatCurrency(value) {
    if (value === null || value === undefined || isNaN(value)) {
        return 'R$ 0,00';
    }
    
    return 'R$ ' + value.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Converter string de moeda para float
function currencyToFloat(currencyStr) {
    if (!currencyStr) return 0.0;
    
    // Remove R$, espaços e pontos de milhares
    var cleanStr = currencyStr.replace(/R\$\s?/g, '').replace(/\./g, '');
    // Troca vírgula por ponto decimal
    cleanStr = cleanStr.replace(',', '.');
    
    var value = parseFloat(cleanStr);
    return isNaN(value) ? 0.0 : value;
}

// Validações de formulário
function setupFormValidations() {
    // Validação em tempo real
    $(document).on('blur', 'input[required]', function() {
        validateField(this);
    });
    
    // Validação antes do submit
    $(document).on('submit', 'form', function(e) {
        var $form = $(this);
        var isValid = true;
        
        $form.find('input[required], select[required]').each(function() {
            if (!validateField(this)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            showAlert('Por favor, corrija os erros no formulário.', 'error');
            return false;
        }
    });
}

// Validar campo individual
function validateField(field) {
    var $field = $(field);
    var value = $field.val().trim();
    var type = $field.attr('type');
    var isValid = true;
    
    // Remover classes de validação anteriores
    $field.removeClass('is-valid is-invalid');
    
    // Verificar se é obrigatório
    if ($field.prop('required') && !value) {
        $field.addClass('is-invalid');
        isValid = false;
    }
    
    // Validações específicas por tipo
    if (value) {
        switch (type) {
            case 'email':
                var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    $field.addClass('is-invalid');
                    isValid = false;
                } else {
                    $field.addClass('is-valid');
                }
                break;
                
            case 'password':
                if (value.length < 6) {
                    $field.addClass('is-invalid');
                    isValid = false;
                } else {
                    $field.addClass('is-valid');
                }
                break;
                
            default:
                if (isValid) {
                    $field.addClass('is-valid');
                }
        }
    }
    
    return isValid;
}

// Sistema de auto-save
function setupAutoSave() {
    var autoSaveTimer;
    
    $(document).on('input change', '[data-autosave]', function() {
        clearTimeout(autoSaveTimer);
        var $field = $(this);
        
        autoSaveTimer = setTimeout(function() {
            autoSaveField($field);
        }, 2000); // Auto-save após 2 segundos de inatividade
    });
}

// Auto-save de campo individual
function autoSaveField($field) {
    var formId = $field.closest('form').attr('id');
    var fieldName = $field.attr('name');
    var fieldValue = $field.val();
    
    if (!formId || !fieldName) return;
    
    // Salvar no localStorage
    var autoSaveKey = 'autosave_' + formId + '_' + fieldName;
    localStorage.setItem(autoSaveKey, fieldValue);
    
    // Mostrar indicador visual
    showAutoSaveIndicator($field);
}

// Indicador visual de auto-save
function showAutoSaveIndicator($field) {
    var $indicator = $('<span class="auto-save-indicator text-success"><i class="fas fa-check"></i></span>');
    
    $field.after($indicator);
    
    setTimeout(function() {
        $indicator.fadeOut(function() {
            $indicator.remove();
        });
    }, 1500);
}

// Carregar dados auto-salvos
function loadAutoSavedData(formId) {
    var $form = $('#' + formId);
    
    $form.find('[data-autosave]').each(function() {
        var $field = $(this);
        var fieldName = $field.attr('name');
        var autoSaveKey = 'autosave_' + formId + '_' + fieldName;
        var savedValue = localStorage.getItem(autoSaveKey);
        
        if (savedValue && !$field.val()) {
            $field.val(savedValue);
            
            // Aplicar formatação se for campo de moeda
            if ($field.hasClass('currency-input')) {
                formatCurrencyInput($field[0]);
            }
        }
    });
}

// Limpar dados auto-salvos
function clearAutoSavedData(formId) {
    var $form = $('#' + formId);
    
    $form.find('[data-autosave]').each(function() {
        var fieldName = $(this).attr('name');
        var autoSaveKey = 'autosave_' + formId + '_' + fieldName;
        localStorage.removeItem(autoSaveKey);
    });
}

// Sistema de notificações
function showAlert(message, type = 'info', duration = 5000) {
    type = type || 'info';
    var alertClass = 'alert-' + (type === 'error' ? 'danger' : type);
    
    var $alert = $(`
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('body').append($alert);
    
    if (duration > 0) {
        setTimeout(function() {
            $alert.fadeOut(function() {
                $alert.remove();
            });
        }, duration);
    }
}

// Verificar conectividade
function checkConnectivity() {
    if (!navigator.onLine) {
        showAlert('Você está offline. Algumas funcionalidades podem não estar disponíveis.', 'warning', 0);
    }
    
    window.addEventListener('online', function() {
        showAlert('Conexão restaurada!', 'success');
    });
    
    window.addEventListener('offline', function() {
        showAlert('Você está offline. Os dados serão salvos localmente.', 'warning', 0);
    });
}

// Utilitários para requisições AJAX
function makeRequest(url, method = 'GET', data = null) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: url,
            method: method,
            data: data,
            dataType: 'json',
            beforeSend: function() {
                // Mostrar loading se necessário
                $('.loading-overlay').show();
            },
            success: function(response) {
                resolve(response);
            },
            error: function(xhr, status, error) {
                reject({ xhr, status, error });
                
                if (xhr.status === 401) {
                    showAlert('Sessão expirada. Redirecionando para login...', 'error');
                    setTimeout(() => {
                        window.location.href = '/auth/login';
                    }, 2000);
                } else {
                    showAlert('Erro na requisição: ' + error, 'error');
                }
            },
            complete: function() {
                $('.loading-overlay').hide();
            }
        });
    });
}

// Função para imprimir relatórios
function printReport() {
    window.print();
}

// Função para exportar dados
function exportData(data, filename, type = 'csv') {
    var blob;
    var link = document.createElement('a');
    
    if (type === 'csv') {
        var csv = convertToCSV(data);
        blob = new Blob([csv], { type: 'text/csv' });
    } else if (type === 'json') {
        blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    }
    
    link.href = URL.createObjectURL(blob);
    link.download = filename + '.' + type;
    link.click();
}

// Converter array para CSV
function convertToCSV(data) {
    if (!data || !data.length) return '';
    
    var headers = Object.keys(data[0]);
    var csv = headers.join(',') + '\n';
    
    data.forEach(row => {
        var values = headers.map(header => {
            var value = row[header] || '';
            // Escapar aspas e adicionar aspas se necessário
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                value = '"' + value.replace(/"/g, '""') + '"';
            }
            return value;
        });
        csv += values.join(',') + '\n';
    });
    
    return csv;
}

// Função para copiar texto para clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Copiado para a área de transferência!', 'success');
        });
    } else {
        // Fallback para navegadores mais antigos
        var textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showAlert('Copiado para a área de transferência!', 'success');
    }
}

// Debug helpers (remover em produção)
window.BrumakeSystem = {
    formatCurrency: formatCurrency,
    currencyToFloat: currencyToFloat,
    showAlert: showAlert,
    makeRequest: makeRequest,
    exportData: exportData,
    copyToClipboard: copyToClipboard
};

console.log('JavaScript do Sistema Brumake carregado com sucesso!');
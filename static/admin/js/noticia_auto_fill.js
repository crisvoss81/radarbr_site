// JavaScript para preenchimento automático de campos no Django Admin
// Arquivo: static/admin/js/noticia_auto_fill.js

(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Verificar se estamos na página de edição de notícia
        if (!$('#noticia_form').length) {
            return;
        }
        
        // Adicionar botão de preenchimento automático
        addAutoFillButton();
        
        // Detectar mudanças no título para sugerir slug e fonte URL
        $('#id_titulo').on('input', function() {
            autoGenerateSlug();
            autoGenerateFonteUrl();
        });
        
        // Detectar mudanças na categoria para atualizar alt text
        $('#id_categoria').on('change', function() {
            updateImageAltText();
        });
    });
    
    function addAutoFillButton() {
        // Encontrar o campo de título
        var tituloField = $('#id_titulo');
        if (!tituloField.length) return;
        
        // Criar botão de preenchimento automático
        var autoFillButton = $('<button type="button" class="btn btn-info" id="auto-fill-btn" style="margin-left: 10px;">🤖 Preencher Automaticamente</button>');
        
        // Adicionar botão após o campo de título
        tituloField.after(autoFillButton);
        
        // Adicionar evento de clique
        autoFillButton.on('click', function() {
            performAutoFill();
        });
        
        // Adicionar estilo ao botão
        autoFillButton.css({
            'background-color': '#17a2b8',
            'border-color': '#17a2b8',
            'color': 'white',
            'padding': '5px 10px',
            'border-radius': '4px',
            'cursor': 'pointer',
            'font-size': '12px'
        });
    }
    
    function autoGenerateSlug() {
        var titulo = $('#id_titulo').val();
        if (!titulo) return;
        
        // Gerar slug baseado no título
        var slug = titulo
            .toLowerCase()
            .replace(/[^a-z0-9\s-]/g, '') // Remover caracteres especiais
            .replace(/\s+/g, '-') // Substituir espaços por hífens
            .replace(/-+/g, '-') // Remover hífens duplicados
            .replace(/^-|-$/g, ''); // Remover hífens do início/fim
        
        // Limitar tamanho do slug
        slug = slug.substring(0, 180);
        
        // Preencher campo slug se estiver vazio
        var slugField = $('#id_slug');
        if (!slugField.val()) {
            slugField.val(slug);
        }
    }
    
    function autoGenerateFonteUrl() {
        var titulo = $('#id_titulo').val();
        if (!titulo) return;
        
        // Gerar fonte URL SEO-friendly baseada no título
        var tituloSlug = titulo
            .toLowerCase()
            .replace(/[^a-z0-9\s-]/g, '') // Remover caracteres especiais
            .replace(/\s+/g, '-') // Substituir espaços por hífens
            .replace(/-+/g, '-') // Remover hífens duplicados
            .replace(/^-|-$/g, ''); // Remover hífens do início/fim
        
        // Limitar tamanho do slug do título
        tituloSlug = tituloSlug.substring(0, 30);
        
        // Gerar timestamp atual
        var now = new Date();
        var timestamp = now.getFullYear().toString() + 
                       (now.getMonth() + 1).toString().padStart(2, '0') + 
                       now.getDate().toString().padStart(2, '0');
        
        // Gerar ID único simples
        var uniqueId = Math.random().toString(36).substring(2, 8);
        
        // Criar fonte URL SEO-friendly
        var fonteUrl = `radarbr-${tituloSlug}-${timestamp}-${uniqueId}`;
        
        // Preencher campo fonte URL se estiver vazio
        var fonteUrlField = $('#id_fonte_url');
        if (!fonteUrlField.val()) {
            fonteUrlField.val(fonteUrl);
        }
    }
    
    function updateImageAltText() {
        var titulo = $('#id_titulo').val();
        var categoria = $('#id_categoria option:selected').text();
        
        if (!titulo) return;
        
        var altText = '';
        if (categoria && categoria !== '---------') {
            altText = `Imagem sobre ${categoria.toLowerCase()} - ${titulo.substring(0, 30)}`;
        } else {
            altText = `Imagem relacionada a ${titulo.substring(0, 50)}`;
        }
        
        // Preencher campo alt text se estiver vazio
        var altField = $('#id_imagem_alt');
        if (!altField.val()) {
            altField.val(altText);
        }
    }
    
    function performAutoFill() {
        var titulo = $('#id_titulo').val().trim();
        var categoriaId = $('#id_categoria').val();
        
        if (!titulo) {
            alert('Por favor, digite um título antes de usar o preenchimento automático.');
            return;
        }
        
        // Mostrar loading
        var button = $('#auto-fill-btn');
        var originalText = button.text();
        button.text('⏳ Preenchendo...').prop('disabled', true);
        
        // Fazer requisição AJAX
        $.ajax({
            url: '../auto-fill/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                titulo: titulo,
                categoria_id: categoriaId
            }),
            success: function(response) {
                if (response.success) {
                    // Preencher campos automaticamente
                    fillFields(response.data);
                    
                    // Mostrar mensagem de sucesso
                    showMessage('✅ Campos preenchidos automaticamente!', 'success');
                } else {
                    showMessage('❌ Erro: ' + response.error, 'error');
                }
            },
            error: function(xhr) {
                var errorMsg = 'Erro ao preencher campos automaticamente.';
                try {
                    var response = JSON.parse(xhr.responseText);
                    errorMsg = response.error || errorMsg;
                } catch (e) {
                    // Usar mensagem padrão
                }
                showMessage('❌ ' + errorMsg, 'error');
            },
            complete: function() {
                // Restaurar botão
                button.text(originalText).prop('disabled', false);
            }
        });
    }
    
    function fillFields(data) {
        // Preencher slug
        if (data.slug) {
            $('#id_slug').val(data.slug);
        }
        
        // Preencher fonte URL
        if (data.fonte_url) {
            $('#id_fonte_url').val(data.fonte_url);
        }
        
        // Preencher nome da fonte
        if (data.fonte_nome) {
            $('#id_fonte_nome').val(data.fonte_nome);
        }
        
        // Preencher alt text da imagem
        if (data.imagem_alt) {
            $('#id_imagem_alt').val(data.imagem_alt);
        }
        
        // Preencher créditos da imagem
        if (data.imagem_credito) {
            $('#id_imagem_credito').val(data.imagem_credito);
        }
        
        // Preencher licença da imagem
        if (data.imagem_licenca) {
            $('#id_imagem_licenca').val(data.imagem_licenca);
        }
        
        // Destacar campos preenchidos
        highlightFilledFields();
    }
    
    function highlightFilledFields() {
        var fields = ['#id_slug', '#id_fonte_url', '#id_fonte_nome', '#id_imagem_alt', '#id_imagem_credito', '#id_imagem_licenca'];
        
        fields.forEach(function(fieldId) {
            var field = $(fieldId);
            if (field.val()) {
                field.css('background-color', '#d4edda');
                setTimeout(function() {
                    field.css('background-color', '');
                }, 2000);
            }
        });
    }
    
    function showMessage(message, type) {
        // Remover mensagens anteriores
        $('.auto-fill-message').remove();
        
        // Criar nova mensagem
        var messageDiv = $('<div class="auto-fill-message" style="margin: 10px 0; padding: 10px; border-radius: 4px; font-weight: bold;"></div>');
        
        if (type === 'success') {
            messageDiv.css({
                'background-color': '#d4edda',
                'color': '#155724',
                'border': '1px solid #c3e6cb'
            });
        } else {
            messageDiv.css({
                'background-color': '#f8d7da',
                'color': '#721c24',
                'border': '1px solid #f5c6cb'
            });
        }
        
        messageDiv.text(message);
        
        // Adicionar mensagem após o botão
        $('#auto-fill-btn').after(messageDiv);
        
        // Remover mensagem após 5 segundos
        setTimeout(function() {
            messageDiv.fadeOut(function() {
                $(this).remove();
            });
        }, 5000);
    }
    
})(django.jQuery);

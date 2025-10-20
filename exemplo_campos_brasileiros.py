# Exemplo de uso dos campos brasileiros do django-localflavor
# Este arquivo demonstra como usar os campos específicos do Brasil

from django.db import models
from localflavor.br.models import BRCPFField, BRCNPJField, BRPostalCodeField, BRStateField
from localflavor.br.forms import BRCPFFormField, BRCNPJFormField, BRPostalCodeFormField, BRStateFormField

class ExemploModeloBrasileiro(models.Model):
    """
    Exemplo de modelo usando campos específicos do Brasil
    """
    # CPF (Cadastro de Pessoa Física)
    cpf = BRCPFField(
        verbose_name="CPF",
        help_text="Digite apenas os números do CPF"
    )
    
    # CNPJ (Cadastro Nacional da Pessoa Jurídica)
    cnpj = BRCNPJField(
        verbose_name="CNPJ",
        help_text="Digite apenas os números do CNPJ"
    )
    
    # CEP (Código de Endereçamento Postal)
    cep = BRPostalCodeField(
        verbose_name="CEP",
        help_text="Digite o CEP no formato 00000-000"
    )
    
    # Estado (UF)
    estado = BRStateField(
        verbose_name="Estado",
        help_text="Selecione o estado"
    )
    
    # Campos adicionais
    nome = models.CharField(max_length=100, verbose_name="Nome")
    email = models.EmailField(verbose_name="E-mail")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    
    class Meta:
        verbose_name = "Exemplo Brasileiro"
        verbose_name_plural = "Exemplos Brasileiros"
    
    def __str__(self):
        return f"{self.nome} - {self.cpf}"

# Exemplo de formulário personalizado
from django import forms

class ExemploFormularioBrasileiro(forms.ModelForm):
    """
    Exemplo de formulário usando campos específicos do Brasil
    """
    class Meta:
        model = ExemploModeloBrasileiro
        fields = ['nome', 'cpf', 'cnpj', 'cep', 'estado', 'email', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS aos campos brasileiros
        self.fields['cpf'].widget.attrs.update({'class': 'form-control'})
        self.fields['cnpj'].widget.attrs.update({'class': 'form-control'})
        self.fields['cep'].widget.attrs.update({'class': 'form-control'})
        self.fields['estado'].widget.attrs.update({'class': 'form-control'})

# Exemplo de validação personalizada
def validar_cpf_cnpj(value):
    """
    Função de exemplo para validação personalizada
    """
    # O django-localflavor já faz a validação automática
    # Esta função é apenas um exemplo de como você pode adicionar
    # validações extras se necessário
    return value

# Exemplo de uso em views
from django.shortcuts import render
from django.contrib import messages

def exemplo_view(request):
    """
    Exemplo de view usando os campos brasileiros
    """
    if request.method == 'POST':
        form = ExemploFormularioBrasileiro(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados salvos com sucesso!')
            return redirect('exemplo_sucesso')
    else:
        form = ExemploFormularioBrasileiro()
    
    return render(request, 'exemplo_template.html', {'form': form})

# Exemplo de template (HTML)
template_exemplo = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo Campos Brasileiros</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Formulário com Campos Brasileiros</h1>
        <form method="post">
            {% csrf_token %}
            <div class="mb-3">
                <label for="{{ form.nome.id_for_label }}" class="form-label">Nome</label>
                {{ form.nome }}
            </div>
            <div class="mb-3">
                <label for="{{ form.cpf.id_for_label }}" class="form-label">CPF</label>
                {{ form.cpf }}
                <div class="form-text">{{ form.cpf.help_text }}</div>
            </div>
            <div class="mb-3">
                <label for="{{ form.cnpj.id_for_label }}" class="form-label">CNPJ</label>
                {{ form.cnpj }}
                <div class="form-text">{{ form.cnpj.help_text }}</div>
            </div>
            <div class="mb-3">
                <label for="{{ form.cep.id_for_label }}" class="form-label">CEP</label>
                {{ form.cep }}
                <div class="form-text">{{ form.cep.help_text }}</div>
            </div>
            <div class="mb-3">
                <label for="{{ form.estado.id_for_label }}" class="form-label">Estado</label>
                {{ form.estado }}
                <div class="form-text">{{ form.estado.help_text }}</div>
            </div>
            <div class="mb-3">
                <label for="{{ form.email.id_for_label }}" class="form-label">E-mail</label>
                {{ form.email }}
            </div>
            <div class="mb-3">
                <label for="{{ form.telefone.id_for_label }}" class="form-label">Telefone</label>
                {{ form.telefone }}
            </div>
            <button type="submit" class="btn btn-primary">Salvar</button>
        </form>
    </div>
</body>
</html>
"""


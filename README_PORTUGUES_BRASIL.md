# Pacote de Localização Português Brasil - Django

Este projeto agora está configurado com suporte completo ao português brasileiro usando o pacote `django-localflavor`.

## O que foi instalado e configurado:

### 1. Pacote django-localflavor
- **Instalado**: `django-localflavor==5.0`
- **Funcionalidade**: Fornece campos específicos para o Brasil (CPF, CNPJ, CEP, Estados, etc.)

### 2. Configurações no settings.py
- ✅ Idioma configurado: `pt-br`
- ✅ Fuso horário: `America/Sao_Paulo`
- ✅ Formatação de números brasileira (ponto para milhares, vírgula para decimais)
- ✅ Formatação de datas brasileira (dd/mm/aaaa)
- ✅ Aplicação `localflavor` adicionada ao `INSTALLED_APPS`

### 3. Campos disponíveis para uso:

#### BRCPFField
```python
from localflavor.br.models import BRCPFField

cpf = BRCPFField(verbose_name="CPF")
```

#### BRCNPJField
```python
from localflavor.br.models import BRCNPJField

cnpj = BRCNPJField(verbose_name="CNPJ")
```

#### BRPostalCodeField
```python
from localflavor.br.models import BRPostalCodeField

cep = BRPostalCodeField(verbose_name="CEP")
```

#### BRStateField
```python
from localflavor.br.models import BRStateField

estado = BRStateField(verbose_name="Estado")
```

### 4. Validações automáticas:
- ✅ CPF: Validação de dígitos verificadores
- ✅ CNPJ: Validação de dígitos verificadores
- ✅ CEP: Validação de formato (00000-000)
- ✅ Estados: Lista completa dos estados brasileiros

### 5. Formatação automática:
- ✅ Números: 1.000.000,50 (formato brasileiro)
- ✅ Datas: 15/10/2025 (formato brasileiro)
- ✅ Horários: 15/10/2025 14:30 (formato brasileiro)

## Como usar:

### 1. Em modelos Django:
```python
from django.db import models
from localflavor.br.models import BRCPFField, BRCNPJField

class Pessoa(models.Model):
    nome = models.CharField(max_length=100)
    cpf = BRCPFField(verbose_name="CPF")
    cnpj = BRCNPJField(verbose_name="CNPJ", blank=True, null=True)
```

### 2. Em formulários:
```python
from django import forms
from localflavor.br.forms import BRCPFFormField, BRCNPJFormField

class PessoaForm(forms.Form):
    nome = forms.CharField(max_length=100)
    cpf = BRCPFFormField(label="CPF")
    cnpj = BRCNPJFormField(label="CNPJ", required=False)
```

### 3. Em templates:
```html
<!-- Os campos são automaticamente formatados -->
{{ form.cpf }}  <!-- Exibe com máscara -->
{{ form.cep }}  <!-- Exibe com máscara -->
{{ form.estado }}  <!-- Exibe lista de estados -->
```

## Benefícios:

1. **Validação automática**: CPF e CNPJ são validados automaticamente
2. **Formatação brasileira**: Números e datas no formato brasileiro
3. **Campos específicos**: Estados, CEP, CPF, CNPJ prontos para uso
4. **Interface amigável**: Mensagens de erro em português
5. **Compatibilidade**: Funciona com Django admin e formulários

## Arquivos modificados:

- ✅ `requirements.txt` - Adicionado django-localflavor
- ✅ `core/settings.py` - Configurações brasileiras
- ✅ `exemplo_campos_brasileiros.py` - Exemplo de uso

## Próximos passos:

1. Use os campos brasileiros em seus modelos
2. Crie formulários com validação automática
3. Personalize as mensagens de erro se necessário
4. Teste a formatação em diferentes navegadores

O pacote está pronto para uso! 🎉


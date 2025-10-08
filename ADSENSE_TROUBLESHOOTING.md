# Troubleshooting AdSense - Erros 400

## Problema Identificado
Os erros 400 nos anúncios do AdSense são causados por:

1. **DEBUG=True** - AdSense não funciona em modo debug local
2. **Site não aprovado** - AdSense precisa aprovar o domínio
3. **Bloqueadores de anúncios** - uBlock Origin, AdBlock, etc.

## Soluções Implementadas

### 1. Sistema de Fallback
- **Local (DEBUG=True):** Mostra placeholders em vez de anúncios
- **Produção (DEBUG=False):** Mostra anúncios reais
- **Slots inválidos:** Mostra placeholder com aviso

### 2. Validação de Slots
- Verifica se slots começam com "123456789" (inválidos)
- Mostra aviso para slots inválidos
- Comando `test_adsense` para diagnosticar

### 3. Configuração Correta
- ✅ ADSENSE_CLIENT: ca-pub-3913403142217011
- ✅ GA4_ID: G-JMQVXP0KHQ
- ✅ Slots válidos configurados
- ✅ ads.txt criado

## Como Testar

### Local (com erros 400):
```bash
python manage.py test_adsense
# Mostra placeholders em vez de anúncios
```

### Produção (sem erros):
1. Deploy no Render com DEBUG=False
2. Aguardar 2-48 horas para aprovação
3. Testar em modo incógnito (sem bloqueadores)

## Próximos Passos

1. **Deploy no Render** com DEBUG=False
2. **Aguardar aprovação** do AdSense (até 48h)
3. **Testar em produção** sem bloqueadores
4. **Monitorar logs** para confirmar funcionamento

## Comandos Úteis

```bash
# Testar configuração
python manage.py test_adsense

# Executar automação
python manage.py auto_publish

# Ping sitemap
python manage.py ping_sitemap
```

## Status Atual
- ✅ Configuração correta
- ✅ Slots válidos
- ✅ Sistema de fallback
- ⏳ Aguardando deploy em produção

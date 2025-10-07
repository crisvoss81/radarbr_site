# Troubleshooting - Comando trends_publish

## Problema: Busca por tópicos no Google Trends não funciona

### Diagnóstico Rápido

Execute o script de teste para diagnosticar problemas:

```bash
python test_gnews.py
```

### Soluções Comuns

#### 1. Problemas de Conectividade
- **Sintoma**: Erro de timeout ou conexão recusada
- **Solução**: 
  - Verificar conexão com internet
  - Testar acesso a `news.google.com`
  - Verificar configurações de proxy/firewall

#### 2. Problemas com a Biblioteca GNews
- **Sintoma**: Erro ao importar ou inicializar GNews
- **Solução**:
  ```bash
  pip install --upgrade gnews
  pip install --upgrade requests
  ```

#### 3. Rate Limiting do Google News
- **Sintoma**: Poucos ou nenhum resultado retornado
- **Solução**:
  - Aguardar alguns minutos antes de executar novamente
  - Usar tópicos manuais como fallback

#### 4. Restrições Geográficas
- **Sintoma**: Resultados vazios ou irrelevantes
- **Solução**:
  - Verificar se o servidor está no Brasil
  - Considerar usar VPN se necessário

### Uso do Comando Melhorado

#### Modo Normal (Busca Automática)
```bash
python manage.py trends_publish --limit 5
```

#### Modo Debug (Mais Informações)
```bash
python manage.py trends_publish --debug --limit 3
```

#### Modo Manual (Tópicos Específicos)
```bash
python manage.py trends_publish --topics "Inteligência Artificial" "Economia Digital" "Sustentabilidade"
```

#### Forçar Publicação (Ignorar Duplicatas)
```bash
python manage.py trends_publish --force --limit 2
```

### Melhorias Implementadas

1. **Múltiplos Fallbacks**: Se Top News falhar, tenta termos específicos
2. **Filtros Melhorados**: Exclui redes sociais dos resultados
3. **Limpeza de Títulos**: Remove fontes e caracteres especiais
4. **Logs Detalhados**: Modo debug mostra cada etapa
5. **Tópicos Manuais**: Opção para usar tópicos específicos
6. **Tratamento de Erros**: Captura e reporta erros específicos

### Estrutura de Fallback

1. **Primeiro**: Busca Top News do Google News Brasil
2. **Segundo**: Tenta termos específicos:
   - "notícias do Brasil"
   - "política Brasil"
   - "economia Brasil"
   - "tecnologia Brasil"
   - "esportes Brasil"
3. **Terceiro**: Usa tópicos manuais se fornecidos
4. **Último**: Retorna erro se nada funcionar

### Logs de Debug

Com `--debug`, você verá:
- Status da inicialização do GNews
- Número de artigos retornados por cada método
- Erros específicos de cada tentativa
- Lista final de tópicos processados
- Detalhes do processamento de cada artigo

### Monitoramento

Para monitorar o funcionamento:
1. Execute com `--debug` para ver logs detalhados
2. Verifique os logs do Django para erros
3. Monitore a criação de artigos no admin
4. Use o script `test_gnews.py` para diagnóstico rápido

### Contato

Se os problemas persistirem:
1. Execute `python test_gnews.py` e compartilhe a saída
2. Verifique os logs do Django
3. Teste a conectividade com `news.google.com`
4. Considere usar tópicos manuais como solução temporária

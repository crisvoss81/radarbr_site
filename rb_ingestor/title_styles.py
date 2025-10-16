# rb_ingestor/title_styles.py
import random
from typing import Dict, List

class TitleStyleManager:
    def __init__(self):
        self.styles = {
            "pergunta_direta": {
                "name": "Pergunta Direta",
                "description": "Títulos em formato de pergunta direta e objetiva",
                "templates": [
                    "O que {keyword} anuncia sobre {keyword}?",
                    "Como {keyword} está mudando o cenário atual?",
                    "Por que {keyword} está em destaque hoje?",
                    "O que esperar de {keyword} nos próximos dias?",
                    "Como {keyword} impacta o mercado atual?"
                ]
            },
            "analise_profunda": {
                "name": "Análise Profunda",
                "description": "Títulos que sugerem análise detalhada e investigativa",
                "templates": [
                    "Análise completa: {keyword} e suas implicações",
                    "Entenda o impacto real de {keyword}",
                    "Investigação: os bastidores de {keyword}",
                    "Análise detalhada sobre {keyword}",
                    "O que realmente está por trás de {keyword}"
                ]
            },
            "urgente_atual": {
                "name": "Urgente/Atual",
                "description": "Títulos que transmitem urgência e atualidade",
                "templates": [
                    "{keyword}: últimas atualizações importantes",
                    "Breaking: {keyword} em desenvolvimento",
                    "{keyword}: o que aconteceu agora",
                    "Atualização urgente sobre {keyword}",
                    "{keyword}: novidades que você precisa saber"
                ]
            },
            "explicativo_didatico": {
                "name": "Explicativo/Didático",
                "description": "Títulos educativos que explicam conceitos",
                "templates": [
                    "Entenda tudo sobre {keyword}",
                    "Guia completo: {keyword} explicado",
                    "O que você precisa saber sobre {keyword}",
                    "Tudo sobre {keyword}: guia definitivo",
                    "Explicando {keyword} de forma simples"
                ]
            },
            "impacto_social": {
                "name": "Impacto Social",
                "description": "Títulos focados no impacto social e na sociedade",
                "templates": [
                    "Como {keyword} afeta a sociedade brasileira",
                    "O impacto social de {keyword} no Brasil",
                    "{keyword}: consequências para a população",
                    "Como {keyword} muda a vida das pessoas",
                    "O que {keyword} significa para o Brasil"
                ]
            },
            "economico_financeiro": {
                "name": "Econômico/Financeiro",
                "description": "Títulos focados em aspectos econômicos e financeiros",
                "templates": [
                    "{keyword}: impacto na economia brasileira",
                    "Análise econômica: {keyword} e o mercado",
                    "Como {keyword} afeta as finanças",
                    "{keyword}: consequências econômicas",
                    "O valor econômico de {keyword}"
                ]
            },
            "politico_institucional": {
                "name": "Político/Institucional",
                "description": "Títulos focados em aspectos políticos e institucionais",
                "templates": [
                    "{keyword}: posicionamento político atual",
                    "Como {keyword} influencia a política",
                    "{keyword}: implicações institucionais",
                    "O papel político de {keyword}",
                    "{keyword}: análise do cenário político"
                ]
            },
            "tecnologico_inovacao": {
                "name": "Tecnológico/Inovação",
                "description": "Títulos focados em tecnologia e inovação",
                "templates": [
                    "{keyword}: a tecnologia por trás",
                    "Inovação em {keyword}: o que há de novo",
                    "Como a tecnologia transforma {keyword}",
                    "{keyword}: avanços tecnológicos",
                    "O futuro tecnológico de {keyword}"
                ]
            }
        }
    
    def get_random_style(self) -> str:
        """Retorna o nome de um estilo aleatório."""
        return random.choice(list(self.styles.keys()))
    
    def get_style_info(self, style_name: str) -> Dict:
        """Retorna as informações de um estilo específico."""
        return self.styles.get(style_name, self.styles["pergunta_direta"])
    
    def generate_title(self, style_name: str, keyword: str) -> str:
        """Gera um título baseado no estilo e palavra-chave."""
        style_info = self.get_style_info(style_name)
        template = random.choice(style_info["templates"])
        
        # Substitui {keyword} pela palavra-chave
        title = template.format(keyword=keyword)
        
        # Limita a 120 caracteres
        if len(title) > 120:
            title = title[:117] + "..."
        
        return title
    
    def generate_smart_title(self, keyword: str, base_title: str = None) -> str:
        """Gera um título inteligente baseado na palavra-chave e título base."""
        if not base_title:
            # Se não há título base, usar apenas o estilo
            style = self.get_random_style()
            return self.generate_title(style, keyword)
        
        # Limpar o título base removendo portais
        clean_title = self._clean_title_from_portals(base_title)
        
        # Reescrever o título limpo mantendo a palavra-chave
        rewritten_title = self._rewrite_title_intelligently(clean_title, keyword)
        
        return rewritten_title
    
    def _clean_title_from_portals(self, title: str) -> str:
        """Remove marcas de portais e colunistas do título."""
        portals_colunistas = [
            'G1', 'Globo', 'Folha', 'Estadão', 'UOL', 'Terra', 'R7', 'IG', 
            'Exame', 'Metrópoles', 'O Globo', 'CNN', 'BBC', 'Reuters',
            'Veja', 'IstoÉ', 'Época', 'CartaCapital', 'Brasil247', '247',
            'Gazeta do Povo', 'Zero Hora', 'Correio Braziliense'
        ]
        
        clean_title = title
        for portal in portals_colunistas:
            patterns = [
                f' - {portal}', f' | {portal}', f' ({portal})',
                f' – {portal}', f' — {portal}', f' • {portal}',
                f'/{portal}', f'\\{portal}'
            ]
            for pattern in patterns:
                clean_title = clean_title.replace(pattern, '')
        
        # Remover menções a autores/colunistas comuns
        author_patterns = [
            'por ', 'Por ', '(por ', '(Por ', 'coluna de ', 'Coluna de '
        ]
        for a in author_patterns:
            if a in clean_title:
                # remove a partir da menção
                clean_title = clean_title.split(a)[0].strip()
        
        return clean_title.strip()
    
    def _rewrite_title_intelligently(self, clean_title: str, keyword: str) -> str:
        """
        Reescreve o título de forma inteligente usando IA para buscar sinônimos dinamicamente.
        """
        try:
            # Usar IA para reescrever o título com sinônimos
            rewritten_title = self._rewrite_with_ai(clean_title, keyword)
            return rewritten_title
        except Exception as e:
            print(f"Erro na reescrita com IA: {e}")
            # Fallback para método simples
            return self._rewrite_title_simple(clean_title, keyword)
    
    def _rewrite_with_ai(self, clean_title: str, keyword: str) -> str:
        """
        Usa IA para reescrever o título com sinônimos e variações inteligentes.
        """
        import openai
        from django.conf import settings
        
        # Calcular margem de tamanho baseada no título original
        base_len = len(clean_title)
        min_len = int(base_len * 0.85)  # 15% menor
        max_len = int(base_len * 1.15)  # 15% maior
        
        prompt = f"""
Você é um editor de notícias especializado em reescrever títulos de forma única e SEO-friendly.

TAREFA: Reescreva o título abaixo trocando palavras por sinônimos e reorganizando a estrutura, mantendo o significado e a palavra-chave obrigatória.

TÍTULO ORIGINAL: "{clean_title}"
PALAVRA-CHAVE OBRIGATÓRIA: "{keyword}"

REGRAS:
1. OBRIGATÓRIO: A palavra-chave "{keyword}" deve aparecer no título reescrito
2. Troque palavras por sinônimos naturais em português brasileiro
3. Reorganize a ordem das palavras mantendo coerência gramatical
4. Mantenha o significado original
5. Tamanho: entre {min_len} e {max_len} caracteres
6. Use capitalização editorial (primeira letra de palavras importantes)
7. NÃO mencione portais ou colunistas
8. Saída APENAS o título reescrito, sem explicações

EXEMPLO:
Original: "Tesla pede que Suprema Corte restabeleça pagamento de US$ 56 bilhões de Musk"
Reescrito: "Tesla solicita que Corte Suprema restaure remuneração de US$ 56 bi para Musk"

TÍTULO REESCRITO:"""

        try:
            # Usar cliente v1 da OpenAI
            try:
                from openai import OpenAI as OpenAIClient
                client = OpenAIClient(api_key=settings.OPENAI_API_KEY)
                chat = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=120,
                    temperature=0.7
                )
                rewritten = chat.choices[0].message.content.strip()
            except Exception:
                # Fallback para pacote antigo, se presente
                rewritten = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=120,
                    temperature=0.7,
                    api_key=settings.OPENAI_API_KEY
                ).choices[0].message.content.strip()
            
            # Limpar possíveis aspas ou formatação extra
            rewritten = rewritten.strip('"').strip("'").strip()
            
            # Garantir que a palavra-chave está presente
            if keyword.lower() not in rewritten.lower():
                # Inserir palavra-chave se não estiver presente
                words = rewritten.split()
                if len(words) > 1:
                    words.insert(1, keyword)
                    rewritten = ' '.join(words)
                else:
                    rewritten = f"{keyword} {rewritten}"
            
            return rewritten
            
        except Exception as e:
            print(f"Erro na API OpenAI: {e}")
            raise e
    
    def _rewrite_title_simple(self, clean_title: str, keyword: str) -> str:
        """
        Método simples de fallback para reescrita de títulos.
        """
        import re
        
        title = clean_title
        
        # Garantir que a palavra-chave está presente
        if keyword.lower() not in title.lower():
            parts = title.split()
            insert_at = 1 if len(parts) > 1 else 0
            parts.insert(insert_at, keyword)
            title = ' '.join(parts)

        # Aplicar algumas substituições básicas
        replacements = {
            "pede que": "solicita que",
            "pede": "solicita", 
            "restabeleça": "restaure",
            "Suprema Corte": "Corte Suprema",
            "pagamento": "remuneração",
            "bilhões": "bi",
            "US$": "USD"
        }
        
        for old, new in replacements.items():
            title = title.replace(old, new)
        
        # Normalizar espaços
        title = re.sub(r"\s+", " ", title).strip()
        
        # Capitalização editorial
        title = self._capitalize_title(title)
        
        return title
    
    def _reorganize_title_words(self, title: str, keyword: str) -> str:
        """Reorganiza as palavras do título mantendo coerência gramatical."""
        words = title.split()
        
        # Se o título é muito curto, não reorganizar
        if len(words) <= 4:
            return title
        
        # Padrões de reorganização
        reorganization_patterns = [
            # Padrão 1: Mover palavra-chave para o início
            lambda w: [keyword] + [word for word in w if word != keyword],
            # Padrão 2: Mover palavra-chave para o meio
            lambda w: w[:len(w)//2] + [keyword] + [word for word in w[len(w)//2:] if word != keyword],
            # Padrão 3: Manter ordem mas trocar posições de palavras adjacentes
            lambda w: self._swap_adjacent_words(w),
            # Padrão 4: Manter ordem original (30% das vezes)
            lambda w: w
        ]
        
        # Escolher padrão aleatório
        pattern = random.choice(reorganization_patterns)
        reorganized = pattern(words)
        
        return ' '.join(reorganized)
    
    def _swap_adjacent_words(self, words: list) -> list:
        """Troca posições de palavras adjacentes aleatoriamente."""
        if len(words) <= 2:
            return words
        
        # Escolher posição aleatória para trocar
        pos = random.randint(0, len(words) - 2)
        words[pos], words[pos + 1] = words[pos + 1], words[pos]
        return words
    
    def _capitalize_title(self, title: str) -> str:
        """Capitaliza palavras importantes do título."""
        # Palavras que devem ficar em minúscula
        lowercase_words = {'de', 'da', 'do', 'das', 'dos', 'e', 'ou', 'em', 'na', 'no', 'nas', 'nos', 'por', 'para', 'com', 'sem', 'sobre', 'entre', 'durante', 'após', 'antes'}
        
        words = title.split()
        capitalized_words = []
        
        for i, word in enumerate(words):
            # Primeira palavra sempre maiúscula
            if i == 0:
                capitalized_words.append(word.capitalize())
            # Palavras importantes (não artigos/preposições)
            elif word.lower() not in lowercase_words:
                capitalized_words.append(word.capitalize())
            else:
                capitalized_words.append(word.lower())
        
        return ' '.join(capitalized_words)

# Instância global
title_style_manager = TitleStyleManager()
